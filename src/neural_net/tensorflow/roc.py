import argparse
import tensorflow as tf
import tensorflow.keras as keras
from os.path import dirname, basename
import json
from model import MainModel
from data import *
import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import auc

def load_model_config(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--model-dir', type=str, required=True)
    parser.add_argument('--data-file', type=str, required=True)

    args = parser.parse_args()
    model_dir = dirname(args.model_dir)
    vocab_file = model_dir + '/vocab.txt'
    test_name = basename(args.data_file)[-9:-4]

    vocabulary = load_vocab(vocab_file)

    _, x_data, y_data = parse_dataset(args.data_file, vocabulary)
    x_padded = tf.constant(pad_data(x_data, vocabulary))
    true_labels = np.array(y_data)[:, 0] == 1.0

    config = load_model_config(model_dir + '/config.txt')
    model = MainModel(**config)
    model.load_weights(model_dir + '/checkpoint.ckpt')
    predictions = model.predict(x_padded)
    #np.savetxt("predictions.csv", predictions, delimiter=",")
    
    tpr = []
    fpr = []
    for thresh in np.linspace(0, 1, num=100):
        preds = predictions[:, 0] > thresh
        TP = sum(preds & true_labels)
        TN = sum(~preds & ~true_labels)
        FP = sum(preds & ~true_labels)
        FN = sum(~preds & true_labels)
        tpr += [TP/(TP+FN)]
        fpr += [FP/(FP+TN)]

    AUC = round(auc(fpr, tpr), 4)
    print('AUC: ', AUC)

    split_lines = model_dir.split('/')[1].split('_')

    fig, ax = plt.subplots()
    for i in np.linspace(0,1,num=11):
        ax.axhline(i, linestyle='--', color='k', alpha=0.4, linewidth=0.5)
        ax.axvline(i, linestyle='--', color='k', alpha=0.4, linewidth=0.5)
    ax.set_xlim(-0.05,1.05)
    ax.set_ylim(-0.05,1.05)
    ax.plot(fpr, tpr, 'r', alpha=0.5)
    ax.plot([0,1], [0,1], 'g:')
    ax.text(0.6, 0.25, 'AUC = ' + str(AUC))
    ax.set(xlabel='False Positive Rate', ylabel='True Positive Rate',
       	   title='ROC Curve for ' + ' '.join(split_lines) + ' ' + test_name)
    fig.savefig(model_dir + '/roc_' + test_name + '.png', dpi=500)
