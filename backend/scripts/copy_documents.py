#!/usr/bin/env python3
"""
Script for copying documents to the documents directory.

This script:
1. Copies documents from a source directory to the documents directory
2. Validates that the documents are in supported formats (PDF, DOCX)
3. Organizes documents by type if needed
"""

import os
import sys
import shutil
import logging
import argparse
from pathlib import Path

# Add parent directory to the path to import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.core.logger import setup_logger
from app.utils.helpers import ensure_dir, sanitize_filename

# Set up logging
logger = setup_logger("copy_documents", level=logging.INFO)

# Supported document types
SUPPORTED_EXTENSIONS = (".pdf", ".docx", ".doc", ".txt", ".csv", ".json")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Copy documents to the documents directory")
    parser.add_argument(
        "--source-dir",
        type=str,
        required=True,
        help="Path to source directory",
    )
    parser.add_argument(
        "--target-dir",
        type=str,
        default=settings.DOCUMENTS_PATH,
        help="Path to target documents directory",
    )
    parser.add_argument(
        "--organize",
        action="store_true",
        help="Organize documents by type",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean target directory before copying",
    )
    return parser.parse_args()

def validate_document(file_path: str) -> bool:
    """
    Validate that a document is in a supported format.
    
    Args:
        file_path (str): Path to document
        
    Returns:
        bool: True if document is valid, False otherwise
    """
    # Check extension
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext not in SUPPORTED_EXTENSIONS:
        logger.warning(f"Unsupported file extension: {file_ext} for file {file_path}")
        return False
    
    # Check if file exists and is not empty
    if not os.path.exists(file_path):
        logger.warning(f"File {file_path} does not exist")
        return False
    
    if os.path.getsize(file_path) == 0:
        logger.warning(f"File {file_path} is empty")
        return False
    
    return True

def copy_documents(source_dir: str, target_dir: str, organize: bool = False, clean: bool = False) -> int:
    """
    Copy documents from source directory to target directory.
    
    Args:
        source_dir (str): Source directory
        target_dir (str): Target directory
        organize (bool): Whether to organize documents by type
        clean (bool): Whether to clean target directory before copying
        
    Returns:
        int: Number of documents copied
    """
    # Ensure directories exist
    ensure_dir(source_dir)
    ensure_dir(target_dir)
    
    # Clean target directory if required
    if clean:
        logger.info(f"Cleaning target directory {target_dir}")
        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
    
    # Find and copy documents
    copied_count = 0
    skipped_count = 0
    
    for root, _, files in os.walk(source_dir):
        for file in files:
            source_path = os.path.join(root, file)
            
            # Validate document
            if not validate_document(source_path):
                skipped_count += 1
                continue
            
            # Sanitize filename
            sanitized_file = sanitize_filename(file)
            
            # Determine target path
            if organize:
                file_ext = os.path.splitext(file)[1].lower()
                folder_name = file_ext[1:]  # Remove the dot
                type_dir = os.path.join(target_dir, folder_name)
                ensure_dir(type_dir)
                target_path = os.path.join(type_dir, sanitized_file)
            else:
                target_path = os.path.join(target_dir, sanitized_file)
            
            # Copy file
            try:
                shutil.copy2(source_path, target_path)
                logger.info(f"Copied {source_path} to {target_path}")
                copied_count += 1
            except Exception as e:
                logger.error(f"Error copying {source_path}: {str(e)}")
                skipped_count += 1
    
    logger.info(f"Copied {copied_count} documents, skipped {skipped_count}")
    return copied_count

def main():
    """Main function"""
    # Parse arguments
    args = parse_args()
    
    # Copy documents
    try:
        copied_count = copy_documents(
            source_dir=args.source_dir,
            target_dir=args.target_dir,
            organize=args.organize,
            clean=args.clean
        )
        
        if copied_count > 0:
            logger.info(f"Successfully copied {copied_count} documents")
            return 0
        else:
            logger.warning(f"No documents were copied")
            return 1
    
    except Exception as e:
        logger.error(f"Error copying documents: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main()) 