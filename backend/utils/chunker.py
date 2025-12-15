"""
Text chunking utilities for document processing.
Implements overlapping chunking strategy for better context preservation.
"""
import re
from typing import List, Dict
from config import CHUNK_SIZE, CHUNK_OVERLAP


def estimate_tokens(text: str) -> int:
    """
    Estimate token count using simple word-based heuristic.
    Approximation: ~1.3 tokens per word for English text.
    
    Args:
        text: Input text
        
    Returns:
        Estimated token count
    """
    words = len(text.split())
    return int(words * 1.3)


def chunk_text(
    text: str,
    filename: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> List[Dict]:
    """
    Split text into overlapping chunks with metadata.
    
    Args:
        text: Full document text
        filename: Source filename for metadata
        chunk_size: Target chunk size in tokens
        chunk_overlap: Overlap between chunks in tokens
        
    Returns:
        List of chunk dictionaries with text and metadata
    """
    if not text or not text.strip():
        return []
    
    # Clean text
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Split into sentences for better boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_tokens = 0
    chunk_index = 0
    
    for sentence in sentences:
        sentence_tokens = estimate_tokens(sentence)
        
        # If single sentence exceeds chunk size, split by words
        if sentence_tokens > chunk_size:
            # Flush current chunk first
            if current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    "text": chunk_text,
                    "filename": filename,
                    "chunk_index": chunk_index,
                    "token_estimate": estimate_tokens(chunk_text)
                })
                chunk_index += 1
                current_chunk = []
                current_tokens = 0
            
            # Split long sentence by words
            words = sentence.split()
            word_chunk = []
            word_tokens = 0
            
            for word in words:
                word_token_count = estimate_tokens(word)
                if word_tokens + word_token_count > chunk_size and word_chunk:
                    chunk_text = ' '.join(word_chunk)
                    chunks.append({
                        "text": chunk_text,
                        "filename": filename,
                        "chunk_index": chunk_index,
                        "token_estimate": estimate_tokens(chunk_text)
                    })
                    chunk_index += 1
                    
                    # Keep overlap
                    overlap_words = max(1, int(len(word_chunk) * (chunk_overlap / chunk_size)))
                    word_chunk = word_chunk[-overlap_words:]
                    word_tokens = estimate_tokens(' '.join(word_chunk))
                
                word_chunk.append(word)
                word_tokens += word_token_count
            
            if word_chunk:
                current_chunk = word_chunk
                current_tokens = word_tokens
            continue
        
        # Check if adding sentence exceeds chunk size
        if current_tokens + sentence_tokens > chunk_size and current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "filename": filename,
                "chunk_index": chunk_index,
                "token_estimate": estimate_tokens(chunk_text)
            })
            chunk_index += 1
            
            # Keep overlap sentences
            overlap_tokens = 0
            overlap_sentences = []
            for sent in reversed(current_chunk):
                sent_tokens = estimate_tokens(sent)
                if overlap_tokens + sent_tokens <= chunk_overlap:
                    overlap_sentences.insert(0, sent)
                    overlap_tokens += sent_tokens
                else:
                    break
            
            current_chunk = overlap_sentences
            current_tokens = overlap_tokens
        
        current_chunk.append(sentence)
        current_tokens += sentence_tokens
    
    # Don't forget the last chunk
    if current_chunk:
        chunk_text = ' '.join(current_chunk)
        chunks.append({
            "text": chunk_text,
            "filename": filename,
            "chunk_index": chunk_index,
            "token_estimate": estimate_tokens(chunk_text)
        })
    
    return chunks
