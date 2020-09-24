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

class MiscDepartmentResponsibleChecker(Checker):
    def __init__(self, department_responsible):
        self.department_responsible = department_responsible

    def check(self, department_responsible):
        return self.department_responsible == department_responsible

    def get_content(self, dictionary):
        return dictionary['misc_department_responsable']

class ClassificationChecker(Checker):
    def __init__(self, classication_dict):
        self.classification_dict = classication_dict
    def check(self, doc_classifications):
        for key, doc_codes in doc_classifications.items():
            check_codes = self.classification_dict[key]
            if key == 'directory code':
                matches = [doc_code for doc_code, code in product(doc_codes, check_codes) if doc_code.startswith(code)]
                if matches:
                    return True


# class Classifier(abc.ABC):

#     def check_dict(self, dictionary):

#         for key in dictionary.keys():
#             if key in self.general_checkers:
#                 checker = self.general_checkers[key]

#                 # TODO if checker a list is
#                 #content = dictionary[key]

#                 content = checker.get_content(dictionary)

#                 b = checker.check(content)
#                 if b:
#                     return True

#         t = dictionary['classifications_type']
#         c = dictionary['classifications_code']
#         for t_i, c_i in zip(t, c):
#             for checker in self.accepted_checkers[t_i]:
#                 b = checker.check(c_i)
#                 if b: return True
#         return 
    

# def directory_code_factory(codes: list):
#     return [DirectoryCodeChecker(code) for code in codes]


# class Acceptor(Classifier):
#     def __init__(self):
#         # self.accepted_checkers = {
#         #     'directory code': directory_code_factory(['062020', '160', ]),
#         #     'eurovec discriptor': None, # TODO
#         # }

#         self.general_checkers = {'misc_author': MiscAuthorChecker('this long author string'),
#                                  'directory code': directory_code_factory(['062020', '160', ])}
