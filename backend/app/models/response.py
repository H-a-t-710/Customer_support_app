from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Generic, TypeVar
from enum import Enum

T = TypeVar('T')

class StatusCode(int, Enum):
    """Status code enum for API responses"""
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500

class ResponseStatus(str, Enum):
    """Status enum for API responses"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class ErrorResponse(BaseModel):
    """Error response model"""
    status: ResponseStatus = Field(ResponseStatus.ERROR, description="Response status")
    status_code: StatusCode = Field(..., description="HTTP status code")
    message: str = Field(..., description="Error message")
    detail: Optional[Any] = Field(None, description="Additional error details")

class SuccessResponse(BaseModel, Generic[T]):
    """Success response model"""
    status: ResponseStatus = Field(ResponseStatus.SUCCESS, description="Response status")
    status_code: StatusCode = Field(StatusCode.OK, description="HTTP status code")
    message: Optional[str] = Field(None, description="Success message")
    data: Optional[T] = Field(None, description="Response data")

class PaginatedResponse(SuccessResponse, Generic[T]):
    """Paginated response model"""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")
    items: List[T] = Field(..., description="List of items") 