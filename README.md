Instructions
------------

To create a training set from the business rules:

*python /business_rules.py \
--input_dir   input_directory \
--output_dir  output_directory*

This will create the *output_directory*, where the train_data.tsv will be created (tab separated value-format). 

use "dbuild.sh" to build the docker image <br />
use "dcli.sh" to start a docker container

Given a document (json), e.g.: https://github.com/ArneDefauw/DGFISMA/blob/master/Doc_class-docker/example.json , the program will return a json containing **accepted_probability** and **rejected_probability**, e.g:

<em>
{
    "<strong>accepted_probability</strong>": 0.8487653948445277,
    "<strong>rejected_probability</strong>": 0.1512346051554722
}
</em>

<br />
<br />

The model located here: https://github.com/ArneDefauw/DGFISMA/tree/master/Doc_class-docker/code_baseline/models_dgfisma/model.p will be used for classification. The model can be re-trained using https://github.com/ArneDefauw/DGFISMA/tree/master/Doc_class-docker/code_baseline

Make sure to update the path to the directory where the newly trained model is located in:
https://github.com/ArneDefauw/DGFISMA/blob/master/Doc_class-docker/dbuild.sh
