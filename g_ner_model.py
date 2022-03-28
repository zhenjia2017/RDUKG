import math
import torch
import torch.nn as nn
import torch.nn.utils.rnn as utils
from torchcrf import CRF


class RNN(nn.Module):
    def __init__(self, inp_size, hid_size, num_layers=1, batch_first=False, dropout=0, bidirectional=False):
        super(RNN, self).__init__()

        self.inp_size = inp_size
        self.hid_size = hid_size
        self.num_layers = num_layers
        self.batch_first = batch_first
        self.dropout = dropout
        if self.num_layers == 1:
            self.dropout = 0
        self.bidirectional = bidirectional

        self.rnn = nn.GRU(
            self.inp_size,
            self.hid_size,
            num_layers=self.num_layers,
            batch_first=self.batch_first,
            dropout=self.dropout,
            bidirectional=self.bidirectional
        )

    def forward(self, inp_len, inp):
        inp_len, indices = torch.sort(inp_len, descending=True)
        inp = inp[indices]
        inp = utils.pack_padded_sequence(inp, inp_len, batch_first=self.batch_first)

        out, _ = self.rnn(inp)
        out, _ = utils.pad_packed_sequence(out, batch_first=self.batch_first)
        _, indices = torch.sort(indices, descending=False)
        out = out[indices]

        return out


class ATT(nn.Module):
    def __init__(self, inp_size, out_size):
        super(ATT, self).__init__()

        self.inp_size = inp_size
        self.out_size = out_size

        self.QK_size = 128

        self.Q = nn.Linear(self.inp_size, self.QK_size, bias=False)
        self.K = nn.Linear(self.inp_size, self.QK_size, bias=False)
        self.V = nn.Linear(self.inp_size, self.out_size, bias=False)
        self.softmax = nn.Softmax(dim=2)

    def forward(self, inp):
        Q = self.Q(inp)
        K = self.K(inp)
        V = self.V(inp)
        Z = torch.matmul(self.softmax(torch.matmul(Q, K.permute(0, 2, 1)) / math.sqrt(self.QK_size)), V)
        return Z


class STACK_CNN(nn.Module):
    def __init__(self, inp_size, out_size, kernel_step):
        super(STACK_CNN, self).__init__()

        self.inp_size = inp_size
        self.out_size = out_size
        self.kernel_step = kernel_step

        self.kernel_size = [x for x in range(self.kernel_step-1, 64, self.kernel_step)]

        self.cnns = nn.ModuleList([
            nn.Conv1d(
                in_channels=self.inp_size,
                out_channels=self.out_size//len(self.kernel_size),
                kernel_size=i,
                padding=i//2
            )
            for i in self.kernel_size
        ])
        self.tanh = nn.Tanh()

    def forward(self, inp):
        out = inp.permute(0, 2, 1)
        out = [conv(out).permute(0, 2, 1) for conv in self.cnns]
        out = torch.cat(out, dim=2)
        out = self.tanh(out)
        return out


class BERT_CRF(nn.Module):
    def __init__(self, num_labels, dropout):
        super(BERT_CRF, self).__init__()

        self.num_labels = num_labels

        self.hid_size = 768

        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(self.hid_size, self.num_labels)
        self.crf = CRF(self.num_labels, batch_first=True)

    def forward(self, length, word2vec, mask, label=None):
        out = self.dropout(word2vec)
        out = self.linear(out)
        max_length = out.shape[1]
        mask = mask[:, :max_length]
        if self.training:
            label = label[:, :max_length]
            loss = -self.crf(out, label, mask=mask.byte(), reduction="mean")
            return loss
        else:
            label = self.crf.decode(out, mask=mask.byte())
            return label


class BERT_BiGRU_CRF(nn.Module):
    def __init__(self, num_labels, dropout):
        super(BERT_BiGRU_CRF, self).__init__()

        self.num_labels = num_labels

        self.hid_size = 768
        self.emb_size = 128
        
        self.rnn = RNN(self.hid_size, self.emb_size//2, batch_first=True, bidirectional=True)
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(self.emb_size, self.num_labels)
        self.crf = CRF(self.num_labels, batch_first=True)

    def forward(self, length, word2vec, mask, label=None):
        out = self.rnn(length, word2vec)
        out = self.dropout(out)
        out = self.linear(out)
        max_length = out.shape[1]
        mask = mask[:, :max_length]
        if self.training:
            label = label[:, :max_length]
            loss = -self.crf(out, label, mask=mask.byte(), reduction="mean")
            return loss
        else:
            label = self.crf.decode(out, mask=mask.byte())
            return label


class BERT_BiGRU_ATT_CRF(nn.Module):
    def __init__(self, num_labels, dropout):
        super(BERT_BiGRU_ATT_CRF, self).__init__()

        self.num_labels = num_labels

        self.hid_size = 768
        self.rnn_size = 128
        self.att_size = 128

        self.rnn = RNN(self.hid_size, self.rnn_size//2, batch_first=True, bidirectional=True)
        self.att = ATT(self.hid_size, self.att_size)

        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(self.rnn_size + self.att_size, self.num_labels)
        self.crf = CRF(self.num_labels, batch_first=True)

    def forward(self, length, word2vec, mask, label=None):
        out_rnn = self.rnn(length, word2vec)
        max_length = out_rnn.shape[1]
        out_att = self.att(word2vec)[:, :max_length, :]
        # out = self.dropout(out_rnn + out_att)
        out = self.dropout(torch.cat([out_rnn, out_att], dim=2))
        # out = self.att(out_rnn)
        # out = self.dropout(out)
        out = self.linear(out)
        mask = mask[:, :max_length]
        if self.training:
            label = label[:, :max_length]
            loss = -self.crf(out, label, mask=mask.byte(), reduction="mean")
            return loss
        else:
            label = self.crf.decode(out, mask=mask.byte())
            return label


class BERT_BiGRU_STACK_CNN_CRF(nn.Module):
    def __init__(self, num_labels, dropout):
        super(BERT_BiGRU_STACK_CNN_CRF, self).__init__()

        self.num_labels = num_labels

        self.hid_size = 768
        self.rnn_size = 128
        self.cnn_size = 64
        self.cnn_ks = 2

        self.rnn = RNN(self.hid_size, self.rnn_size//2, batch_first=True, bidirectional=True)
        self.cnn = STACK_CNN(self.hid_size, self.cnn_size, self.cnn_ks)
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(self.rnn_size+self.cnn_size, self.num_labels)
        self.crf = CRF(self.num_labels, batch_first=True)

    def forward(self, length, word2vec, mask, label=None):
        out = self.dropout(word2vec)
        out_rnn = self.rnn(length, out)
        max_length = out_rnn.shape[1]
        out_cnn = self.cnn(out)[:, :max_length, :]
        out = torch.cat([out_rnn, out_cnn], dim=2)
        out = self.dropout(out)
        out = self.linear(out)
        mask = mask[:, :max_length]
        if self.training:
            label = label[:, :max_length]
            loss = -self.crf(out, label, mask=mask.byte(), reduction="mean")
            return loss
        else:
            label = self.crf.decode(out, mask=mask.byte())
            return label
