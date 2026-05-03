# PSKGPT: GPT-Style Language Model from Scratch in PyTorch

PSKGPT is a from-scratch implementation of a GPT-style autoregressive language model built in PyTorch. It implements the core ideas behind decoder-only language models: tokenization, embeddings, causal self-attention, Transformer blocks, next-token prediction, optimization, checkpointing, and controlled text generation.

The notebook contains two versions:

- `PSKGPT`: a baseline character-level GPT model
- `PSKGPT v2`: an upgraded model with a custom BPE tokenizer, RMSNorm, SwiGLU, KV cache, weight tying, top-k/top-p sampling, and inference utilities

The model is trained on Tiny Shakespeare and learns to generate Shakespeare-style text one token at a time.

## Table of Contents

- [Project Overview](#project-overview)
- [Model Configuration](#model-configuration)
- [Dataset](#dataset)
- [Custom BPE Tokenizer](#custom-bpe-tokenizer)
- [Autoregressive Language Modeling](#autoregressive-language-modeling)
- [Embeddings](#embeddings)
- [Transformer Architecture](#transformer-architecture)
- [Self-Attention](#self-attention)
- [Multi-Head Attention](#multi-head-attention)
- [Causal Masking](#causal-masking)
- [Residual Connections](#residual-connections)
- [RMSNorm](#rmsnorm)
- [SwiGLU Feed-Forward Network](#swiglu-feed-forward-network)
- [Rotary Positional Embeddings](#rotary-positional-embeddings)
- [KV Cache](#kv-cache)
- [Weight Tying](#weight-tying)
- [Training Pipeline](#training-pipeline)
- [Optimization Techniques](#optimization-techniques)
- [Inference Pipeline](#inference-pipeline)
- [Sampling Methods](#sampling-methods)
- [Attention Visualization](#attention-visualization)
- [Usage](#usage)
- [Requirements](#requirements)
- [Project Status](#project-status)

## Project Overview

This project is an educational but technically complete implementation of a small GPT-style model. Instead of using Hugging Face Transformers or other high-level libraries, the notebook implements the main components directly in PyTorch.

The project demonstrates:

- How text becomes token IDs
- How token IDs become vectors
- How attention lets tokens communicate
- How causal masking enforces left-to-right generation
- How a Transformer predicts the next token
- How training minimizes cross-entropy loss
- How decoding strategies control generation quality
- How KV caching improves inference speed

At a high level, the model learns a probability distribution:

```text
P(next token | previous tokens)
```

For a sequence:

```text
x_1, x_2, x_3, ..., x_T
```

the model learns:

```text
P(x_t | x_1, x_2, ..., x_{t-1})
```

This is the central idea behind GPT-style language modeling.

## Model Configuration

The upgraded `PSKGPT v2` configuration uses:

| Parameter | Value |
|---|---:|
| Context length | 256 tokens |
| Embedding size | 384 |
| Attention heads | 8 |
| Transformer layers | 8 |
| Dropout | 0.1 |
| Batch size | 32 |
| Learning rate | 2e-4 |
| Max iterations | 20,000 |
| Tokenizer | Custom BPE |
| BPE merges | 1,000 |
| Vocabulary size | 1,004 |
| Parameters | ~14.7M |

The baseline model uses a smaller character-level setup:

| Parameter | Value |
|---|---:|
| Context length | 128 |
| Embedding size | 256 |
| Attention heads | 8 |
| Transformer layers | 6 |
| Vocabulary size | 65 |
| Parameters | ~4.8M |

## Dataset

The model is trained on Tiny Shakespeare:

```text
https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt
```

Dataset statistics from the notebook:

| Metric | Value |
|---|---:|
| Raw characters | 1,115,394 |
| BPE tokens | 399,734 |
| Train tokens | 359,760 |
| Validation tokens | 39,974 |

The split is:

```text
90% training
10% validation
```

The dataset is small enough for fast experimentation but rich enough to learn dialogue structure, character names, punctuation, and Shakespeare-like phrasing.

## Custom BPE Tokenizer

The upgraded model implements a custom Byte Pair Encoding tokenizer.

Tokenization is the process of converting raw text into integer IDs. Neural networks do not operate on strings directly; they operate on tensors. A tokenizer bridges that gap.

### Why BPE?

A character tokenizer has a tiny vocabulary but long sequences.

```text
"king" -> ["k", "i", "n", "g"]
```

A word tokenizer has shorter sequences but a huge vocabulary and poor handling of unknown words.

```text
"king" -> ["king"]
```

BPE sits between these two extremes. It learns frequent subword units:

```text
"speaking" -> ["speak", "ing"]
```

This gives:

- Shorter sequences than character tokenization
- Smaller vocabulary than word tokenization
- Better handling of rare or unseen words

### BPE Algorithm

The notebook uses this process:

1. Pretokenize text into words and punctuation using regex
2. Split each word into characters
3. Add an end-of-word marker `</w>`
4. Count adjacent token pairs
5. Merge the most frequent pair
6. Repeat for `num_merges = 1000`
7. Build `stoi` and `itos` lookup tables

Example initial representation:

```text
"king" -> ("k", "i", "n", "g", "</w>")
```

If `"i" + "n"` is frequent, BPE may merge it:

```text
("k", "i", "n", "g", "</w>")
-> ("k", "in", "g", "</w>")
```

Later, if `"k" + "in"` is frequent:

```text
("k", "in", "g", "</w>")
-> ("kin", "g", "</w>")
```

Eventually:

```text
("kin", "g</w>")
```

### Mathematical Intuition

BPE is a greedy compression algorithm. At each step, it chooses the adjacent pair with maximum frequency:

```text
(a*, b*) = argmax count(a, b)
```

Then every occurrence of `(a*, b*)` is replaced by the merged token `a*b`.

The intuition is simple: frequent patterns should become single units because this reduces sequence length and makes the model spend less computation rediscovering common chunks.

### Encode and Decode

Encoding maps text to token IDs:

```python
ids = encode("ROMEO speaking")
```

Decoding maps token IDs back to text:

```python
text = decode(ids)
```

The notebook uses:

```python
stoi = {token: id}
itos = {id: token}
```

## Autoregressive Language Modeling

PSKGPT is an autoregressive model. It predicts the next token using only previous tokens.

Given:

```text
x = [x_1, x_2, x_3, ..., x_T]
```

the training target is:

```text
y = [x_2, x_3, x_4, ..., x_{T+1}]
```

So the model receives:

```text
"ROMEO:"
```

and learns to predict what token should come next.

### Probability Factorization

The probability of a full sequence is decomposed as:

```text
P(x_1, x_2, ..., x_T)
= P(x_1) P(x_2 | x_1) P(x_3 | x_1, x_2) ... P(x_T | x_1, ..., x_{T-1})
```

More compactly:

```text
P(x_1:T) = product over t of P(x_t | x_<t)
```

This is why causal masking is required. The model must not see future tokens while predicting the current target.

## Embeddings

Token IDs are discrete integers, but neural networks need continuous vectors. The embedding layer maps each token ID to a learned vector.

```python
self.token_embedding = nn.Embedding(cfg.vocab_size, cfg.n_embd)
```

If the vocabulary size is `V` and embedding dimension is `C`, the embedding table has shape:

```text
V x C
```

For `PSKGPT v2`:

```text
1004 x 384
```

### Mathematical Intuition

An embedding lookup is equivalent to selecting a row from a matrix.

If token `i` is represented as a one-hot vector `e_i`, then:

```text
embedding_i = e_i W
```

where:

```text
W is the embedding matrix
```

The model learns this matrix during training. Tokens that appear in similar contexts tend to develop similar vector representations.

## Positional Embeddings

Self-attention alone does not know token order. Without positional information, the model sees a bag of token vectors.

The notebook uses learned absolute positional embeddings:

```python
self.position_embedding = nn.Embedding(cfg.block_size, cfg.n_embd)
```

For each position:

```text
0, 1, 2, ..., T-1
```

the model learns a position vector. Token and position embeddings are added:

```text
x = token_embedding + position_embedding
```

### Mathematical Intuition

The model input at position `t` becomes:

```text
h_t = E[token_t] + P[t]
```

where:

- `E[token_t]` is the token meaning
- `P[t]` is the position signal

This lets the same token have different representations depending on where it appears in the sequence.

## Transformer Architecture

The model is a stack of Transformer decoder blocks.

```text
Input token IDs
    |
Token + position embeddings
    |
Transformer block 1
    |
Transformer block 2
    |
...
    |
Transformer block N
    |
Final normalization
    |
Language modeling head
    |
Logits over vocabulary
```

Each block contains:

```text
RMSNorm
Multi-head causal self-attention
Residual connection
RMSNorm
SwiGLU feed-forward network
Residual connection
```

The Transformer alternates between:

- Communication across tokens through attention
- Per-token nonlinear transformation through the feed-forward network

## Self-Attention

Self-attention is the core operation that lets every token look at previous tokens and decide which ones matter.

For each input vector `x`, the model computes:

```text
q = x W_Q
k = x W_K
v = x W_V
```

where:

- `q` is the query: what this token is looking for
- `k` is the key: what this token offers to be matched against
- `v` is the value: the information this token contributes

### Attention Score

For two tokens `i` and `j`, attention score is:

```text
score(i, j) = q_i dot k_j
```

If the dot product is large, token `i` should pay more attention to token `j`.

The score is scaled:

```text
score(i, j) = (q_i dot k_j) / sqrt(d_k)
```

where `d_k` is the head dimension.

### Why Divide by sqrt(d_k)?

As vector dimension grows, dot products tend to grow in magnitude. Large scores push softmax into saturated regions, where one token gets almost all probability and gradients become less useful.

Scaling by `sqrt(d_k)` keeps the variance of attention scores stable.

### Attention Weights

Scores are converted into probabilities using softmax:

```text
attention_weights = softmax(QK^T / sqrt(d_k))
```

Then values are combined:

```text
output = attention_weights V
```

Full formula:

```text
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
```

### Intuition

Each output token becomes a weighted mixture of previous token information.

For example, in:

```text
"The king said he"
```

the token `"he"` may attend strongly to `"king"` because that token helps resolve meaning.

## Multi-Head Attention

Instead of using one attention operation, the model uses multiple attention heads.

```python
n_head = 8
```

Each head gets a smaller projection of the embedding dimension.

For `PSKGPT v2`:

```text
n_embd = 384
n_head = 8
head_size = 384 / 8 = 48
```

Each head computes attention independently:

```text
head_i = Attention(Q_i, K_i, V_i)
```

The outputs are concatenated:

```text
concat = [head_1, head_2, ..., head_8]
```

Then projected back to the model dimension:

```text
output = concat W_O
```

### Mathematical Intuition

One attention head might learn syntax, another might learn speaker names, another might learn punctuation or long-range dependencies.

Multi-head attention gives the model several independent "views" of the same context.

## Causal Masking

Causal masking prevents the model from looking ahead.

When predicting token `t`, the model can only attend to:

```text
tokens 1 through t
```

It cannot attend to:

```text
tokens t+1 through T
```

The notebook uses a lower-triangular matrix:

```python
self.register_buffer(
    "tril",
    torch.tril(torch.ones(cfg.block_size, cfg.block_size))
)
```

Masking is applied before softmax:

```python
wei = wei.masked_fill(self.tril[:T, :T] == 0, float("-inf"))
```

### Mathematical Intuition

The raw attention matrix has shape:

```text
T x T
```

Entry `(i, j)` means:

```text
how much token i attends to token j
```

For autoregressive generation, entries where `j > i` are illegal. They are set to negative infinity:

```text
score(i, j) = -inf if j > i
```

After softmax:

```text
softmax(-inf) = 0
```

So future tokens receive zero attention probability.

## Residual Connections

Each block uses residual connections:

```python
x = x + attention(norm(x))
x = x + ffwd(norm(x))
```

### Mathematical Intuition

Instead of forcing each layer to learn an entirely new representation, residual connections let layers learn updates:

```text
x_next = x + f(x)
```

This improves gradient flow. During backpropagation, gradients can flow through the identity path even if `f(x)` is hard to optimize.

Residual connections make deep neural networks easier to train.

## RMSNorm

`PSKGPT v2` uses RMSNorm:

```python
rms = x.pow(2).mean(dim=-1, keepdim=True).sqrt()
x_norm = x / (rms + eps)
return scale * x_norm
```

RMSNorm normalizes each token vector by its root mean square.

For a vector:

```text
x = [x_1, x_2, ..., x_d]
```

RMS is:

```text
RMS(x) = sqrt((1/d) * sum(x_i^2))
```

Then:

```text
RMSNorm(x) = x / RMS(x) * gamma
```

where `gamma` is a learned scale parameter.

### RMSNorm vs LayerNorm

LayerNorm uses:

```text
(x - mean(x)) / std(x)
```

RMSNorm skips mean subtraction and uses only magnitude normalization.

### Intuition

RMSNorm controls the scale of activations without changing their mean. This is computationally simpler and commonly used in modern LLM architectures.

## SwiGLU Feed-Forward Network

The baseline model uses a ReLU MLP:

```text
Linear -> ReLU -> Linear
```

The upgraded model uses a SwiGLU-style feed-forward layer:

```python
x1 = self.w1(x)
x2 = self.w2(x)
out = self.proj(F.silu(x1) * x2)
```

### SwiGLU Formula

The operation is:

```text
SwiGLU(x) = SiLU(x W_1) * (x W_2)
```

followed by an output projection:

```text
FFN(x) = SwiGLU(x) W_3
```

SiLU is:

```text
SiLU(z) = z * sigmoid(z)
```

### Mathematical Intuition

SwiGLU creates a learned gate.

- `x W_1` decides what information should pass
- `x W_2` contains the candidate content
- Multiplication gates the content elementwise

This is more expressive than a standard ReLU MLP because the network can dynamically control which features are amplified or suppressed.

## Rotary Positional Embeddings

The notebook includes an `apply_rope` function for Rotary Positional Embeddings.

RoPE rotates pairs of query/key dimensions by an angle that depends on token position.

For a pair of dimensions:

```text
[x_1, x_2]
```

RoPE applies a 2D rotation:

```text
x'_1 = x_1 cos(theta) - x_2 sin(theta)
x'_2 = x_1 sin(theta) + x_2 cos(theta)
```

where `theta` depends on position and dimension.

### Mathematical Intuition

Instead of adding position vectors, RoPE injects position by rotating query and key vectors. The dot product between rotated vectors naturally depends on relative position.

This is useful because attention scores become sensitive to how far apart two tokens are.

### Note

The notebook defines the RoPE helper, but the active `PSKGPT v2` forward pass still uses learned absolute positional embeddings.

## KV Cache

KV cache is used during autoregressive inference.

Without KV cache, generating each new token recomputes keys and values for the entire context.

For a sequence length `T`, that means repeated work:

```text
step 1: compute K,V for 1 token
step 2: compute K,V for 2 tokens
step 3: compute K,V for 3 tokens
...
```

With KV cache, previous keys and values are reused:

```python
if past_k is not None:
    k = torch.cat([past_k, k], dim=1)
    v = torch.cat([past_v, v], dim=1)
```

### Mathematical Intuition

During generation, old tokens do not change. Their key and value projections also do not change.

So instead of recomputing:

```text
K = X W_K
V = X W_V
```

for all previous tokens every time, the model stores:

```text
K_cached, V_cached
```

and only computes projections for the newest token.

This makes inference significantly faster for long generations.

## Weight Tying

The model ties input token embeddings and output projection weights:

```python
self.lm_head.weight = self.token_embedding.weight
```

The token embedding maps token IDs to vectors:

```text
token_id -> embedding vector
```

The language modeling head maps hidden states back to vocabulary logits:

```text
hidden state -> logits over tokens
```

### Mathematical Intuition

Without weight tying:

```text
Embedding matrix: V x C
Output matrix:    C x V
```

With weight tying, the output matrix reuses the embedding matrix transpose.

This encourages consistency:

- The vector used to represent a token as input is also used to score that token as output
- Parameter count is reduced
- Generalization can improve

## Training Pipeline

The training pipeline performs standard next-token prediction.

Steps:

1. Download Tiny Shakespeare
2. Train the custom BPE tokenizer
3. Encode the full corpus into token IDs
4. Split into train and validation sets
5. Sample random batches of length `block_size`
6. Feed input tokens into the model
7. Predict next-token logits
8. Compute cross-entropy loss
9. Backpropagate gradients
10. Clip gradients
11. Update weights with AdamW
12. Evaluate periodically
13. Save the best checkpoint

### Batch Construction

For each sampled chunk:

```text
x = [t_1, t_2, ..., t_n]
y = [t_2, t_3, ..., t_{n+1}]
```

The model predicts every target token in parallel during training.

## Cross-Entropy Loss

The model outputs logits:

```text
logits shape = B x T x V
```

where:

- `B` is batch size
- `T` is sequence length
- `V` is vocabulary size

Softmax converts logits into probabilities:

```text
p_i = exp(z_i) / sum_j exp(z_j)
```

Cross-entropy for the correct token `y` is:

```text
loss = -log(p_y)
```

For all tokens:

```text
L = -(1/N) * sum log P(correct token)
```

### Intuition

If the model assigns high probability to the correct next token, loss is low.

If the model assigns low probability to the correct next token, loss is high.

Training adjusts model weights to increase the probability of correct next tokens.

## Optimization Techniques

### AdamW

AdamW is used as the optimizer:

```python
torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=0.1)
```

Adam adapts learning rates per parameter using estimates of first and second moments of gradients.

Weight decay penalizes large weights and helps regularization.

### Learning Rate Warmup

The learning rate starts small and gradually increases:

```text
lr(step) = base_lr * step / warmup_iters
```

### Intuition

Early in training, model weights are random and gradients can be unstable. Warmup prevents overly large updates at the beginning.

### Cosine Decay

After warmup, the learning rate follows a cosine schedule:

```text
lr = base_lr * 0.5 * (1 + cos(pi * progress))
```

This gradually reduces update size as training progresses.

### Gradient Clipping

The notebook clips gradients:

```python
torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
```

This prevents exploding gradients by limiting the maximum gradient norm.

### Dropout

Dropout randomly zeroes some activations during training.

This prevents the model from relying too heavily on specific neurons and helps regularization.

## Inference Pipeline

The inference pipeline generates text from a prompt.

```python
generate_text(
    prompt="ROMEO:\n",
    max_new_tokens=200,
    temperature=0.8,
    top_k=40,
    top_p=0.9
)
```

Generation steps:

1. Encode the prompt
2. Pass tokens through the model
3. Take logits from the final position
4. Scale logits by temperature
5. Convert logits to probabilities with softmax
6. Apply top-k filtering if enabled
7. Apply top-p filtering if enabled
8. Sample the next token
9. Append it to the sequence
10. Repeat until `max_new_tokens` is reached
11. Decode generated IDs back into text

## Sampling Methods

### Greedy Decoding

Greedy decoding always selects the most likely token:

```text
next_token = argmax P(token | context)
```

It is deterministic but can produce repetitive text.

### Temperature Scaling

Temperature controls randomness:

```text
p_i = softmax(z_i / temperature)
```

Lower temperature sharpens the distribution:

```text
temperature < 1
```

Higher temperature flattens the distribution:

```text
temperature > 1
```

### Intuition

- Low temperature: safer, more predictable output
- High temperature: more diverse, more surprising output

### Top-k Sampling

Top-k keeps only the `k` most probable tokens.

For example:

```python
top_k = 40
```

All tokens outside the top 40 are assigned probability zero. The remaining probabilities are renormalized.

### Intuition

Top-k prevents the model from sampling extremely unlikely tokens while still allowing diversity.

### Top-p Sampling

Top-p, also called nucleus sampling, keeps the smallest set of tokens whose cumulative probability is at least `p`.

For example:

```python
top_p = 0.9
```

If sorted probabilities are:

```text
[0.40, 0.25, 0.15, 0.08, 0.05, ...]
```

then top-p keeps tokens until cumulative probability crosses `0.9`.

### Intuition

Top-p adapts to uncertainty:

- If the model is confident, only a few tokens are kept
- If the model is uncertain, more tokens are kept

This often produces better text than fixed top-k alone.

## Attention Visualization

The notebook stores attention weights:

```python
self.last_attn = wei.detach()
```

This allows visualization of attention matrices using heatmaps.

Available utilities:

- `inspect_next_token(prompt)`
- `plot_attention(prompt)`
- `plot_multihead_attention(prompt, block_idx=0)`

An attention matrix has shape:

```text
T x T
```

Rows represent the current token. Columns represent tokens being attended to.

The value at `(i, j)` means:

```text
how much token i attends to token j
```

This helps inspect whether the model is learning meaningful dependencies.

## Model Checkpoint

The trained `PSKGPT v2` checkpoint is hosted externally to keep this GitHub repository lightweight:

[Download `best_v2.pt`](https://drive.google.com/file/d/1zcxszdYVD-SSVOGybM8xX3g2Txb4BpJw/view?usp=sharing)

After downloading, place the checkpoint in the project root:

```text
PSKGPT/
  best_v2.pt
  demo_generate.py
  tokenizer_bpe.json
```

The notebook also saves `model_final.pt` during training, but `best_v2.pt` is the recommended checkpoint for inference.

## Results

The model learns Shakespeare-style dialogue patterns, character names, punctuation, and short phrase structure.

The training logs show that validation loss improves early and later worsens while training loss continues to fall. This indicates overfitting, which is expected when training a relatively expressive model on a compact dataset.

Best validation performance is observed around step `2200` in the notebook logs.

## Usage

Open the notebook:

```bash
jupyter notebook pskgpt-gpt-from-scratch-optimized.ipynb
```

Run the cells in order.

Generate text:

```python
print(gen("ROMEO:\n", tokens=200))
```

Customize decoding:

```python
print(generate_text(
    prompt="To be or not to be ",
    max_new_tokens=150,
    temperature=0.8,
    top_k=40,
    top_p=0.9
))
```

Inspect next-token probabilities:

```python
inspect_next_token("ROMEO:\n")
```

Visualize attention:

```python
plot_attention("The king loves the queen ")
plot_multihead_attention("ROMEO:\n")
```

## Demo

The terminal demo below shows PSKGPT loading the trained checkpoint and generating Shakespeare-style text from a prompt.

![PSKGPT terminal generation demo](assets/pskgpt-demo.gif)

If the GIF does not render, open the MP4 version directly:

[Watch the terminal demo](assets/pskgpt-demo.mp4)

## Run Locally

The repository includes a standalone inference script:

```text
demo_generate.py
```

Before running inference, download the trained checkpoint from Google Drive and place it in the project root:

[Download `best_v2.pt`](https://drive.google.com/file/d/1zcxszdYVD-SSVOGybM8xX3g2Txb4BpJw/view?usp=sharing)

Run a short generation demo from the terminal:

```bash
python demo_generate.py --device cpu --prompt $'ROMEO:\n' --tokens 180 --temperature 0.8 --top-k 40 --top-p 0.9
```

The script loads `best_v2.pt`, uses the cached BPE tokenizer from `tokenizer_bpe.json`, and streams generated text to the terminal.

## Requirements

```bash
pip install torch requests matplotlib seaborn
```

Recommended environment:

- Python 3.10+
- PyTorch
- CUDA-enabled GPU for faster training
- Jupyter Notebook or JupyterLab

The notebook was executed in a GPU-backed Kaggle environment with an NVIDIA Tesla T4.

## Notebook Structure

```text
PSKGPT: Setup + Config
PSKGPT: Load Dataset
PSKGPT: Character Tokenizer
PSKGPT: Dataset + Batch Loader
PSKGPT: Single Head Self-Attention
PSKGPT: Multi-Head Attention
PSKGPT: Feed-Forward Network
PSKGPT: Transformer Block
PSKGPT: Full GPT Model
PSKGPT: Training Loop
PSKGPT: Inference

PSKGPT v2: Setup + Config
PSKGPT v2: BPE Tokenizer
PSKGPT v2: Dataset + Batch Loader
PSKGPT v2: RMSNorm
PSKGPT v2: SwiGLU
PSKGPT v2: KV Cache
PSKGPT v2: Weight Tying
PSKGPT v2: Training + Checkpointing
PSKGPT v2: Sampling + Evaluation Suite
```

## Key Learning Outcomes

This project explains and implements the core mechanics behind GPT-style LLMs:

- Tokenization converts raw text into learnable discrete units
- Embeddings map tokens into continuous vector space
- Positional embeddings provide order information
- Self-attention lets each token retrieve information from context
- Multi-head attention learns multiple relationship patterns in parallel
- Causal masking enforces autoregressive generation
- RMSNorm stabilizes activations
- SwiGLU improves feed-forward expressiveness through gating
- KV caching accelerates inference
- Weight tying reduces parameters and aligns input/output token spaces
- Cross-entropy trains the model to maximize next-token likelihood
- Top-k, top-p, and temperature control generation behavior

## Project Status

PSKGPT is a compact but complete GPT-style language model implementation. It is suitable for studying Transformer internals, experimenting with tokenizer design, analyzing attention behavior, and understanding how modern autoregressive language models are trained and used for generation.
