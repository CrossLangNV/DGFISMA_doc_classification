import jsonlines, os
from multiprocessing import Pool
from langdetect import detect
from itertools import product
from base64 import b64encode, b64decode
import argparse

'''

Directory codes:
062020  = Right of establishment and freedom to provide services / Sectoral application
160     = General, financial and institutional matters / Financial and budgetary provisions
1040    = Economic and monetary policy and free movement of capital / Free movement of capital
1030    = Economic and monetary policy and free movement of capital / Economic policy

Eurovoc descriptors:
4838    = European Investment Bank
5455    = European Central Bank
5460	= European Bank for Reconstruction and Development
5465    = Money laundering
8434    = Counterfeiting

Subject matter:
BEI     = European Investment Bank
BCE     = European Central Bank

Summary codes:
1409    = Economic and monetary affairs / Banking and financial services
2414    = Internal market / Banking and finance
240403  = Internal market / Single market for services / Financial services: insurance
'''

accepted_directory_codes = ['062020', '0160', '1040', '1030']
accepted_eurovoc_descriptors = ['4838', '5455', '5460', '5465', '8434']
accepted_subject_matter = ['BEI', 'BCE']
accepted_summary_codes = ['1409', '2414', '240403']

'''
Directory codes:
08      = Competition policy
09      = Taxation
117020  = External relations / Development policy / Aid to developing countries

Eurovoc descriptors:
889     = State aid

'''
rejected_directory_codes = ['08', '117020', '09']
rejected_eurovoc_descriptors = ['889']
rejected_subject_matter = []

def bootstrap(input_dir, output_dir):
    '''
    bootstrap() takes an input directory and output directory as argument.
    It reads all .jsonl-files and creates a training set according to the business rules.
    It writes the output to a .tsv-file in the output_dir
    '''
    pool = Pool()                     # Create a multiprocessing Pool

    os.makedirs(output_dir, exist_ok=True)

    training_set_output = os.path.join(output_dir, 'train_data.tsv')
    if os.path.isfile(training_set_output):
        raise Exception('A training file already exists in the output directory.')

    all_files = [os.path.join(input_dir, filename) for filename in os.listdir(input_dir) if filename.endswith('.jsonl')]
    results = pool.map(parse_jsonlines, all_files)  # process files iterable with pool

    with open(training_set_output, 'w+') as output_file:
        output_file.writelines(f"{result}\n" for result in results if result is not None)

    pool.close()    #close the multiprocessing pool
    pool.join()

def parse_jsonlines(path):
    with jsonlines.open(path) as reader:
        for obj in reader:
            if 'content' in obj:
                if 'eurlex' in obj['website']:
                    training_line = addEurlexLabels(obj)
                    if training_line:
                        #Each line here is training data as required by the train.py script.
                        return training_line

def addEurlexLabels(dictionary):
    '''
    This function takes in a dictionary loaded from json and creates labels according to the Eurlex business rules. It will return 'None' if neither.
    '''
    if isAcceptedEurlex(dictionary):
        encoded_doc = getText(dictionary)
        if encoded_doc:
            label=1
            label_name='accepted'
            return f"{encoded_doc.decode()  }\t{ label_name }\t{label}"

    elif isRejectedEurlex(dictionary):
        encoded_doc = getText(dictionary)
        if encoded_doc:
            label=0
            label_name='rejected'
            return f"{encoded_doc.decode()  }\t{ label_name }\t{label}"
        
def getText(dictionary):
    '''
    Takes in a dictionary (loaded from json) and returns a base64 encoded string from the 'content'-key.
    '''
    content = dictionary['content']
    if isinstance(content, list):
        content = content[0]
    document = ' '.join(content.split())
    if detect(document) == 'en':
        encoded_document = b64encode(document.encode())
        return encoded_document

def isAcceptedEurlex(dictionary):
    '''
    isAcceptedEurlex() determines whether one of the codes is accepted.
    '''
    if 'misc_author' in dictionary:
        if 'Directorate-General for Financial Stability, Financial Services and Capital Markets Union' in dictionary['misc_author']:
            return True

    if 'misc_department_responsible' in dictionary:
        if 'FISMA' in dictionary['misc_department_responsible']:
            return True

    elif 'classifications_type' in dictionary and 'classifications_code' in dictionary:
        if isaccepted_code(dictionary, 'directory code', accepted_directory_codes):
            return True
        elif isaccepted_code(dictionary, 'eurovoc descriptor', accepted_eurovoc_descriptors):
            return True
        elif isaccepted_code(dictionary, 'subject matter', accepted_subject_matter):
            return True
        elif isaccepted_code(dictionary, 'summary code', accepted_summary_codes):
            return True

def isRejectedEurlex(dictionary):
    '''
    isRejectedEurlex() determines whether one of the codes is accepted.
    '''
    if 'classifications_type' in dictionary and 'classifications_code' in dictionary:
        if isaccepted_code(dictionary, 'directory code', rejected_directory_codes):
            return True
        elif isaccepted_code(dictionary, 'eurovoc descriptor', rejected_eurovoc_descriptors):
            return True
        elif isaccepted_code(dictionary, 'subject matter', rejected_subject_matter):
            return True

def isaccepted_code(dictionary, classification_type, accepted_codes):
    #This functions checks whether any of the classification codes of a certain type start with any of the accepted (or rejected) codes. It expects the dictionary object, the classification type and a list of the accepted codes.
    code_indices = [i for i, x in enumerate(dictionary['classifications_type']) if x == classification_type]
    if code_indices:
        all_codes = [dictionary['classifications_code'][index] for index in code_indices]
        matches = [code for code, accepted_code in product(all_codes, accepted_codes) if code.startswith(accepted_code)]
        if matches:
            return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", dest="input_dir", help="Location of the data export.", required=True)
    parser.add_argument("--output_dir", dest="output_dir", help="output directory (where the train data will be written to)", required=True)
    args = parser.parse_args()

    bootstrap(input_dir=args.input_dir, output_dir=args.output_dir)