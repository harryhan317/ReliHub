"""
Tests for Claude and Moonshot Providers
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.llm_provider.claude_provider import ClaudeProvider
from app.services.llm_provider.moonshot_provider import MoonshotProvider
from app.services.llm_provider.factory import ProviderFactory


# Test Claude Provider
class TestClaudeProvider:
    """Test Claude Provider"""
    
    def test_init(self):
        """Test Claude Provider initialization"""
        provider = ClaudeProvider(
            api_key="sk-test",
            base_url="https://api.anthropic.com"
        )
        
        assert provider.api_key == "sk-test"
        assert provider.base_url == "https://api.anthropic.com"
    
    @pytest.mark.asyncio
    async def test_get_models(self):
        """Test getting available models"""
        provider = ClaudeProvider(api_key="sk-test")
        
        models = await provider.get_models()
        
        assert len(models) == 3
        assert any(m["id"] == "claude-3-opus-20240229" for m in models)
        assert any(m["id"] == "claude-3-sonnet-20240229" for m in models)
        assert any(m["id"] == "claude-3-haiku-20240307" for m in models)
    
    @pytest.mark.asyncio
    async def test_count_tokens(self):
        """Test token counting"""
        provider = ClaudeProvider(api_key="sk-test")
        
        messages = [
            {"role": "user", "content": "Hello, how are you?"}
        ]
        
        tokens = await provider.count_tokens(messages)
        assert tokens > 0
        print(f"Claude token count: {tokens}")
    
    @pytest.mark.asyncio
    async def test_chat_completion_stream(self):
        """Test streaming chat completion (mocked)"""
        provider = ClaudeProvider(api_key="sk-test")
        
        messages = [
            {"role": "user", "content": "Say hello"}
        ]
        
        # Create async iterator for lines
        async def mock_aiter_lines():
            lines = [
                "data: {\"type\": \"content_block_delta\", \"delta\": {\"text\": \"Hello\"}}",
                "data: {\"type\": \"content_block_delta\", \"delta\": {\"text\": \"!\"}}",
                "data: {\"type\": \"message_stop\"}"
            ]
            for line in lines:
                yield line
        
        # Create mock response
        mock_response = AsyncMock()
        mock_response.aiter_lines = mock_aiter_lines
        mock_response.raise_for_status = MagicMock()
        
        # Create a class that supports async context manager
        class MockStreamContext:
            async def __aenter__(self):
                return mock_response
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None
        
        provider.client.stream = MagicMock(return_value=MockStreamContext())
        
        chunks = []
        async for chunk in provider.chat_completion(
            messages=messages,
            model="claude-3-sonnet-20240229",
            stream=True
        ):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        assert chunks[0]["content"] == "Hello"


# Test Moonshot Provider
class TestMoonshotProvider:
    """Test Moonshot Provider"""
    
    def test_init(self):
        """Test Moonshot Provider initialization"""
        provider = MoonshotProvider(
            api_key="sk-test",
            base_url="https://api.moonshot.cn/v1"
        )
        
        assert provider.api_key == "sk-test"
        assert provider.base_url == "https://api.moonshot.cn/v1"
    
    @pytest.mark.asyncio
    async def test_get_models(self):
        """Test getting available models"""
        provider = MoonshotProvider(api_key="sk-test")
        
        models = await provider.get_models()
        
        assert len(models) == 3
        assert any(m["id"] == "moonshot-v1-8k" for m in models)
        assert any(m["id"] == "moonshot-v1-32k" for m in models)
        assert any(m["id"] == "moonshot-v1-128k" for m in models)
    
    @pytest.mark.asyncio
    async def test_count_tokens(self):
        """Test token counting"""
        provider = MoonshotProvider(api_key="sk-test")
        
        messages = [
            {"role": "user", "content": "你好，请问你是谁？"}
        ]
        
        tokens = await provider.count_tokens(messages)
        assert tokens > 0
        print(f"Moonshot token count: {tokens}")
    
    @pytest.mark.asyncio
    async def test_chat_completion_stream(self):
        """Test streaming chat completion (mocked)"""
        provider = MoonshotProvider(api_key="sk-test")
        
        messages = [
            {"role": "user", "content": "介绍一下你自己"}
        ]
        
        # Create async iterator for lines
        async def mock_aiter_lines():
            lines = [
                "data: {\"choices\": [{\"delta\": {\"content\": \"你好\"}, \"finish_reason\": null}]}",
                "data: {\"choices\": [{\"delta\": {\"content\": \"！\"}, \"finish_reason\": null}]}",
                "data: [DONE]"
            ]
            for line in lines:
                yield line
        
        # Create mock response
        mock_response = AsyncMock()
        mock_response.aiter_lines = mock_aiter_lines
        mock_response.raise_for_status = MagicMock()
        
        # Create a class that supports async context manager
        class MockStreamContext:
            async def __aenter__(self):
                return mock_response
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None
        
        provider.client.stream = MagicMock(return_value=MockStreamContext())
        
        chunks = []
        async for chunk in provider.chat_completion(
            messages=messages,
            model="moonshot-v1-8k",
            stream=True
        ):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        assert chunks[0]["content"] == "你好"


# Test Provider Factory with new providers
class TestProviderFactoryExtended:
    """Test Provider Factory with all providers"""
    
    def test_get_claude_provider(self):
        """Test getting Claude provider"""
        provider = ProviderFactory.get_provider(
            provider_name="claude",
            api_key="sk-test",
            base_url="https://api.anthropic.com"
        )
        
        assert isinstance(provider, ClaudeProvider)
        assert provider.api_key == "sk-test"
    
    def test_get_moonshot_provider(self):
        """Test getting Moonshot provider"""
        provider = ProviderFactory.get_provider(
            provider_name="moonshot",
            api_key="sk-test",
            base_url="https://api.moonshot.cn/v1"
        )
        
        assert isinstance(provider, MoonshotProvider)
        assert provider.api_key == "sk-test"
    
    def test_all_providers_registered(self):
        """Test all providers are registered"""
        expected_providers = ["deepseek", "openai", "claude", "moonshot"]
        
        for provider_name in expected_providers:
            assert provider_name in ProviderFactory.PROVIDERS
            print(f"✅ {provider_name} is registered")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
