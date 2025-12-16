"""
Configuration settings for the RAG application.
Optimized for Render free tier deployment.
"""
import os
from dataclasses import dataclass
from typing import List

# OpenRouter API Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Site info for OpenRouter (optional but recommended)
SITE_URL = os.getenv("SITE_URL", "https://rag-demo.onrender.com")
SITE_NAME = os.getenv("SITE_NAME", "RAG Demo App")


@dataclass
class ModelConfig:
    """Configuration for each LLM model."""
    name: str
    model_id: str
    max_context_tokens: int
    timeout: int = 8  # seconds


# Models in priority order (all free tier)
MODELS: List[ModelConfig] = [
    ModelConfig(
        name="Hermes 3 405B",
        model_id="nousresearch/hermes-3-llama-3.1-405b:free",
        max_context_tokens=8000,
        timeout=8
    ),
    ModelConfig(
        name="Mistral 7B",
        model_id="mistralai/mistral-7b-instruct:free",
        max_context_tokens=4000,
        timeout=8
    ),
    ModelConfig(
        name="Llama 3.3 70B",
        model_id="meta-llama/llama-3.3-70b-instruct:free",
        max_context_tokens=3000,
        timeout=8
    ),
]

# Retrieval settings
TOP_K_CHUNKS = 3
CHUNK_SIZE = 600  # tokens (target 500-700)
CHUNK_OVERLAP = 100

# RAG Prompt Template
RAG_PROMPT_TEMPLATE = """You are a retrieval-augmented assistant.
Answer using ONLY the provided context.
If the answer is not in the context, say "I don't know."

Cite sources using:
[source: filename, chunk]

Context:
{context}

Question:
{question}

Answer:"""
