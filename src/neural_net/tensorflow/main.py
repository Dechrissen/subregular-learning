import argparse
from datetime import datetime
import json
import os

import tensorflow as tf
tf.get_logger().setLevel("ERROR")
import tensorflow.keras as keras
from tensorflow.keras.callbacks import TensorBoard
from transformers import (
    DefaultFlowCallback,
    DistilBertConfig,
    TFBertForSequenceClassification,
    TFDistilBertForSequenceClassification
)

from data import *
from model import MainModel


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-data", type=str, required=True)
    parser.add_argument("--val-data", type=str, required=True)
    parser.add_argument("--output-dir", type=str, required=True)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--embed-dim", type=int, default=100)
    parser.add_argument("--dropout", type=float, default=0.2)
    parser.add_argument("--rnn-type", type=str, default="simple")
    parser.add_argument("--bidi", type=bool, default=False)
    args = parser.parse_args()

    model_path = os.path.dirname(args.output_dir)
    os.makedirs(model_path, exist_ok=True)

    vocabulary = {"pad": 0}
    vocabulary, x_train, y_train = parse_dataset(args.train_data, vocabulary)
    vocabulary, x_val, y_val = parse_dataset(args.val_data, vocabulary)
    vocab_file = f"{model_path}/vocab.txt"
    save_vocab(vocab_file, vocabulary)

    max_length = 64
    tf.random.set_seed(1234)

    x_train = tf.constant(pad_data(x_train, vocabulary))
    x_val = tf.constant(pad_data(x_val, vocabulary))
    y_train = tf.constant(y_train)
    y_val = tf.constant(y_val)

    if args.rnn_type == "distilbert":
        config = {
            "vocab_size":len(vocabulary),
            "max_position_embeddings":max_length,
            "n_layers":2,
            "n_heads":4,
            "dim":128,
            "hidden_dim":128,
            "dropout":args.dropout,
            "attention_dropout":args.dropout,
            "seq_classif_dropout":args.dropout
        }
        distilbertconfig = DistilBertConfig(**config)
        model = TFDistilBertForSequenceClassification(distilbertconfig)
        # model = TFDistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased")
    else:
        config = {
            "vocab_size":len(vocabulary),
            "embed_dim":args.embed_dim,
            "dropout":args.dropout,
            "rnn_type":args.rnn_type,
            "bidi":args.bidi
        }
        model = MainModel(**config)

    config_file = f"{model_path}/config.json"
    with open(config_file, "w") as f:
        json.dump(config, f)

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=2e-5),
        loss=keras.losses.BinaryCrossentropy(),
        metrics=[keras.metrics.BinaryAccuracy()]
    )

    checkpoint_path = os.path.join(model_path, "checkpoint.ckpt")
    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath=checkpoint_path,
        save_weights_only=True,
        monitor="val_acc",
        mode="max"
    )

    time_now = datetime.now()
    time_now_format = time_now.strftime("%Y%m%d-%H%M%S")
    log_dir = f"{model_path}/logs/fit/{time_now_format}"
    tensorboard_callback = TensorBoard(log_dir=log_dir, histogram_freq=1)

    callbacks = [checkpoint_callback, tensorboard_callback]

    training_record = model.fit(
        x_train,
        y_train,
        batch_size=args.batch_size,
        epochs=args.epochs,
        validation_data=(x_val, y_val),
        callbacks=callbacks
    )

    total_time = (datetime.now()-time_now).total_seconds()
    print(f"TOTAL TRAINING TIME IN SECONDS: {total_time}")
