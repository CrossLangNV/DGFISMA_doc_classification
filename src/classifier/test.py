import os
import argparse
import pickle
from base64 import b64encode, b64decode
import pandas as pd
import numpy as np
from sklearn import metrics
import string

def size_mb(docs):
    return sum(len(s.encode('utf-8')) for s in docs) / 1e6


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    #Input-output:
    parser.add_argument("--filename", dest="filename",
                        help="path to the test data (tsv file with at each line: base64 encoded document \t label \t label_nr )", required=True)
    parser.add_argument("--model_path", dest="model_path",
                        help="path to the classfier (python pickle format)", required=True)
    parser.add_argument("--output_file", dest="output_file",
                        help="output file with predicted labels", required=True)
    
    args = parser.parse_args()
    
    #read in (test data)
    data=pd.read_csv(  args.filename, sep='\t' , header=None ) 

    test_data=data[0].tolist()
    test_labels=data[2].tolist()
    
    del data
    
    remove_punctuation_numbers=True
    
    if remove_punctuation_numbers:
        print( "Removing punctuation and numbers" )
        test_data=[ b64decode( doc ).decode().translate(str.maketrans('', '', string.punctuation+'0123456789'  )) for doc in test_data  ]
        
    else:
        test_data=[ b64decode( doc ).decode() for doc in test_data  ]
    
    data_test_size_mb = size_mb(test_data)

    print("%d documents - %0.3fMB (test set)" % (
        len(test_data), data_test_size_mb))
    print("%d categories" % len(  np.unique( test_labels  ).tolist()  ))
    print()
    
    #load the classifier 

    clf = pickle.load( open(  args.model_path  , "rb" ) )

    pred=clf.predict( test_data  )
    pred_proba=clf.predict_proba( test_data )


    print(metrics.classification_report(test_labels, pred  ))
    
    
    os.makedirs(  os.path.dirname( args.output_file ) , exist_ok=True  )
    
    with open(  args.output_file ,  "w"  ) as fp:
        for pred_label, pred_proba_label in zip(pred, pred_proba):
            fp.write( f"{pred_label} {pred_proba_label}\n"     )
            