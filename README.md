# DGFISMA Document Classifier

This repo contains the source code for the automatic classification and identification of retrieved documents.
It also includes user scripts for the maintenance of the classification model.

In code_baseline you'll find the most recent model trained on data extracted according to the business rules.

Instructions Business Rules
------------

code_baseline/src/businessrules contains the configurable user script for extracting training data from a solr export.

The user script business_rules.py is used to bootstrap the training data for the document classifier. It starts from a solr export with files in jsonlines format. The business rules can be configured in conf.py.

*python business_rules.py \
--input_dir directory/containing/solr/export \
--output_dir  output_directory/for/training_data.tsv*

The resulting training_data.tsv can be used to train the classifier model.


Instructions Classifier Model training
------------

code_baseline/src/classifier contains the scripts needed to train a classifier model.

Code to do document classification with Tfidf and support vector machines.

To download newsgroup data:

*python get_data_newsgroups.py --output_dir DATA/newsgroup*

This script will create the folder *DATA/newsgroup* and the files *train_data.tsv* and *test_data.tsv*, with at each line: *base64 encoded document* /t *target_name* /t *label*. 

To train a classifier on the train data:
First you have to modify conf.py: 
filename = "/path/to/train_data.tsv"
output_dir = "/path/of/output_folder"

*python /train.py*

This will create the *output_folder*, where the trained classfier will be saved (python pickle format). The cross validation scores will also be written to this output directory in json format.

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


Instructions Classifier API
------------

The source code can be found at code_baseline/src/app.

use the shell script "dbuild.sh" to build the docker image <br />

Building the docker image will result in a classifier app that can be plugged into the DGFISMA project.

Given a document (json), e.g.: https://github.com/ArneDefauw/DGFISMA/blob/master/Doc_class-docker/example.json , the program will return a json containing **accepted_probability** and **rejected_probability**, e.g:

<em>
{
    "<strong>accepted_probability</strong>": 0.8487653948445277,
    "<strong>rejected_probability</strong>": 0.1512346051554722
}
</em>

<br />
<br />

If you want to update the model with a newly trained model, make sure to copy it to the /src/app/models directory. Running dbuild.sh will then create a docker API with your new classifier model.

Running dcli.sh will start the classifier API.