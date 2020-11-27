import os
import sys
import argparse
import pickle
from base64 import b64encode, b64decode
import pandas as pd
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", dest="model_path",
                        help="path to the classfier (python pickle format)", required=True)
    args = parser.parse_args()
    
    clf = pickle.load( open(  args.model_path  , "rb" ) )

    document=input()
    print( clf.predict( [document]   )[0] )
