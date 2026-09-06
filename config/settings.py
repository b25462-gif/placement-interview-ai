"""
Centralized settings management using pydantic-settings.
All config values are read from environment variables / .env file.
"""

from pathlib import Path
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GroqSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GROQ_", env_file=".env", extra="ignore")

    api_key: str = Field(..., description="Groq API key")
    model: str = Field("llama-3.3-70b-versatile", description="Groq model name")
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(2048, ge=256, le=8192)


class EmbeddingSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="EMBEDDING_", env_file=".env", extra="ignore")

    model: str = Field("all-MiniLM-L6-v2", description="HuggingFace sentence-transformer model")


class VectorStoreSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", env_file=".env", extra="ignore")

    vector_store_type: Literal["chroma", "faiss"] = Field("chroma")
    chroma_persist_dir: str = Field("./vector_store/chroma_db")
    faiss_index_path: str = Field("./vector_store/faiss_index")


class RAGSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAG_", env_file=".env", extra="ignore")

    chunk_size: int = Field(500, ge=100, le=2000)
    chunk_overlap: int = Field(50, ge=0, le=200)
    top_k: int = Field(5, ge=1, le=20)


class MCPSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MCP_", env_file=".env", extra="ignore")

    host: str = Field("0.0.0.0")
    port: int = Field(8001)
    server_name: str = Field("placement-interview-mcp")


class APISettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="API_", env_file=".env", extra="ignore")

    host: str = Field("0.0.0.0")
    port: int = Field(8000)
    debug: bool = Field(True)
    secret_key: str = Field("change_me_in_production")
    cors_origins: str = Field("http://localhost:8501,http://localhost:3000")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


class DataSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", env_file=".env", extra="ignore")

    data_dir: str = Field("./data")
    resumes_dir: str = Field("./data/resumes")
    job_descriptions_dir: str = Field("./data/job_descriptions")
    question_bank_dir: str = Field("./data/question_bank")


class InterviewSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", env_file=".env", extra="ignore")

    max_interview_questions: int = Field(10, ge=3, le=30)
    interview_difficulty: Literal["easy", "medium", "hard"] = Field("medium")
    feedback_detail_level: Literal["brief", "detailed", "comprehensive"] = Field("detailed")


class AppSettings:
    """Aggregated application settings — instantiate once and share."""

    def __init__(self) -> None:
        self.groq = GroqSettings()
        self.embedding = EmbeddingSettings()
        self.vector_store = VectorStoreSettings()
        self.rag = RAGSettings()
        self.mcp = MCPSettings()
        self.api = APISettings()
        self.data = DataSettings()
        self.interview = InterviewSettings()
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        for path_str in [
            self.data.data_dir,
            self.data.resumes_dir,
            self.data.job_descriptions_dir,
            self.data.question_bank_dir,
            self.vector_store.chroma_persist_dir,
        ]:
            Path(path_str).mkdir(parents=True, exist_ok=True)


# Singleton — import this everywhere
settings = AppSettings()
