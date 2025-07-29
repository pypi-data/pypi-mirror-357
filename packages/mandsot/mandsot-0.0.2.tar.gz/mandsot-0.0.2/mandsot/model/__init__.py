import torch
import torch.nn as nn
import importlib.resources as pkg_resources
from mandsot import pretrained


class MandSOT(nn.Module):
    def __init__(self):
        super(MandSOT, self).__init__()
        self.conv1 = nn.Conv1d(in_channels=80, out_channels=128, kernel_size=2, stride=1, padding=1)
        self.pool1 = nn.MaxPool1d(kernel_size=2, stride=2)

        self.conv2 = nn.Conv1d(in_channels=128, out_channels=256, kernel_size=2, stride=1, padding=1)
        self.pool2 = nn.MaxPool1d(kernel_size=2, stride=2)

        self.conv3 = nn.Conv1d(in_channels=256, out_channels=256, kernel_size=2, stride=1, padding=1)
        self.pool3 = nn.MaxPool1d(kernel_size=2, stride=2)

        self.dropout = nn.Dropout(p=0.2)
        # self.embedding_layer = nn.Embedding(num_embeddings=30, embedding_dim=64)

        self.fc1 = nn.Linear(in_features=36096, out_features=512)
        self.fc2 = nn.Linear(in_features=512, out_features=256)
        self.fc3 = nn.Linear(in_features=256, out_features=1)

    def forward(self, mfcc, initial):
        x = self.pool1(torch.relu(self.conv1(mfcc)))
        x = self.pool2(torch.relu(self.conv2(x)))
        x = self.pool3(torch.relu(self.conv3(x)))

        # x = torch.cat([x, x1, x2, x3], 2)
        x = torch.flatten(x, start_dim=1)

        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)

        return x


class MandSOTRNN(nn.Module):
    def __init__(self, input_dim=80, hidden_dim=128, rnn_layers=1, dropout=0.3):
        super(MandSOTRNN, self).__init__()

        self.rnn = nn.GRU(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=rnn_layers,
            batch_first=True,
            bidirectional=True
        )

        self.dropout = nn.Dropout(dropout)
        self.pooling = nn.AdaptiveAvgPool1d(1)

        self.fc1 = nn.Linear(hidden_dim * 2, 128)
        self.fc2 = nn.Linear(128, 1)

    def forward(self, x, initial):
        # x: [B, T, 80]
        x = x.transpose(1, 2)  # → [B, T, 80]
        rnn_out, _ = self.rnn(x)  # → [B, T, 2H]
        rnn_out = rnn_out.transpose(1, 2)  # → [B, 2H, T]
        pooled = self.pooling(rnn_out).squeeze(-1)  # → [B, 2H]
        x = self.dropout(torch.relu(self.fc1(pooled)))  # → [B, 128]
        out = self.fc2(x).squeeze(-1)  # → [B]
        return out


class MandSOTTransformer(nn.Module):
    def __init__(
        self,
        input_dim=117,
        d_model=256,
        nhead=4,
        num_layers=4,
        dim_feedforward=512,
        dropout=0.1,
        max_len=750
    ):
        super(MandSOTTransformer, self).__init__()

        self.input_proj = nn.Linear(input_dim, d_model)
        self.pos_embedding = nn.Parameter(torch.randn(1, max_len, d_model))

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        self.attn_fc = nn.Linear(d_model, 1)
        self.fc = nn.Linear(d_model, 1)

    def forward(self, x, initial=None):
        x = x.transpose(1, 2)
        B, T, _ = x.size()

        x = self.input_proj(x)
        x = x + self.pos_embedding[:, :T, :]
        x = self.transformer(x)

        attn_scores = self.attn_fc(x)
        attn_weights = torch.softmax(attn_scores, dim=1)
        x = (x * attn_weights).sum(dim=1)

        out = self.fc(x).squeeze(-1)
        return out


def load_model(model_class, model_path=None, device='cpu', verbose=True):
    if model_path is None:
        with pkg_resources.path(pretrained, 'sot_best.pth') as default_path:
            model_path = str(default_path)
        if verbose:
            print(f"Using default pretrained model: {model_path}")
    else:
        if verbose:
            print(f"Using user-specified model: {model_path}")

    # load model
    model = model_class()
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)

    return model
