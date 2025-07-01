import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

import fitz  # PyMuPDF
import docx

from ..core.config import settings
from ..core.logger import logger
from ..utils.text_splitter import TextSplitter
from ..utils.preprocessor import clean_text
from ..utils.document_loader import load_document


class DocumentProcessor:
    """Service for processing documents into chunks for embedding"""
    
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.documents_path = settings.DOCUMENTS_PATH
        self.processed_path = settings.PROCESSED_PATH
        self.text_splitter = TextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        
        # Ensure processed directory exists
        os.makedirs(self.processed_path, exist_ok=True)
        
    def process_all_documents(self) -> List[Dict[str, Any]]:
        """Process all documents in the documents directory"""
        all_chunks = []
        documents_dir = Path(self.documents_path)
        
        if not documents_dir.exists():
            logger.error(f"Documents directory does not exist: {self.documents_path}")
            return []
            
        for file_path in documents_dir.glob("**/*"):
            if not file_path.is_file():
                continue
                
            if file_path.suffix.lower() in ['.pdf', '.docx', '.doc']:
                try:
                    logger.info(f"Processing document: {file_path}")
                    document_chunks = self.process_document(str(file_path))
                    all_chunks.extend(document_chunks)
                except Exception as e:
                    logger.error(f"Error processing document {file_path}: {str(e)}")
        
        # Save processed chunks
        self._save_chunks(all_chunks)
        return all_chunks
    
    def process_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a single document into chunks with metadata"""
        text = load_document(file_path)
        
        if not text:
            logger.warning(f"No text extracted from document: {file_path}")
            return []
            
        # Clean and preprocess text
        cleaned_text = clean_text(text)
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(cleaned_text)
        
        # Create document chunks with metadata
        document_chunks = []
        for i, chunk_text in enumerate(chunks):
            chunk = {
                "id": f"{os.path.basename(file_path)}_chunk_{i}",
                "text": chunk_text,
                "metadata": {
                    "source": file_path,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "source_type": os.path.splitext(file_path)[1][1:].lower()
                }
            }
            document_chunks.append(chunk)
            
        return document_chunks
    
    def _save_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """Save processed chunks to disk"""
        output_path = os.path.join(self.processed_path, "chunks.json")
        with open(output_path, 'w') as f:
            json.dump(chunks, f, indent=2)
        logger.info(f"Saved {len(chunks)} chunks to {output_path}")
        
    def get_processed_chunks(self) -> List[Dict[str, Any]]:
        """Get previously processed chunks from disk"""
        chunks_path = os.path.join(self.processed_path, "chunks.json")
        if not os.path.exists(chunks_path):
            logger.warning("No processed chunks found")
            return []
            
        with open(chunks_path, 'r') as f:
            chunks = json.load(f)
        return chunks 