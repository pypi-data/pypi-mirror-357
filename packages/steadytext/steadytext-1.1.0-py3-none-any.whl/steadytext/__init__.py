"""
SteadyText: Deterministic text generation and embedding with zero configuration.

AIDEV-NOTE: Fixed "Never Fails" - embed() now catches TypeErrors & returns zero vectors
"""

# Version of the steadytext package - should match pyproject.toml
__version__ = "1.1.0"

# Import core functions and classes for public API
import numpy as np
from typing import Optional, Any, Union, Tuple, Dict, Iterator
from .core.generator import generate as _generate, generate_iter as _generate_iter
from .core.embedder import create_embedding
from .utils import (
    logger,
    DEFAULT_SEED,
    GENERATION_MAX_NEW_TOKENS,
    EMBEDDING_DIMENSION,
    get_cache_dir,
)
from .models.loader import get_generator_model_instance, get_embedding_model_instance


def generate(
    prompt: str,
    return_logprobs: bool = False,
    eos_string: str = "[EOS]",
    model: Optional[str] = None,
    model_repo: Optional[str] = None,
    model_filename: Optional[str] = None,
    size: Optional[str] = None,
) -> Union[str, Tuple[str, Optional[Dict[str, Any]]]]:
    """Generate text deterministically from a prompt.

    Args:
        prompt: The input prompt to generate from
        return_logprobs: If True, a tuple (text, logprobs) is returned
        eos_string: Custom end-of-sequence string. "[EOS]" means use model's default.
                   Otherwise, generation stops when this string is encountered.
        model: Model name from registry (e.g., "qwen2.5-3b", "qwen3-8b")
        model_repo: Custom Hugging Face repository ID
        model_filename: Custom model filename
        size: Size identifier ("small", "medium", "large") - maps to Qwen3 0.6B/1.7B/4B models

    Returns:
        Generated text string, or tuple (text, logprobs) if return_logprobs=True
        
    Examples:
        # Use default model
        text = generate("Hello, world!")
        
        # Use size parameter
        text = generate("Quick response", size="small")
        
        # Use a model from the registry
        text = generate("Explain quantum computing", model="qwen2.5-3b")
        
        # Use a custom model
        text = generate(
            "Write a poem",
            model_repo="Qwen/Qwen2.5-7B-Instruct-GGUF",
            model_filename="qwen2.5-7b-instruct-q8_0.gguf"
        )
    """
    return _generate(
        prompt,
        return_logprobs=return_logprobs,
        eos_string=eos_string,
        model=model,
        model_repo=model_repo,
        model_filename=model_filename,
        size=size,
    )


def generate_iter(
    prompt: str,
    eos_string: str = "[EOS]",
    include_logprobs: bool = False,
    model: Optional[str] = None,
    model_repo: Optional[str] = None,
    model_filename: Optional[str] = None,
    size: Optional[str] = None,
) -> Iterator[Union[str, Dict[str, Any]]]:
    """Generate text iteratively, yielding tokens as they are produced.

    This function streams tokens as they are generated, useful for real-time
    output or when you want to process tokens as they arrive. Falls back to
    yielding words from deterministic output when model is unavailable.

    Args:
        prompt: The input prompt to generate from
        eos_string: Custom end-of-sequence string. "[EOS]" means use model's default.
                   Otherwise, generation stops when this string is encountered.
        include_logprobs: If True, yield dicts with token and logprob info
        model: Model name from registry (e.g., "qwen2.5-3b")
        model_repo: Custom Hugging Face repository ID
        model_filename: Custom model filename
        size: Size identifier ("small", "medium", "large") - maps to Qwen3 0.6B/1.7B/4B models

    Yields:
        str: Generated tokens/words as they are produced (if include_logprobs=False)
        dict: Token info with 'token' and 'logprobs' keys (if include_logprobs=True)
    """
    return _generate_iter(
        prompt,
        eos_string=eos_string,
        include_logprobs=include_logprobs,
        model=model,
        model_repo=model_repo,
        model_filename=model_filename,
        size=size,
    )


def embed(text_input) -> np.ndarray:
    """Create embeddings for text input."""
    try:
        return create_embedding(text_input)
    except TypeError as e:
        logger.error(f"Invalid input type for embedding: {e}")
        return np.zeros(EMBEDDING_DIMENSION, dtype=np.float32)


def preload_models(verbose: bool = False):
    """Preload models to ensure they're available for generation and embedding."""
    if verbose:
        logger.info("Preloading generator model...")
    get_generator_model_instance()

    if verbose:
        logger.info("Preloading embedding model...")
    get_embedding_model_instance()

    if verbose:
        logger.info("Model preloading completed.")


def get_model_cache_dir() -> str:
    """Get the model cache directory path as a string."""
    return str(get_cache_dir())


# Export public API
__all__ = [
    "generate",
    "generate_iter",
    "embed",
    "preload_models",
    "get_model_cache_dir",
    "DEFAULT_SEED",
    "GENERATION_MAX_NEW_TOKENS",
    "EMBEDDING_DIMENSION",
    "logger",
    "__version__",
]
