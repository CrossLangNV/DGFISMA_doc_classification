from typing import List
import json
import os
import pickle
import string
import configparser
from configparser import ConfigParser

from base64 import b64decode, b64encode

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

PATH=os.getcwd()

CONFIG = configparser.ConfigParser()
CONFIG.read( os.path.join( PATH, "train.config"  ) )

def size_mb(docs):
    return sum(len(s.encode('utf-8')) for s in docs) / 1e6

def train( config:ConfigParser=CONFIG):
    
    #1)Data

    #create outputdir

    os.makedirs( config[ 'INPUT/OUTPUT' ].get('OUTPUT_DIR') , exist_ok=True  )
    
    threshold=config[ 'TFIDF_PARAMETERS' ].getfloat( 'THRESHOLD_FEATURE_SELECTION' )
    max_features=config[ 'TFIDF_PARAMETERS' ].getint( 'MAX_FEATURES' )
            
    #read in (train data)
    data=pd.read_csv(  config[ "INPUT/OUTPUT" ].get('INPUT_FILE')  , sep='\t' , header=None ) 

    train_data=data[0].tolist()
    train_labels=data[2].tolist()
    
    if config[ 'TFIDF_PARAMETERS' ].getboolean( 'REMOVE_PUNCTUATION_NUMBERS' ):
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

    if config["TFIDF_PARAMETERS"].get( 'LANGUAGE' )=='':
        language=None
    
    print( "Using Tfidf Vectorizer." )
    vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5,
                             stop_words= config["TFIDF_PARAMETERS"].get( 'LANGUAGE' ) )

    if config[ 'TFIDF_PARAMETERS' ].getboolean( 'BALANCED' ):
        print("Using balanced class weights.")
        class_weight = 'balanced'
    else:
        class_weight = None
    
    if config["TFIDF_PARAMETERS"].getboolean( 'FEATURE_SELECTION_SVC' ):
        print( f"Extracting features via sklearn.feature_selection. SelectKbest using LinearSVC.")
        feature_selection=SelectFromModel(estimator=LinearSVC(penalty=config["TFIDF_PARAMETERS"].get( 'PENALTY_FEATURE_SELECTION'), dual=False,
                                                          tol=1e-3, class_weight=class_weight ), threshold=threshold, max_features=max_features ) 
        
    else:
        feature_selection=None

    classifier=LinearSVC(penalty=config[ 'TFIDF_PARAMETERS' ].get( 'PENALTY' ) , loss="squared_hinge" , dual=config[ 'TFIDF_PARAMETERS'].getboolean('DUAL') , class_weight=class_weight )
    
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
        'vectorizer__max_df': [0.5 ] ,#[0.3,0.4,0.5,0.6,0.7 ]
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
        'vectorizer__max_df': [0.5  ] ,
        'classification__base_estimator__C': list(np.logspace(-3, 1, 5)) 
        }


    scoring=['f1', 'precision', 'recall']

    search = GridSearchCV(clf, param_grid, scoring=scoring , n_jobs=config[ 'TFIDF_PARAMETERS' ].getint( 'JOBS' ) , cv=5, refit=scoring[0], return_train_score=True   )

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
    
    json.dump(scores_dict, open( os.path.join( config[ "INPUT/OUTPUT" ].get('OUTPUT_DIR'), "cross_validation_scores.json"  ), "w" ))
    
    if config["TFIDF_PARAMETERS"].getboolean( 'FEATURE_SELECTION_SVC' ):

        print("Selected features are: \n")
        
        select=search.best_estimator_.named_steps[ 'feature_selection' ]
        vec=search.best_estimator_.named_steps[ 'vectorizer' ]
        
        i=0

        assert( select.get_support().shape[0]  ==  len(  vec.get_feature_names() ) )
        for selected, feature in zip( select.get_support(), vec.get_feature_names()  ):
            if selected:
                i=i+1
                print(feature)

        print( f"{i} selected features from total of {len( vec.get_feature_names() )}" )
    
    #3) Save the classifier

    pickle.dump( search.best_estimator_ , open( os.path.join( config[ "INPUT/OUTPUT" ].get('OUTPUT_DIR'), "model.p"  ), "wb" ) )
    
if __name__ == "__main__":
    train()