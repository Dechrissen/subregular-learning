import argparse
import csv
from datetime import datetime
from itertools import product
import json
import multiprocessing
import numpy as np
import os
import warnings
import yaml

import tensorflow as tf
from tensorflow import keras
from keras import layers
from keras.models import Sequential, Model
from keras.utils.layer_utils import count_params

from data import *
from predict_direct import predict
from eval_direct import evaluate_predictions

warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)
tf.get_logger().setLevel("ERROR")


class TransformerBlock(layers.Layer):
    def __init__(self, embed_dim, num_heads, dropout=0.1):
        super().__init__()
        self.att = layers.MultiHeadAttention(
            num_heads=num_heads, key_dim=embed_dim, dropout=dropout
        )
        self.layernorm = layers.LayerNormalization(epsilon=1e-6)
        self.dropout = layers.Dropout(dropout)

    def call(self, inputs, training):
        attn_output = self.att(inputs, inputs)
        out = self.dropout(attn_output, training=training)
        out = self.layernorm(inputs + out)
        return out


class MainModel(Model):
    def __init__(
        self,
        vocab_size,
        embed_dim=100,
        ff_dim=64,
        num_ff_layers=2,
        dropout=0.1,
        model_type="simple",
        bidi=False,
    ):
        super().__init__()

        self.max_length = 64
        self.model_type = model_type
        self.embeddings = layers.Embedding(vocab_size, embed_dim)

        # initialize non-transformer layers
        rnn_cells = [layers.LSTMCell(embed_dim, dropout=dropout) for _ in range(2)]
        stacked_lstm = layers.StackedRNNCells(rnn_cells)
        model_layers = {
            "simple": layers.SimpleRNN(embed_dim, dropout=dropout),
            "gru": layers.GRU(embed_dim, dropout=dropout),
            "lstm": layers.LSTM(embed_dim, dropout=dropout),
            "stackedrnn": layers.RNN(stacked_lstm),
        }

        if model_type == "transformer":
            self.pos_emb = layers.Embedding(self.max_length, embed_dim)
            self.transformer_blocks = Sequential(
                [
                    TransformerBlock(embed_dim=embed_dim, num_heads=2, dropout=0.2)
                    for _ in range(2)
                ]
            )
            self.pooling = layers.GlobalAveragePooling1D()
        else:
            model_layer = model_layers[model_type]
            self.model_layer = (
                layers.Bidirectional(model_layer) if bidi else model_layer
            )

        # feed forward layers
        self.ffn = Sequential(
            [layers.Dense(ff_dim, activation="relu") for _ in range(num_ff_layers)]
        )
        self.layernorm = layers.LayerNormalization(epsilon=1e-6)
        self.dropout = layers.Dropout(dropout)

        self.linear_layer = layers.Dense(2)
        self.softmax_layer = layers.Softmax()

    def call(self, inputs, training=False):
        out = self.embeddings(inputs)

        if self.model_type == "transformer":
            positions = tf.range(start=0, limit=self.max_length, delta=1)
            positions = self.pos_emb(positions)
            out += positions
            out = self.transformer_blocks(out, training=training)
            out = self.pooling(out)
        else:
            out = self.model_layer(out, training=training)

        out = self.ffn(out)
        out = self.dropout(out, training=training)
        out = self.layernorm(out)
        out = self.linear_layer(out)
        out = self.softmax_layer(out)
        return out


def train_eval_model(
    idx,
    model_type,
    padding,
    num_ff_layers,
    embed_dim,
    learning_rate,
    dropout,
    epochs,
    loss,
    optimizer,
    train_data,
    val_data,
    output_dir,
):
    """Trains and evaluates an NN for a specific setting of hyperparameters."""
    model_id = "".join(str(i) for i in idx)
    model_path = os.path.join(output_dir, f"Model_{model_id}")
    os.makedirs(model_path, exist_ok=True)

    vocabulary = {"pad": 0}
    vocabulary, x_train, y_train = parse_dataset(train_data, vocabulary)
    vocabulary, x_val, y_val = parse_dataset(val_data, vocabulary)
    vocab_file = os.path.join(model_path, "vocab.txt")
    save_vocab(vocab_file, vocabulary)

    x_train = tf.constant(pad_data(x_train, vocabulary))
    x_val = tf.constant(pad_data(x_val, vocabulary))
    y_train = tf.constant(y_train)
    y_val = tf.constant(y_val)

    midpoint = x_val.shape[0] // 2
    x_val, x_test = x_val[:midpoint], x_val[midpoint:]
    y_val, y_test = y_val[:midpoint], y_val[midpoint:]

    tf.random.set_seed(1234)

    config = {
        "vocab_size": len(vocabulary),
        "ff_dim": 64,
        "num_ff_layers": num_ff_layers,
        "embed_dim": embed_dim,
        "dropout": dropout,
        "model_type": model_type,
        "bidi": False,
    }
    config_file = os.path.join(model_path, "config.json")
    with open(config_file, "w") as file:
        json.dump(config, file)

    losses = {
        "BinaryCrossEntropy": keras.losses.BinaryCrossentropy(),
        "MeanSquaredError": keras.losses.MeanSquaredError(),
    }
    optimizers = {
        "RMSprop": keras.optimizers.RMSprop,
        "Adam": keras.optimizers.Adam,
        "SGD": keras.optimizers.SGD,
    }
    loss = losses[loss]
    optimizer = optimizers[optimizer]

    model = MainModel(**config)
    model.compile(
        optimizer=optimizer(learning_rate=learning_rate),
        loss=loss,
        metrics=[
            keras.metrics.BinaryAccuracy(),
            keras.metrics.MeanSquaredError(),
            keras.metrics.MeanAbsoluteError(),
        ],
    )

    checkpoint_path = os.path.join(model_path, "checkpoint.ckpt")
    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath=checkpoint_path,
        save_weights_only=True,
        monitor="val_acc",
        mode="max",
    )
    callbacks = [checkpoint_callback]

    time_now = datetime.now()

    training_record = model.fit(
        x_train,
        y_train,
        batch_size=64,
        epochs=epochs,
        validation_data=(x_val, y_val),
        callbacks=callbacks,
    )

    total_time = (datetime.now() - time_now).total_seconds()
    print(f"TOTAL TRAINING TIME IN SECONDS: {total_time}\n")
    model.summary()

    trainable_params = sum(count_params(layer) for layer in model.trainable_weights)
    h_param_config = {
        "model_type": model_type,
        "padding": padding,
        "num_ff_layers": num_ff_layers,
        "embed_dim": embed_dim,
        "learning_rate": learning_rate,
        "dropout": dropout,
        "epochs": epochs,
        "loss": loss,
        "optimizer": optimizer,
        "trainable_params": trainable_params,
    }
    h_param_config_file = os.path.join(model_path, "model_config.yaml")
    with open(h_param_config_file, "w") as file:
        yaml.dump(h_param_config, file)

    lang = train_data.split("/")[2].split("_")[0]
    test_size = "Mid"
    test_types = ["SR", "SA", "LR", "LA"]
    data_files = [
        os.path.join("data_gen", test_size, f"{lang}_Test{test_type}.txt")
        for test_type in test_types
    ]

    predictions = model.predict(x_test)
    category_predictions = tf.math.argmax(predictions, axis=1) > 0
    y_binary = tf.equal(y_test[:, 1], 1.0)
    correct_preds = category_predictions == y_binary
    acc = np.mean(tf.cast(correct_preds, tf.float32))

    # for test_type, data_file in zip(test_types, data_files):
    #     predict(model, model_path, data_file, f"Test{test_type}", vocabulary)
    #     evaluate_predictions(f"{model_path}/Test{test_type}_pred.txt")
    #
    # acc_sr = get_accuracy_from_file(os.path.join(model_path, "TestSR_eval.txt"))
    # acc_sa = get_accuracy_from_file(os.path.join(model_path, "TestSA_eval.txt"))
    # acc_lr = get_accuracy_from_file(os.path.join(model_path, "TestLR_eval.txt"))
    # acc_la = get_accuracy_from_file(os.path.join(model_path, "TestLA_eval.txt"))

    return acc


def worker(pair):
    """Worker that trains and evaluates a model for a specific h_param setting."""
    idx, h_params = pair
    val_acc = train_eval_model(idx, *h_params)
    return idx, val_acc


def enumerated_product(*args):
    """Multidimensional version of enumerate()."""
    yield from zip(product(*(range(len(x)) for x in args)), product(*args))


def get_accuracy_from_file(file_path):
    lines = open(file_path, "r").readlines()
    for line in lines:
        if line.startswith("Accuracy:"):
            accuracy = line.split()[1]
            return float(accuracy)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-data", type=str, required=True)
    parser.add_argument("--val-data", type=str, required=True)
    parser.add_argument("--output-dir", type=str, required=True)
    parser.add_argument("--bidi", type=bool, default=False)
    args = parser.parse_args()

    # model_type = ["simple", "gru", "lstm", "stackedrnn", "transformer"]
    # padding = ["end"]
    # num_ff_layers = [2, 4]
    # embed_dim = [32, 256]
    # learning_rate = [0.01, 0.0001]
    # dropout = [0.1]
    # epochs = [32, 64]
    # loss = ["BinaryCrossEntropy", "MeanSquaredError"]
    # optimizer = ["RMSprop", "Adam", "SGD"]

    model_type = ["simple", "lstm", "transformer"]
    padding = ["end"]
    num_ff_layers = [2, 3]
    embed_dim = [32, 64]
    learning_rate = [0.001, 0.01]
    dropout = [0.1]
    epochs = [32]
    loss = ["BinaryCrossEntropy", "MeanSquaredError"]
    optimizer = ["SGD"]

    hp_arrays = [
        model_type,
        padding,
        num_ff_layers,
        embed_dim,
        learning_rate,
        dropout,
        epochs,
        loss,
        optimizer,
    ]

    enumerated_hp_grid = enumerated_product(
        *hp_arrays,
        [args.train_data],
        [args.val_data],
        [args.output_dir],
    )

    time_now = datetime.now()
    time_now_format = time_now.strftime("%Y%m%d-%H%M%S")

    num_processes = multiprocessing.cpu_count()
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(worker, enumerated_hp_grid)

    total_time = (datetime.now() - time_now).total_seconds()
    print(f"TOTAL GRID SEARCH TIME IN SECONDS: {total_time}\n")

    sorted_results = list(reversed(sorted(results, key=lambda x: x[1])))
    print(sorted_results)

    # write results to file in decreasing order of performance
    columns = [
        "model_type",
        "padding",
        "num_ff_layers",
        "embed_dim",
        "learning_rate",
        "dropout",
        "epochs",
        "loss",
        "optimizer",
        "acc",
    ]
    results_fname = os.path.join(args.output_dir, "results.csv")
    with open(results_fname, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        hp_values = lambda idx: [hp_arrays[i][idx[i]] for i in range(len(hp_arrays))]
        for res in sorted_results:
            row = hp_values(res[0]) + [res[1]]
            writer.writerow(row)
