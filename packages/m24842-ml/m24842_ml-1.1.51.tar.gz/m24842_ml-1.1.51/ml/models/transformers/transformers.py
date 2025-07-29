import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.linalg as LA
import torch.autograd as AG
import math
from einops import rearrange
import opt_einsum
from rotary_embedding_torch import RotaryEmbedding
from .attention import *
from ..common import *

class Transformer(nn.Module):
    def __init__(self, emb_dim, input_dim, output_dim,
                 n_layers=1, n_heads=1, mlp_dim=None, attn_sink=False,
                 dropout=0.0, causal=True, use_embedding=True, weight_tying=False,
                 mlp_bias=True, attn_bias=True,
                 pos_encoding=None, pos_encoding_max_len=None,
                 device="cpu"):
        super().__init__()
        self.emb_dim = emb_dim
        self.output_dim = output_dim
        self.causal = causal
        self.n_layers = n_layers
        self.n_heads = n_heads
        self.mlp_dim = mlp_dim if mlp_dim is not None else 2*emb_dim
        
        self.use_embedding = use_embedding
        if use_embedding: self.embedding = nn.Embedding(input_dim, emb_dim, device=device)
        else: self.embedding = nn.Linear(input_dim, emb_dim, bias=False, device=device)
        
        self.out_proj = nn.Linear(emb_dim, output_dim, bias=False, device=device)
        
        self.pos_encoding = pos_encoding
        if pos_encoding == "rope":
            self.rope = RotaryEmbedding(dim=emb_dim//(2*self.n_heads), use_xpos=False, cache_if_possible=False)
        elif pos_encoding == "xpos":
            self.rope = RotaryEmbedding(dim=emb_dim//(2*self.n_heads), use_xpos=True, cache_if_possible=False)
        elif pos_encoding == "abs":
            assert pos_encoding_max_len is not None, "pos_encoding_max_len must be provided for absolute positional encoding"
            self.pos_encoding_max_len = pos_encoding_max_len
        else: self.rope = None
        
        self.layers = nn.ModuleList([
            nn.ModuleDict(
                dict(
                    norm1 = nn.RMSNorm(emb_dim, device=device),
                    abs_pos_encoding = nn.Embedding(pos_encoding_max_len, emb_dim, device=device) if pos_encoding == "abs" else None,
                    dropout1 = nn.Dropout(dropout),
                    attention = MultiheadAttention(emb_dim, self.n_heads, attn_sink=attn_sink, bias=attn_bias, batch_first=True, device=device),
                    norm2 = nn.RMSNorm(emb_dim, device=device),
                    dropout2 = nn.Dropout(dropout),
                    feedforward = nn.Sequential(
                        nn.Linear(emb_dim, self.mlp_dim, bias=mlp_bias, device=device),
                        nn.ReLU(),
                        nn.Dropout(dropout),
                        nn.Linear(self.mlp_dim, emb_dim, bias=mlp_bias, device=device)
                    )
                )
            ) for _ in range(self.n_layers)
        ])
        self.norm_f = nn.RMSNorm(emb_dim, device=device)
        
        nn.init.xavier_uniform_(self.embedding.weight)
        if weight_tying: self.out_proj.weight = self.embedding.weight
        else: nn.init.xavier_uniform_(self.out_proj.weight)
        
        self.to(device)
        
    def forward(self, x):
        seq_len = x.size(1)
        if self.use_embedding: x = self.embedding(x.long())
        else: x = self.embedding(x)
        if self.causal: mask = torch.triu(torch.full((seq_len, seq_len), float('-inf'), device=x.device), diagonal=1)
        else: mask = None
        for layer in self.layers:
            x = layer.norm1(x)
            if layer.abs_pos_encoding is not None:
                pos = torch.arange(seq_len, device=x.device, dtype=torch.long).unsqueeze(0).expand(x.size(0), -1)
                x = x + layer.abs_pos_encoding(pos)
            a_out = layer.attention(x, attn_mask=mask, rope=self.rope if self.pos_encoding == "rope" else None)
            x = layer.norm2(x + layer.dropout1(a_out))
            ff_out = layer.feedforward(x)
            x = x + layer.dropout2(ff_out)
        x = self.norm_f(x)
        x = self.out_proj(x)
        return x

class LinearTransformer(nn.Module):
    def __init__(self, emb_dim, input_dim, output_dim,
                 n_layers=1, n_heads=1, mlp_dim=None, attn_sink=False,
                 dropout=0.0, causal=True, use_embedding=True, weight_tying=False,
                 mlp_bias=True, attn_bias=True,
                 pos_encoding=None, pos_encoding_max_len=None,
                 device="cpu"):
        super().__init__()
        self.emb_dim = emb_dim
        self.output_dim = output_dim
        self.causal = causal
        self.n_layers = n_layers
        self.n_heads = n_heads
        self.mlp_dim = mlp_dim if mlp_dim is not None else 2*emb_dim
        
        self.use_embedding = use_embedding
        if use_embedding: self.embedding = nn.Embedding(input_dim, emb_dim, device=device)
        else: self.embedding = nn.Linear(input_dim, emb_dim, bias=False, device=device)
        
        self.out_proj = nn.Linear(emb_dim, output_dim, bias=False, device=device)
        
        self.pos_encoding = pos_encoding
        if pos_encoding == "rope":
            self.rope = RotaryEmbedding(dim=emb_dim//(2*self.n_heads), use_xpos=False, cache_if_possible=False)
        elif pos_encoding == "xpos":
            self.rope = RotaryEmbedding(dim=emb_dim//(2*self.n_heads), use_xpos=True, cache_if_possible=False)
        elif pos_encoding == "abs":
            assert pos_encoding_max_len is not None, "pos_encoding_max_len must be provided for absolute positional encoding"
            self.pos_encoding_max_len = pos_encoding_max_len
        else: self.rope = None
        
        self.layers = nn.ModuleList([
            nn.ModuleDict(
                dict(
                    norm1 = nn.RMSNorm(emb_dim, device=device),
                    dropout1 = nn.Dropout(dropout),
                    abs_pos_encoding = nn.Embedding(pos_encoding_max_len, emb_dim, device=device) if pos_encoding == "abs" else None,
                    attention = LinearAttention(emb_dim, self.n_heads, attn_sink=attn_sink, bias=attn_bias, device=device),
                    norm2 = nn.RMSNorm(emb_dim, device=device),
                    dropout2 = nn.Dropout(dropout),
                    feedforward = nn.Sequential(
                        nn.Linear(emb_dim, self.mlp_dim, bias=mlp_bias, device=device),
                        nn.ReLU(),
                        nn.Dropout(dropout),
                        nn.Linear(self.mlp_dim, emb_dim, bias=mlp_bias, device=device)
                    )
                )
            ) for _ in range(self.n_layers)
        ])
        self.norm_f = nn.RMSNorm(emb_dim, device=device)
        
        nn.init.xavier_uniform_(self.embedding.weight)
        if weight_tying: self.out_proj.weight = self.embedding.weight
        else: nn.init.xavier_uniform_(self.out_proj.weight)
        
        self.to(device)
        
    def forward(self, x):
        seq_len = x.size(1)
        if self.use_embedding: x = self.embedding(x.long())
        else: x = self.embedding(x)
        for layer in self.layers:
            x = layer.norm1(x)
            if layer.abs_pos_encoding is not None:
                pos = torch.arange(seq_len, device=x.device, dtype=torch.long).unsqueeze(0).expand(x.size(0), -1)
                x = x + layer.abs_pos_encoding(pos)
            a_out = layer.attention(x, rope=self.rope if self.pos_encoding == "rope" else None, causal=self.causal)
            x = layer.norm2(x + layer.dropout1(a_out))
            ff_out = layer.feedforward(x)
            x = x + layer.dropout2(ff_out)
        x = self.norm_f(x)
        x = self.out_proj(x)
        return x

class OrthoLinearTransformer(nn.Module):
    def __init__(self, emb_dim, input_dim, output_dim,
                 n_layers=1, n_heads=1, mlp_dim=None, attn_sink=False,
                 dropout=0.0, causal=True, use_embedding=True, weight_tying=False,
                 mlp_bias=True, attn_bias=True,
                 pos_encoding=None, pos_encoding_max_len=None,
                 device="cpu"):
        super().__init__()
        self.emb_dim = emb_dim
        self.output_dim = output_dim
        self.causal = causal
        self.n_heads = n_heads
        self.n_layers = n_layers
        self.mlp_dim = mlp_dim if mlp_dim is not None else 2*emb_dim
        
        self.use_embedding = use_embedding
        if use_embedding: self.embedding = nn.Embedding(input_dim, emb_dim, device=device)
        else: self.embedding = nn.Linear(input_dim, emb_dim, bias=False, device=device)
        
        self.out_proj = nn.Linear(emb_dim, output_dim, bias=False, device=device)
        
        self.pos_encoding = pos_encoding
        if pos_encoding == "rope":
            self.rope = RotaryEmbedding(dim=emb_dim//(2*self.n_heads), use_xpos=False, cache_if_possible=False)
        elif pos_encoding == "xpos":
            self.rope = RotaryEmbedding(dim=emb_dim//(2*self.n_heads), use_xpos=True, cache_if_possible=False)
        elif pos_encoding == "abs":
            assert pos_encoding_max_len is not None, "pos_encoding_max_len must be provided for absolute positional encoding"
            self.pos_encoding_max_len = pos_encoding_max_len
        else: self.rope = None
        
        self.layers = nn.ModuleList([
            nn.ModuleDict(
                dict(
                    norm1 = nn.RMSNorm(emb_dim, device=device),
                    dropout1 = nn.Dropout(dropout),
                    abs_pos_encoding = nn.Embedding(pos_encoding_max_len, emb_dim, device=device) if pos_encoding == "abs" else None,
                    attention = OrthoLinearAttention(emb_dim, self.n_heads, attn_sink=attn_sink, bias=attn_bias, device=device),
                    norm2 = nn.RMSNorm(emb_dim, device=device),
                    dropout2 = nn.Dropout(dropout),
                    feedforward = nn.Sequential(
                        nn.Linear(emb_dim, self.mlp_dim, bias=mlp_bias, device=device),
                        nn.ReLU(),
                        nn.Dropout(dropout),
                        nn.Linear(self.mlp_dim, emb_dim, bias=mlp_bias, device=device)
                    )
                )
            ) for _ in range(self.n_layers)
        ])
        self.norm_f = nn.RMSNorm(emb_dim, device=device)
        
        nn.init.xavier_uniform_(self.embedding.weight)
        if weight_tying: self.out_proj.weight = self.embedding.weight
        else: nn.init.xavier_uniform_(self.out_proj.weight)
        
        self.to(device)
        
    def forward(self, x):
        seq_len = x.size(1)
        if self.use_embedding: x = self.embedding(x.long())
        else: x = self.embedding(x)
        for layer in self.layers:
            x = layer.norm1(x)
            if layer.abs_pos_encoding is not None:
                pos = torch.arange(seq_len, device=x.device, dtype=torch.long).unsqueeze(0).expand(x.size(0), -1)
                x = x + layer.abs_pos_encoding(pos)
            a_out = layer.attention(x, rope=self.rope if self.pos_encoding == "rope" else None, causal=self.causal)
            x = layer.norm2(x + layer.dropout1(a_out))
            ff_out = layer.feedforward(x)
            x = x + layer.dropout1(ff_out)
        x = self.norm_f(x)
        x = self.out_proj(x)
        return x

class CompressionTransformer(nn.Module):
    def __init__(self, emb_dim, input_dim, output_dim,
                 n_layers=1, n_heads=1, mlp_dim=None, mem_dim=16, attn_sink=False, 
                 dropout=0.0, causal=True, use_embedding=True, weight_tying=False,
                 mlp_bias=True, attn_bias=True,
                 pos_encoding=None, pos_encoding_max_len=None,
                 device="cpu"):
        super().__init__()
        self.emb_dim = emb_dim
        self.output_dim = output_dim
        self.causal = causal
        self.n_layers = n_layers
        self.n_heads = n_heads
        self.mlp_dim = mlp_dim if mlp_dim is not None else 2*emb_dim
        self.compressed_len = mem_dim
        
        self.use_embedding = use_embedding
        if use_embedding: self.embedding = nn.Embedding(input_dim, emb_dim, device=device)
        else: self.embedding = nn.Linear(input_dim, emb_dim, bias=False, device=device)
        
        self.out_proj = nn.Linear(emb_dim, output_dim, bias=False, device=device)
        
        self.pos_encoding = pos_encoding
        if pos_encoding == "rope":
            self.rope = RotaryEmbedding(dim=emb_dim//(2*self.n_heads), use_xpos=False, cache_if_possible=False)
        elif pos_encoding == "xpos":
            self.rope = RotaryEmbedding(dim=emb_dim//(2*self.n_heads), use_xpos=True, cache_if_possible=False)
        elif pos_encoding == "abs":
            assert pos_encoding_max_len is not None, "pos_encoding_max_len must be provided for absolute positional encoding"
            self.pos_encoding_max_len = pos_encoding_max_len
        else: self.rope = None
        
        self.layers = nn.ModuleList([
            nn.ModuleDict(
                dict(
                    norm1 = nn.RMSNorm(emb_dim, device=device),
                    dropout1 = nn.Dropout(dropout),
                    abs_pos_encoding = nn.Embedding(pos_encoding_max_len, emb_dim, device=device) if pos_encoding == "abs" else None,
                    attention = CompressionAttention(emb_dim, self.n_heads, compressed_len=self.compressed_len, attn_sink=attn_sink, dropout=dropout, bias=attn_bias, batch_first=True, device=device),
                    norm2 = nn.RMSNorm(emb_dim, device=device),
                    dropout2 = nn.Dropout(dropout),
                    feedforward = nn.Sequential(
                        nn.Linear(emb_dim, self.mlp_dim, bias=mlp_bias, device=device),
                        nn.ReLU(),
                        nn.Dropout(dropout),
                        nn.Linear(self.mlp_dim, emb_dim, bias=mlp_bias, device=device)
                    )
                )
            ) for _ in range(self.n_layers)
        ])
        self.norm_f = nn.RMSNorm(emb_dim, device=device)
        
        nn.init.xavier_uniform_(self.embedding.weight)
        if weight_tying: self.out_proj.weight = self.embedding.weight
        else: nn.init.xavier_uniform_(self.out_proj.weight)
        
        self.to(device)
        
    def forward(self, x):
        seq_len = x.size(1)
        if self.use_embedding: x = self.embedding(x.long())
        else: x = self.embedding(x)
        for layer in self.layers:
            x = layer.norm1(x)
            if layer.abs_pos_encoding is not None:
                pos = torch.arange(seq_len, device=x.device, dtype=torch.long).unsqueeze(0).expand(x.size(0), -1)
                x = x + layer.abs_pos_encoding(pos)
            a_out = layer.attention(x, rope=self.rope if self.pos_encoding == "rope" else None, causal=self.causal)
            x = layer.norm2(x + layer.dropout1(a_out))
            ff_out = layer.feedforward(x)
            x = x = x + layer.dropout2(ff_out)
        x = self.norm_f(x)
        x = self.out_proj(x)
        return x

class SlidingWindowTransformer(nn.Module):
    def __init__(self, emb_dim, input_dim, output_dim,
                 n_layers=1, n_heads=1, mlp_dim=None, window_len=64, masked_window=True,
                 attn_sink=False, dilate=True, dilation_factor=None, dropout=0.0,
                 causal=True, use_embedding=True, weight_tying=False,
                 mlp_bias=True, attn_bias=True,
                 pos_encoding=None, pos_encoding_max_len=None,
                 device="cpu"):
        super().__init__()
        self.emb_dim = emb_dim
        self.output_dim = output_dim
        self.causal = causal
        self.n_layers = n_layers
        self.n_heads = n_heads
        self.mlp_dim = mlp_dim if mlp_dim is not None else 2*emb_dim
        
        self.use_embedding = use_embedding
        if use_embedding: self.embedding = nn.Embedding(input_dim, emb_dim, device=device)
        else: self.embedding = nn.Linear(input_dim, emb_dim, bias=False, device=device)
        
        self.out_proj = nn.Linear(emb_dim, output_dim, bias=False, device=device)
        
        self.pos_encoding = pos_encoding
        if pos_encoding == "rope":
            self.rope = RotaryEmbedding(dim=emb_dim//(2*self.n_heads), use_xpos=False, cache_if_possible=False)
        elif pos_encoding == "xpos":
            self.rope = RotaryEmbedding(dim=emb_dim//(2*self.n_heads), use_xpos=True, cache_if_possible=False)
        elif pos_encoding == "abs":
            assert pos_encoding_max_len is not None, "pos_encoding_max_len must be provided for absolute positional encoding"
            self.pos_encoding_max_len = pos_encoding_max_len
        else: self.rope = None
        
        dilation_factor = window_len if dilation_factor is None else dilation_factor
        self.layers = nn.ModuleList([
            nn.ModuleDict(
                dict(
                    norm1 = nn.RMSNorm(emb_dim, device=device),
                    dropout1 = nn.Dropout(dropout),
                    abs_pos_encoding = nn.Embedding(pos_encoding_max_len, emb_dim, device=device) if pos_encoding == "abs" else None,
                    attention = SlidingWindowAttention(emb_dim, self.n_heads, window_len=window_len, masked_window=masked_window, attn_sink=attn_sink, dilation=dilation_factor**i if dilate else 1, dropout=dropout, bias=attn_bias, batch_first=True, device=device),
                    norm2 = nn.RMSNorm(emb_dim, device=device),
                    dropout2 = nn.Dropout(dropout),
                    feedforward = nn.Sequential(
                        nn.Linear(emb_dim, self.mlp_dim, bias=mlp_bias, device=device),
                        nn.ReLU(),
                        nn.Dropout(dropout),
                        nn.Linear(self.mlp_dim, emb_dim, bias=mlp_bias, device=device)
                    )
                )
            ) for i in range(self.n_layers)
        ])
        self.norm_f = nn.RMSNorm(emb_dim, device=device)
        
        nn.init.xavier_uniform_(self.embedding.weight)
        if weight_tying: self.out_proj.weight = self.embedding.weight
        else: nn.init.xavier_uniform_(self.out_proj.weight)
        
        self.to(device)
    
    def forward(self, x):
        seq_len = x.size(1)
        if self.use_embedding: x = self.embedding(x.long())
        else: x = self.embedding(x)
        for layer in self.layers:
            x = layer.norm1(x)
            if layer.abs_pos_encoding is not None:
                pos = torch.arange(seq_len, device=x.device, dtype=torch.long).unsqueeze(0).expand(x.size(0), -1)
                x = x + layer.abs_pos_encoding(pos)
            a_out = layer.attention(x, rope=self.rope if self.pos_encoding == "rope" else None, causal=self.causal)
            x = layer.norm2(x + layer.dropout1(a_out))
            ff_out = layer.feedforward(x)
            x = x = x + layer.dropout2(ff_out)
        x = self.norm_f(x)
        x = self.out_proj(x)
        return x

class FastTransformer(nn.Module):
    def __init__(self, emb_dim, input_dim, output_dim,
                 n_layers=1, n_heads=1, mlp_dim=None,
                 window_len=64, n_dilations=2, dilation_factor=None,
                 attn_sink=False, dropout=0.0, masked_window=True,
                 causal=True, use_embedding=True, weight_tying=False,
                 mlp_bias=True, attn_bias=True,
                 pos_encoding=None, pos_encoding_max_len=None,
                 device="cpu"):
        super().__init__()
        self.emb_dim = emb_dim
        self.output_dim = output_dim
        self.causal = causal
        self.n_layers = n_layers
        self.n_heads = n_heads
        self.mlp_dim = mlp_dim if mlp_dim is not None else 2*emb_dim
        
        self.use_embedding = use_embedding
        if use_embedding: self.embedding = nn.Embedding(input_dim, emb_dim, device=device)
        else: self.embedding = nn.Linear(input_dim, emb_dim, bias=False, device=device)
        
        self.out_proj = nn.Linear(emb_dim, output_dim, bias=False, device=device)
        
        self.pos_encoding = pos_encoding
        if pos_encoding == "rope":
            self.rope = RotaryEmbedding(dim=emb_dim//(2*self.n_heads), use_xpos=False, cache_if_possible=False)
        elif pos_encoding == "xpos":
            self.rope = RotaryEmbedding(dim=emb_dim//(2*self.n_heads), use_xpos=True, cache_if_possible=False)
        elif pos_encoding == "abs":
            assert pos_encoding_max_len is not None, "pos_encoding_max_len must be provided for absolute positional encoding"
            self.pos_encoding_max_len = pos_encoding_max_len
        else: self.rope = None
        
        dilation_factor = window_len if dilation_factor is None else dilation_factor
        self.layers = nn.ModuleList([
            nn.ModuleDict(
                dict(
                    norm1 = nn.RMSNorm(emb_dim, device=device),
                    dropout1 = nn.Dropout(dropout),
                    abs_pos_encoding = nn.Embedding(pos_encoding_max_len, emb_dim, device=device) if pos_encoding == "abs" else None,
                    attention = FastAttention(emb_dim, self.n_heads, window_len=window_len, n_dilations=n_dilations, dilation_factor=dilation_factor, attn_sink=attn_sink, masked_window=masked_window, dropout=dropout, bias=attn_bias, batch_first=True, device=device),
                    norm2 = nn.RMSNorm(emb_dim, device=device),
                    dropout2 = nn.Dropout(dropout),
                    feedforward = nn.Sequential(
                        nn.Linear(emb_dim, self.mlp_dim, bias=mlp_bias, device=device),
                        nn.ReLU(),
                        nn.Dropout(dropout),
                        nn.Linear(self.mlp_dim, emb_dim, bias=mlp_bias, device=device)
                    )
                )
            ) for i in range(self.n_layers)
        ])
        self.norm_f = nn.RMSNorm(emb_dim, device=device)
        
        nn.init.xavier_uniform_(self.embedding.weight)
        if weight_tying: self.out_proj.weight = self.embedding.weight
        else: nn.init.xavier_uniform_(self.out_proj.weight)
        
        self.to(device)
    
    def forward(self, x):
        seq_len = x.size(1)
        if self.use_embedding: x = self.embedding(x.long())
        else: x = self.embedding(x)
        for layer in self.layers:
            x = layer.norm1(x)
            if layer.abs_pos_encoding is not None:
                pos = torch.arange(seq_len, device=x.device, dtype=torch.long).unsqueeze(0).expand(x.size(0), -1)
                x = x + layer.abs_pos_encoding(pos)
            a_out = layer.attention(x, rope=self.rope if self.pos_encoding == "rope" else None, causal=self.causal)
            x = layer.norm2(x + layer.dropout1(a_out))
            ff_out = layer.feedforward(x)
            x = x = x + layer.dropout2(ff_out)
        x = self.norm_f(x)
        x = self.out_proj(x)
        return x

class DiffusionTransformer(nn.Module):
    def __init__(self, emb_dim, input_dim, output_dim,
                 n_layers=1, n_heads=1, mlp_dim=None, attn_sink=False,
                 dropout=0.0, weight_tying=False,
                 mlp_bias=True, attn_bias=True,
                 pos_encoding=None, pos_encoding_max_len=None,
                 device="cpu"):
        super().__init__()
        self.emb_dim = emb_dim
        assert input_dim == output_dim, "input_dim and output_dim must be the same for DiffusionTransformer"
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.n_layers = n_layers
        self.n_heads = n_heads
        self.mlp_dim = mlp_dim if mlp_dim is not None else 2*emb_dim
        
        self.embedding = nn.Linear(input_dim, emb_dim, bias=False, device=device)
        
        self.out_proj = nn.Linear(emb_dim, output_dim, bias=False, device=device)
        
        self.pos_encoding = pos_encoding
        if pos_encoding == "rope":
            self.rope = RotaryEmbedding(dim=emb_dim//(2*self.n_heads), use_xpos=False, cache_if_possible=False)
        elif pos_encoding == "xpos":
            self.rope = RotaryEmbedding(dim=emb_dim//(2*self.n_heads), use_xpos=True, cache_if_possible=False)
        elif pos_encoding == "abs":
            assert pos_encoding_max_len is not None, "pos_encoding_max_len must be provided for absolute positional encoding"
            self.pos_encoding_max_len = pos_encoding_max_len
        else: self.rope = None
        
        self.layers = nn.ModuleList([
            nn.ModuleDict(
                dict(
                    norm1 = nn.RMSNorm(emb_dim, device=device),
                    abs_pos_encoding = nn.Embedding(pos_encoding_max_len, emb_dim, device=device) if pos_encoding == "abs" else None,
                    dropout1 = nn.Dropout(dropout),
                    attention = MultiheadAttention(emb_dim, self.n_heads, attn_sink=attn_sink, bias=attn_bias, batch_first=True, device=device),
                    norm2 = nn.RMSNorm(emb_dim, device=device),
                    dropout2 = nn.Dropout(dropout),
                    feedforward = nn.Sequential(
                        nn.Linear(emb_dim, self.mlp_dim, bias=mlp_bias, device=device),
                        nn.ReLU(),
                        nn.Dropout(dropout),
                        nn.Linear(self.mlp_dim, emb_dim, bias=mlp_bias, device=device)
                    )
                )
            ) for _ in range(self.n_layers)
        ])
        self.norm_f = nn.RMSNorm(emb_dim, device=device)
        
        nn.init.xavier_uniform_(self.embedding.weight)
        if weight_tying: self.out_proj.weight = self.embedding.weight
        else: nn.init.xavier_uniform_(self.out_proj.weight)
        
        self.to(device)
    
    def get_noise(self, x, profile_fn=None, scale=1.0, offset=0.0):
        """
        Args:
            x: input tensor of shape (batch_size, seq_len, emb_dim)
            profile_fn: function to apply to profile gaussian noise, defaults to identity
            scale: scaling factor for profile step resolution, defaults to 1.0
            offset: offset to apply the profile_fn from the end of the sequence, defaults to 0.0
        """
        if profile_fn is None: profile_fn = lambda x: x
        seq_len = x.size(1)
        noise = torch.randn_like(x, device=x.device)
        axis = offset + scale * torch.arange(-seq_len, 0, dtype=torch.float32, device=x.device).reshape(1, seq_len, 1)
        profiled_noise = profile_fn(axis) * noise
        return profiled_noise
    
    def forward(self, x):
        seq_len = x.size(1)
        x_orig = x.clone()
        x = self.embedding(x)
        for layer in self.layers:
            x = layer.norm1(x)
            if layer.abs_pos_encoding is not None:
                pos = torch.arange(seq_len, device=x.device, dtype=torch.long).unsqueeze(0).expand(x.size(0), -1)
                x = x + layer.abs_pos_encoding(pos)
            a_out = layer.attention(x, attn_mask=None, rope=self.rope if self.pos_encoding == "rope" else None)
            x = layer.norm2(x + layer.dropout1(a_out))
            ff_out = layer.feedforward(x)
            x = x + layer.dropout2(ff_out)
        x = self.norm_f(x)
        x = self.out_proj(x)
        return x_orig - x