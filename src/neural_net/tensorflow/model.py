import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import models, layers


class MainModel(models.Model):
    def __init__(
        self,
        vocab_size,
        embed_dim=100,
        dropout=0.2,
        rnn_type="simple",
        bidi=False
    ):
        super().__init__()

        self.rnn_type = rnn_type
        self.embeddings = layers.Embedding(vocab_size, embed_dim)

        if rnn_type == "stackrnn":
            rnn_cells = [
                layers.LSTMCell(embed_dim, dropout=dropout)
                for _ in range(2)
            ]
            stacked_lstm = layers.StackedRNNCells(rnn_cells)

        rnn_layers = {
            "lstm":layers.LSTM(embed_dim, dropout=dropout),
            "gru":layers.GRU(embed_dim, dropout=dropout),
            "simple":layers.SimpleRNN(embed_dim, dropout=dropout),
            "stackrnn":layers.RNN(stacked_lstm)
        }

        try:
            rnn_layer = rnn_layers[rnn_type]
        except KeyError:
            raise ValueError("Invalid RNN type")
        
        if bidi:
            self.rnn_layer = layers.Bidirectional(rnn_layer)
        else:
            self.rnn_layer = rnn_layer
        self.linear_layer = layers.Dense(2)
        self.softmax_layer = layers.Softmax()

    def __call__(self, inputs, value=None, training=False):
        out = self.embeddings(inputs)
        out = self.rnn_layer(out, training=training)
        out = self.linear_layer(out)
        out = self.softmax_layer(out)
        return out
