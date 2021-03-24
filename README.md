# DGFISMA Document Classifier

This repo contains the source code for the automatic classification and identification of retrieved documents.
It also includes user scripts for the maintenance of the classification model.

In `src/app/models` you'll find the most recent model trained on data extracted according to the business rules.

Instructions Business Rules and creation of a train set.
------------

`src/businessrules` contains the configurable user script for extracting training data from a solr export.

The user script business_rules.py is used to create the training data for the document classifier. It starts from a solr export with files in jsonlines format. The business rules can be configured in `src/businessrulesconf.py`.

In order to create the training data, the following commands need to be run from a python console:

```
from businessrules.business_rules import bootstrap

bootstrap( DATA_PATH , OUTPUT_PATH )
```

, with `DATA_PATH` the path to the directory containing the *solr* export in *.jsonl* format. The training data will be written to `OUTPUT_PATH/train_data.tsv`. This dataset can be used to train the model for document classification.

`bootstrap` can also be run as a python script from a terminal.

We also refer to the the notebook *src/notebooks/run_bootstrap.ipynb* for an example on how to run the *bootstrap* script.

Instructions Classifier Model training
------------

`src/classifier` contains the scripts needed to train a model for document classification(TfIDF + support vector machines).

In order to train a model, the following commands can be run from a python console:

```
from classifier.train import train

import configparser

CONFIG = configparser.ConfigParser()
CONFIG.read( "src/classifier/train.config" )

train( CONFIG  )
```

`train` can also be run as a python script from a terminal.

We advise to use the following configuration for `train.config`:

```
[INPUT/OUTPUT]
INPUT_FILE = OUTPUT_PATH/train_data.tsv
OUTPUT_DIR = OUTPUT_DIR/MODELS/MODEL

[TFIDF_PARAMETERS]
LANGUAGE = english
FEATURE_SELECTION_SVC = True
PENALTY_FEATURE_SELECTION = l1
THRESHOLD_FEATURE_SELECTION=1e-5
PENALTY = l2
DUAL = False
REMOVE_PUNCTUATION_NUMBERS = True
BALANCED = True
JOBS = -1
```

To evaluate the classifier on a labeled test set: 

```
python test.py \
--filename test_data.tsv \
--model_path  OUTPUT_DIR/MODELS/MODEL/model.p \
--output_file output_folder/results
```

, with *test_data.tsv* a tab separated file with at each line: *base64_encoded_document \t label_description \t label*. This will write the predicted labels to the *results* file in the output directory, and print a classification report to the screen.

To use the classfier on new data (unlabeled, base64):

```
python /predict.py \
--filename test_data \
--model_path  OUTPUT_DIR/MODELS/MODEL/model.p \
--output_file output_folder/results_predict*
```

with *test_data* a plain file with at each line a base64 encoded document.

We also refer to *src/notebooks/train_classifier.ipynb* for an example on how to run the *train* and *evaluation* scripts. 

Instructions Classifier API
------------

The source code can be found at `src/app`.

use the shell script "dbuild.sh" to build the docker image <br />

Building the docker image will result in a classifier app that can be plugged into the DGFISMA project.

Given a document (json), e.g.: *example.json* , the API will return a json containing **accepted_probability** and **rejected_probability**, e.g:

<em>
{
    "<strong>accepted_probability</strong>": 0.8487653948445277,
    "<strong>rejected_probability</strong>": 0.1512346051554722
}
</em>

<br />
<br />

If you want to update the model with a newly trained model, make sure to copy the *model.p* file it to the `/src/app/models` directory. Running dbuild.sh will then create a docker API with your new classifier model.

Running dcli.sh will start the classifier API.