import torch.nn as nn
import torch.nn.functional as F
import torch
import math


class SleePyCoBackbone(nn.Module):

    def __init__(self):
        super(SleePyCoBackbone, self).__init__()

        # architecture
        self.init_layer = self.make_layers(in_channels=1, out_channels=64, n_layers=2, maxpool_size=None, first=True)
        self.layer1 = self.make_layers(in_channels=64, out_channels=128, n_layers=2, maxpool_size=5)
        self.layer2 = self.make_layers(in_channels=128, out_channels=192, n_layers=3, maxpool_size=5)
        self.layer3 = self.make_layers(in_channels=192, out_channels=256, n_layers=3, maxpool_size=5)
        self.layer4 = self.make_layers(in_channels=256, out_channels=256, n_layers=3, maxpool_size=5)

        self.fp_dim = 128
        self.conv_c5 = nn.Conv1d(256, self.fp_dim, 1, 1, 0)

        self.conv_c4 = nn.Conv1d(256, self.fp_dim, 1, 1, 0)

        self.conv_c3 = nn.Conv1d(192, self.fp_dim, 1, 1, 0)

    def make_layers(self, in_channels, out_channels, n_layers, maxpool_size, first=False):
        layers = []
        layers = layers + [MaxPool1d(maxpool_size)] if not first else layers

        for i in range(n_layers):
            conv1d = nn.Conv1d(in_channels, out_channels, kernel_size=3, padding=1)
            layers += [conv1d, nn.BatchNorm1d(out_channels)]
            if i == n_layers - 1:
                layers += [ChannelGate(in_channels)]
            layers += [nn.PReLU()]
            in_channels = out_channels

        return nn.Sequential(*layers)

    def forward(self, x):
        out = []

        c1 = self.init_layer(x)
        c2 = self.layer1(c1)
        c3 = self.layer2(c2)
        c4 = self.layer3(c3)
        c5 = self.layer4(c4)

        p5 = self.conv_c5(c5)
        out.append(p5)
        p4 = self.conv_c4(c4)
        out.append(p4)
        p3 = self.conv_c3(c3)
        out.append(p3)

        return out


class MaxPool1d(nn.Module):
    def __init__(self, maxpool_size):
        super(MaxPool1d, self).__init__()
        self.maxpool_size = maxpool_size
        self.maxpool = nn.MaxPool1d(kernel_size=maxpool_size, stride=maxpool_size)

    def forward(self, x):
        _, _, n_samples = x.size()
        if n_samples % self.maxpool_size != 0:
            pad_size = self.maxpool_size - (n_samples % self.maxpool_size)
            if pad_size % 2 != 0:
                left_pad = pad_size // 2
                right_pad = pad_size // 2 + 1
            else:
                left_pad = pad_size // 2
                right_pad = pad_size // 2
            x = F.pad(x, (left_pad, right_pad), mode='constant')

        x = self.maxpool(x)

        return x


class BasicConv(nn.Module):
    def __init__(self, in_planes, out_planes, kernel_size, stride=1, padding=0, dilation=1, groups=1, relu=True,
                 bn=True, bias=False):
        super(BasicConv, self).__init__()
        self.out_channels = out_planes
        self.conv = nn.Conv1d(in_planes, out_planes, kernel_size=kernel_size, stride=stride, padding=padding,
                              dilation=dilation, groups=groups, bias=bias)
        self.bn = nn.BatchNorm1d(out_planes, eps=1e-5, momentum=0.01, affine=True) if bn else None
        self.relu = nn.ReLU() if relu else None

    def forward(self, x):
        x = self.conv(x)
        if self.bn is not None:
            x = self.bn(x)
        if self.relu is not None:
            x = self.relu(x)
        return x


class ChannelGate(nn.Module):
    def __init__(self, gate_channels, reduction_ratio=16, pool_types=['avg']):
        super(ChannelGate, self).__init__()
        self.gate_channels = gate_channels
        self.mlp = nn.Sequential(
            nn.Flatten(),
            nn.Linear(gate_channels, gate_channels // reduction_ratio),
            nn.ReLU(),
            nn.Linear(gate_channels // reduction_ratio, gate_channels)
        )
        self.pool_types = pool_types

    def forward(self, x):
        channel_att_sum = None
        for pool_type in self.pool_types:
            if pool_type == 'avg':
                avg_pool = F.avg_pool1d(x, x.size(2), stride=x.size(2))
                channel_att_raw = self.mlp(avg_pool)
            elif pool_type == 'max':
                max_pool = F.max_pool1d(x, x.size(2), stride=x.size(2))
                channel_att_raw = self.mlp(max_pool)
            elif pool_type == 'lp':
                lp_pool = F.lp_pool2d(x, 2, (x.size(2), x.size(3)), stride=(x.size(2), x.size(3)))
                channel_att_raw = self.mlp(lp_pool)
            elif pool_type == 'lse':
                # LSE pool only
                lse_pool = logsumexp_2d(x)
                channel_att_raw = self.mlp(lse_pool)

            if channel_att_sum is None:
                channel_att_sum = channel_att_raw
            else:
                channel_att_sum = channel_att_sum + channel_att_raw

        scale = F.sigmoid(channel_att_sum).unsqueeze(2).expand_as(x)
        return x * scale


def logsumexp_2d(tensor):
    tensor_flatten = tensor.view(tensor.size(0), tensor.size(1), -1)
    s, _ = torch.max(tensor_flatten, dim=2, keepdim=True)
    outputs = s + (tensor_flatten - s).exp().sum(dim=2, keepdim=True).log()
    return outputs


feature_len_dict = [[5, 24, 120], [10, 48, 240], [15, 72, 360], [20, 96, 480], [24, 120, 600], [29, 144, 720],
                    [34, 168, 840], [39, 192, 960], [44, 216, 1080], [48, 240, 1200]]


class PositionalEncoding(nn.Module):

    def __init__(self, in_features, out_features):
        super(PositionalEncoding, self).__init__()
        self.num_scales = 128

        self.fc = nn.Linear(in_features=in_features, out_features=out_features)
        self.act_fn = nn.PReLU()

        if self.num_scales > 1:
            self.max_len = feature_len_dict[10 - 1][3 - 1]
        else:
            self.max_len = 5000

        pe = torch.zeros(self.max_len, out_features)
        position = torch.arange(0, self.max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, out_features, 2).float() * (-math.log(10000.0) / out_features))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = self.act_fn(self.fc(x))

        if self.num_scales > 1:
            hop = self.max_len // x.size(0)
            pe = self.pe[hop // 2::hop, :]
        else:
            pe = self.pe

        if pe.shape[0] != x.size(0):  # 保证pe大小和x的大小相同
            pe = pe[:x.size(0), :]

        x = x + pe

        return x


class Transformer(nn.Module):

    def __init__(self, nheads, num_encoder_layers, pool='attn'):

        super(Transformer, self).__init__()

        self.model_dim = 128
        self.feedforward_dim = 128

        self.in_features = 128
        self.out_features = 128

        self.pos_encoding = PositionalEncoding(self.in_features, self.out_features)

        self.transformer_layer = nn.TransformerEncoderLayer(
            d_model=self.model_dim,
            nhead=nheads,
            dim_feedforward=self.feedforward_dim,
            dropout=0
        )
        self.transformer = nn.TransformerEncoder(self.transformer_layer, num_layers=num_encoder_layers)

        self.pool = pool

        if pool == 'attn':
            self.w_ha = nn.Linear(self.model_dim, self.model_dim, bias=True)
            self.w_at = nn.Linear(self.model_dim, 1, bias=False)

        self.fc = nn.Linear(self.model_dim, 6)

    def forward(self, x):
        x = x.transpose(0, 1)
        x = self.pos_encoding(x)
        x = self.transformer(x)
        x = x.transpose(0, 1)

        if self.pool == 'mean':
            x = x.mean(dim=1)
        elif self.pool == 'last':
            x = x[:, -1]
        elif self.pool == 'attn':
            a_states = torch.tanh(self.w_ha(x))
            alpha = torch.softmax(self.w_at(a_states), dim=1).view(x.size(0), 1, x.size(1))
            x = torch.bmm(alpha, a_states).view(x.size(0), -1)
        elif self.pool == None:
            x = x
        else:
            raise NotImplementedError

        out = self.fc(x)

        return out


class MainModel(nn.Module):

    def __init__(self):

        super(MainModel, self).__init__()

        self.feature = SleePyCoBackbone()

        self.classifier = Transformer(nheads=8, num_encoder_layers=6, pool='attn')

    def get_max_len(self, features):
        len_list = []
        for feature in features:
            len_list.append(feature.shape[1])

        return max(len_list)

    def forward(self, x):
        outputs = []
        features = self.feature(x)

        for feature in features:
            feature = feature.transpose(1, 2)
            output = self.classifier(feature)
            outputs.append(output)

        return outputs
