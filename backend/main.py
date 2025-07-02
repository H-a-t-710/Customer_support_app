import os
os.environ["POSTHOG_DISABLED"] = "True"
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# Disable Chromadb telemetry capture to prevent errors from signature mismatch
try:
    # Import and patch the telemetry module to prevent errors
    import chromadb.telemetry.product.posthog as _ctp  # type: ignore
    # Use a no-op function that accepts any number of arguments
    _ctp.capture = lambda *args, **kwargs: None  # type: ignore[attr-defined]
except ImportError:
    pass

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api.routes import chat, documents, health
from app.core.config import settings
from app.services.rag_service import RAGService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Chatbot API",
    description="API for Retrieval-Augmented Generation chatbot using Google's Gemini model with insurance documents and Angel One support content",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG service
rag_service = RAGService()

# Include API routes
app.include_router(health.router, tags=["health"], prefix="/api/health")
app.include_router(chat.router, tags=["chat"], prefix="/api/chat")
app.include_router(documents.router, tags=["documents"], prefix="/api/documents")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        logger.info("Initializing RAG service with force reload of documents and web content...")
        # Force reindex to ensure vector store is seeded with document embeddings
        rag_service.initialize(force_reload=True, include_web=True)
        logger.info("RAG service initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing RAG service: {str(e)}")
        # Don't exit, as we want the API to still be available
        # The RAG service will attempt to initialize when needed

if __name__ == "__main__":
    # Disable auto-reloading to avoid watchfiles errors
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False) 