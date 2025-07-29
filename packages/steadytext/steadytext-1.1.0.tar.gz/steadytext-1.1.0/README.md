<p align="center">
    <img src="https://github.com/user-attachments/assets/735141f8-56ff-40ce-8a4e-013dbecfe299" alt="SteadyText Logo" height=320 width=480 />
</p>

# SteadyText

*Deterministic text generation and embeddings with zero configuration*

[![](https://img.shields.io/pypi/v/steadytext.svg)](https://pypi.org/project/steadytext/)
[![](https://img.shields.io/pypi/pyversions/steadytext.svg)](https://pypi.org/project/steadytext/)
[![](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Same input → same output. Every time.**
No more flaky tests, unpredictable CLI tools, or inconsistent docs. SteadyText makes AI outputs as reliable as hash functions.

Ever had an AI test fail randomly? Or a CLI tool give different answers each run? SteadyText makes AI outputs reproducible - perfect for testing, tooling, and anywhere you need consistent results.

> [!TIP]
> ✨ _Powered by open-source AI workflows from [**Julep**](https://julep.ai)._ ✨

---

## 🚀 Quick Start

```bash
pip install steadytext
```

```python
import steadytext

# Deterministic text generation
code = steadytext.generate("implement binary search in Python")
assert "def binary_search" in code  # Always passes!

# Streaming (also deterministic)
for token in steadytext.generate_iter("explain quantum computing"):
    print(token, end="", flush=True)

# Deterministic embeddings
vec = steadytext.embed("Hello world")  # 1024-dim numpy array

# Model switching (new in v1.0.0!)
fast_response = steadytext.generate("Quick task", model="qwen2.5-0.5b")
quality_response = steadytext.generate("Complex analysis", model="qwen2.5-7b")

# Size-based selection (new!)
small = steadytext.generate("Quick response", size="small")    # Qwen3-0.6B
medium = steadytext.generate("Standard task", size="medium")   # Qwen3-1.7B (default)
large = steadytext.generate("Complex analysis", size="large")  # Qwen3-4B
```

_Or,_

```bash
uvx steadytext generate 'hello'
```

---

## 🔧 How It Works

SteadyText achieves determinism via:

* **Fixed seeds:** Constant randomness seed (`42`)
* **Greedy decoding:** Always chooses highest-probability token
* **Frecency cache:** LRU cache with frequency counting—popular prompts stay cached longer
* **Quantized models:** 8-bit quantization ensures identical results across platforms
* **Model switching:** Dynamically switch between models while maintaining determinism (v1.0.0+)

This means `generate("hello")` returns the exact same 512 tokens on any machine, every single time.

---

## 📦 Installation & Models

Install stable release:

```bash
pip install steadytext
```

#### Models

**Default models (v1.0.0)**:

* Generation: `Qwen3-1.7B-Q8_0` (1.83GB)
* Embeddings: `Qwen3-0.6B-Q8_0` (610MB)

**Dynamic model switching (new in v1.0.0):**

Switch between different models at runtime:

```python
# Use built-in model registry
text = steadytext.generate("Hello", model="qwen2.5-3b")

# Use size parameter for Qwen3 models
text = steadytext.generate("Hello", size="large")  # Uses Qwen3-4B

# Or specify custom models
text = steadytext.generate(
    "Hello",
    model_repo="Qwen/Qwen2.5-7B-Instruct-GGUF",
    model_filename="qwen2.5-7b-instruct-q8_0.gguf"
)
```

Available models: `qwen3-0.6b`, `qwen3-1.7b`, `qwen3-4b`, `qwen3-8b`, `qwen2.5-0.5b`, `qwen2.5-1.5b`, `qwen2.5-3b`, `qwen2.5-7b`

Size shortcuts: `small` (0.6B), `medium` (1.7B, default), `large` (4B)

> Each model produces deterministic outputs. The default model remains fixed per major version.

---

## ⚡ Performance

SteadyText delivers deterministic AI with production-ready performance:

* **Text Generation**: 21.4 generations/sec (46.7ms latency)
* **Embeddings**: 104-599 embeddings/sec (single to batch-50)
* **Cache Speedup**: 48x faster for repeated prompts
* **Memory**: ~1.4GB models, 150-200MB runtime
* **100% Deterministic**: Same output every time

📊 **[Full benchmarks →](docs/benchmarks.md)**

---

## 🎯 Examples

Use SteadyText in tests or CLI tools for consistent, reproducible results:

```python
# Testing with reliable assertions
def test_ai_function():
    result = my_ai_function("test input")
    expected = steadytext.generate("expected output for 'test input'")
    assert result == expected  # No flakes!

# CLI tools with consistent outputs
import click

@click.command()
def ai_tool(prompt):
    print(steadytext.generate(prompt))
```

📂 **[More examples →](examples/)**

---

## 🖥️ CLI Usage

```bash
# Generate text
st generate "write a hello world function"

# Stream output
st generate "explain recursion" --stream

# Get embeddings
st embed "machine learning"

# Vector operations
st vector similarity "cat" "dog"
st vector search "Python" candidate1.txt candidate2.txt candidate3.txt

# Create and search FAISS indices
st index create *.txt --output docs.faiss
st index search docs.faiss "how to install" --top-k 5

# Generate with automatic context from index
st generate "what is the configuration?" --index-file docs.faiss

# Preload models
st models --preload
```

---

## 📋 When to Use SteadyText

✅ **Perfect for:**

* Testing AI features (reliable asserts)
* Deterministic CLI tooling
* Reproducible documentation & demos
* Offline/dev/staging environments
* Semantic caching and embedding search
* Vector similarity comparisons
* Document retrieval & RAG applications

❌ **Not ideal for:**

* Creative or conversational tasks
* Latest knowledge queries
* Large-scale chatbot deployments

---

## 🔍 API Overview

```python
# Text generation
steadytext.generate(prompt: str) -> str
steadytext.generate(prompt, return_logprobs=True)

# Streaming generation
steadytext.generate_iter(prompt: str)

# Embeddings
steadytext.embed(text: str | List[str]) -> np.ndarray

# Model preloading
steadytext.preload_models(verbose=True)
```

### Vector Operations (CLI)

```bash
# Compute similarity between texts
st vector similarity "text1" "text2" [--metric cosine|dot]

# Calculate distance between texts
st vector distance "text1" "text2" [--metric euclidean|manhattan|cosine]

# Find most similar text from candidates
st vector search "query" file1.txt file2.txt [--top-k 3]

# Average multiple text embeddings
st vector average "text1" "text2" "text3"

# Vector arithmetic
st vector arithmetic "king" - "man" + "woman"
```

### Index Management (CLI)

```bash
# Create FAISS index from documents
st index create doc1.txt doc2.txt --output my_index.faiss

# View index information
st index info my_index.faiss

# Search index
st index search my_index.faiss "query text" --top-k 5

# Use index with generation
st generate "question" --index-file my_index.faiss
```

📚 [Full API Documentation](docs/api.md)

---

## 🔧 Configuration

Control caching behavior via environment variables:

```bash
# Generation cache (default: 256 entries, 50MB)
export STEADYTEXT_GENERATION_CACHE_CAPACITY=256
export STEADYTEXT_GENERATION_CACHE_MAX_SIZE_MB=50

# Embedding cache (default: 512 entries, 100MB)
export STEADYTEXT_EMBEDDING_CACHE_CAPACITY=512
export STEADYTEXT_EMBEDDING_CACHE_MAX_SIZE_MB=100
```

---

## 📖 API Reference

### Text Generation

#### `generate(prompt: str, return_logprobs: bool = False) -> Union[str, Tuple[str, Optional[Dict]]]`

Generate deterministic text from a prompt.

```python
text = steadytext.generate("Write a haiku about Python")

# With log probabilities
text, logprobs = steadytext.generate("Explain AI", return_logprobs=True)
```

- **Parameters:**
  - `prompt`: Input text to generate from
  - `return_logprobs`: If True, returns tuple of (text, logprobs)
- **Returns:** Generated text string, or tuple if `return_logprobs=True`

#### `generate_iter(prompt: str) -> Iterator[str]`

Generate text iteratively, yielding tokens as they are produced.

```python
for token in steadytext.generate_iter("Tell me a story"):
    print(token, end="", flush=True)
```

- **Parameters:**
  - `prompt`: Input text to generate from
- **Yields:** Text tokens/words as they are generated

### Embeddings

#### `embed(text_input: Union[str, List[str]]) -> np.ndarray`

Create deterministic embeddings for text input.

```python
# Single string
vec = steadytext.embed("Hello world")

# List of strings (averaged)
vecs = steadytext.embed(["Hello", "world"])
```

- **Parameters:**
  - `text_input`: String or list of strings to embed
- **Returns:** 1024-dimensional L2-normalized numpy array (float32)

### Utilities

#### `preload_models(verbose: bool = False) -> None`

Preload models before first use.

```python
steadytext.preload_models()  # Silent
steadytext.preload_models(verbose=True)  # With progress
```

#### `get_model_cache_dir() -> str`

Get the path to the model cache directory.

```python
cache_dir = steadytext.get_model_cache_dir()
print(f"Models are stored in: {cache_dir}")
```

### Constants

```python
steadytext.DEFAULT_SEED  # 42
steadytext.GENERATION_MAX_NEW_TOKENS  # 512
steadytext.EMBEDDING_DIMENSION  # 1024
```

---

## 🤝 Contributing

Contributions are welcome!
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

* **Code:** MIT
* **Models:** MIT (Qwen3)

---

Built with ❤️ for developers tired of flaky AI tests.
