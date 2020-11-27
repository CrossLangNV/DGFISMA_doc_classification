# Business Rules

The user script business_rules.py is used to bootstrap the training data for the document classifier. It starts from a solr export with files in jsonlines format. The business rules can be configured in conf.py.

*python business_rules.py \
--input_dir directory/containing/solr/export \
--output_dir  output_directory/for/training_data.tsv*

The resulting training_data.tsv can be used to train the classifier model.