"""
Main FastAPI application entry point.
Run with: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from config.settings import settings
from config.logging_config import setup_logging
from app.api.routes import router

# Initialize logging
setup_logging("DEBUG" if settings.api.debug else "INFO")

# Create FastAPI app
app = FastAPI(
    title="🎯 Student Placement Interview AI",
    description="""
## AI-Powered Placement Interview Coach

An intelligent mock interview system using:
- **Groq LLM** (llama-3.3-70b) for natural conversation
- **RAG** for context-aware questions from your resume & JD
- **MCP** for modular tool orchestration
- **Vector Store** for semantic search

### Features
- 🤖 Conduct full mock interviews
- 📊 Get detailed answer evaluation
- 📝 Resume feedback
- 📚 Personalized study plans
- 🔧 MCP tool integration
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes
app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    logger.info("=" * 50)
    logger.info("🎯 Placement Interview AI starting up...")
    logger.info(f"   Model: {settings.groq.model}")
    logger.info(f"   Embeddings: {settings.embedding.model}")
    logger.info(f"   Vector Store: {settings.vector_store.vector_store_type}")
    logger.info(f"   API Docs: http://localhost:{settings.api.port}/docs")
    logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Placement Interview AI shutting down...")


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "🎯 Student Placement Interview AI",
        "version": "1.0.0",
        "docs": "/docs",
        "api": "/api/v1",
        "status": "running",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.debug,
        log_level="debug" if settings.api.debug else "info",
    )
