from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    """Document processing status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentMetadata(BaseModel):
    """Document metadata model"""
    source: str = Field(..., description="Source of the document")
    page: Optional[int] = Field(None, description="Page number (for PDFs)")
    type: str = Field(..., description="Document type (e.g., pdf, docx)")
    chunk: Optional[int] = Field(None, description="Chunk number")
    total_chunks: Optional[int] = Field(None, description="Total chunks in document")

class DocumentChunk(BaseModel):
    """Document chunk model"""
    content: str = Field(..., description="Content of the document chunk")
    metadata: DocumentMetadata = Field(..., description="Metadata of the document chunk")

class DocumentUpload(BaseModel):
    """Document upload request model"""
    filename: str = Field(..., description="Name of the document")
    description: Optional[str] = Field(None, description="Description of the document")

class DocumentResponse(BaseModel):
    """Document response model"""
    id: str = Field(..., description="Document ID")
    filename: str = Field(..., description="Name of the document")
    status: DocumentStatus = Field(..., description="Status of document processing")
    description: Optional[str] = Field(None, description="Description of the document")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Update timestamp")
    message: Optional[str] = Field(None, description="Status message")
    chunk_count: Optional[int] = Field(None, description="Number of chunks created") 