#Input/output
filename = ""
output_dir = ""

#Parameters for calculation of features:
vectorizer_type = "tfidf"           #Vectorizer used for feature extraction.
language = "english"                #Language used by Vectorizer (i.e. stopwords).

#Feature selection:
feature_selection_svc = False       #If set to True, using sklearn.feature_selection.SelectFromModel with linear SVC
penalty_feature_selection = "l1"    #Penalty of linear SVC classifier used for feature selection. Choices=['l1','l2']

#Parameters classifier:
penalty = "l2"                      #Penalty of linear SVC classifier used for classification. Choices=[ 'l1','l2' ]
dual = False                        #Solve the dual or primal optimization problem. Prefer dual=False when n_samples > n_features (i.e. when doing feature selection beforehand)
remove_punctuation_numbers = True   #Whether to remove punctuation and numbers from the training data.
balanced = False                    #The “balanced” mode automatically adjusts weights inversely proportional to class frequencies in the input data.
jobs = -1                           #Number of jobs to run in parallel. -1 means using all processors