#!/usr/bin/env python3
"""
Script for processing documents and adding them to the vector database.

This script:
1. Loads documents from the documents directory
2. Splits documents into chunks optimized for insurance content
3. Creates embeddings using the HuggingFace model
4. Adds the chunks to the ChromaDB vector store
"""

import os
# Disable ChromaDB telemetry to prevent posthog capture() errors
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import sys
import logging
import argparse
from pathlib import Path

# Add parent directory to the path to import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.embedding_service import EmbeddingService
from app.utils.document_loader import DocumentLoader
from app.utils.text_splitter import TextSplitter
from app.services.vector_store_service import VectorStoreService
from app.core.config import settings
from app.core.logger import setup_logger
from app.utils.helpers import ensure_dir

# Set up logging
logger = setup_logger("process_documents", level=logging.INFO)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Process insurance documents and add them to the vector store")
    parser.add_argument(
        "--documents-dir",
        type=str,
        default=settings.DOCUMENTS_PATH,
        help="Path to documents directory",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=settings.PROCESSED_PATH,
        help="Path to output directory for processed documents",
    )
    parser.add_argument(
        "--vector-db-path",
        type=str,
        default=settings.VECTOR_DB_PATH,
        help="Path to vector database",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=settings.CHUNK_SIZE,
        help="Document chunk size (default: 800)",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=settings.CHUNK_OVERLAP,
        help="Document chunk overlap (default: 100)",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="BAAI/bge-small-en-v1.5",
        help="HuggingFace embedding model name",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset the vector database",
    )
    return parser.parse_args()

def main():
    """Main function"""
    # Parse arguments
    args = parse_args()
    
    # Log configuration
    logger.info(f"Processing insurance documents with the following configuration:")
    logger.info(f"- Documents directory: {args.documents_dir}")
    logger.info(f"- Output directory: {args.output_dir}")
    logger.info(f"- Vector DB path: {args.vector_db_path}")
    logger.info(f"- Chunk size: {args.chunk_size}")
    logger.info(f"- Chunk overlap: {args.chunk_overlap}")
    logger.info(f"- Embedding model: {args.model_name}")
    logger.info(f"- Reset vector store: {args.reset}")
    
    # Ensure directories exist
    ensure_dir(args.documents_dir)
    ensure_dir(args.output_dir)
    ensure_dir(args.vector_db_path)
    
    try:
        # Initialize embedding service with HuggingFace model
        logger.info(f"Initializing embedding service with model: {args.model_name}")
        embedding_service = EmbeddingService(
            model_name=args.model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize the document loader
        logger.info("Initializing document loader")
        document_loader = DocumentLoader(documents_dir=args.documents_dir)
        
        # Initialize the text splitter optimized for insurance documents
        logger.info(f"Initializing text splitter with chunk size {args.chunk_size} and overlap {args.chunk_overlap}")
        text_splitter = TextSplitter(
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            insurance_specific=True
        )
        
        # Initialize vector store service with our embedding service
        logger.info("Initializing vector store service")
        vector_store = VectorStoreService(
            vector_store_path=args.vector_db_path,
            embedding_service=embedding_service
        )
        
        # Reset vector store if specified
        if args.reset:
            logger.info("Resetting vector store collection")
            vector_store.reset_collection()
        
        # Load all documents
        logger.info(f"Loading documents from {args.documents_dir}")
        documents = document_loader.load_all_documents()
        logger.info(f"Loaded {len(documents)} document parts")
        
        if not documents:
            logger.error("No documents found. Please check the documents directory.")
            return 1
        
        # Split documents into chunks
        logger.info("Splitting documents into chunks")
        document_chunks = text_splitter.split_documents(documents)
        logger.info(f"Created {len(document_chunks)} document chunks")
        
        # Save processed chunks
        output_file = os.path.join(args.output_dir, "chunks.json")
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(document_chunks, f, default=str, ensure_ascii=False, indent=2)
        logger.info(f"Saved chunks to {output_file}")
        
        # Add documents to vector store
        logger.info(f"Adding {len(document_chunks)} chunks to vector store")
        vector_store.add_documents(document_chunks)
        logger.info("Successfully added documents to vector store")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error processing documents: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main()) 