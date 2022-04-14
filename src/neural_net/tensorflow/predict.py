import argparse
import tensorflow as tf
import tensorflow.keras as keras
from os.path import dirname, basename
import json
from model import MainModel
from data import *

def indices_to_text(indices, index_map):
    result = ""
    for index in indices:
        result += index_map[index]
    return result

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
    test_name = basename(args.data_file)[-10:-4]

    vocabulary = load_vocab(vocab_file)

    index_to_char = {}
    for item in vocabulary:
        index_to_char[vocabulary[item]] = item

    _, x_data, y_data = parse_dataset(args.data_file, vocabulary)
    x_padded = tf.constant(pad_data(x_data, vocabulary))
    true_labels = tf.math.argmax(y_data, axis=1)

    #model = keras.models.load_model(model_dir)
    config = load_model_config(model_dir + '/config.txt')
    model = MainModel(**config)
    #model.compile(optimizer=keras.optimizers.Adam(), loss=keras.losses.BinaryCrossentropy(), metrics)
    model.load_weights(model_dir + '/checkpoint.ckpt')

    predictions = model.predict(x_padded)
    category_predictions = tf.math.argmax(predictions, axis=1)

    with open(model_dir + "/" + test_name + "_pred.txt", 'w') as f:
        for i in range(len(x_data)):
            string = indices_to_text(x_data[i], index_to_char)
            true_label = 'TRUE' if true_labels[i] == 0 else 'FALSE'
            predicted_label = 'TRUE' if category_predictions[i] == 0 else 'FALSE'
            f.write(string + '\t' + true_label + '\t' + predicted_label + '\n')

    with open(model_dir + "/" + test_name + "_probs.txt", 'w') as f:
        for i in range(len(predictions)):
            f.write(str(predictions[i, 0]) + ' ' + str(predictions[i, 1]) + '\n')
