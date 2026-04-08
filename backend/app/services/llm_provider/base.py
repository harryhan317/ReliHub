"""
Abstract base class for LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, List


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = True
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Chat completion interface
        
        Args:
            messages: List of messages [{"role": "user", "content": "hello"}]
            model: Model name
            temperature: Temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream output
            
        Yields:
            {
                "content": str,
                "finish_reason": str|None,
                "usage": dict
            }
        """
        pass
    
    @abstractmethod
    def count_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        Count tokens in messages
        
        Args:
            messages: List of messages
            
        Returns:
            Token count
        """
        pass
    
    @abstractmethod
    def get_models(self) -> List[Dict[str, Any]]:
        """
        Get available models
        
        Returns:
            List of model info:
            [
                {
                    "id": str,
                    "name": str,
                    "max_tokens": int,
                    "description": str
                }
            ]
        """
        pass
