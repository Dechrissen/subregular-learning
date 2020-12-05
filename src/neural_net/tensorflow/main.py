import argparse
import tensorflow as tf
import tensorflow.keras as keras
import os.path as path
from data import *
from model import MainModel

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--train-data', type=str, required=True)
    parser.add_argument('--val-data', type=str, required=True)
    parser.add_argument('--output-dir', type=str, required=True)
    parser.add_argument('--batch-size', type=int, default=64)
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--embed-dim', type=int, default=100)
    parser.add_argument('--dropout', type=float, default=0.2)
    parser.add_argument('--rnn-type', type=str, default="lstm")
    parser.add_argument('--bidi', type=bool, default=False)

    args = parser.parse_args()
    model_path = path.dirname(args.output_dir)
    vocab_file = model_path + '/vocab.txt'
    config_file = model_path + '/config.txt'

    vocabulary = {'pad': 0}

    vocabulary, x_train, y_train = parse_dataset(args.train_data, vocabulary)
    vocabulary, x_val, y_val = parse_dataset(args.val_data, vocabulary)

    x_train = tf.constant(pad_data(x_train, vocabulary))
    x_val = tf.constant(pad_data(x_val, vocabulary))
    y_train = tf.constant(y_train)
    y_val = tf.constant(y_val)

    config = {'vocab_size': len(vocabulary), 'embed_dim': args.embed_dim,
            'dropout': args.dropout, 'rnn_type': args.rnn_type, 'bidi': args.bidi}

    model = MainModel(**config)
    model.compile(optimizer=keras.optimizers.Adam(),
            loss=keras.losses.BinaryCrossentropy(),
            metrics=[keras.metrics.BinaryAccuracy()])
    training_record = model.fit(x_train, y_train, batch_size=args.batch_size,
            epochs=args.epochs, validation_data=(x_val, y_val))

    model.save(model_path)
    save_vocab(vocab_file, vocabulary)
    with open(config_file, 'w') as f:
        f.write(str(config))
