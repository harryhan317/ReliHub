"""
Tests for LLM Provider module.
"""

import pytest

from app.services.llm_provider.deepseek_provider import DeepSeekProvider


class TestDeepSeekProvider:
    """Test cases for DeepSeekProvider"""
    
    @pytest.fixture
    def provider(self):
        """Create a DeepSeekProvider instance"""
        return DeepSeekProvider(api_key="test-key")
    
    def test_init(self, provider):
        """Test provider initialization"""
        assert provider.api_key == "test-key"
        assert "deepseek.com" in provider.base_url
    
    def test_count_tokens_empty(self, provider):
        """Test token counting with empty messages"""
        messages = []
        tokens = provider.count_tokens(messages)
        assert tokens == 0
    
    def test_count_tokens_simple(self, provider):
        """Test token counting with simple message"""
        messages = [{"role": "user", "content": "Hello"}]
        tokens = provider.count_tokens(messages)
        assert tokens > 0
    
    def test_count_tokens_chinese(self, provider):
        """Test token counting with Chinese text"""
        messages = [{"role": "user", "content": "你好，世界"}]
        tokens = provider.count_tokens(messages)
        assert tokens > 0
    
    def test_get_models(self, provider):
        """Test getting available models"""
        models = provider.get_models()
        assert len(models) > 0
        assert any(m["id"] == "deepseek-chat" for m in models)
        assert any(m["id"] == "deepseek-coder" for m in models)


class TestDeepSeekProviderSync:
    """Sync test cases for DeepSeekProvider"""
    
    @pytest.fixture
    def provider(self):
        """Create a DeepSeekProvider instance"""
        return DeepSeekProvider(api_key="test-key")
    
    def test_chat_completion_stream(self, provider):
        """Test streaming chat completion"""
        from unittest.mock import MagicMock, patch
        
        messages = [{"role": "user", "content": "Hello"}]
        
        def mock_stream_response():
            chunks = [
                'data: {"choices": [{"delta": {"content": "Hello"}, "finish_reason": null}]}',
                'data: {"choices": [{"delta": {"content": "!"}, "finish_reason": null}]}',
                'data: [DONE]'
            ]
            for chunk in chunks:
                yield chunk
        
        with patch('httpx.Client.stream') as mock_stream:
            mock_response = MagicMock()
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=None)
            mock_response.iter_lines = mock_stream_response
            mock_response.raise_for_status = MagicMock()
            mock_stream.return_value.__enter__ = MagicMock(return_value=mock_response)
            
            chunks = []
            for chunk in provider.chat_completion(messages, stream=True):
                chunks.append(chunk)
            
            assert len(chunks) > 0
    
    def test_chat_completion_non_stream(self, provider):
        """Test non-streaming chat completion"""
        from unittest.mock import MagicMock, patch
        
        messages = [{"role": "user", "content": "Hello"}]
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {"content": "Hello!"},
                    "finish_reason": "stop"
                }
            ],
            "usage": {"total_tokens": 10}
        }
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(provider.client, 'post', return_value=mock_response):
            chunks = []
            for chunk in provider.chat_completion(messages, stream=False):
                chunks.append(chunk)
            
            assert len(chunks) == 1
            assert chunks[0]["content"] == "Hello!"
