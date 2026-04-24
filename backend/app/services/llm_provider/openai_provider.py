"""
OpenAI LLM Provider

Implements LLMProvider interface for OpenAI API.
API Documentation: https://platform.openai.com/docs/api-reference
"""

import logging
from typing import Any, Dict, Generator, List

import httpx

from .base import LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI LLM Provider"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1"
    ):
        """
        Initialize OpenAI Provider
        
        Args:
            api_key: OpenAI API Key
            base_url: OpenAI API base URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.Client(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=120.0
        )
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = True
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Chat completion using OpenAI API
        
        Args:
            messages: List of messages
            model: Model name (gpt-3.5-turbo, gpt-4, etc.)
            temperature: Temperature (0.0-2.0)
            max_tokens: Maximum tokens
            stream: Whether to stream output
            
        Yields:
            Dict with content, finish_reason, and usage
        """
        url = "/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        try:
            if stream:
                with self.client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    
                    for line in response.iter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            
                            if data == "[DONE]":
                                break
                            
                            try:
                                import json
                                chunk = json.loads(data)
                                
                                if chunk.get("choices"):
                                    choice = chunk["choices"][0]
                                    delta = choice.get("delta", {})
                                    content = delta.get("content", "")
                                    finish_reason = choice.get("finish_reason")
                                    
                                    if content or finish_reason:
                                        yield {
                                            "content": content,
                                            "finish_reason": finish_reason,
                                            "usage": chunk.get("usage")
                                        }
                            except json.JSONDecodeError as e:
                                logger.error(f"Failed to parse chunk: {e}")
            else:
                response = self.client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                if result.get("choices"):
                    choice = result["choices"][0]
                    message = choice.get("message", {})
                    
                    yield {
                        "content": message.get("content", ""),
                        "finish_reason": choice.get("finish_reason"),
                        "usage": result.get("usage")
                    }
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            yield {
                "content": f"Error: {e.response.status_code}",
                "finish_reason": "error",
                "usage": None
            }
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            yield {
                "content": "Error: Connection failed",
                "finish_reason": "error",
                "usage": None
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            yield {
                "content": f"Error: {str(e)}",
                "finish_reason": "error",
                "usage": None
            }
    
    def count_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        Estimate token count
        
        Uses tiktoken if available, otherwise falls back to estimation.
        
        Args:
            messages: List of messages
            
        Returns:
            Estimated token count
        """
        try:
            import tiktoken
            encoding = tiktoken.get_encoding("cl100k_base")
            
            total_tokens = 0
            for message in messages:
                content = message.get("content", "")
                role = message.get("role", "")
                tokens = len(encoding.encode(f"{role}: {content}"))
                total_tokens += tokens
            
            return total_tokens
        except ImportError:
            total_tokens = 0
            for message in messages:
                content = message.get("content", "")
                chinese_chars = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
                english_chars = len(content) - chinese_chars
                tokens = int(chinese_chars / 1.5 + english_chars / 4)
                total_tokens += tokens
            return total_tokens
    
    def get_models(self) -> List[Dict[str, Any]]:
        """
        Get available OpenAI models
        
        Returns:
            List of model info
        """
        return [
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "max_tokens": 4096,
                "description": "Fast and efficient for most tasks"
            },
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "max_tokens": 8192,
                "description": "Most capable model"
            },
            {
                "id": "gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "max_tokens": 128000,
                "description": "Faster GPT-4 with larger context"
            }
        ]
