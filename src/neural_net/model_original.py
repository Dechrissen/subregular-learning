import torch
import torch.nn as nn
import torch.nn.functional as F


class Predictor(nn.Module):
    def __init__(self, voc_size, dim=100):
        super(Predictor, self).__init__()
        self.embedding = nn.Embedding(voc_size + 1, dim, padding_idx=0)
        self.lstm = nn.LSTM(dim, dim, batch_first=True)
        self.linear = nn.Linear(dim, 2)
        self.softmax = nn.LogSoftmax(dim=1)

    def forward(self, inputs, input_lengths, h0, c0):
        embedded = self.embedding(inputs)
        packed = torch.nn.utils.rnn.pack_padded_sequence(embedded, input_lengths, True)
        output, (hn, cn) = self.lstm(packed, (h0, c0))
        output, size = torch.nn.utils.rnn.pad_packed_sequence(output)
        out = self.linear(hn.squeeze())
        return self.softmax(out)
