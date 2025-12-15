"""
Document ingestion pipeline.
Handles file upload, text extraction, chunking, and embedding.
"""
from typing import Dict, List
from utils.loaders import load_document
from utils.chunker import chunk_text
from retriever import retriever


def ingest_document(content: bytes, filename: str) -> Dict:
    """
    Process and ingest a document into the vector store.
    
    Args:
        content: Raw file bytes
        filename: Original filename
        
    Returns:
        Ingestion result with statistics
    """
    # Extract text from document
    text, metadata = load_document(content, filename)
    
    if not text.strip():
        return {
            "success": False,
            "error": "No text content extracted from document",
            "filename": filename
        }
    
    # Chunk the text
    chunks = chunk_text(text, filename)
    
    if not chunks:
        return {
            "success": False,
            "error": "Failed to create chunks from document",
            "filename": filename
        }
    
    # Add to vector store
    num_added = retriever.add_chunks(chunks)
    
    return {
        "success": True,
        "filename": filename,
        "chunks_created": num_added,
        "document_type": metadata.get("type", "unknown"),
        "total_chunks_in_store": len(retriever.chunks)
    }


def get_ingestion_stats() -> Dict:
    """Get current ingestion statistics."""
    return retriever.get_stats()


def clear_all_documents() -> Dict:
    """Clear all ingested documents."""
    retriever.clear()
    return {"success": True, "message": "All documents cleared"}
