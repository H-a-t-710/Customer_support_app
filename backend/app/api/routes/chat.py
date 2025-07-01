from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request
from typing import List, Dict, Any
import logging
import json
import uuid
from datetime import datetime
from app.models.chat import ChatRequest, ChatResponse, ChatHistory, Source, SourceMetadata
from app.services.rag_service import RAGService
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage for chat history (in production, use a database)
chat_histories = {}

# Create RAG service instance
rag_service = RAGService()

# Initialize RAG service
try:
    # Initialize with both document and web content
    rag_service.initialize(include_web=True)
    logger.info("RAG service initialized in chat routes")
except Exception as e:
    logger.error(f"Failed to initialize RAG service in chat routes: {str(e)}")

@router.post("/message")
async def process_message(chat_request: ChatRequest, request: Request) -> ChatResponse:
    """
    Process a chat message and return a response.
    """
    try:
        # Log the incoming request
        logger.info(f"Received chat request: {chat_request.message[:50]}...")
        
        # Process the query using RAG service with specified settings
        response_data = rag_service.process_query(
            query=chat_request.message,
            include_web=chat_request.include_web
        )
        
        # Convert sources to pydantic models
        sources = []
        for source in response_data.get("sources", []):
            metadata = source.get("metadata", {})
            sources.append(Source(
                content=source.get("content", ""),
                metadata=SourceMetadata(
                    source=metadata.get("source", "Unknown"),
                    page=metadata.get("page"),
                    source_type=metadata.get("source_type")
                ),
                similarity=source.get("similarity")
            ))
        
        # Create response
        response = ChatResponse(
            message=response_data["text"],
            sources=sources,
            session_id=chat_request.session_id
        )
        
        # Save to chat history
        session_id = str(chat_request.session_id)
        if session_id not in chat_histories:
            chat_histories[session_id] = []
            
        # Add user message
        chat_histories[session_id].append({
            "role": "user",
            "content": chat_request.message,
            "timestamp": datetime.now().isoformat(),
        })
        
        # Add assistant response
        chat_histories[session_id].append({
            "role": "assistant",
            "content": response_data["text"],
            "sources": response_data["sources"],
            "timestamp": datetime.now().isoformat(),
        })
        
        return response
    
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str) -> ChatHistory:
    """
    Get chat history for a session.
    """
    if session_id not in chat_histories:
        raise HTTPException(
            status_code=404,
            detail=f"Chat history not found for session {session_id}"
        )
        
    return ChatHistory(
        session_id=uuid.UUID(session_id),
        messages=chat_histories[session_id]
    )

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time chat.
    """
    await websocket.accept()
    
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            include_web = message_data.get("include_web", True)
            
            # Add user message to history
            chat_histories[session_id].append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now().isoformat(),
            })
            
            # Process query
            try:
                # Send "thinking" status
                await websocket.send_text(json.dumps({
                    "type": "status",
                    "content": "thinking"
                }))
                
                # Process the query using RAG service with specified settings
                response_data = rag_service.process_query(
                    query=user_message,
                    include_web=include_web
                )
                
                # Add assistant response to history
                chat_histories[session_id].append({
                    "role": "assistant",
                    "content": response_data["text"],
                    "sources": response_data["sources"],
                    "timestamp": datetime.now().isoformat(),
                })
                
                # Send response to client
                await websocket.send_text(json.dumps({
                    "type": "message",
                    "content": response_data["text"],
                    "sources": response_data["sources"]
                }))
                
            except Exception as e:
                logger.error(f"Error processing websocket message: {str(e)}")
                logger.error(traceback.format_exc())
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "content": f"Error processing message: {str(e)}"
                }))
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        logger.error(traceback.format_exc()) 