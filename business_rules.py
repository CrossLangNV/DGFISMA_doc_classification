import json, os
from multiprocessing import Pool
from itertools import product


def parse_files(path):
    with open(path, 'r') as inputfile:
        pydict = json.loads(inputfile.readlines()[0])
        if check_accepted(pydict):
            pass
        if check_rejected(pydict):
            pass

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
def check_accepted(dictionary):
    accepted_directory_codes = ['062020', '0160', '1040', '1030']
    accepted_eurovoc_descriptors = ['4838', '5455', '5460', '5465', '8434']
    accepted_subject_matter = ['BEI', 'BCE']
    accepted_summary_codes = ['1409', '2414', '240403']

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

'''
Directory codes:
08      = Competition policy
09      = Taxation
117020  = External relations / Development policy / Aid to developing countries
'''
def check_rejected(dictionary):
    rejected_dircodes = ['08', '117020', '09']
    rejected_eurovoc = []
    rejected_subject_matter = []

    if 'classifications_type' in dictionary and 'classifications_code' in dictionary:
        if isaccepted_code(dictionary, 'directory code', rejected_dircodes):
            return True
        elif isaccepted_code(dictionary, 'eurovoc descriptor', rejected_eurovoc):
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
    odir = '/home/sandervanbeers/Desktop/DGFISMA/DATA_DUMP_13_08_ALL/EURLEX'
    all_files = [os.path.join(odir, filename) for filename in os.listdir(odir)]
    pool = Pool()                     # Create a multiprocessing Pool
    pool.map(parse_files, all_files)  # process files iterable with pool
    pool.close()
    pool.join()