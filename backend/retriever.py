"""
TF-IDF based retriever for semantic search.
Lightweight implementation using scikit-learn, optimized for Render free tier.
No Rust compilation required.
"""
import numpy as np
from typing import List, Dict, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import TOP_K_CHUNKS


class TFIDFRetriever:
    """
    In-memory TF-IDF vector store for document retrieval.
    Recreated on each startup (stateless design).
    Uses scikit-learn - no Rust/FAISS dependencies.
    """
    
    def __init__(self):
        """Initialize the retriever."""
        print("Initializing TF-IDF Retriever (lightweight mode)")
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.tfidf_matrix = None
        self.chunks: List[Dict] = []
        print("Retriever initialized")
    
    def add_chunks(self, chunks: List[Dict]) -> int:
        """
        Add document chunks to the vector store.
        
        Args:
            chunks: List of chunk dictionaries with 'text' field
            
        Returns:
            Number of chunks added
        """
        if not chunks:
            return 0
        
        # Add new chunks
        self.chunks.extend(chunks)
        
        # Re-fit vectorizer on all texts
        texts = [chunk["text"] for chunk in self.chunks]
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        return len(chunks)
    
    def search(self, query: str, top_k: int = TOP_K_CHUNKS) -> List[Dict]:
        """
        Search for most similar chunks to query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of chunk dictionaries with similarity scores
        """
        if self.tfidf_matrix is None or len(self.chunks) == 0:
            return []
        
        # Limit top_k to available chunks
        top_k = min(top_k, len(self.chunks))
        
        # Transform query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Build results
        results = []
        for i, idx in enumerate(top_indices):
            chunk = self.chunks[idx].copy()
            chunk["score"] = float(similarities[idx])
            chunk["rank"] = i + 1
            results.append(chunk)
        
        return results
    
    def get_stats(self) -> Dict:
        """Get retriever statistics."""
        return {
            "total_chunks": len(self.chunks),
            "index_size": len(self.chunks),
            "dimension": self.vectorizer.max_features if self.vectorizer else 0,
            "model": "TF-IDF (scikit-learn)"
        }
    
    def clear(self):
        """Clear all stored chunks and reset index."""
        self.tfidf_matrix = None
        self.chunks = []
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        print("Retriever cleared")


# Singleton instance
retriever = TFIDFRetriever()
