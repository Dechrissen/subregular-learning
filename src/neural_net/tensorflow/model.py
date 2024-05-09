import numpy as np
import warnings

import tensorflow as tf
from tensorflow import keras
from keras import layers
from keras.models import Sequential, Model
from keras.utils.layer_utils import count_params

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
