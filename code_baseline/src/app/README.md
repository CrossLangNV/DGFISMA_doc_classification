Instructions
------------


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