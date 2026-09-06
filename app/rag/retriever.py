"""
RAG Retriever — fetches relevant context from vector store and formats it for the LLM.
"""

from typing import List, Optional
from loguru import logger

from langchain_core.documents import Document
from .vector_store import VectorStoreManager


class RAGRetriever:
    def __init__(self, vector_store: VectorStoreManager, top_k: int = 5):
        self.vector_store = vector_store
        self.top_k = top_k

    def get_context(
        self,
        query: str,
        doc_type: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> str:
        """
        Retrieve relevant docs and return as formatted context string.
        doc_type: filter by 'resume' | 'job_description' | 'question_bank'
        """
        k = top_k or self.top_k
        filter_dict = {"doc_type": doc_type} if doc_type else None
        docs = self.vector_store.similarity_search(query, k=k, filter=filter_dict)

        if not docs:
            return "No relevant context found."

        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("filename", "unknown")
            dtype = doc.metadata.get("doc_type", "")
            context_parts.append(
                f"[Context {i} | {dtype} | {source}]\n{doc.page_content.strip()}"
            )

        return "\n\n---\n\n".join(context_parts)

    def get_resume_context(self, query: str) -> str:
        return self.get_context(query, doc_type="resume")

    def get_jd_context(self, query: str) -> str:
        return self.get_context(query, doc_type="job_description")

    def get_question_context(self, query: str) -> str:
        return self.get_context(query, doc_type="question_bank")

    def get_combined_context(self, query: str) -> str:
        """Get context from all sources combined."""
        resume_ctx = self.get_resume_context(query)
        jd_ctx = self.get_jd_context(query)
        q_ctx = self.get_question_context(query)
        return f"## Resume Context\n{resume_ctx}\n\n## Job Description Context\n{jd_ctx}\n\n## Question Bank Context\n{q_ctx}"

    def get_relevant_documents(self, query: str) -> List[Document]:
        """Return raw Document objects."""
        return self.vector_store.similarity_search(query, k=self.top_k)
