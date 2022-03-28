import math
import torch
import torch.nn as nn
import torch.nn.utils.rnn as utils


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


class CNN(nn.Module):
    def __init__(self, inp_size, out_size):
        super(CNN, self).__init__()

        self.inp_size = inp_size
        self.out_size = out_size

        self.kernel_size = [2, 3, 5, 7]

        self.cnns = nn.ModuleList([
            nn.Conv1d(
                in_channels=self.inp_size,
                out_channels=self.out_size//len(self.kernel_size),
                kernel_size=i,
            )
            for i in self.kernel_size
        ])

        self.tanh = nn.Tanh()

    def forward(self, inp):
        out = [
            conv(inp.permute(0, 2, 1)).permute(0, 2, 1)
            for conv in self.cnns
        ]
        out = self.tanh(torch.cat([torch.max(o, dim=1)[0] for o in out], dim=1))
        return out


class PCNN(nn.Module):
    def __init__(self, inp_size, out_size):
        super(PCNN, self).__init__()

        self.inp_size = inp_size
        self.out_size = out_size // 2

        self.kernel_size = [3, 5]

        self.cnns = nn.ModuleList([
            nn.ModuleList([
                nn.Conv1d(
                    in_channels=self.inp_size,
                    out_channels=self.out_size//len(self.kernel_size),
                    kernel_size=i,
                ),
                nn.Conv1d(
                    in_channels=self.inp_size,
                    out_channels=self.out_size//len(self.kernel_size),
                    kernel_size=i,
                )
            ])
            for i in self.kernel_size
        ])

    def forward(self, inp1, inp2):
        out = [
            torch.cat([
                torch.max(conv[0](inp1.permute(0, 2, 1)).permute(0, 2, 1), dim=1)[0],
                torch.max(conv[1](inp2.permute(0, 2, 1)).permute(0, 2, 1), dim=1)[0],
            ], dim=1)
            for conv in self.cnns
        ]
        out = torch.cat(out, dim=1)
        return out


class RNN_MAXPOOL(nn.Module):
    def __init__(self, entity_num, relation_num, dropout):
        super(RNN_MAXPOOL, self).__init__()

        self.inp_size = 768
        self.hid_size = 128
        self.entity_num = entity_num
        self.relation_num = relation_num

        self.emb_size = 4
        self.emb = nn.Embedding(3, self.emb_size)

        self.rnn = RNN(self.inp_size+self.emb_size, self.hid_size//2, batch_first=True, bidirectional=True)
        self.linear = nn.Linear(self.hid_size, self.relation_num)
        self.dropout = nn.Dropout(dropout)

        self.loss = nn.CrossEntropyLoss(reduction="mean")

    def forward(self, length, inp, sub, obj, sub_pos, obj_pos, m1, m2, rel=None):
        out = self.dropout(inp)
        out = torch.cat([out, self.emb((sub_pos == 1).long()*2 + (obj_pos == 1).long())], dim=2)
        out = self.rnn(length, out)
        out = torch.max(out, dim=1)[0]
        out = self.linear(out)
        if self.training:
            loss = self.loss(out, rel)
            return loss
        else:
            pred = torch.max(out, dim=1).indices
            return pred


# Attention-based bidirectional long short-term memory networks for relation classification[ACL2016]
class RNN_ATT(nn.Module):
    def __init__(self, entity_num, relation_num, dropout):
        super(RNN_ATT, self).__init__()

        self.inp_size = 768
        self.hid_size = 128
        self.entity_num = entity_num
        self.relation_num = relation_num

        self.emb_size = 4
        self.emb = nn.Embedding(3, self.emb_size)

        self.rnn = RNN(self.inp_size+self.emb_size, self.hid_size//2, batch_first=True, bidirectional=True)
        self.w = nn.Linear(self.hid_size, 1, bias=0)
        self.linear = nn.Linear(self.hid_size, self.relation_num)

        self.tanh = nn.Tanh()
        self.softmax = nn.Softmax(dim=1)
        self.dropout = nn.Dropout(dropout)

        self.loss = nn.CrossEntropyLoss(reduction="mean")

    def forward(self, length, inp, sub, obj, sub_pos, obj_pos, m1, m2, rel=None):
        out = self.dropout(inp)
        out = torch.cat([out, self.emb((sub_pos == 1).long()*2 + (obj_pos == 1).long())], dim=2)
        out = self.rnn(length, out)
        out = self.tanh(self.softmax(self.w(self.tanh(out))).permute(0, 2, 1).matmul(out)[:, 0, :])
        out = self.linear(out)
        if self.training:
            loss = self.loss(out, rel)
            return loss
        else:
            pred = torch.max(out, dim=1).indices
            return pred


class CNN_MAXPOOL(nn.Module):
    def __init__(self, entity_num, relation_num, dropout):
        super(CNN_MAXPOOL, self).__init__()

        self.inp_size = 768
        self.hid_size = 128
        self.entity_num = entity_num
        self.relation_num = relation_num

        self.emb_size = 4
        self.emb = nn.Embedding(3, self.emb_size)

        self.cnn = CNN(self.inp_size+self.emb_size, self.hid_size)
        self.linear = nn.Linear(self.hid_size, self.relation_num)
        self.dropout = nn.Dropout(dropout)

        self.loss = nn.CrossEntropyLoss(reduction="mean")

    def forward(self, length, inp, sub, obj, sub_pos, obj_pos, m1, m2, rel=None):
        out = self.dropout(inp)
        out = torch.cat([out, self.emb((sub_pos == 1).long()*2 + (obj_pos == 1).long())], dim=2)
        out = self.cnn(out)
        out = self.linear(out)
        if self.training:
            loss = self.loss(out, rel)
            return loss
        else:
            pred = torch.max(out, dim=1).indices
            return pred


class CNN_ATT(nn.Module):
    def __init__(self, entity_num, relation_num, dropout):
        super(CNN_ATT, self).__init__()

        self.inp_size = 768
        self.hid_size = 128
        self.entity_num = entity_num
        self.relation_num = relation_num

        self.emb_size = 4
        self.emb = nn.Embedding(3, self.emb_size)

        self.kernel_size = [2, 3, 5, 7]

        self.cnns = nn.ModuleList([
            nn.Conv1d(
                in_channels=self.inp_size+self.emb_size,
                out_channels=self.hid_size//len(self.kernel_size),
                kernel_size=i,
            )
            for i in self.kernel_size
        ])
        self.w = nn.ModuleList([
            nn.Linear(self.hid_size//len(self.kernel_size), 1, bias=0)
            for _ in self.kernel_size
        ])
        self.linear = nn.Linear(self.hid_size, self.relation_num)

        self.tanh = nn.Tanh()
        self.softmax = nn.Softmax(dim=1)
        self.dropout = nn.Dropout(dropout)

        self.loss = nn.CrossEntropyLoss(reduction="mean")

    def forward(self, length, inp, sub, obj, sub_pos, obj_pos, m1, m2, rel=None):
        out = self.dropout(inp)
        out = torch.cat([out, self.emb((sub_pos == 1).long()*2 + (obj_pos == 1).long())], dim=2)
        out = [
            conv(out.permute(0, 2, 1)).permute(0, 2, 1)
            for conv in self.cnns
        ]
        out = [
            self.tanh(self.softmax(self.w[i](self.tanh(out[i]))).permute(0, 2, 1).matmul(out[i])[:, 0, :])
            for i in range(len(self.kernel_size))
        ]
        out = torch.cat(out, dim=1)
        out = self.linear(out)
        if self.training:
            loss = self.loss(out, rel)
            return loss
        else:
            pred = torch.max(out, dim=1).indices
            return pred


class RNN_CNN(nn.Module):
    def __init__(self, entity_num, relation_num, dropout):
        super(RNN_CNN, self).__init__()

        self.inp_size = 768
        self.hid_size = 128
        self.entity_num = entity_num
        self.relation_num = relation_num

        self.emb_size = 4
        self.emb = nn.Embedding(3, self.emb_size)

        self.rnn = RNN(self.inp_size+self.emb_size, self.hid_size//2, batch_first=True, bidirectional=True)
        self.cnn = CNN(self.hid_size, self.hid_size)
        self.linear = nn.Linear(self.hid_size, self.relation_num)
        self.dropout = nn.Dropout(dropout)

        self.loss = nn.CrossEntropyLoss(reduction="mean")

    def forward(self, length, inp, sub, obj, sub_pos, obj_pos, m1, m2, rel=None):
        out = self.dropout(inp)
        out = torch.cat([out, self.emb((sub_pos == 1).long()*2 + (obj_pos == 1).long())], dim=2)
        # rnn_out = torch.max(self.rnn(length, out), dim=1)[0]
        # cnn_out = self.cnn(out)
        # out = torch.cat([rnn_out, cnn_out], dim=1)
        # out = rnn_out + cnn_out
        out = self.cnn(self.rnn(length, out))
        out = self.linear(out)
        if self.training:
            loss = self.loss(out, rel)
            return loss
        else:
            pred = torch.max(out, dim=1).indices
            return pred


class PCNN_MAXPOOL(nn.Module):
    def __init__(self, entity_num, relation_num, dropout):
        super(PCNN_MAXPOOL, self).__init__()

        self.inp_size = 768
        self.hid_size = 128
        self.entity_num = entity_num
        self.relation_num = relation_num

        self.emb_size = 4
        self.emb = nn.Embedding(3, self.emb_size)

        self.pcnn = PCNN(self.inp_size+self.emb_size, self.hid_size)
        self.linear = nn.Linear(self.hid_size, self.relation_num)
        self.dropout = nn.Dropout(dropout)

        self.loss = nn.CrossEntropyLoss(reduction="mean")

    def forward(self, length, inp, sub, obj, sub_pos, obj_pos, m1, m2, rel=None):
        out = self.dropout(inp)
        out = torch.cat([out, self.emb((sub_pos == 1).long()*2 + (obj_pos == 1).long())], dim=2)
        inp_1 = out * m1.float().unsqueeze(dim=2).expand(out.shape)
        inp_2 = out * m2.float().unsqueeze(dim=2).expand(out.shape)
        out = self.pcnn(inp_1, inp_2)
        out = self.linear(out)
        if self.training:
            loss = self.loss(out, rel)
            return loss
        else:
            pred = torch.max(out, dim=1).indices
            return pred


class EN_INFO_PCNN(nn.Module):
    def __init__(self, entity_num, relation_num, dropout):
        super(EN_INFO_PCNN, self).__init__()

        self.inp_size = 768
        self.entity_num = entity_num
        self.relation_num = relation_num

        self.pos_size = 16
        self.lbl_size = 16
        self.pcnn_size = 64

        self.position_emb = nn.Embedding(129, self.pos_size)
        self.entity_emb = nn.Embedding(self.entity_num, self.lbl_size)

        self.pcnn = PCNN(self.inp_size+2*self.pos_size, self.pcnn_size)
        # self.pcnn = PCNN(self.inp_size, self.pcnn_size)
        self.linear = nn.Linear(2*self.lbl_size+self.pcnn_size, self.relation_num)
        # self.linear = nn.Linear(self.pcnn_size, self.relation_num)
        self.dropout = nn.Dropout(dropout)

        self.loss = nn.CrossEntropyLoss(reduction="mean")

    def forward(self, length, inp, sub, obj, sub_pos, obj_pos, m1, m2, rel=None):
        out = self.dropout(inp)
        s_p = self.position_emb(sub_pos)
        o_p = self.position_emb(obj_pos)
        inp_1 = torch.cat([out * m1.float().unsqueeze(dim=2).expand(out.shape), s_p, o_p], dim=2)
        inp_2 = torch.cat([out * m2.float().unsqueeze(dim=2).expand(out.shape), s_p, o_p], dim=2)
        # inp_1 = out * m1.float().unsqueeze(dim=2).expand(out.shape)
        # inp_2 = out * m2.float().unsqueeze(dim=2).expand(out.shape)
        out = self.pcnn(inp_1, inp_2)
        out = torch.cat([out, self.entity_emb(sub), self.entity_emb(obj)], dim=1)
        out = self.linear(out)
        if self.training:
            loss = self.loss(out, rel)
            return loss
        else:
            pred = torch.max(out, dim=1).indices
            return pred
