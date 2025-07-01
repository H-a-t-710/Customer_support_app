import re
import logging
from typing import List, Dict, Any, Optional
from app.core.config import settings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextSplitter:
    """
    Utility for splitting documents into chunks for embedding.
    """
    
    def __init__(
        self, 
        chunk_size: int = None, 
        chunk_overlap: int = None,
        insurance_specific: bool = True
    ):
        """
        Initialize the text splitter.
        
        Args:
            chunk_size (int, optional): Maximum chunk size
            chunk_overlap (int, optional): Chunk overlap
            insurance_specific (bool): Whether to use insurance-specific separators
        """
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        self.insurance_specific = insurance_specific
        
        # Define separators optimized for insurance documents
        if insurance_specific:
            self.separators = [
                "\n\n",  # Paragraph breaks
                "\n",    # Line breaks
                "Medical Event",  # Common in SBC documents
                "Services You May Need",  # Common in SBC documents
                "What You Will Pay",  # Common in SBC documents
                "Limitations, Exceptions, & Other Important Information",  # Common in SBC documents
                "Common Medical Event",  # Common in SBC documents
                ". ",    # Sentence breaks
                "? ",    # Question breaks
                "! ",    # Exclamation breaks
                ", ",    # Comma breaks
                " ",     # Word breaks
                ""       # Character breaks
            ]
        else:
            # Default separators
            self.separators = ["\n\n", "\n", ". ", "? ", "! ", ", ", " ", ""]
        
        # Initialize the langchain text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators
        )
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks.
        
        Args:
            text (str): Text to split
            
        Returns:
            List[str]: List of text chunks
        """
        if not text:
            return []
        
        try:
            chunks = self.text_splitter.split_text(text)
            return chunks
        except Exception as e:
            logger.error(f"Error splitting text: {str(e)}")
            # Fallback to simple chunking if advanced splitting fails
            return self._simple_split(text)
    
    def split_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Split documents into chunks.
        
        Args:
            documents (List[Dict[str, Any]]): Documents to split
            
        Returns:
            List[Dict[str, Any]]: List of document chunks
        """
        if not documents:
            return []
        
        all_chunks = []
        
        for doc in documents:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {}).copy()
            
            if not content:
                continue
            
            try:
                # Split the text
                text_chunks = self.split_text(content)
                
                # Create document chunks
                for i, chunk_text in enumerate(text_chunks):
                    # Update metadata with chunk information
                    chunk_metadata = metadata.copy()
                    chunk_metadata.update({
                        "chunk": i,
                        "total_chunks": len(text_chunks)
                    })
                    
                    # Create chunk document
                    chunk_doc = {
                        "content": chunk_text,
                        "metadata": chunk_metadata
                    }
                    
                    all_chunks.append(chunk_doc)
                
            except Exception as e:
                logger.error(f"Error splitting document: {str(e)}")
                # Skip failed document
                continue
        
        logger.info(f"Split {len(documents)} documents into {len(all_chunks)} chunks")
        return all_chunks
    
    def _simple_split(self, text: str, max_length: int = None) -> List[str]:
        """
        Simple fallback text splitting by character count.
        
        Args:
            text (str): Text to split
            max_length (int, optional): Maximum chunk size
            
        Returns:
            List[str]: List of text chunks
        """
        max_len = max_length or self.chunk_size
        overlap = min(100, max_len // 10)  # 10% overlap by default
        
        # Split by paragraphs first
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If paragraph fits in current chunk, add it
            if len(current_chunk) + len(paragraph) <= max_len:
                current_chunk += paragraph + "\n\n"
            else:
                # If current chunk is not empty, add it to chunks
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Start new chunk with current paragraph
                if len(paragraph) <= max_len:
                    current_chunk = paragraph + "\n\n"
                else:
                    # Split long paragraph by sentences
                    sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                    current_chunk = ""
                    
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) <= max_len:
                            current_chunk += sentence + " "
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            
                            # If sentence is too long, split by character
                            if len(sentence) > max_len:
                                for i in range(0, len(sentence), max_len - overlap):
                                    chunks.append(sentence[i:i + max_len])
                                current_chunk = ""
                            else:
                                current_chunk = sentence + " "
        
        # Add the last chunk if not empty
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks 