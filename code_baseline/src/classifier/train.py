import logging
import numpy as np
from base64 import b64encode
from base64 import b64decode
import argparse
import os
import sys
from time import time
import pandas as pd
import pickle
import string
import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_selection import SelectFromModel
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn import metrics
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import cross_validate
from sklearn.model_selection import GridSearchCV


def size_mb(docs):
    return sum(len(s.encode('utf-8')) for s in docs) / 1e6

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    #Input-output:
    parser.add_argument("--filename", dest="filename",
                        help="path to the training data (tsv file with at each line: base64 encoded document \t label \t label_nr )", required=True)
    parser.add_argument("--output_dir", dest="output_dir",
                        help="path to the output folder", required=True)
    #Parameters for calculation of features:
    parser.add_argument("--vectorizer_type", dest="vectorizer_type", type=str , default='tfidf' , choices=[ 'tfidf', None] , help="vectorizer used for feature extraction" , required=False ) 
    parser.add_argument("--language", dest="language", type=str , default='english' , help="language used by Vectorizer (i.e. stopwords)" , required=False )
    #Feature selection:
    parser.add_argument("--feature_selection_svc", dest="feature_selection_svc", action='store_true' ,default=False,
                        help="If set to True, using sklearn.feature_selection.SelectFromModel with linear SVC", required=False)
    parser.add_argument("--penalty_feature_selection", dest="penalty_feature_selection", type=str, default="l1", choices=['l1','l2'], help="penalty of linear SVC classifier used for feature selection", required=False)
    #Parameters classfier:
    parser.add_argument("--penalty", dest="penalty", type=str ,default="l2", choices=[ 'l1','l2' ],
                        help="penalty of linear SVC classifier used for classification", required=False)
    parser.add_argument("--dual", dest="dual", action='store_true' ,default=False,
                        help="Solve the dual or primal optimization problem. Prefer dual=False when n_samples > n_features (i.e. when doing feature selection beforehand)", required=False)
    parser.add_argument( "--remove_punctuation_numbers", dest="remove_punctuation_numbers", action='store_true' ,default=False,
                        help="Whether to remove punctuation and numbers from the training data.", required=False  )
    parser.add_argument( "--balanced", dest="balanced", action="store_true", default=False,
                        help="The “balanced” mode automatically adjusts weights inversely proportional to class frequencies in the input data.", required=False)
    parser.add_argument( "--jobs", dest="jobs", type=int, default=-1,
                        help="Number of jobs to run in parallel. -1 means using all processors", required=False)
    args = parser.parse_args()
    
    
    #1)Data

    #create outputdir

    os.makedirs( args.output_dir, exist_ok=True  )

    #read in (train data)
    data=pd.read_csv(  args.filename  , sep='\t' , header=None ) 

    train_data=data[0].tolist()
    train_labels=data[2].tolist()
    del data

    
    if args.remove_punctuation_numbers:
        print( "Removing punctuation and numbers" )
        train_data=[ b64decode( doc ).decode().translate(str.maketrans('', '', string.punctuation+'0123456789'  )) for doc in train_data  ]
        
    else:
        train_data=[ b64decode( doc ).decode() for doc in train_data  ]
    
    data_train_size_mb = size_mb(train_data)

    print("%d documents - %0.3fMB (training set)" % (
        len(train_data), data_train_size_mb))
    print("%d categories" % len(  np.unique( train_labels  ).tolist()  ))
    print()

    #2)Train

    if args.language=='':
        args.language=None
    
    print( "Using Tfidf Vectorizer." )
    vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5,
                             stop_words= args.language )

    
    if args.balanced:
        print("Using balanced class weights.")
        class_weight = 'balanced'
    else:
        class_weight = None
    
    if args.feature_selection_svc:
        print( f"Extracting features via sklearn.feature_selection. SelectKbest using LinearSVC.")
        feature_selection=SelectFromModel(LinearSVC(penalty=args.penalty_feature_selection, dual=False,
                                                          tol=1e-3,class_weight=class_weight )) 
    else:
        feature_selection=None

    classifier=LinearSVC(penalty=args.penalty, loss="squared_hinge" , dual=args.dual, class_weight=class_weight )
    
    #calibrated the classifier (for predict_proba): 
    calibrated_classifier = CalibratedClassifierCV(classifier , cv=5 ) 
    
    if feature_selection:
        clf=Pipeline([
        ( 'vectorizer', vectorizer)  ,
        ('feature_selection',  feature_selection  )   ,
        ('classification', calibrated_classifier  )
        ])
        
        #grid
        param_grid = {
        'vectorizer__max_df': [0.3,0.4,0.5,0.6,0.7 ] ,
        'feature_selection__estimator__C': [1.0] ,
        'classification__base_estimator__C': list(np.logspace(-3, 1, 5)) 
        }
        
    else:
        clf=Pipeline([
        ( 'vectorizer', vectorizer)  ,
        ('classification', calibrated_classifier  )
        ])

        #grid
        param_grid = {
        'vectorizer__max_df': [0.3,0.4,0.5,0.6,0.7 ] ,
        'classification__base_estimator__C': list(np.logspace(-3, 1, 5)) 
        }


    scoring=['f1', 'precision', 'recall']

    search = GridSearchCV(clf, param_grid, scoring=scoring , n_jobs=args.jobs, cv=5, refit=scoring[0], return_train_score=True   )

    search.fit(train_data, train_labels)

    #show the selected features (i.e. keywords used for classification):

    scores_dict = {
    'mean_train_f1': search.cv_results_['mean_train_f1'][ search.best_index_],
    'std_train_f1': search.cv_results_['std_train_f1'][ search.best_index_] * 2,
    'mean_test_f1': search.cv_results_['mean_test_f1'][ search.best_index_],
    'std_test_f1': search.cv_results_['std_test_f1'][ search.best_index_] * 2,
    'mean_train_precision': search.cv_results_['mean_train_precision'][ search.best_index_],
    'std_train_precision': search.cv_results_['std_train_precision'][ search.best_index_] * 2,
    'mean_test_precision': search.cv_results_['mean_test_precision'][ search.best_index_],
    'std_test_precision': search.cv_results_['std_test_precision'][ search.best_index_] * 2,  
    'mean_train_recall': search.cv_results_['mean_train_recall'][ search.best_index_],
    'std_train_recall': search.cv_results_['std_train_recall'][ search.best_index_] * 2,
    'mean_test_recall': search.cv_results_['mean_test_recall'][ search.best_index_],
    'std_test_recall': search.cv_results_['std_test_recall'][ search.best_index_] * 2,   
    'mean_fit_time' : search.cv_results_['mean_fit_time'][ search.best_index_],
    'std_fit_time' : search.cv_results_['std_fit_time'][ search.best_index_]*2
    }
    
    json.dump(scores_dict, open( os.path.join( args.output_dir, "cross_validation_scores.json"  ), "w" ))
    
    if args.feature_selection_svc:

        print("Selected features are: \n")
        
        select=search.best_estimator_.named_steps[ 'feature_selection' ]
        vec=search.best_estimator_.named_steps[ 'vectorizer' ]
        
        i=0

        assert( select.get_support().shape[0]  ==  len(  vec.get_feature_names() ) ) 
        for selected, feature in zip( select.get_support(), vec.get_feature_names()  ):
            if selected:
                i=i+1
                print(feature)

        print( f"{i} selected features" )
    
    #3) Save the classifier

    pickle.dump( search.best_estimator_ , open( os.path.join( args.output_dir, "model.p"  ), "wb" ) )
    
    