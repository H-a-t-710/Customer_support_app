import os
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from app.services.embedding_service import EmbeddingService, embedding_service_singleton
import chromadb
from chromadb.utils import embedding_functions
from app.core.config import settings
import uuid
from chromadb.config import Settings as ChromaSettings  # disable telemetry via config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStoreService:
    """
    Service for managing document embeddings and vector database operations.
    """
    
    def __init__(self, vector_store_path: Optional[str] = None, embedding_service: Optional[EmbeddingService] = None):
        """
        Initialize the vector store service.
        
        Args:
            vector_store_path (str, optional): Path to vector store
            embedding_service (EmbeddingService, optional): Embedding service
        """
        self.vector_store_path = vector_store_path or settings.VECTOR_DB_PATH
        logger.info(f"ChromaDB vector store path: {os.path.abspath(self.vector_store_path)}")
        
        # Ensure vector store directory exists
        os.makedirs(self.vector_store_path, exist_ok=True)
        
        # Initialize embedding service if not provided
        self.embedding_service = embedding_service or embedding_service_singleton
        
        # Initialize ChromaDB client with telemetry disabled
        self.client = chromadb.PersistentClient(
            path=self.vector_store_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
                is_persistent=True
            )
        )
        
        # Define custom embedding function that uses our embedding service
        self.embedding_function = self._create_embedding_function()
        
        # Collections dictionary to keep track of created collections
        self.collections = {}
        
        # Create or get default collection with the embedding function
        self.get_or_create_collection("documents")
    
    def _create_embedding_function(self):
        """
        Create a custom embedding function that uses our embedding service.
        
        Returns:
            callable: Embedding function
        """
        # Custom function that uses our embedding service
        class CustomEmbeddingFunction(embedding_functions.EmbeddingFunction):
            def __init__(self, embedding_service):
                self.embedding_service = embedding_service
            
            def __call__(self, texts):
                return self.embedding_service.create_embeddings(texts)
        
        return CustomEmbeddingFunction(self.embedding_service)
    
    def get_or_create_collection(self, collection_name: str = "documents"):
        """
        Get or create a collection.
        
        Args:
            collection_name (str): Name of the collection
            
        Returns:
            chromadb.Collection: The collection
        """
        try:
            # Check if we already have this collection cached
            if collection_name in self.collections:
                return self.collections[collection_name]
                
            # Get or create the collection
            collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
            
            # Cache the collection
            self.collections[collection_name] = collection
            
            logger.info(f"Collection '{collection_name}' has {collection.count()} documents")
            return collection
            
        except Exception as e:
            logger.error(f"Error getting or creating collection '{collection_name}': {str(e)}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]], collection_name: str = "documents") -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents (List[Dict[str, Any]]): List of documents with content and metadata
            collection_name (str): Name of the collection to add documents to
        """
        if not documents:
            logger.warning("No documents to add to vector store")
            return
        
        # Get or create the collection
        collection = self.get_or_create_collection(collection_name)
        
        ids = []
        texts = []
        metadatas = []
        
        for i, doc in enumerate(documents):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            
            if not content:
                continue
                
            # Generate a unique ID for the document with a UUID to ensure uniqueness
            doc_id = f"doc_{metadata.get('source', 'unknown')}_{metadata.get('page', i)}_{metadata.get('chunk', i)}_{str(uuid.uuid4())[:8]}"
            doc_id = doc_id.replace("/", "_").replace("\\", "_")
            
            ids.append(doc_id)
            texts.append(content)
            metadatas.append(metadata)
        
        if not texts:
            logger.warning("No valid documents to add to vector store")
            return
            
        try:
            # Add documents to collection (embeddings are created by the embedding function)
            collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas
            )
            logger.info(f"Added {len(texts)} documents to '{collection_name}' collection")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise
    
    def query(self, query_text: str, top_k: int = 5, threshold: float = 0.6, collection_name: str = "documents") -> List[Dict[str, Any]]:
        """
        Query the vector store for relevant documents.
        
        Args:
            query_text (str): Query text
            top_k (int): Number of results to return
            threshold (float): Similarity threshold
            collection_name (str): Name of the collection to query
            
        Returns:
            List[Dict[str, Any]]: List of relevant documents with scores
        """
        try:
            # Get the collection
            collection = self.get_or_create_collection(collection_name)
            
            # Query the collection
            # The embedding function will handle query embedding
            results = collection.query(
                query_texts=[query_text],
                n_results=top_k
            )
            
            # Safety check for results structure
            if not results or not isinstance(results, dict):
                logger.warning(f"Unexpected query results format: {results}")
                return []
                
            # Get result components with safe defaults
            documents = results.get("documents", [])
            metadatas = results.get("metadatas", []) 
            distances = results.get("distances", [])
            
            # Safety check for empty results
            if not documents or not documents[0]:
                return []
                
            # Process results - ensure all lists have values
            relevant_docs = []
            if documents and documents[0] and metadatas and metadatas[0] and distances and distances[0]:
                for doc, meta, dist in zip(documents[0], metadatas[0], distances[0]):
                    # Convert distance to similarity (ChromaDB uses cosine distance)
                    similarity = 1 - dist  # Convert cosine distance to similarity
                    
                    # Filter by threshold
                    if similarity >= threshold:
                        relevant_docs.append({
                            "content": doc,
                            "metadata": meta,
                            "similarity": similarity
                        })
            
            return relevant_docs
            
        except Exception as e:
            logger.error(f"Error querying vector store: {str(e)}")
            return []  # Return empty list on error instead of raising
            
    def reset_collection(self, collection_name: str = "documents") -> None:
        """
        Delete and recreate the collection.
        
        Args:
            collection_name (str): Name of the collection to reset
        """
        try:
            # Delete collection if it exists
            try:
                self.client.delete_collection(collection_name)
                # Remove from cache if it exists
                if collection_name in self.collections:
                    del self.collections[collection_name]
            except Exception as e:
                logger.warning(f"Error deleting collection '{collection_name}': {str(e)}")
                
            # Create new collection with our embedding function
            collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
            
            # Update cache
            self.collections[collection_name] = collection
            
            logger.info(f"Reset vector store collection '{collection_name}'")
        except Exception as e:
            logger.error(f"Error resetting collection '{collection_name}': {str(e)}")
            raise
    
    def list_collections(self) -> List[str]:
        """
        List all collections in the vector store.
        
        Returns:
            List[str]: List of collection names
        """
        try:
            collections = self.client.list_collections()
            return [c.name for c in collections]
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            return []
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        Get information about a collection.
        
        Args:
            collection_name (str): Name of the collection
            
        Returns:
            Dict[str, Any]: Collection information
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            count = collection.count()
            return {
                "name": collection_name,
                "count": count
            }
        except Exception as e:
            logger.error(f"Error getting collection info for '{collection_name}': {str(e)}")
            return {"name": collection_name, "count": 0, "error": str(e)}

# Singleton instance for app-wide use
vector_store_service_singleton = VectorStoreService() 