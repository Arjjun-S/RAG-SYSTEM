"""
Question-Answering pipeline using RAG.
Combines retrieval and LLM generation with citations.
"""
from typing import Dict, List
from retriever import retriever
from llm_router import llm_router
from config import RAG_PROMPT_TEMPLATE, TOP_K_CHUNKS
from utils.chunker import estimate_tokens


def build_context(chunks: List[Dict]) -> str:
    """
    Build context string from retrieved chunks.
    
    Args:
        chunks: List of retrieved chunk dictionaries
        
    Returns:
        Formatted context string with source references
    """
    context_parts = []
    
    for chunk in chunks:
        source_ref = f"[source: {chunk['filename']}, chunk {chunk['chunk_index']}]"
        context_parts.append(f"{source_ref}\n{chunk['text']}")
    
    return "\n\n---\n\n".join(context_parts)


def format_citations(chunks: List[Dict]) -> List[Dict]:
    """
    Format chunks into citation objects.
    
    Args:
        chunks: List of retrieved chunk dictionaries
        
    Returns:
        List of citation dictionaries
    """
    citations = []
    for chunk in chunks:
        citations.append({
            "filename": chunk["filename"],
            "chunk_index": chunk["chunk_index"],
            "text_preview": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
            "relevance_score": round(chunk.get("score", 0), 3)
        })
    return citations


def answer_question(question: str, top_k: int = TOP_K_CHUNKS) -> Dict:
    """
    Answer a question using RAG pipeline.
    
    Args:
        question: User's question
        top_k: Number of chunks to retrieve
        
    Returns:
        Response dictionary with answer, citations, and model info
    """
    # Check if we have any documents
    stats = retriever.get_stats()
    if stats["total_chunks"] == 0:
        return {
            "success": False,
            "error": "No documents uploaded. Please upload a document first.",
            "answer": None,
            "citations": [],
            "model_used": None
        }
    
    # Retrieve relevant chunks
    chunks = retriever.search(question, top_k=top_k)
    
    if not chunks:
        return {
            "success": False,
            "error": "No relevant content found for your question.",
            "answer": None,
            "citations": [],
            "model_used": None
        }
    
    # Build context
    context = build_context(chunks)
    
    # Estimate context tokens
    context_tokens = estimate_tokens(context)
    question_tokens = estimate_tokens(question)
    prompt_overhead = 150  # Template text
    total_tokens = context_tokens + question_tokens + prompt_overhead
    
    # Build prompt
    prompt = RAG_PROMPT_TEMPLATE.format(
        context=context,
        question=question
    )
    
    try:
        # Generate answer with failover
        answer, model_used = llm_router.generate(
            prompt=prompt,
            max_context_tokens=total_tokens
        )
        
        # Format citations
        citations = format_citations(chunks)
        
        return {
            "success": True,
            "answer": answer,
            "citations": citations,
            "model_used": model_used,
            "chunks_used": len(chunks),
            "context_tokens": total_tokens
        }
        
    except RuntimeError as e:
        return {
            "success": False,
            "error": str(e),
            "answer": None,
            "citations": format_citations(chunks),
            "model_used": None
        }
