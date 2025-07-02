import logging
from typing import List, Dict, Any, Optional
from app.services.vector_store_service import vector_store_service_singleton
from app.services.embedding_service import embedding_service_singleton
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService
from app.utils.document_loader import DocumentLoader
from app.utils.text_splitter import TextSplitter
from app.utils.web_crawler import WebCrawler, process_web_content
from app.core.config import settings
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    """
    Retrieval-Augmented Generation service that combines document retrieval
    with language model response generation.
    """
    
    def __init__(self):
        """
        Initialize the RAG service with its component services.
        """
        self.vector_store = vector_store_service_singleton
        self.retrieval_service = RetrievalService(vector_store=self.vector_store)
        self.llm = LLMService()
        self.embedding_service = embedding_service_singleton
        self.document_loader = DocumentLoader(settings.DOCUMENTS_PATH)
        self.text_splitter = TextSplitter()
        self.web_crawler = WebCrawler(
            base_url=settings.WEB_CRAWL_BASE_URL,
            rate_limit=settings.WEB_CRAWL_RATE_LIMIT
        )
    
    def process_documents(self) -> int:
        """
        Process all documents in the documents directory and add them to the vector store.
        
        Returns:
            int: Number of documents processed
        """
        try:
            # Reset document collection
            self.vector_store.reset_collection("documents")
            
            # Load all documents
            documents = self.document_loader.load_all_documents()
            logger.info(f"Loaded {len(documents)} document parts")
            
            # Split documents into chunks
            split_docs = self.text_splitter.split_documents(documents)
            logger.info(f"Created {len(split_docs)} document chunks")
            
            # Add to vector store
            self.vector_store.add_documents(split_docs, collection_name="documents")
            
            return len(split_docs)
        except Exception as e:
            logger.error(f"Error processing documents: {str(e)}")
            raise
    
    def process_web_content(self, force_crawl: bool = False) -> int:
        """
        Process web content from Angel One support pages.
        
        Args:
            force_crawl (bool): Force recrawling of web content
            
        Returns:
            int: Number of web content chunks processed
        """
        try:
            # Reset web document collection
            self.vector_store.reset_collection(settings.WEB_CRAWL_COLLECTION)
            
            # Get crawled data or crawl web
            existing_data = self.web_crawler.get_crawled_data()
            
            if not existing_data or force_crawl:
                logger.info(f"Crawling web content from {settings.WEB_CRAWL_BASE_URL}")
                web_data = self.web_crawler.crawl()
            else:
                logger.info(f"Using existing crawled data with {len(existing_data)} pages")
                web_data = existing_data
            
            if not web_data:
                logger.warning("No web data found or crawled")
                return 0
            
            # Process web content
            processed_docs = process_web_content(web_data)
            logger.info(f"Created {len(processed_docs)} document chunks from web content")
            
            # Split documents into chunks using general text splitting
            web_text_splitter = TextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                insurance_specific=False  # Use general text splitting for web content
            )
            
            split_docs = web_text_splitter.split_documents(processed_docs)
            logger.info(f"Split web content into {len(split_docs)} chunks")
            
            # Add to vector store
            self.vector_store.add_documents(
                split_docs, 
                collection_name=settings.WEB_CRAWL_COLLECTION
            )
            
            return len(split_docs)
            
        except Exception as e:
            logger.error(f"Error processing web content: {str(e)}")
            return 0
    
    def process_query(self, query: str, include_web: bool = True, top_k: int = None, threshold: float = None) -> Dict[str, Any]:
        """
        Process a user query using the RAG pipeline.
        
        Args:
            query (str): User query
            include_web (bool): Whether to include web content in retrieval
            top_k (int): Maximum number of documents to retrieve
            threshold (float): Similarity threshold for retrieval
            
        Returns:
            Dict[str, Any]: LLM response with sources
        """
        try:
            top_k = top_k or settings.RETRIEVAL_TOP_K
            threshold = threshold or settings.RETRIEVAL_THRESHOLD
            
            # Get context from retrieval service
            if include_web:
                # Get from both collections and combine
                doc_context = self.retrieval_service.retrieve(
                    query=query,
                    top_k=top_k,
                    threshold=threshold,
                    collection_name="documents"
                )
                
                web_context = self.retrieval_service.retrieve(
                    query=query,
                    top_k=top_k,
                    threshold=threshold,
                    collection_name=settings.WEB_CRAWL_COLLECTION
                )
                
                # Combine and re-rank based on similarity
                combined_context = doc_context + web_context
                combined_context.sort(key=lambda x: x.get("similarity", 0), reverse=True)
                
                # Take top results
                context_documents = combined_context[:top_k] if len(combined_context) > top_k else combined_context
            else:
                # Only get from documents collection
                context_documents = self.retrieval_service.retrieve(
                    query=query,
                    top_k=top_k,
                    threshold=threshold,
                    collection_name="documents"
                )
            
            logger.info(f"Retrieved {len(context_documents)} relevant documents")
            
            # Generate response using the LLM
            response = self.llm.generate_response(query, context_documents)
            
            return response
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "text": "I encountered an error while processing your query. Please try again.",
                "sources": []
            }
    
    def initialize(self, force_reload: bool = False, include_web: bool = True) -> bool:
        """
        Initialize the RAG service, optionally reloading all documents.
        
        Args:
            force_reload (bool): Force reloading of documents
            include_web (bool): Whether to include web content
            
        Returns:
            bool: True if initialization was successful
        """
        try:
            # Check if we need to initialize the vector store or if a force reload is requested
            vector_db_file_path = os.path.join(self.vector_store.vector_store_path, "chroma.sqlite3")
            
            # Only force reload if the database file does not exist, or if force_reload is explicitly True
            if force_reload or not os.path.exists(vector_db_file_path):
                logger.info("Initializing vector store with documents")
                self.process_documents()
                logger.info(f"'documents' collection count: {self.vector_store.get_collection_info('documents').get('count')}")
                
                if include_web:
                    logger.info("Initializing vector store with web content")
                    self.process_web_content(force_crawl=force_reload)
                    logger.info(f"'{settings.WEB_CRAWL_COLLECTION}' collection count: {self.vector_store.get_collection_info(settings.WEB_CRAWL_COLLECTION).get('count')}")
            else:
                # Just ensure collections exist
                self.vector_store.get_or_create_collection("documents")
                if include_web:
                    self.vector_store.get_or_create_collection(settings.WEB_CRAWL_COLLECTION)
            
            return True
        except Exception as e:
            logger.error(f"Error initializing RAG service: {str(e)}")
            return False 