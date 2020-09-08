from base64 import b64encode
from base64 import b64decode
import pandas as pd
import os
import argparse

#download dataset from https://www.kaggle.com/lakshmi25npathi/sentiment-analysis-of-imdb-movie-reviews/data , and put the csv ('IMDB Dataset.csv') in the input_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    #Input-output:
        
    parser.add_argument("--input_dir", dest="input_dir",
                        help="location of 'IMDB Dataset.csv'", required=True)
    parser.add_argument("--output_dir", dest="output_dir",
                        help="output directory (where train and test data will be written to)", required=True)
    parser.add_argument('--shuffle', dest='shuffle', action='store_true')


    args = parser.parse_args()
    
    imdb_data=pd.read_csv( os.path.join(  args.input_dir ,'IMDB Dataset.csv' )  )
    
    if args.shuffle:
        print("shuffling...")
        imdb_data = imdb_data.sample(frac=1).reset_index(drop=True)
    
    data_train=imdb_data[25000:]
    data_test=imdb_data[:25000]

    target_dic={}
    target_dic['positive']=1
    target_dic['negative']=0

    os.makedirs( args.output_dir , exist_ok=True  )

    with open( os.path.join(  args.output_dir, "train_data.tsv"  ) , 'w'  ) as f:
        for doc, sentiment in zip(data_train.review, data_train.sentiment):
            encoded_doc = b64encode( doc.encode() )
            f.write( f"{encoded_doc.decode()  }\t{ sentiment }\t{ target_dic[ sentiment ] }\n" )

    with open( os.path.join(  args.output_dir, "test_data.tsv"  ) , 'w'  ) as f:
        for doc, sentiment in zip(data_test.review, data_test.sentiment):
            encoded_doc = b64encode( doc.encode() )
            f.write( f"{encoded_doc.decode()  }\t{ sentiment }\t{ target_dic[ sentiment ] }\n" )
