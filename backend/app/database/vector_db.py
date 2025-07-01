import os
import logging
import chromadb
from typing import List, Dict, Any, Optional
from app.core.config import settings as app_settings
from chromadb.config import Settings
from app.core.logger import get_logger

# Set up logging
logger = get_logger(__name__)

# Disable ChromaDB telemetry completely
os.environ["ANONYMIZED_TELEMETRY"] = "False"

class VectorDatabase:
    """
    Vector database wrapper for ChromaDB.
    """
    
    def __init__(self, persist_directory=None):
        """
        Initialize the vector database.
        
        Args:
            persist_directory (str, optional): Directory to persist the database. Defaults to None.
        """
        self.persist_directory = persist_directory or app_settings.VECTOR_DB_PATH
        self.client = None
        self.collection = None
        
    def initialize(self, collection_name="documents"):
        """
        Initialize the ChromaDB client and collection.
        
        Args:
            collection_name (str, optional): Name of the collection. Defaults to "documents".
        """
        try:
            # Ensure directory exists
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Initialize client with persistence and explicitly disable telemetry
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"Initialized ChromaDB collection: {collection_name}")
            logger.info(f"Collection has {self.collection.count()} documents")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {str(e)}")
            raise
    
    def add_documents(self, documents, embeddings, ids, metadatas=None):
        """
        Add documents to the collection.
        
        Args:
            documents (List[str]): List of document texts.
            embeddings (List[List[float]]): List of document embeddings.
            ids (List[str]): List of document IDs.
            metadatas (List[dict], optional): List of document metadata. Defaults to None.
        """
        try:
            # Check for duplicate IDs before adding
            if len(ids) != len(set(ids)):
                # Find and log duplicate IDs
                seen = set()
                duplicates = [x for x in ids if x in seen or seen.add(x)]
                logger.warning(f"Found {len(duplicates)} duplicate IDs. Adding unique suffix to make them unique.")
                
                # Make IDs unique by adding a suffix
                unique_ids = []
                id_counts = {}
                for doc_id in ids:
                    if doc_id in id_counts:
                        id_counts[doc_id] += 1
                        unique_id = f"{doc_id}_{id_counts[doc_id]}"
                    else:
                        id_counts[doc_id] = 0
                        unique_id = doc_id
                    unique_ids.append(unique_id)
                
                # Use the unique IDs
                ids = unique_ids
            
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                ids=ids,
                metadatas=metadatas
            )
            logger.info(f"Added {len(documents)} documents to the collection")
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {str(e)}")
            raise
    
    def query(self, query_embedding, n_results=5):
        """
        Query the collection.
        
        Args:
            query_embedding (List[float]): Query embedding.
            n_results (int, optional): Number of results to return. Defaults to 5.
            
        Returns:
            dict: Query results.
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            return results
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {str(e)}")
            raise
    
    def delete(self, ids=None):
        """
        Delete documents from the collection.
        
        Args:
            ids (List[str], optional): List of document IDs to delete. Defaults to None.
        """
        try:
            if ids:
                self.collection.delete(ids=ids)
                logger.info(f"Deleted {len(ids)} documents from the collection")
            else:
                # Delete all documents
                self.collection.delete()
                logger.info("Deleted all documents from the collection")
        except Exception as e:
            logger.error(f"Error deleting documents from ChromaDB: {str(e)}")
            raise

    def get_or_create_collection(self, name: str, metadata: Dict[str, Any] = None):
        """
        Get or create a collection.
        
        Args:
            name (str): Collection name
            metadata (Dict[str, Any], optional): Collection metadata
            
        Returns:
            chromadb.Collection: ChromaDB collection
        """
        try:
            collection = self.client.get_or_create_collection(
                name=name,
                metadata=metadata or {}
            )
            return collection
        except Exception as e:
            logger.error(f"Error getting or creating collection {name}: {str(e)}")
            raise
    
    def delete_collection(self, name: str) -> bool:
        """
        Delete a collection.
        
        Args:
            name (str): Collection name
            
        Returns:
            bool: True if collection was deleted successfully
        """
        try:
            self.client.delete_collection(name)
            logger.info(f"Collection {name} deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {name}: {str(e)}")
            return False
    
    def get_collection_info(self, name: str) -> Dict[str, Any]:
        """
        Get collection information.
        
        Args:
            name (str): Collection name
            
        Returns:
            Dict[str, Any]: Collection information
        """
        try:
            collection = self.client.get_collection(name)
            count = collection.count()
            return {
                "name": name,
                "count": count
            }
        except Exception as e:
            logger.error(f"Error getting collection info for {name}: {str(e)}")
            return {"name": name, "count": 0, "error": str(e)}
    
    def list_collections(self) -> List[str]:
        """
        List all collections.
        
        Returns:
            List[str]: List of collection names
        """
        try:
            collections = self.client.list_collections()
            return [c.name for c in collections]
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            return [] 