from tensorflow.keras import models, layers

class MainModel(models.Model):
    def __init__(self, vocab_size : int, embed_dim : int = 100,
            dropout : float = 0.2, rnn_type : str = "simple", bidi : bool = False):
        super().__init__()

        self.embeddings = layers.Embedding(vocab_size, embed_dim)

        if rnn_type == "lstm":
            rnn_layer = layers.LSTM(embed_dim, dropout=dropout)
        elif rnn_type == "gru":
            rnn_layer = layers.GRU(embed_dim, dropout=dropout)
        elif rnn_type == "simple":
            rnn_layer = layers.SimpleRNN(embed_dim, dropout=dropout)
        else:
            raise ValueError("Invalid RNN Type")

        self.rnn_layer = layers.Bidirectional(rnn_layer) if bidi else rnn_layer
        self.linear_layer = layers.Dense(2)
        self.softmax_layer = layers.Softmax()

    def call(self, inputs, training : bool = False):
        out = self.embeddings(inputs)
        out = self.rnn_layer(out, training=training)
        out = self.linear_layer(out)
        out = self.softmax_layer(out)
        return out
