#!/usr/bin/env python3
"""
Script to crawl the Angel One support website and process the results.
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
    Main function to crawl website and process content.
    """
    parser = argparse.ArgumentParser(description="Crawl Angel One support website")
    parser.add_argument("--base-url", default="https://www.angelone.in/support", 
                        help="Base URL to start crawling from")
    parser.add_argument("--max-pages", type=int, default=100, 
                        help="Maximum number of pages to crawl")
    parser.add_argument("--rate-limit", type=float, default=1.0, 
                        help="Time to wait between requests in seconds")
    parser.add_argument("--force-crawl", action="store_true", 
                        help="Force crawling even if data exists")
    parser.add_argument("--collection-name", default="web_documents", 
                        help="Name of the vector collection to store web content")
    parser.add_argument("--no-embed", action="store_true", 
                        help="Skip embedding and storing in vector database")
    
    args = parser.parse_args()
    
    # Initialize crawler
    crawler = WebCrawler(
        base_url=args.base_url,
        max_pages=args.max_pages,
        rate_limit=args.rate_limit
    )
    
    # Check if crawled data exists
    existing_data = crawler.get_crawled_data()
    
    if not existing_data or args.force_crawl:
        logger.info(f"Starting crawler for {args.base_url}")
        web_data = crawler.crawl()
    else:
        logger.info(f"Using existing crawled data with {len(existing_data)} pages")
        web_data = existing_data
    
    if not web_data:
        logger.error("No web data found or crawled")
        return
    
    logger.info(f"Processing {len(web_data)} web pages")
    
    # Process web content
    processed_docs = process_web_content(web_data)
    logger.info(f"Created {len(processed_docs)} document chunks from web content")
    
    # Skip embedding if requested
    if args.no_embed:
        logger.info("Skipping embedding and vector storage")
        return
    
    # Split documents into chunks
    text_splitter = TextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        insurance_specific=False  # Use general text splitting for web content
    )
    
    split_docs = text_splitter.split_documents(processed_docs)
    logger.info(f"Split web content into {len(split_docs)} chunks")
    
    # Initialize embedding service
    embedding_service = EmbeddingService()
    
    # Initialize vector store
    vector_store = VectorStoreService()
    
    # Create or get collection for web documents
    collection = vector_store.get_or_create_collection(args.collection_name)
    logger.info(f"Using collection '{args.collection_name}' for web documents")
    
    # Add documents to vector store
    vector_store.add_documents(split_docs, collection_name=args.collection_name)
    logger.info(f"Added {len(split_docs)} web document chunks to vector store")

if __name__ == "__main__":
    main() 