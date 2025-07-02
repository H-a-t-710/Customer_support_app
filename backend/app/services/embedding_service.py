import os
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from app.core.config import settings

# Import HuggingFace embeddings
from langchain_huggingface import HuggingFaceEmbeddings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Service for creating document embeddings using HuggingFace models
    instead of TF-IDF vectorization.
    """
    
    def __init__(self, model_name: Optional[str] = None, model_kwargs: Optional[Dict[str, Any]] = None, encode_kwargs: Optional[Dict[str, Any]] = None):
        """
        Initialize the embedding service.
        
        Args:
            model_name (str, optional): HuggingFace model name
            model_kwargs (Dict[str, Any], optional): Keyword arguments for the model
            encode_kwargs (Dict[str, Any], optional): Keyword arguments for encoding
        """
        self.model_name = model_name or os.environ.get("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
        self.model_kwargs = model_kwargs or {'device': 'cpu'}
        self.encode_kwargs = encode_kwargs or {'normalize_embeddings': True}
        
        # Initialize the embeddings object with the specified model only
        self._initialize_embeddings()
    
    def _initialize_embeddings(self) -> None:
        """
        Initialize the HuggingFace embeddings model.
        """
        logger.info(f"Initializing HuggingFace embeddings with model: {self.model_name}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs=self.model_kwargs,
            encode_kwargs=self.encode_kwargs
        )
        logger.info("HuggingFace embeddings initialized successfully")
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for a list of texts.
        
        Args:
            texts (List[str]): List of text strings to embed
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        if not texts:
            logger.warning("No texts provided for embedding")
            return []
        
        try:
            # Process texts in batches to avoid potential memory issues
            batch_size = 32
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                logger.info(f"Creating embeddings for batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
                
                # Use the HuggingFace embeddings object
                batch_embeddings = self.embeddings.embed_documents(batch_texts)
                all_embeddings.extend(batch_embeddings)
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        Create embedding for a single query text.
        
        Args:
            text (str): Query text to embed
            
        Returns:
            List[float]: Embedding vector
        """
        if not text:
            logger.warning("Empty query text provided for embedding")
            return [0.0] * 384  # default zero vector dimension for BAAI/bge-small-en-v1.5
        
        try:
            # Use the HuggingFace embeddings query method
            embedding = self.embeddings.embed_query(text)
            return embedding
        except Exception as e:
            logger.error(f"Error embedding query: {str(e)}")
            raise

# Singleton instance for global use
embedding_service_singleton = EmbeddingService() 