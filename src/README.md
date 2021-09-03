# MODEL DEPLOYMENT

Usage
=====

parse.py: parse the original nginx log file into a csv file with fields
urlfeaturizer.py: convert a file with two columns "urls,target" into a new file "feature,target"
cosine.py: is used to generate features for urls
train.py: is used to train a xgboost machine learning model (remember the target is manually defined. In my case 0 is BAD GUYS, 1 OK)
predict.py: is used to make inference from a model by givin on cmdline the url

Example usage
=============
1) parse the nginx log file: parse.py all.log log_parsed.csv
2) Annotate manually your urls on log_parsed.csv and extract a file "urls,annotated_targets"
 2.1) Remove duplicate urls (i.e. cat dataset.target.csv | sort | uniq >> dataset.target.uniq.csv
3) Produce features: urlfeaturizer.py dataset.target.uniq.csv dataset.features.target.csv
4) Train the model: train.py dataset.features.target.csv out_model
5) Make inference: predict.py "url" out_model

Enjoy

