import logging
from typing import List, Dict, Any, Optional
from app.services.vector_store_service import VectorStoreService, vector_store_service_singleton
from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetrievalService:
    """
    Service for retrieving relevant documents based on queries.
    """
    
    def __init__(self, vector_store: Optional[VectorStoreService] = None):
        """
        Initialize the retrieval service.
        
        Args:
            vector_store (VectorStoreService, optional): Vector store service
        """
        self.vector_store = vector_store or vector_store_service_singleton
    
    def retrieve(self, query: str, top_k: int = 5, threshold: float = 0.6, collection_name: str = "documents") -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query (str): Query text
            top_k (int): Number of documents to retrieve
            threshold (float): Similarity threshold
            collection_name (str): Name of the collection to query
            
        Returns:
            List[Dict[str, Any]]: List of relevant documents
        """
        try:
            # Query the vector store
            results = self.vector_store.query(
                query_text=query,
                top_k=top_k,
                threshold=threshold,
                collection_name=collection_name
            )
            
            # Log results
            logger.info(f"Retrieved {len(results)} documents from '{collection_name}' for query: '{query}'")
            
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving documents from '{collection_name}' for query '{query}': {str(e)}")
            return []
    
    def retrieve_from_all(self, query: str, top_k: int = 5, threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents from all collections.
        
        Args:
            query (str): Query text
            top_k (int): Number of documents to retrieve per collection
            threshold (float): Similarity threshold
            
        Returns:
            List[Dict[str, Any]]: List of relevant documents from all collections
        """
        try:
            # Get all collections
            collections = self.vector_store.list_collections()
            
            all_results = []
            
            # Query each collection
            for collection_name in collections:
                results = self.retrieve(
                    query=query,
                    top_k=top_k,
                    threshold=threshold,
                    collection_name=collection_name
                )
                
                # Add collection name to metadata
                for result in results:
                    if "metadata" in result:
                        result["metadata"]["collection"] = collection_name
                
                all_results.extend(results)
            
            # Sort by similarity
            all_results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
            
            # Take top results
            return all_results[:top_k] if len(all_results) > top_k else all_results
            
        except Exception as e:
            logger.error(f"Error retrieving documents from all collections for query '{query}': {str(e)}")
            return []
    
    def retrieve_multi_collection(
        self, 
        query: str, 
        collections: List[str], 
        top_k: int = 5, 
        threshold: float = 0.6
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents from multiple specified collections.
        
        Args:
            query (str): Query text
            collections (List[str]): List of collection names
            top_k (int): Number of documents to retrieve per collection
            threshold (float): Similarity threshold
            
        Returns:
            List[Dict[str, Any]]: List of relevant documents from specified collections
        """
        try:
            all_results = []
            
            # Query each collection
            for collection_name in collections:
                results = self.retrieve(
                    query=query,
                    top_k=top_k,
                    threshold=threshold,
                    collection_name=collection_name
                )
                
                # Add collection name to metadata
                for result in results:
                    if "metadata" in result:
                        result["metadata"]["collection"] = collection_name
                
                all_results.extend(results)
            
            # Sort by similarity
            all_results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
            
            # Take top results
            return all_results[:top_k] if len(all_results) > top_k else all_results
            
        except Exception as e:
            logger.error(f"Error retrieving documents from multiple collections for query '{query}': {str(e)}")
            return []
    
    def rerank(self, query: str, documents: List[Dict[str, Any]], top_n: int = 3) -> List[Dict[str, Any]]:
        """
        Rerank retrieved documents for better relevance.
        
        Args:
            query (str): Query text
            documents (List[Dict[str, Any]]): Retrieved documents
            top_n (int): Number of documents to keep after reranking
            
        Returns:
            List[Dict[str, Any]]: Reranked documents
        """
        if not documents:
            return []
        
        try:
            # Simple reranking based on similarity score
            reranked = sorted(documents, key=lambda x: x.get("similarity", 0), reverse=True)
            
            # Take the top N
            result = reranked[:top_n]
            
            # Log results
            if result:
                top_score = result[0].get("similarity", 0)
                logger.info(f"Reranked documents, top score: {top_score:.4f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error reranking documents: {str(e)}")
            return documents[:top_n] if documents else []
    
    def get_context(self, query: str, max_tokens: int = 3000, collection_name: str = "documents") -> str:
        """
        Get context for a query, formatted for the LLM.
        
        Args:
            query (str): Query text
            max_tokens (int): Maximum number of tokens to include
            collection_name (str): Name of the collection to query
            
        Returns:
            str: Formatted context
        """
        try:
            # Retrieve documents
            documents = self.retrieve(query, collection_name=collection_name)
            
            # Rerank documents
            reranked_documents = self.rerank(query, documents)
            
            # Format context
            context_parts = []
            
            for i, doc in enumerate(reranked_documents):
                content = doc.get("content", "")
                metadata = doc.get("metadata", {})
                
                source = metadata.get("source", "Unknown")
                page = metadata.get("page", "")
                source_type = metadata.get("source_type", "")
                
                # Format source citation
                if source_type == "web" or source_type == "web_faq":
                    source_citation = f"[Web Document {i+1}: {source}]"
                elif page:
                    source_citation = f"[Document {i+1}: {source} (Page {page})]"
                else:
                    source_citation = f"[Document {i+1}: {source}]"
                
                # Add to context parts
                context_parts.append(f"{source_citation}\n{content}\n")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error getting context for query '{query}': {str(e)}")
            return ""
    
    def get_combined_context(self, query: str, max_tokens: int = 3000) -> str:
        """
        Get combined context from all collections for a query.
        
        Args:
            query (str): Query text
            max_tokens (int): Maximum number of tokens to include
            
        Returns:
            str: Formatted context from all collections
        """
        try:
            # Retrieve documents from all collections
            documents = self.retrieve_from_all(query)
            
            # Rerank documents
            reranked_documents = self.rerank(query, documents)
            
            # Format context
            context_parts = []
            
            for i, doc in enumerate(reranked_documents):
                content = doc.get("content", "")
                metadata = doc.get("metadata", {})
                
                source = metadata.get("source", "Unknown")
                page = metadata.get("page", "")
                source_type = metadata.get("source_type", "")
                collection = metadata.get("collection", "Unknown Collection")
                
                # Format source citation based on source type
                if source_type == "web" or source_type == "web_faq":
                    source_citation = f"[Web Document {i+1}: {source}]"
                elif page:
                    source_citation = f"[Document {i+1}: {source} (Page {page})]"
                else:
                    source_citation = f"[Document {i+1}: {source}]"
                
                # Add to context parts
                context_parts.append(f"{source_citation}\n{content}\n")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error getting combined context for query '{query}': {str(e)}")
            return "" 