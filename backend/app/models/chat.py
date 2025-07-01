from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID, uuid4


class MessageBase(BaseModel):
    """Base message model"""
    content: str = Field(..., description="Content of the message")


class SourceMetadata(BaseModel):
    """Source metadata model"""
    source: str = Field(..., description="Source document name or URL")
    page: Optional[int] = Field(None, description="Page number, if applicable")
    source_type: Optional[str] = Field(None, description="Source type (pdf, docx, web, etc.)")


class Source(BaseModel):
    """Source model"""
    content: str = Field(..., description="Source content")
    metadata: SourceMetadata = Field(..., description="Source metadata")
    similarity: Optional[float] = Field(None, description="Similarity score")


class ChatMessage(MessageBase):
    """Chat message model with role"""
    role: str = Field(..., description="Role of the message sender (user or assistant)")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the message")
    sources: Optional[List[Source]] = Field(None, description="Sources used for the response")


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User message")
    session_id: UUID = Field(default_factory=uuid4, description="Session ID")
    include_web: bool = Field(True, description="Whether to include web content in retrieval")


class ChatResponse(BaseModel):
    """Chat response model"""
    message: str = Field(..., description="Assistant message")
    sources: List[Source] = Field(default_factory=list, description="Sources used for the response")
    session_id: UUID = Field(..., description="Session ID")


class ChatHistory(BaseModel):
    """Chat history model"""
    session_id: UUID = Field(..., description="Session ID")
    messages: List[ChatMessage] = Field(default_factory=list, description="Chat messages") 