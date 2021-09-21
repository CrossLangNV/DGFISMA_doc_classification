import jsonlines
import argparse
import os
from base64 import b64decode, b64encode
from multiprocessing import Pool

import conf

ACCEPTED_EUROVOC_NUMBERS=set( [conf.accepted_eurovoc_terms_descriptors[ key ] for key in conf.accepted_eurovoc_terms_descriptors] )
REJECTED_EUROVOC_NUMBERS=set( [conf.rejected_eurovoc_terms_descriptors[ key ] for key in conf.rejected_eurovoc_terms_descriptors] )

class EurlexDocument:
    """Representation of the Eurlex document
    """
    def __init__(self, jsonline_dictionary):
        """Contstructs an EurlexDocument object from a dictionary obtained through jsonline.

        :param jsonline_dictionary: Eurlex document from jsonline string
        :type jsonline_dictionary: dict
        """
        self.content = jsonline_dictionary.get('content', '')
        self.celex_id=jsonline_dictionary.get( 'celex', '' )
        if isinstance(self.celex_id, list):
            self.celex_id = self.celex_id[0]
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

        self.classifications_name = dict()
        for type_, code_ in zip(jsonline_dictionary.get('classifications_type', []),jsonline_dictionary.get('classifications_label', [])):
            if type_ in self.classifications_name:
                self.classifications_name[type_].append(code_)
            else:
                self.classifications_name[type_] = [code_]          
                
        self.acceptance_state = 'unvalidated'

    def set_state(self, state):
        assert state in ['accepted', 'rejected'], """State should be 'accepted' or 'rejected'"""
        self.acceptance_state = state
    
    '''
    def get_content(self, key):
        if key == 'misc_author':
            return self.misc_author
        elif key == 'misc_department_responsible':
            return self.misc_department_responsable
        elif key == 'classifications':
            return self.classifications
    '''

    def get_label(self):
        document = ' '.join(self.content.split())
        celex_id=self.celex_id
        encoded_doc = b64encode(document.encode())
        if self.acceptance_state == 'accepted':
            label = 1
            label_name = 'accepted'
            return f"{encoded_doc.decode()  }\t{ label_name }\t{label}\t{celex_id}"

        if self.acceptance_state == 'rejected':
            label = 0
            label_name = 'rejected'
            return f"{encoded_doc.decode()  }\t{ label_name }\t{label}\t{celex_id}"
        
        
def classify( eurlex_doc: EurlexDocument ):
    
    #1. classify author
    
    if set( eurlex_doc.misc_author ).intersection( set( conf.accepted_authors ) ):
        eurlex_doc.set_state( 'accepted' )
        return
    
    #2. classify departement
    
    if set( eurlex_doc.misc_department_responsable ).intersection( set( conf.accepted_dep_responsible ) ):
        eurlex_doc.set_state( 'accepted' )
        return

    #3. classify summary code
    
    if 'summary codes' in eurlex_doc.classifications:
        if set( conf.accepted_summary_codes ).intersection( set( eurlex_doc.classifications['summary codes'] ) ):
            eurlex_doc.set_state( 'accepted' )
            return

    #4. classify directory code
    
    if 'directory code' in eurlex_doc.classifications:
        if set( conf.accepted_directory_codes ).intersection( set( eurlex_doc.classifications['directory code'] )  ):
            eurlex_doc.set_state( 'accepted' )
            return
            
    if 'directory code' in eurlex_doc.classifications:
        if set( conf.rejected_directory_codes ).intersection( set( eurlex_doc.classifications['directory code'] )  ):
            eurlex_doc.set_state( 'rejected' )
            return
         
    #accept under condition:
    if 'directory code' in eurlex_doc.classifications:
        if set( conf.accepted_directory_codes_under_eurovoc_condition ).intersection( set( eurlex_doc.classifications['directory code'] )  ):
            #accept if at least two listed in ACCEPT EUROVOC and no listed in REJECT EUROVOC
            if 'eurovoc descriptor' in eurlex_doc.classifications:
                if len( list( ACCEPTED_EUROVOC_NUMBERS.intersection( set( eurlex_doc.classifications[ 'eurovoc descriptor' ] )))) >= 2:
                    if not REJECTED_EUROVOC_NUMBERS.intersection( set( eurlex_doc.classifications[ 'eurovoc descriptor' ] )):
                        eurlex_doc.set_state( 'accepted' )
                        return
                    
    #5. classify eurovoc code:
    
    #reject documents with any of the rejected eurovoc terms
    if 'eurovoc descriptor' in eurlex_doc.classifications:
        if REJECTED_EUROVOC_NUMBERS.intersection( set( eurlex_doc.classifications[ 'eurovoc descriptor' ] )):
            eurlex_doc.set_state( 'rejected' )
            return
                 
    #accept if at least two listed in ACCEPT EUROVOC and no listed in REJECT EUROVOC
    if 'eurovoc descriptor' in eurlex_doc.classifications:
        if len( list( ACCEPTED_EUROVOC_NUMBERS.intersection( set( eurlex_doc.classifications[ 'eurovoc descriptor' ] )))) >= 2:
            if not REJECTED_EUROVOC_NUMBERS.intersection( set( eurlex_doc.classifications[ 'eurovoc descriptor' ] )):
                eurlex_doc.set_state( 'accepted' )
                return
        
def parse_jsonlines( file ):
    with jsonlines.open( file ) as reader:
        for obj in reader:
            if 'content' in obj:
                if 'eurlex' in obj[ 'website' ]:
                    eurlex_doc=EurlexDocument( obj )
                    if eurlex_doc:
                        classify( eurlex_doc )
                        label = eurlex_doc.get_label()
                        return label

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
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", dest="input_dir", help="Location of the data export.", required=True)
    parser.add_argument("--output_dir", dest="output_dir", help="output directory (where the train data will be written to)", required=True)
    args = parser.parse_args()

    bootstrap(input_dir=args.input_dir, output_dir=args.output_dir)