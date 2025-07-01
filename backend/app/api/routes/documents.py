from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Form, Query
from typing import List, Dict, Any, Optional
import shutil
import os
import logging
from pathlib import Path
import uuid
from app.services.rag_service import RAGService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Create RAG service instance
rag_service = RAGService()

# In-memory storage for upload status tracking (in production, use a database)
upload_statuses = {}

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None)
):
    """
    Upload a new document and process it in the background.
    """
    try:
        # Generate a unique ID for this upload
        upload_id = str(uuid.uuid4())
        
        # Save the file to the documents directory
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in [".pdf", ".docx"]:
            raise HTTPException(
                status_code=400,
                detail="Only PDF and DOCX files are supported"
            )
        
        # Create path to save file
        documents_path = Path(rag_service.document_loader.documents_dir)
        save_path = documents_path / file.filename
        
        # Save file
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Set initial status
        upload_statuses[upload_id] = {
            "status": "uploading",
            "filename": file.filename,
            "description": description,
            "message": "File uploaded, processing will begin shortly"
        }
        
        # Process document in background
        background_tasks.add_task(process_document, upload_id, save_path)
        
        return {
            "upload_id": upload_id,
            "status": "uploading",
            "message": "File uploaded successfully, processing in background"
        }
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading document: {str(e)}"
        )

@router.get("/status/{upload_id}")
async def get_upload_status(upload_id: str):
    """
    Get the status of a document upload.
    """
    if upload_id not in upload_statuses:
        raise HTTPException(
            status_code=404,
            detail=f"Upload ID {upload_id} not found"
        )
    
    return upload_statuses[upload_id]

@router.get("/list")
async def list_documents():
    """
    List all available documents.
    """
    try:
        documents_path = Path(rag_service.document_loader.documents_dir)
        documents = []
        
        for file_path in documents_path.glob("**/*"):
            if file_path.is_file() and file_path.suffix.lower() in [".pdf", ".docx"]:
                documents.append({
                    "filename": file_path.name,
                    "path": str(file_path.relative_to(documents_path)),
                    "size": file_path.stat().st_size,
                    "last_modified": file_path.stat().st_mtime
                })
        
        return documents
    
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing documents: {str(e)}"
        )

@router.post("/reindex")
async def reindex_documents(background_tasks: BackgroundTasks):
    """
    Reindex all documents in the background.
    """
    try:
        # Generate ID for this reindex operation
        reindex_id = str(uuid.uuid4())
        
        # Set initial status
        upload_statuses[reindex_id] = {
            "status": "reindexing",
            "message": "Started reindexing all documents"
        }
        
        # Process in background
        background_tasks.add_task(reindex_all_documents, reindex_id)
        
        return {
            "reindex_id": reindex_id,
            "status": "reindexing",
            "message": "Started reindexing all documents"
        }
        
    except Exception as e:
        logger.error(f"Error initiating reindex: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error initiating reindex: {str(e)}"
        )

# Background task functions
def process_document(upload_id: str, document_path: Path):
    """
    Process a document in the background.
    """
    try:
        # Update status
        upload_statuses[upload_id]["status"] = "processing"
        upload_statuses[upload_id]["message"] = "Processing document"
        
        # Load the document
        documents = rag_service.document_loader.load_document(str(document_path))
        
        # Split the document
        split_docs = rag_service.text_splitter.split_documents(documents)
        
        # Add to vector store
        rag_service.vector_store.add_documents(split_docs)
        
        # Update status
        upload_statuses[upload_id]["status"] = "completed"
        upload_statuses[upload_id]["message"] = f"Document processed successfully, added {len(split_docs)} chunks"
        upload_statuses[upload_id]["chunks"] = len(split_docs)
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        upload_statuses[upload_id]["status"] = "error"
        upload_statuses[upload_id]["message"] = f"Error processing document: {str(e)}"

def reindex_all_documents(reindex_id: str):
    """
    Reindex all documents in the background.
    """
    try:
        # Update status
        upload_statuses[reindex_id]["status"] = "processing"
        upload_statuses[reindex_id]["message"] = "Processing all documents"
        
        # Process all documents
        num_chunks = rag_service.process_documents()
        
        # Update status
        upload_statuses[reindex_id]["status"] = "completed"
        upload_statuses[reindex_id]["message"] = f"Reindexed all documents successfully, added {num_chunks} chunks"
        upload_statuses[reindex_id]["chunks"] = num_chunks
        
    except Exception as e:
        logger.error(f"Error reindexing documents: {str(e)}")
        upload_statuses[reindex_id]["status"] = "error"
        upload_statuses[reindex_id]["message"] = f"Error reindexing documents: {str(e)}" 