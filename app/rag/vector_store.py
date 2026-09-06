"""
Vector Store Manager — stores and retrieves document embeddings using ChromaDB or FAISS.
"""

from pathlib import Path
from typing import List, Optional
from loguru import logger

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma, FAISS

from .embeddings import EmbeddingModel


class VectorStoreManager:
    def __init__(
        self,
        store_type: str = "chroma",
        persist_dir: str = "./vector_store/chroma_db",
        embedding_model_name: str = "all-MiniLM-L6-v2",
    ):
        self.store_type = store_type
        self.persist_dir = persist_dir
        self.embedding = EmbeddingModel(embedding_model_name)
        self.store = None
        self._load_existing()

    def _load_existing(self):
        """Try to load an existing vector store from disk."""
        try:
            if self.store_type == "chroma":
                path = Path(self.persist_dir)
                if path.exists() and any(path.iterdir()):
                    self.store = Chroma(
                        persist_directory=self.persist_dir,
                        embedding_function=self.embedding.get(),
                    )
                    logger.info(f"Loaded existing Chroma store from {self.persist_dir}")
            elif self.store_type == "faiss":
                faiss_file = Path(self.persist_dir) / "index.faiss"
                if faiss_file.exists():
                    self.store = FAISS.load_local(
                        self.persist_dir,
                        self.embedding.get(),
                        allow_dangerous_deserialization=True,
                    )
                    logger.info(f"Loaded existing FAISS store from {self.persist_dir}")
        except Exception as e:
            logger.warning(f"Could not load existing store: {e}")
            self.store = None

    def build_from_documents(self, documents: List[Document]) -> None:
        """Build vector store from a list of LangChain Documents."""
        if not documents:
            logger.warning("No documents provided — vector store not built.")
            return

        logger.info(f"Building {self.store_type} vector store with {len(documents)} chunks...")

        if self.store_type == "chroma":
            self.store = Chroma.from_documents(
                documents=documents,
                embedding=self.embedding.get(),
                persist_directory=self.persist_dir,
            )
            logger.info("Chroma store built and persisted.")

        elif self.store_type == "faiss":
            self.store = FAISS.from_documents(
                documents=documents,
                embedding=self.embedding.get(),
            )
            Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
            self.store.save_local(self.persist_dir)
            logger.info("FAISS store built and saved.")

    def add_documents(self, documents: List[Document]) -> None:
        """Add new documents to an existing store."""
        if self.store is None:
            self.build_from_documents(documents)
            return
        self.store.add_documents(documents)
        logger.info(f"Added {len(documents)} new chunks to store.")

    def similarity_search(self, query: str, k: int = 5, filter: Optional[dict] = None) -> List[Document]:
        """Return top-k relevant documents for a query."""
        if self.store is None:
            logger.warning("Vector store is empty — returning no results.")
            return []
        try:
            return self.store.similarity_search(query, k=k, filter=filter)
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []

    def is_ready(self) -> bool:
        return self.store is not None
