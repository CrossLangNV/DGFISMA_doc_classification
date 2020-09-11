from cleaning import clean_html, clean_pdf, delete_annexes
from business_rules import check_accepted, check_rejected
from multiprocessing import Pool
from langdetect import detect
from base64 import b64encode, b64decode
import json, os


def preprocessFiles(path):
    with open(path, 'r') as inputfile:
        pydict = json.loads(inputfile.readlines()[0])
        if addLabels(pydict):
            print(addLabels(pydict), file=open('NO_ANNEX_train_data.tsv', 'a'))
        

def addLabels(dictionary):
#This function will label according to the business rules. It will return 'None' if neither.
    if check_accepted(dictionary):
        label=1
        label_name='accepted'
        encoded_doc = getText(dictionary)
        if encoded_doc:
            return f"{encoded_doc.decode()  }\t{ label_name }\t{label}"

    elif check_rejected(dictionary):
        label=0
        label_name='declined'
        encoded_doc = getText(dictionary)
        if encoded_doc:
            return f"{encoded_doc.decode()  }\t{ label_name }\t{label}"
        
def getText(dictionary):
#Takes in a dictionary (loaded from the .json) and returns a base64 encoded string.
    articles = clean_html(dictionary['content_html'][0])
    articles = delete_annexes(articles)
    document = ' '.join(articles)
    if detect(document) == 'en':
        encoded_document = b64encode(document.encode())
        return encoded_document


if __name__ == "__main__":
    odir = '/home/sandervanbeers/Desktop/DGFISMA/DATA_DUMP_13_08_ALL/EURLEX'
    all_files = [os.path.join(odir, filename) for filename in os.listdir(odir)]
    pool = Pool()                         # Create a multiprocessing Pool
    pool.map(preprocessFiles, all_files)  # process files iterable with pool
    pool.close()
    pool.join()