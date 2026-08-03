"""
Pluggable Embedding Providers for Project Astra.
Supports SentenceTransformers, OpenAI/Gemini stubs, and deterministic lightweight fallback embeddings.
"""

from abc import ABC, abstractmethod
from typing import List
import hashlib
import numpy as np

from app.utils.logger import logger


class BaseEmbeddingProvider(ABC):
    """Abstract interface for pluggable text embedding providers."""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generates a dense float vector embedding for input text."""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generates vector embeddings for a batch of texts."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns embedding vector dimensionality."""
        pass


class SentenceTransformerEmbedding(BaseEmbeddingProvider):
    """
    Local SentenceTransformer embedding provider.
    Uses 'all-MiniLM-L6-v2' (384 dimensions) by default.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading SentenceTransformer model '{self.model_name}'...")
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer ({e}). Falling back to FastHashEmbedding.")
                self._model = FastHashEmbedding(dim=384)

    def embed_text(self, text: str) -> List[float]:
        self._load_model()
        if isinstance(self._model, FastHashEmbedding):
            return self._model.embed_text(text)
        embedding = self._model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        self._load_model()
        if isinstance(self._model, FastHashEmbedding):
            return self._model.embed_batch(texts)
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    @property
    def dimension(self) -> int:
        return 384


class FastHashEmbedding(BaseEmbeddingProvider):
    """
    Deterministic pseudo-vector embedding provider using SHA256 hashing.
    Used as an instant, zero-dependency fallback for offline/testing environments.
    """

    def __init__(self, dim: int = 384):
        self._dim = dim

    def embed_text(self, text: str) -> List[float]:
        tokens = text.lower().split()
        if not tokens:
            return [0.0] * self._dim

        vec = np.zeros(self._dim, dtype=np.float32)
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            # Spread hash bytes into dimension slots
            for i, byte in enumerate(digest):
                idx = (i * 13 + byte) % self._dim
                vec[idx] += (byte / 255.0) - 0.5

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]

    @property
    def dimension(self) -> int:
        return self._dim
