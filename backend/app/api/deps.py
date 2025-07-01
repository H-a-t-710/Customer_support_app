from typing import Generator
from app.services.rag_service import RAGService
from app.services.vector_store_service import VectorStoreService
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService
from app.services.embedding_service import EmbeddingService

def get_rag_service() -> Generator[RAGService, None, None]:
    """
    Get RAG service dependency.
    
    Yields:
        Generator[RAGService, None, None]: RAG service
    """
    service = RAGService()
    try:
        yield service
    finally:
        # Cleanup code if needed
        pass

def get_vector_store_service() -> Generator[VectorStoreService, None, None]:
    """
    Get vector store service dependency.
    
    Yields:
        Generator[VectorStoreService, None, None]: Vector store service
    """
    service = VectorStoreService()
    try:
        yield service
    finally:
        # Cleanup code if needed
        pass

def get_llm_service() -> Generator[LLMService, None, None]:
    """
    Get LLM service dependency.
    
    Yields:
        Generator[LLMService, None, None]: LLM service
    """
    service = LLMService()
    try:
        yield service
    finally:
        # Cleanup code if needed
        pass

def get_retrieval_service() -> Generator[RetrievalService, None, None]:
    """
    Get retrieval service dependency.
    
    Yields:
        Generator[RetrievalService, None, None]: Retrieval service
    """
    service = RetrievalService()
    try:
        yield service
    finally:
        # Cleanup code if needed
        pass

def get_embedding_service() -> Generator[EmbeddingService, None, None]:
    """
    Get embedding service dependency.
    
    Yields:
        Generator[EmbeddingService, None, None]: Embedding service
    """
    service = EmbeddingService()
    try:
        yield service
    finally:
        # Cleanup code if needed
        pass 