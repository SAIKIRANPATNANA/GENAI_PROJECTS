import argparse
import json
import random
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import requests
import torch
import torch.nn as nn
import torch.nn.functional as F


DATASET_URL = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"


@dataclass
class Config:
    vocab_size: int = 0
    block_size: int = 256
    n_embd: int = 384
    n_head: int = 8
    n_layer: int = 8
    dropout: float = 0.1
    bias: bool = True
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


cfg = Config()


def pretokenize(text):
    import re

    return re.findall(r"\w+|[^\w\s]", text)


def get_pair_counts(vocab):
    pairs = Counter()
    for word, freq in vocab.items():
        for i in range(len(word) - 1):
            pairs[(word[i], word[i + 1])] += freq
    return pairs


def merge_pair(pair, vocab):
    new_vocab = Counter()
    replacement = pair[0] + pair[1]

    for word, freq in vocab.items():
        new_word = []
        i = 0

        while i < len(word):
            if i < len(word) - 1 and (word[i], word[i + 1]) == pair:
                new_word.append(replacement)
                i += 2
            else:
                new_word.append(word[i])
                i += 1

        new_vocab[tuple(new_word)] += freq

    return new_vocab


class BPETokenizer:
    def __init__(self, num_merges=1000):
        self.num_merges = num_merges
        self.merges = []
        self.stoi = {}
        self.itos = {}

    def train(self, text):
        words = pretokenize(text)
        vocab = Counter()

        for word in words:
            tokens = tuple(list(word) + ["</w>"])
            vocab[tokens] += 1

        for _ in range(self.num_merges):
            pairs = get_pair_counts(vocab)
            if not pairs:
                break

            best = max(pairs, key=pairs.get)
            self.merges.append(best)
            vocab = merge_pair(best, vocab)

        tokens = set()
        for word in vocab:
            for token in word:
                tokens.add(token)

        tokens = sorted(tokens)
        self.stoi = {token: i for i, token in enumerate(tokens)}
        self.itos = {i: token for token, i in self.stoi.items()}

    def save(self, path):
        data = {
            "num_merges": self.num_merges,
            "merges": self.merges,
            "tokens": [self.itos[i] for i in range(len(self.itos))],
        }
        Path(path).write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text())
        tokenizer = cls(num_merges=data["num_merges"])
        tokenizer.merges = [tuple(pair) for pair in data["merges"]]
        tokens = data["tokens"]
        tokenizer.stoi = {token: i for i, token in enumerate(tokens)}
        tokenizer.itos = {i: token for token, i in tokenizer.stoi.items()}
        return tokenizer

    @property
    def vocab_size(self):
        return len(self.stoi)

    def encode(self, text):
        words = pretokenize(text)
        output = []

        for word in words:
            symbols = list(word) + ["</w>"]

            for pair in self.merges:
                i = 0
                new_symbols = []

                while i < len(symbols):
                    if i < len(symbols) - 1 and (symbols[i], symbols[i + 1]) == pair:
                        new_symbols.append(symbols[i] + symbols[i + 1])
                        i += 2
                    else:
                        new_symbols.append(symbols[i])
                        i += 1

                symbols = new_symbols

            output.extend(symbols)
        return [self.stoi[token] for token in output]

    def decode(self, ids):
        tokens = [self.itos[i] for i in ids]
        text = "".join(tokens)
        return text.replace("</w>", " ")


class RMSNorm(nn.Module):
    def __init__(self, dim, eps=1e-8):
        super().__init__()
        self.eps = eps
        self.scale = nn.Parameter(torch.ones(dim))

    def forward(self, x):
        rms = x.pow(2).mean(dim=-1, keepdim=True).sqrt()
        return self.scale * (x / (rms + self.eps))


class Head(nn.Module):
    def __init__(self, head_size):
        super().__init__()
        self.key = nn.Linear(cfg.n_embd, head_size, bias=False)
        self.query = nn.Linear(cfg.n_embd, head_size, bias=False)
        self.value = nn.Linear(cfg.n_embd, head_size, bias=False)
        self.dropout = nn.Dropout(cfg.dropout)
        self.register_buffer("tril", torch.tril(torch.ones(cfg.block_size, cfg.block_size)))

    def forward(self, x, past_k=None, past_v=None):
        batch_size, token_count, _ = x.shape

        k = self.key(x)
        q = self.query(x)
        v = self.value(x)

        if past_k is not None:
            k = torch.cat([past_k, k], dim=1)
            v = torch.cat([past_v, v], dim=1)

        wei = q @ k.transpose(-2, -1) * (k.shape[-1] ** -0.5)

        if past_k is None:
            wei = wei.masked_fill(self.tril[:token_count, :token_count] == 0, float("-inf"))

        wei = F.softmax(wei, dim=-1)
        wei = self.dropout(wei)
        out = wei @ v
        return out, k, v


class MultiHeadAttention(nn.Module):
    def __init__(self):
        super().__init__()
        head_size = cfg.n_embd // cfg.n_head
        self.heads = nn.ModuleList([Head(head_size) for _ in range(cfg.n_head)])
        self.proj = nn.Linear(cfg.n_embd, cfg.n_embd)
        self.dropout = nn.Dropout(cfg.dropout)

    def forward(self, x, past_kv=None):
        new_kv = []
        outputs = []

        for i, head in enumerate(self.heads):
            past_k, past_v = (None, None)
            if past_kv is not None:
                past_k, past_v = past_kv[i]

            out, k, v = head(x, past_k, past_v)
            outputs.append(out)
            new_kv.append((k, v))

        out = torch.cat(outputs, dim=-1)
        out = self.proj(out)
        return out, new_kv


class FeedForward(nn.Module):
    def __init__(self):
        super().__init__()
        hidden_dim = int((2 / 3) * 4 * cfg.n_embd)
        self.w1 = nn.Linear(cfg.n_embd, hidden_dim, bias=cfg.bias)
        self.w2 = nn.Linear(cfg.n_embd, hidden_dim, bias=cfg.bias)
        self.proj = nn.Linear(hidden_dim, cfg.n_embd, bias=cfg.bias)
        self.dropout = nn.Dropout(cfg.dropout)

    def forward(self, x):
        x1 = self.w1(x)
        x2 = self.w2(x)
        return self.dropout(self.proj(F.silu(x1) * x2))


class Block(nn.Module):
    def __init__(self):
        super().__init__()
        self.norm1 = RMSNorm(cfg.n_embd)
        self.attn = MultiHeadAttention()
        self.norm2 = RMSNorm(cfg.n_embd)
        self.ffwd = FeedForward()

    def forward(self, x, past_kv=None):
        attn_out, new_kv = self.attn(self.norm1(x), past_kv)
        x = x + attn_out
        x = x + self.ffwd(self.norm2(x))
        return x, new_kv


class PSKGPT(nn.Module):
    def __init__(self):
        super().__init__()
        self.token_embedding = nn.Embedding(cfg.vocab_size, cfg.n_embd)
        self.position_embedding = nn.Embedding(cfg.block_size, cfg.n_embd)
        self.blocks = nn.ModuleList([Block() for _ in range(cfg.n_layer)])
        self.ln_f = RMSNorm(cfg.n_embd)
        self.lm_head = nn.Linear(cfg.n_embd, cfg.vocab_size, bias=False)
        self.lm_head.weight = self.token_embedding.weight

    def forward(self, idx, targets=None, past_kv=None):
        batch_size, token_count = idx.shape

        tok_emb = self.token_embedding(idx)
        pos = torch.arange(token_count, device=idx.device)
        pos_emb = self.position_embedding(pos)
        x = tok_emb + pos_emb

        new_kv_all = []
        for i, block in enumerate(self.blocks):
            past = None if past_kv is None else past_kv[i]
            x, new_kv = block(x, past)
            new_kv_all.append(new_kv)

        x = self.ln_f(x)
        logits = self.lm_head(x)

        loss = None
        if targets is not None:
            _, _, vocab_size = logits.shape
            loss = F.cross_entropy(logits.view(batch_size * token_count, vocab_size), targets.view(batch_size * token_count))

        return logits, loss, new_kv_all

    @staticmethod
    def sample_top_p(probs, p=0.9):
        sorted_probs, sorted_indices = torch.sort(probs, descending=True)
        cumulative_probs = torch.cumsum(sorted_probs, dim=-1)

        cutoff = cumulative_probs > p
        cutoff[..., 1:] = cutoff[..., :-1].clone()
        cutoff[..., 0] = False

        sorted_probs[cutoff] = 0.0
        sorted_probs = sorted_probs / sorted_probs.sum()

        idx = torch.multinomial(sorted_probs, 1)
        return sorted_indices[idx]

    @torch.no_grad()
    def generate(self, idx, max_new_tokens, temperature=1.0, top_k=None, top_p=None):
        past_kv = None

        for _ in range(max_new_tokens):
            idx_cond = idx[:, -1:] if past_kv else idx[:, -cfg.block_size:]
            logits, _, past_kv = self(idx_cond, past_kv=past_kv)
            logits = logits[:, -1, :] / temperature
            probs = F.softmax(logits, dim=-1)

            if top_k is not None:
                v, _ = torch.topk(probs, top_k)
                probs[probs < v[:, [-1]]] = 0
                probs = probs / probs.sum(dim=-1, keepdim=True)

            if top_p is not None:
                idx_next = self.sample_top_p(probs[0], top_p).unsqueeze(0)
            else:
                idx_next = torch.multinomial(probs, 1)

            idx = torch.cat((idx, idx_next), dim=1)
            yield idx_next.item()


def load_dataset(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def stream_text(text, delay):
    for ch in text:
        print(ch, end="", flush=True)
        if delay > 0:
            time.sleep(delay)


def main():
    parser = argparse.ArgumentParser(description="Run PSKGPT text generation from the terminal.")
    parser.add_argument("--prompt", default="ROMEO:\n", help="Prompt text to continue.")
    parser.add_argument("--tokens", type=int, default=180, help="Number of new tokens to generate.")
    parser.add_argument("--temperature", type=float, default=0.8, help="Sampling temperature.")
    parser.add_argument("--top-k", type=int, default=40, help="Top-k sampling cutoff. Use 0 to disable.")
    parser.add_argument("--top-p", type=float, default=0.9, help="Top-p sampling cutoff. Use 0 to disable.")
    parser.add_argument("--checkpoint", default="best_v2.pt", help="Path to the trained checkpoint.")
    parser.add_argument("--dataset-url", default=DATASET_URL, help="Dataset URL used to rebuild the BPE tokenizer.")
    parser.add_argument("--tokenizer-cache", default="tokenizer_bpe.json", help="Path for the cached BPE tokenizer.")
    parser.add_argument("--rebuild-tokenizer", action="store_true", help="Force rebuilding the BPE tokenizer cache.")
    parser.add_argument("--device", default=cfg.device, help="Device to use: cuda, cpu, or auto-detected default.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument("--delay", type=float, default=0.015, help="Delay per printed character for recording.")
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    random.seed(args.seed)
    cfg.device = args.device

    print("PSKGPT terminal demo")
    print("====================")
    print(f"Device      : {cfg.device}")
    print(f"Checkpoint  : {args.checkpoint}")
    cache_path = Path(args.tokenizer_cache)
    if cache_path.exists() and not args.rebuild_tokenizer:
        print(f"Tokenizer   : loading {cache_path}")
        tokenizer = BPETokenizer.load(cache_path)
    else:
        print("Tokenizer   : training custom BPE from Tiny Shakespeare...")
        text = load_dataset(args.dataset_url)
        tokenizer = BPETokenizer(num_merges=1000)
        tokenizer.train(text)
        tokenizer.save(cache_path)
        print(f"Tokenizer   : saved {cache_path}")

    cfg.vocab_size = tokenizer.vocab_size

    print(f"Vocab size  : {cfg.vocab_size}")
    print("Model       : loading weights...")

    model = PSKGPT().to(cfg.device)
    state_dict = torch.load(args.checkpoint, map_location=cfg.device)
    model.load_state_dict(state_dict)
    model.eval()

    top_k = None if args.top_k <= 0 else args.top_k
    top_p = None if args.top_p <= 0 else args.top_p

    ids = tokenizer.encode(args.prompt)
    if len(ids) == 0:
        ids = [0]

    idx = torch.tensor([ids], dtype=torch.long, device=cfg.device)

    print(f"Temperature : {args.temperature}")
    print(f"Top-k       : {top_k}")
    print(f"Top-p       : {top_p}")
    print()
    print("Prompt")
    print("------")
    stream_text(args.prompt, args.delay)
    print()
    print()
    print("Generated")
    print("---------")

    generated_ids = []
    for token_id in model.generate(
        idx,
        max_new_tokens=args.tokens,
        temperature=args.temperature,
        top_k=top_k,
        top_p=top_p,
    ):
        generated_ids.append(token_id)
        stream_text(tokenizer.decode([token_id]), args.delay)

    print()


if __name__ == "__main__":
    main()
