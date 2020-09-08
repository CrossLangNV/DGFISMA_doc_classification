#!/usr/local/bin/python
from flask import Flask
from flask import request
from flask import abort
import string
import pickle
import base64
import binascii

from cleaning import clean_html, clean_pdf, delete_annexes

app = Flask(__name__)

MODEL_PATH="/work/models/model.p"

@app.route('/classify_doc', methods=['POST'])
def classify_doc():    
    if not request.json:
        abort(400) 
    output_json={}
    if ('content' not in request.json) or ('content_type' not in request.json):
        print( "'content' and/or 'content_type' field missing" )
        output_json['rejected_probability']=-9999
        output_json['accepted_probability']=-9999
    else:
        
        try:
            decoded_content=base64.b64decode( request.json['content']  ).decode( 'utf-8' ) #TO DO: do not send very large ( e.g. >20Mb) files to cleaning and classification pipeline.
        except binascii.Error:
            print( f"could not decode the 'content' field. Make sure it is in base64 encoding." )
            output_json['rejected_probability']=-9999
            output_json['accepted_probability']=-9999
            return output_json
        
        if request.json[ 'content_type'] == 'pdf':
            articles=clean_pdf( decoded_content )

        elif request.json[ 'content_type'] == 'html' or request.json[ 'content_type'] == 'xhtml':
            articles=clean_html( decoded_content )
            
        else:
            print( f"content type { request.json[ 'content_type'] } not supported by Doc_class app" )   
            output_json['rejected_probability']=-9999
            output_json['accepted_probability']=-9999
            return output_json

        articles=delete_annexes(articles)
        articles_text=" ".join( articles )     
        articles_text=articles_text.replace( "\n", " "  ).translate(str.maketrans('', '', string.punctuation+'0123456789'  ))
                
        clf = pickle.load( open( MODEL_PATH  , "rb" ) )
        probabilities=list( clf.predict_proba( [ articles_text ] )[0] )
        output_json['rejected_probability']=probabilities[0]
        output_json['accepted_probability']=probabilities[1]
    return output_json
    
@app.route('/')
def index():
    return "Up and running"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=False)
    
