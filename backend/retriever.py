"""
FAISS-based vector retriever for semantic search.
In-memory implementation optimized for Render free tier.
"""
import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import faiss

from config import EMBEDDING_MODEL, TOP_K_CHUNKS


class FAISSRetriever:
    """
    In-memory FAISS vector store for document retrieval.
    Recreated on each startup (stateless design).
    """
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """
        Initialize the retriever with embedding model.
        
        Args:
            model_name: SentenceTransformers model name
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        # Initialize empty FAISS index (L2 distance)
        self.index: Optional[faiss.IndexFlatL2] = None
        
        # Store chunk metadata
        self.chunks: List[Dict] = []
        
        print(f"Retriever initialized with dimension: {self.dimension}")
    
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
        
        # Extract texts
        texts = [chunk["text"] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        
        # Initialize index if needed
        if self.index is None:
            self.index = faiss.IndexFlatL2(self.dimension)
        
        # Add to FAISS
        self.index.add(embeddings.astype('float32'))
        
        # Store metadata
        self.chunks.extend(chunks)
        
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
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # Limit top_k to available chunks
        top_k = min(top_k, self.index.ntotal)
        
        # Encode query
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True
        ).astype('float32')
        
        # Search FAISS
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Build results
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.chunks):
                chunk = self.chunks[idx].copy()
                # Convert L2 distance to similarity score (0-1)
                chunk["score"] = float(1 / (1 + dist))
                chunk["rank"] = i + 1
                results.append(chunk)
        
        return results
    
    def get_stats(self) -> Dict:
        """Get retriever statistics."""
        return {
            "total_chunks": len(self.chunks),
            "index_size": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "model": EMBEDDING_MODEL
        }
    
    def clear(self):
        """Clear all stored chunks and reset index."""
        self.index = None
        self.chunks = []
        print("Retriever cleared")


# Singleton instance
retriever = FAISSRetriever()
