"""
Embedding model wrapper using sentence-transformers via LangChain.
"""

from functools import lru_cache
from loguru import logger
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings


class EmbeddingModel:
    """Singleton-style embedding model wrapper."""

    _instance = None

    def __new__(cls, model_name: str = "all-MiniLM-L6-v2"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if self._initialized:
            return
        logger.info(f"Loading embedding model: {model_name}")
        self.model_name = model_name
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        self._initialized = True
        logger.info("Embedding model ready.")

    def get(self) -> HuggingFaceEmbeddings:
        """Return the underlying LangChain embeddings object."""
        return self.embeddings

    def embed_query(self, text: str) -> list[float]:
        return self.embeddings.embed_query(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.embeddings.embed_documents(texts)
