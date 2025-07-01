#!/usr/bin/env python3
"""
Script to process Angel One website content for the RAG system.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add the parent directory to sys.path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.utils.web_crawler import WebCrawler, process_web_content
from app.utils.text_splitter import TextSplitter
from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService
from app.core.config import settings
from app.core.logger import get_logger

# Set up logging
logger = get_logger(__name__)

def main():
    """
    Main function to process Angel One website content.
    """
    parser = argparse.ArgumentParser(description="Process Angel One website content for the RAG system")
    parser.add_argument("--force-crawl", action="store_true", 
                        help="Force crawling even if data exists")
    parser.add_argument("--max-pages", type=int, default=settings.WEB_CRAWL_MAX_PAGES, 
                        help="Maximum number of pages to crawl")
    parser.add_argument("--rate-limit", type=float, default=settings.WEB_CRAWL_RATE_LIMIT, 
                        help="Time to wait between requests in seconds")
    parser.add_argument("--collection-name", default=settings.WEB_CRAWL_COLLECTION, 
                        help="Name of the vector collection to store web content")
    parser.add_argument("--reset", action="store_true", 
                        help="Reset the vector collection before processing")
    
    args = parser.parse_args()
    
    # Initialize vector store
    vector_store = VectorStoreService()
    
    # Check if collection needs to be reset
    if args.reset:
        logger.info(f"Resetting collection {args.collection_name}")
        vector_store.reset_collection(args.collection_name)
    
    # Initialize web crawler
    crawler = WebCrawler(
        base_url=settings.WEB_CRAWL_BASE_URL,
        max_pages=args.max_pages,
        rate_limit=args.rate_limit
    )
    
    # Check if crawled data exists
    existing_data = crawler.get_crawled_data()
    
    if not existing_data or args.force_crawl:
        logger.info(f"Crawling Angel One support website: {settings.WEB_CRAWL_BASE_URL}")
        web_data = crawler.crawl()
    else:
        logger.info(f"Using existing crawled data with {len(existing_data)} pages")
        web_data = existing_data
    
    if not web_data:
        logger.error("No web data found or crawled")
        return
    
    # Process web content
    logger.info(f"Processing {len(web_data)} web pages")
    processed_docs = process_web_content(web_data)
    logger.info(f"Created {len(processed_docs)} document chunks from web content")
    
    # Split documents into chunks
    text_splitter = TextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        insurance_specific=False  # Use general text splitting for web content
    )
    
    split_docs = text_splitter.split_documents(processed_docs)
    logger.info(f"Split web content into {len(split_docs)} chunks")
    
    # Add to vector store
    vector_store.add_documents(split_docs, collection_name=args.collection_name)
    logger.info(f"Added {len(split_docs)} web document chunks to vector store")
    
    # Verify collection info
    collection_info = vector_store.get_collection_info(args.collection_name)
    logger.info(f"Collection '{args.collection_name}' now has {collection_info.get('count', 0)} documents")

if __name__ == "__main__":
    main() 