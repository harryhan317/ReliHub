"""
Moonshot LLM Provider (月之暗面)

Implements LLMProvider interface for Moonshot API.
API Documentation: https://platform.moonshot.cn/docs
"""

import logging
from typing import Any, AsyncGenerator, Dict, List

import httpx

from .base import LLMProvider

logger = logging.getLogger(__name__)


class MoonshotProvider(LLMProvider):
    """Moonshot (月之暗面) LLM Provider"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.moonshot.cn/v1"
    ):
        """
        Initialize Moonshot Provider
        
        Args:
            api_key: Moonshot API Key
            base_url: Moonshot API base URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=120.0
        )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "moonshot-v1-8k",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Chat completion using Moonshot API
        
        Args:
            messages: List of messages
            model: Model name (moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k)
            temperature: Temperature (0.0-1.0)
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
                async with self.client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
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
                response = await self.client.post(url, json=payload)
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
        finally:
            await self.client.aclose()
    
    async def count_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        Estimate token count
        
        Moonshot uses similar tokenization to GPT models.
        
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
            # Fallback to estimation
            total_tokens = 0
            for message in messages:
                content = message.get("content", "")
                chinese_chars = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
                english_chars = len(content) - chinese_chars
                tokens = int(chinese_chars / 1.5 + english_chars / 4)
                total_tokens += tokens
            return total_tokens
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """
        Get available Moonshot models
        
        Returns:
            List of model info
        """
        return [
            {
                "id": "moonshot-v1-8k",
                "name": "Moonshot V1 8K",
                "max_tokens": 8192,
                "description": "Standard model with 8K context"
            },
            {
                "id": "moonshot-v1-32k",
                "name": "Moonshot V1 32K",
                "max_tokens": 32768,
                "description": "Large context model"
            },
            {
                "id": "moonshot-v1-128k",
                "name": "Moonshot V1 128K",
                "max_tokens": 131072,
                "description": "Ultra large context model"
            }
        ]
