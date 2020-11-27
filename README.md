# DGFISMA Document Classifier

This repo contains the source code for the automatic classification and identification of retrieved documents.
It also includes user scripts for the maintenance of the classification model.

In code_baseline you'll find the most recent model trained on data extracted according to business rules.

In code_baseline/src/app the classification API can be found along with more detailed instructions.

code_baseline/src/businessrules contains the configurable user script for extracting training data from a solr export.

code_baseline/src/classifier contains the scripts needed to train a classifier model.