# CSE538_FinalProject

Please provide a google drive link to your packaged code or give us a link to your github repo hosting these. The code should be structured with a README that clearly specifies the following: 1. List the original source for your code base. Include the URL to the original source. 2. The list of files that you modified and the specific functions within each file you modified for your project. 3. A list of commands that provide how you train and test your baseline and the systems you built. 4. A list of the major software requirements that are needed to run your system. (E.g. Tensorflow 2.3, Python 243.12, CUDA abd2.0, nltk2401.11, allen-nlp 5.0). These descriptions should be adequate enough to help anyone who wants to run your system

## Dependencies

-   Python >= 3.6
-   Tensorflow >= 2.0

## Data Generation

TBD

## Neural Models

To train a single model, run the program `src/neural_net/tensorflow/main.py`. Most of its arguments are self-expanatory, but note that the `--bidi` flag denotes whether the model's RNN is bidirectional. Valid values for `--rnn-type` are either "gru" or "lstm".

To produce a set of predictions from a data file and a model, run the program `src/neural_net/tensorflow/predict.py`. It outputs the model's predictions to a file consisting of the name of the test data file and `_pred.txt` in the model directory.

To evaluate a model's predictions, run the script `src/neural_net/tensorflow/eval.py`. This program takes a prediction file as produced by `predict.py` and writes to an equivalantly-named `_eval.txt` file also in the model directory. This file reports a number of statistics regarding the model's predictions.

## Batch Training Scripts

The scripts `train_all.sh` and `train_all_lstm.sh` do not take any arguments and will produce all of the models examined in our report. After they have been run, the scripts `collect_evals.sh` and `collect_evals_lstm.sh` can be run without arguments to collect all of the evaluation metrics we considered into a single csv file.
