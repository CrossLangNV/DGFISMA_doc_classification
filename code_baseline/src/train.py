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
    parser.add_argument("--vectorizer_type", dest="vectorizer_type", type=str , default='tfidf' , choices=[ 'tfidf', 'hashing'] , help="vectorizer used for feature extraction" , required=False ) 
    parser.add_argument("--n_features", dest="n_features", type=int ,default=2**16,
                        help="nr of features when using the hashing vectorizer (ignored when tfidf is used", required=False)
    parser.add_argument("--language", dest="language", type=str , default='english' , help="language used by Vectorizer (i.e. stopwords)" , required=False )
    #Feature selection:
    parser.add_argument("--n_select_chi2", dest="n_select_chi2", type=int ,default=None,
                        help="nr of features selected by chi2 test. Ignored when set to 'None'", required=False)
    parser.add_argument("--feature_selection_svc", dest="feature_selection_svc", action='store_true' ,default=False,
                        help="If set to True, using sklearn.feature_selection.SelectFromModel with linear SVC", required=False)
    parser.add_argument("--penalty_feature_selection", dest="penalty_feature_selection", type=str, default="l1", choices=['l1','l2'], help="penalty of linear SVC classifier used for feature selection", required=False)
    #Parameters classfier:
    parser.add_argument("--penalty", dest="penalty", type=str ,default="l2", choices=[ 'l1','l2' ],
                        help="penalty of linear SVC classifier used for classification", required=False)
    parser.add_argument("--loss", dest="loss", type=str ,default="squared_hinge",choices=[ 'hinge','squared_hinge' ],
                        help='Specifies the loss function. Hinge is standard SVM loss, while squared_hinge is the square of the hinge loss.', required=False)
    parser.add_argument("--dual", dest="dual", action='store_true' ,default=False,
                        help="Solve the dual or primal optimization problem. Prefer dual=False when n_samples > n_features (i.e. when doing feature selection beforehand)", required=False)
    parser.add_argument( "--remove_punctuation_numbers", dest="remove_punctuation_numbers", action='store_true' ,default=False,
                        help="Whether to remove punctuation and numbers from the training data.", required=False  )
    parser.add_argument( "--balanced", dest="balanced", action="store_true", default=False,
                        help="The “balanced” mode automatically adjusts weights inversely proportional to class frequencies in the input data.", required=False)
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
    
    if args.vectorizer_type=='tfidf':
        print( "Using Tfidf Vectorizer." )
        vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5,
                                 stop_words= args.language )

    elif args.vectorizer_type=='hashing':  
        print( "Using Hashing Vectorizer." )
        vectorizer = HashingVectorizer(stop_words=args.language, alternate_sign=False,
                                       n_features=args.n_features)

    if args.n_select_chi2:
        print( f"Extracting {args.n_select_chi2} features by a chi-squared test.")
        ch2 = SelectKBest(chi2, k=args.n_select_chi2)
    else:
        ch2= None

    if args.feature_selection_svc:
        print( f"Extracting features via sklearn.feature_selection. SelectKbest using LinearSVC.")
        feature_selection=SelectFromModel(LinearSVC(penalty=args.penalty_feature_selection, dual=False,
                                                          tol=1e-3)) 
    else:
        feature_selection=None

    if args.balanced:
        print("Using balanced class weights.")
        class_weight = 'balanced'
    else:
        class_weight = None

    classifier=LinearSVC(penalty=args.penalty, loss=args.loss , dual=args.dual, class_weight=class_weight )
    #calibrated the classifier (for predict_proba): 
    calibrated_classifier = CalibratedClassifierCV(classifier , cv=5 ) 
    
    clf=Pipeline([
    ( 'vectorizer', vectorizer)  ,
    ( 'chisquare', ch2  )  ,
    ('feature_selection',  feature_selection  )   ,
    ('classification', calibrated_classifier  )
    ])

    clf.fit(  train_data , train_labels )
    scoring = ['f1', 'precision', 'recall']
    scores = cross_validate(clf, train_data, train_labels, cv=5, scoring=scoring, return_train_score=True)
    scores_dict = {
        'mean_train_f1': scores['train_f1'].mean(),
        'std_train_f1': scores['train_f1'].std() * 2,
        'mean_test_f1': scores['test_f1'].mean(),
        'std_test_f1': scores['test_f1'].std() * 2,
        'mean_train_precision': scores['train_precision'].mean(),
        'std_train_precision': scores['train_precision'].std() * 2,
        'mean_test_precision': scores['test_precision'].mean(),
        'std_test_precision': scores['test_precision'].std() * 2,
        'mean_train_recall': scores['train_recall'].mean(),
        'std_train_recall': scores['train_recall'].std() * 2,
        'mean_test_recall': scores['test_recall'].mean(),
        'std_test_recall': scores['test_recall'].std() * 2,
        'mean_fit_time': scores['fit_time'].mean(),
        'std_fit_time':  scores['fit_time'].std() * 2
    }
    json.dump(scores_dict, open( os.path.join( args.output_dir, "cross_validation_scores.json"  ), "w" ))

    #show the selected features (i.e. keywords used for classification):
    
    if args.feature_selection_svc and not args.n_select_chi2:

        print("Selected features are: \n")
        
        select=clf.named_steps['feature_selection']
        vec=clf.named_steps[ 'vectorizer' ]
        select.get_support()

        i=0

        assert( select.get_support().shape[0]  ==  len(  vec.get_feature_names() ) ) 
        for selected, feature in zip( select.get_support(), vec.get_feature_names()  ):
            if selected:
                i=i+1
                print(feature)

        print( f"{i} selected features" )
    
    
    
    #3) Save the classifier

    pickle.dump( clf , open( os.path.join( args.output_dir, "model.p"  ), "wb" ) )
    
    