import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API configuration
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "RAG Chatbot"
    
    # CORS configuration
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Google Gemini API configuration
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Security settings
    API_KEY: str = os.environ.get("API_KEY", "")
    API_KEY_REQUIRED: bool = os.environ.get("API_KEY_REQUIRED", "false").lower() == "true"
    RATE_LIMIT_ENABLED: bool = os.environ.get("RATE_LIMIT_ENABLED", "false").lower() == "true"
    
    # Vector database configuration
    VECTOR_DB_PATH: str = os.environ.get("VECTOR_DB_PATH", "./data/vector_store")
    
    # Document processing configuration
    CHUNK_SIZE: int = int(os.environ.get("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.environ.get("CHUNK_OVERLAP", "50"))
    
    # Embedding model configuration
    EMBEDDING_MODEL: str = os.environ.get("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    
    # Data paths
    DOCUMENTS_PATH: str = os.environ.get("DOCUMENTS_PATH", "../documents")
    PROCESSED_PATH: str = os.environ.get("PROCESSED_PATH", "./data/processed")
    
    # Web crawling configuration
    WEB_CRAWL_BASE_URL: str = os.environ.get("WEB_CRAWL_BASE_URL", "https://www.angelone.in/support")
    WEB_CRAWL_MAX_PAGES: int = int(os.environ.get("WEB_CRAWL_MAX_PAGES", "100"))
    WEB_CRAWL_RATE_LIMIT: float = float(os.environ.get("WEB_CRAWL_RATE_LIMIT", "1.0"))
    WEB_CRAWL_COLLECTION: str = os.environ.get("WEB_CRAWL_COLLECTION", "web_documents")
    
    # Retrieval configuration
    RETRIEVAL_TOP_K: int = int(os.environ.get("RETRIEVAL_TOP_K", "5"))
    RETRIEVAL_THRESHOLD: float = float(os.environ.get("RETRIEVAL_THRESHOLD", "0.6"))
    
    # Logging configuration
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.environ.get("LOG_FORMAT", "console")  # console or json
    LOG_FILE: str = os.environ.get("LOG_FILE", "")
    
    # ChromaDB configuration
    CHROMA_ANONYMIZED_TELEMETRY: bool = os.environ.get("CHROMA_ANONYMIZED_TELEMETRY", "false").lower() == "true"

    class Config:
        case_sensitive = True

# Create settings object
settings = Settings() 