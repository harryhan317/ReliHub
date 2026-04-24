"""
Claude LLM Provider (Anthropic)

Implements LLMProvider interface for Claude API.
API Documentation: https://docs.anthropic.com/claude/reference
"""

import logging
from typing import Any, AsyncGenerator, Dict, List

import httpx

from .base import LLMProvider

logger = logging.getLogger(__name__)


class ClaudeProvider(LLMProvider):
    """Anthropic Claude LLM Provider"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.anthropic.com"
    ):
        """
        Initialize Claude Provider
        
        Args:
            api_key: Anthropic API Key
            base_url: Anthropic API base URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            timeout=120.0
        )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Chat completion using Claude API
        
        Args:
            messages: List of messages
            model: Model name (claude-3-opus, claude-3-sonnet, claude-3-haiku)
            temperature: Temperature (0.0-1.0)
            max_tokens: Maximum tokens
            stream: Whether to stream output
            
        Yields:
            Dict with content, finish_reason, and usage
        """
        url = "/v1/messages"
        
        # Convert messages to Claude format
        system_message = "You are a helpful assistant."
        claude_messages = []
        
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "system":
                system_message = content
            elif role == "user":
                claude_messages.append({"role": "user", "content": content})
            elif role == "assistant":
                claude_messages.append({"role": "assistant", "content": content})
        
        payload = {
            "model": model,
            "messages": claude_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream,
            "system": system_message
        }
        
        try:
            if stream:
                async with self.client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            
                            try:
                                import json
                                event = json.loads(data)
                                event_type = event.get("type", "")
                                
                                if event_type == "content_block_delta":
                                    delta = event.get("delta", {})
                                    content = delta.get("text", "")
                                    
                                    if content:
                                        yield {
                                            "content": content,
                                            "finish_reason": None,
                                            "usage": None
                                        }
                                elif event_type == "message_stop":
                                    yield {
                                        "content": "",
                                        "finish_reason": "stop",
                                        "usage": event.get("usage")
                                    }
                            except json.JSONDecodeError as e:
                                logger.error(f"Failed to parse chunk: {e}")
            else:
                response = await self.client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                if result.get("content"):
                    content = result["content"][0].get("text", "")
                    
                    yield {
                        "content": content,
                        "finish_reason": "stop",
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
            # Fallback to estimation (Claude uses ~4 chars per token)
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
        Get available Claude models
        
        Returns:
            List of model info
        """
        return [
            {
                "id": "claude-3-opus-20240229",
                "name": "Claude 3 Opus",
                "max_tokens": 4096,
                "description": "Most powerful Claude model"
            },
            {
                "id": "claude-3-sonnet-20240229",
                "name": "Claude 3 Sonnet",
                "max_tokens": 4096,
                "description": "Balanced performance"
            },
            {
                "id": "claude-3-haiku-20240307",
                "name": "Claude 3 Haiku",
                "max_tokens": 4096,
                "description": "Fastest and most compact"
            }
        ]
