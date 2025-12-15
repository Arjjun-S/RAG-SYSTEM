"""
FastAPI main application for RAG system.
Lightweight, stateless design for Render free tier deployment.
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

from ingest import ingest_document, get_ingestion_stats, clear_all_documents
from qa import answer_question
from llm_router import llm_router

# Initialize FastAPI app
app = FastAPI(
    title="RAG Demo API",
    description="Lightweight RAG application for document Q&A with multi-model failover",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3


class QuestionResponse(BaseModel):
    success: bool
    answer: Optional[str] = None
    citations: list = []
    model_used: Optional[str] = None
    error: Optional[str] = None
    chunks_used: Optional[int] = None
    context_tokens: Optional[int] = None


class UploadResponse(BaseModel):
    success: bool
    filename: Optional[str] = None
    chunks_created: Optional[int] = None
    total_chunks_in_store: Optional[int] = None
    error: Optional[str] = None


class StatsResponse(BaseModel):
    total_chunks: int
    index_size: int
    dimension: int
    model: str
    available_llms: list


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint for Render."""
    return {
        "status": "healthy",
        "api_key_configured": bool(os.getenv("OPENROUTER_API_KEY"))
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "RAG Demo API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /upload",
            "ask": "POST /ask",
            "stats": "GET /stats",
            "clear": "POST /clear",
            "health": "GET /health"
        }
    }


# Document upload
@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and ingest a document (PDF or TXT).
    
    The document will be:
    1. Text extracted
    2. Chunked into segments
    3. Embedded using SentenceTransformers
    4. Stored in FAISS index
    """
    # Validate file type
    filename = file.filename or "unknown"
    if not (filename.lower().endswith('.pdf') or filename.lower().endswith('.txt')):
        raise HTTPException(
            status_code=400,
            detail="Only .pdf and .txt files are supported"
        )
    
    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read file: {str(e)}"
        )
    
    # Check file size (limit to 5MB for free tier)
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 5MB."
        )
    
    # Ingest document
    try:
        result = ingest_document(content, filename)
        return UploadResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(e)}"
        )


# Question answering
@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about uploaded documents.
    
    Uses RAG pipeline:
    1. Embed question
    2. Retrieve relevant chunks
    3. Generate answer with LLM
    4. Return answer with citations
    """
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )
    
    # Limit question length
    if len(request.question) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Question too long. Maximum 1000 characters."
        )
    
    try:
        result = answer_question(
            question=request.question,
            top_k=min(request.top_k or 3, 5)  # Cap at 5
        )
        return QuestionResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Question answering failed: {str(e)}"
        )


# Get statistics
@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get current system statistics."""
    stats = get_ingestion_stats()
    stats["available_llms"] = llm_router.get_available_models()
    return StatsResponse(**stats)


# Clear all documents
@app.post("/clear")
async def clear_documents():
    """Clear all uploaded documents from memory."""
    result = clear_all_documents()
    return result


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    print("=" * 50)
    print("RAG Demo API Starting...")
    print(f"API Key configured: {bool(os.getenv('OPENROUTER_API_KEY'))}")
    print(f"Available models: {llm_router.get_available_models()}")
    print("=" * 50)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
