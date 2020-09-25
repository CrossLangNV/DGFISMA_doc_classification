import abc
from itertools import product

class Checker(abc.ABC):
    """Outline for Checkers

    :param abc: Inherit from abstract base class
    :type abc: Abstract Base Class
    """
    @abc.abstractmethod
    def check(self) -> bool:
        pass


class MiscAuthorChecker(Checker):
    """Class to check Eurlex authors

    :param Checker: Base class it inherits from
    :type Checker: Checker base class
    """
    def __init__(self, list_authors):
        """Contruct with the list of authors it needs to perform a check against

        :param list_authors: List of accepted/rejected authors
        :type list_authors: list
        """
        self.authors = set(list_authors)

    def check(self, authors):
        """Checks if any of the authors is in the self.authors list

        :param authors: list of authors in Eurlex document
        :type authors: list
        :return: returns True if the list of authors is in self.authors
        :rtype: bool
        """
        if isinstance(authors, str):
            authors = [authors]
        set_authors = set(authors)
        if set_authors.intersection(self.authors):
            return True

class MiscDepartmentChecker(Checker):
    """Class to check Eurlex departments responsible

    :param Checker: Base class it inherits from
    :type Checker: Checker base class
    """
    def __init__(self, list_departments):
        """construct the class with the list of departments it needs to perform a check against.

        :param list_departments: list of accepted/rejected departments
        :type list_departments: List
        """
        self.departments = set(list_departments)

    def check(self, departments):
        """Checks if any of the departments from the Eurlex document is in self.departments

        :param departments: list of departments in the Eurlex document
        :type departments: list
        :return: True if any matches are found
        :rtype: bool
        """
        if isinstance(departments, str):
            departments = [departments]
        set_departments = set(departments)
        if set_departments.intersection(self.departments):
            return True


class ClassificationChecker(Checker):
    """This class checks the classification parameters

    :param Checker: The checker base class it inherits from
    :type Checker: Checker base class
    """
    def __init__(self, classication_dict):
        """Contructs the classification checker with a dictionary containing the values it needs to check against.

        :param classication_dict: dictionary containing the accepted/rejected parameters
        :type classication_dict: dictionary
        """
        self.classification_dict = classication_dict
        
    def check(self, doc_classifications):
        """Checks content of doc_classification dictionary against the configured classification_dict dictionary and returns True if a match is found.

        :param doc_classifications: The classifications of the Eurlex document.
        :type doc_classifications: dict
        :return: True if a match is found
        :rtype: bool
        """
        
        for key, doc_codes in doc_classifications.items():
            check_codes = self.classification_dict[key]
            if key == 'directory code' or key == 'summary codes':
                matches = [doc_code for doc_code, code in product(doc_codes, check_codes) if doc_code.startswith(code)]
                if matches:
                    return True
            elif key == 'eurovoc descriptor' or key == 'subject matter':
                doc_codes = set(doc_codes)
                check_codes = set(check_codes)
                if doc_codes.intersection(check_codes):
                    return True
