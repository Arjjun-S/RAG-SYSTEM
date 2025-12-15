"""
LLM Router with multi-model failover for OpenRouter API.
Tries models sequentially and handles timeouts/errors gracefully.
"""
import requests
import json
from typing import Tuple, Optional
from config import (
    MODELS, 
    OPENROUTER_API_KEY, 
    OPENROUTER_BASE_URL,
    SITE_URL,
    SITE_NAME
)


class LLMRouter:
    """
    Routes LLM requests through OpenRouter with automatic failover.
    Tries each model in priority order until one succeeds.
    """
    
    def __init__(self):
        self.models = MODELS
        self.api_key = OPENROUTER_API_KEY
        
    def _call_model(self, model_id: str, prompt: str, timeout: int) -> Optional[str]:
        """
        Make a single API call to OpenRouter.
        
        Args:
            model_id: The OpenRouter model identifier
            prompt: The prompt to send
            timeout: Request timeout in seconds
            
        Returns:
            Response text or None if failed
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": SITE_URL,
            "X-Title": SITE_NAME,
        }
        
        payload = {
            "model": model_id,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,  # Lower temperature for factual responses
            "max_tokens": 1024,
        }
        
        try:
            response = requests.post(
                OPENROUTER_BASE_URL,
                headers=headers,
                data=json.dumps(payload),
                timeout=timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
            
            # Log error for debugging
            print(f"Model {model_id} returned status {response.status_code}: {response.text[:200]}")
            return None
            
        except requests.exceptions.Timeout:
            print(f"Model {model_id} timed out after {timeout}s")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Model {model_id} request failed: {str(e)}")
            return None
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"Model {model_id} response parsing failed: {str(e)}")
            return None
    
    def generate(self, prompt: str, max_context_tokens: int = None) -> Tuple[str, str]:
        """
        Generate a response using the first available model.
        
        Args:
            prompt: The prompt to send
            max_context_tokens: Optional limit on context size
            
        Returns:
            Tuple of (response_text, model_name)
            
        Raises:
            RuntimeError: If all models fail
        """
        errors = []
        
        for model in self.models:
            # Skip model if context is too large
            if max_context_tokens and max_context_tokens > model.max_context_tokens:
                print(f"Skipping {model.name}: context too large ({max_context_tokens} > {model.max_context_tokens})")
                continue
            
            print(f"Trying model: {model.name} ({model.model_id})")
            
            response = self._call_model(
                model_id=model.model_id,
                prompt=prompt,
                timeout=model.timeout
            )
            
            if response:
                return response, model.name
            
            errors.append(f"{model.name}: failed")
        
        # All models failed
        error_msg = "All models failed: " + "; ".join(errors)
        raise RuntimeError(error_msg)
    
    def get_available_models(self) -> list:
        """Return list of available model names."""
        return [m.name for m in self.models]


# Singleton instance
llm_router = LLMRouter()
