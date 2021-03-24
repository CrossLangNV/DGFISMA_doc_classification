import base64
import pickle
import binascii
from os.path import join
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

path_model = "/models/model.p"

model = pickle.load( open( path_model, "rb"))

class Document(BaseModel):
    content: str

app = FastAPI()

@app.post("/classify_doc")
async def classify(document: Document):
    try:
        decoded_content =  base64.b64decode(document.content).decode( 'utf-8' )
        #remove punctuation and numbers before doing predictions
        decoded_content=decoded_content.translate(str.maketrans('', '', string.punctuation+'0123456789'  ))
                
    except binascii.Error:
        raise HTTPException(status_code=400, detail="could not decode the 'content' field. Make sure it is in valid base64 encoding.")
    probabilities=list( model.predict_proba( [ decoded_content])[0])

    output_json = {}
    output_json['rejected_probability']=probabilities[0]
    output_json['accepted_probability']=probabilities[1]
    
    return output_json