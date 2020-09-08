# doc_classification_tfidf

Code to do document classification with Tfidf and support vector machines.

To download newsgroup data:

*python get_data_newsgroups.py --output_dir DATA/newsgroup*

This script will create the folder *DATA/newsgroup* and the files *train_data.tsv* and *test_data.tsv*, with at each line: *base64 encoded document* /t *target_name* /t *label*. 

To train a classifier on the train data:

*python /train.py \
--filename DATA/newsgroup/train_data.tsv \
--output_dir  output_folder \
--vectorizer_type tfidf \
--feature_selection_svc*

This will create the *output_folder*, where the trained classfier will be saved (python pickle format). 

To evaluate the classifier on a labeled test set: 

*python test.py \
--filename DATA/newsgroup/test_data.tsv \
--model_path  output_folder/model.p \
--output_file output_folder/results*

This will write the predicted labels to the *results* file in the output directory.  

To use the classfier on new data (unlabeled, base64):

*python /predict.py \
--filename DATA/newsgroup/test_data \
--model_path  output_folder/model.p \
--output_file output_folder/results_predict*

with *test_data* a plain file with at each line a base64 encoded document.

