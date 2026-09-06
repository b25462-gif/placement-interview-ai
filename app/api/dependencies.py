"""
FastAPI dependency injectors — shared objects across routes.
"""

from functools import lru_cache
from loguru import logger

from config.settings import settings
from app.agents.groq_client import GroqClient
from app.models.session_manager import session_manager


@lru_cache(maxsize=1)
def get_groq_client() -> GroqClient:
    return GroqClient(
        api_key=settings.groq.api_key,
        model=settings.groq.model,
        temperature=settings.groq.temperature,
        max_tokens=settings.groq.max_tokens,
    )


def get_retriever():
    """
    Try to load RAG retriever. If embeddings/vector store fail,
    return a dummy retriever so the interview still works.
    """
    try:
        from app.rag.document_loader import DocumentLoader
        from app.rag.vector_store import VectorStoreManager
        from app.rag.retriever import RAGRetriever

        vs = VectorStoreManager(
            store_type=settings.vector_store.vector_store_type,
            persist_dir=settings.vector_store.chroma_persist_dir,
            embedding_model_name=settings.embedding.model,
        )
        if not vs.is_ready():
            loader = DocumentLoader(
                chunk_size=settings.rag.chunk_size,
                chunk_overlap=settings.rag.chunk_overlap,
            )
            docs = loader.load_all_data(
                resumes_dir=settings.data.resumes_dir,
                jd_dir=settings.data.job_descriptions_dir,
                qbank_dir=settings.data.question_bank_dir,
            )
            if docs:
                vs.build_from_documents(docs)
        return RAGRetriever(vector_store=vs, top_k=settings.rag.top_k)
    except Exception as e:
        logger.warning(f"RAG unavailable, using dummy retriever: {e}")
        return DummyRetriever()


class DummyRetriever:
    """Fallback retriever when RAG/embeddings are not available."""

    def get_context(self, query: str, doc_type=None, top_k=None) -> str:
        return f"No RAG context available. Generate questions based on general knowledge for: {query}"

    def get_resume_context(self, query: str) -> str:
        return "Resume: Experienced software engineering student with skills in Python, Java, DSA, and web development."

    def get_jd_context(self, query: str) -> str:
        return f"Job: {query} — requires strong DSA, system design, coding skills, and problem-solving ability."

    def get_question_context(self, query: str) -> str:
        return "Question bank: Focus on DSA, OOP, DBMS, OS, CN, system design, and behavioral questions."

    def get_combined_context(self, query: str) -> str:
        return self.get_resume_context(query) + "\n" + self.get_jd_context(query)

    def get_relevant_documents(self, query: str) -> list:
        return []


@lru_cache(maxsize=1)
def get_mcp_server():
    from app.mcp.mcp_server import create_mcp_server
    return create_mcp_server(
        name=settings.mcp.server_name,
        retriever=get_retriever(),
        groq_client=get_groq_client(),
    )


def get_session_manager():
    return session_manager
