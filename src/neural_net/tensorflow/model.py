import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential, Model
import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)


class TransformerBlock(layers.Layer):
    def __init__(self, embed_dim, num_heads, ff_dim, dropout=0.1):
        super(TransformerBlock, self).__init__()
        self.att = layers.MultiHeadAttention(
            num_heads=num_heads,
            key_dim=embed_dim,
            dropout=dropout
        )
        self.ffn = Sequential([
            layers.Dense(ff_dim, activation="tanh"), 
            layers.Dense(embed_dim),
        ])
        self.layernorm1 = layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = layers.Dropout(dropout)
        self.dropout2 = layers.Dropout(dropout)

    def call(self, inputs, training):
        attn_output = self.att(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        out2 = self.layernorm2(out1 + ffn_output)
        return out2


class MainModel(Model):
    def __init__(
        self,
        vocab_size,
        max_length,
        embed_dim=100,
        dropout=0.2,
        rnn_type="simple",
        bidi=False
    ):
        super().__init__()

        self.max_length = 64
        self.rnn_type = rnn_type
        self.embeddings = layers.Embedding(vocab_size, embed_dim)

        # TRANSFORMER
        if rnn_type == "transformer":
            self.pos_emb = layers.Embedding(self.max_length, embed_dim)
            self.transformer_block = TransformerBlock(
                embed_dim=embed_dim,
                num_heads=2,
                ff_dim=100,
                dropout=0.0
            )
            self.pooling = layers.GlobalAveragePooling1D()

        # STACKED RNN
        rnn_cells = [
            layers.LSTMCell(embed_dim, dropout=dropout)
            for _ in range(2)
        ]
        stacked_lstm = layers.StackedRNNCells(rnn_cells)

        rnn_layers = {
            "lstm":layers.LSTM(embed_dim, dropout=dropout),
            "gru":layers.GRU(embed_dim, dropout=dropout),
            "simple":layers.SimpleRNN(embed_dim, dropout=dropout),
            "stackedrnn":layers.RNN(stacked_lstm)
        }

        if rnn_type != "transformer":
            try:
                rnn_layer = rnn_layers[rnn_type]
            except KeyError:
                raise ValueError(f"{rnn_type} is an invalid RNN type.")
            if bidi:
                self.rnn_layer = layers.Bidirectional(rnn_layer)
            else:
                self.rnn_layer = rnn_layer
        
        self.linear_layer = layers.Dense(2)
        self.softmax_layer = layers.Softmax()

    def call(self, inputs, training=False):
        out = self.embeddings(inputs)

        if self.rnn_type == "transformer":
            x_len = tf.shape(inputs)[-1]
            positions = tf.range(start=0, limit=self.max_length, delta=1)
            positions = self.pos_emb(positions)
            out += positions
            out = self.transformer_block(out, training=training)
            out = self.pooling(out)
        else:
            out = self.rnn_layer(out, training=training)

        out = self.linear_layer(out)
        out = self.softmax_layer(out)
        return out
