import argparse
import os
from base64 import b64decode, b64encode
from itertools import product
from multiprocessing import Pool

import jsonlines
from langdetect import detect
from checkers import MiscAuthorChecker, MiscDepartmentChecker, ClassificationChecker

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
accepted_classifications = {
    'directory code': ['062020', '0160', '1040', '1030'],
    'eurovoc descriptor': ['4838', '5455', '5460', '5465', '8434'],
    'subject matter': ['BEI', 'BCE'],
    'summary codes': ['1409', '2414', '240403']
}
accepted_authors = ['Directorate-General for Financial Stability, Financial Services and Capital Markets Union']
accepted_departments = []

'''
Directory codes:
08      = Competition policy
09      = Taxation
117020  = External relations / Development policy / Aid to developing countries

Eurovoc descriptors:
889     = State aid

'''

rejected_classifications = {
    'directory code': ['08', '117020', '09'],
    'eurovoc descriptor': ['889'],
    'subject matter': [],
    'summary codes': []
}
rejected_authors = []
rejected_departments = []



class EurlexDocument:
    """Representation of the Eurlex document
    """
    def __init__(self, jsonline_dictionary):
        """Contstructs an EurlexDocument object from a dictionary obtained through jsonline.

        :param jsonline_dictionary: Eurlex document from jsonline string
        :type jsonline_dictionary: dict
        """
        self.content = jsonline_dictionary.get('content', '')
        if isinstance(self.content, list):
            self.content = self.content[0]
        self.misc_author = jsonline_dictionary.get('misc_author', [])
        self.misc_department_responsable = jsonline_dictionary.get('misc_department_responsible', [])
        self.classifications = dict()
        for type_, code_ in zip(jsonline_dictionary.get('classifications_type', []),jsonline_dictionary.get('classifications_code', [])):
            if type_ in self.classifications:
                self.classifications[type_].append(code_)
            else:
                self.classifications[type_] = [code_]
        self.acceptance_state = 'unvalidated'

    def set_state(self, state):
        assert state in ['accepted', 'rejected'], """State should be 'accepted' or 'rejected'"""
        self.acceptance_state = state
    
    def get_content(self, key):
        if key == 'misc_author':
            return self.misc_author
        elif key == 'misc_department_responsible':
            return self.misc_department_responsable
        elif key == 'classifications':
            return self.classifications

    def get_label(self):
        document = ' '.join(self.content.split())
        encoded_doc = b64encode(document.encode())
        if self.acceptance_state == 'accepted':
            label = 1
            label_name = 'accepted'
            return f"{encoded_doc.decode()  }\t{ label_name }\t{label}"
        if self.acceptance_state == 'rejected':
            label = 0
            label_name = 'rejected'
            return f"{encoded_doc.decode()  }\t{ label_name }\t{label}"


class EurlexClassifier:
    def classify(self, eurlex_document:EurlexDocument):
        for key, checker in self.checkers.items():
            if checker.check(eurlex_document.get_content(key=key)):
                return True
            

class Acceptor(EurlexClassifier):
    def __init__(self):
        self.checkers = {
        'misc_author': MiscAuthorChecker(accepted_authors),
        'misc_department_responsible': MiscDepartmentChecker(accepted_departments),
        'classifications': ClassificationChecker(accepted_classifications),
        }

class Rejector(EurlexClassifier):
    def __init__(self):
        self.checkers = {
        'misc_author': MiscAuthorChecker(rejected_authors),
        'misc_department_responsible': MiscDepartmentChecker(rejected_departments),
        'classifications': ClassificationChecker(rejected_classifications),
        }



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
                    doc = EurlexDocument(obj)
                    if acceptor.classify(doc):
                        doc.set_state('accepted')
                    if rejector.classify(doc):
                        doc.set_state('rejected')
                    label = doc.get_label()
                    return label

if __name__ == "__main__":
    import timeit
    start = timeit.default_timer()
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", dest="input_dir", help="Location of the data export.", required=True)
    parser.add_argument("--output_dir", dest="output_dir", help="output directory (where the train data will be written to)", required=True)
    args = parser.parse_args()

    acceptor = Acceptor()
    rejector = Rejector()
    bootstrap(input_dir=args.input_dir, output_dir=args.output_dir)
    stop = timeit.default_timer()
    print('Time: ', stop - start) 