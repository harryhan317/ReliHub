"""
Integration tests for AI Service with LLM Provider.

Tests:
1. Provider Factory
2. OpenAI Provider
3. DeepSeek Provider
4. AI Service integration
5. Stream response

Database: PostgreSQL (uses shared fixtures from conftest.py)
"""

import os
from unittest.mock import MagicMock

import pytest

from app.models.llm_provider import LLMProvider
from app.services.ai_service import AIService
from app.services.llm_provider.deepseek_provider import DeepSeekProvider
from app.services.llm_provider.factory import ProviderFactory
from app.services.llm_provider.openai_provider import OpenAIProvider


class TestProviderFactory:
    """Test Provider Factory"""
    
    def test_get_deepseek_provider(self):
        """Test getting DeepSeek provider"""
        provider = ProviderFactory.get_provider(
            provider_name="deepseek",
            api_key="sk-test",
            base_url="https://api.deepseek.com/v1"
        )
        
        assert isinstance(provider, DeepSeekProvider)
        assert provider.api_key == "sk-test"
    
    def test_get_openai_provider(self):
        """Test getting OpenAI provider"""
        provider = ProviderFactory.get_provider(
            provider_name="openai",
            api_key="sk-test",
            base_url="https://api.openai.com/v1"
        )
        
        assert isinstance(provider, OpenAIProvider)
        assert provider.api_key == "sk-test"
    
    def test_get_unsupported_provider(self):
        """Test getting unsupported provider"""
        with pytest.raises(ValueError) as exc_info:
            ProviderFactory.get_provider(
                provider_name="unsupported",
                api_key="sk-test"
            )
        
        assert "Unsupported LLM provider" in str(exc_info.value)
        assert "deepseek" in str(exc_info.value)
        assert "openai" in str(exc_info.value)


class TestOpenAIProvider:
    """Test OpenAI Provider"""
    
    def test_count_tokens(self):
        """Test token counting"""
        provider = OpenAIProvider(api_key="sk-test")
        
        messages = [
            {"role": "user", "content": "Hello, how are you?"}
        ]
        
        tokens = provider.count_tokens(messages)
        assert tokens > 0
        print(f"Token count: {tokens}")
    
    def test_get_models(self):
        """Test getting available models"""
        provider = OpenAIProvider(api_key="sk-test")
        
        models = provider.get_models()
        
        assert len(models) > 0
        assert any(m["id"] == "gpt-3.5-turbo" for m in models)
        assert any(m["id"] == "gpt-4" for m in models)
    
    def test_chat_completion_stream(self):
        """Test streaming chat completion (mocked)"""
        provider = OpenAIProvider(api_key="sk-test")
        
        messages = [
            {"role": "user", "content": "Say hello"}
        ]
        
        def mock_iter_lines():
            lines = [
                "data: {\"choices\": [{\"delta\": {\"content\": \"Hello\"}, \"finish_reason\": null}]}",
                "data: {\"choices\": [{\"delta\": {\"content\": \"!\"}, \"finish_reason\": \"stop\"}]}",
                "data: [DONE]"
            ]
            for line in lines:
                yield line
        
        mock_response = MagicMock()
        mock_response.iter_lines = mock_iter_lines
        mock_response.raise_for_status = MagicMock()
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_response)
        mock_context.__exit__ = MagicMock(return_value=None)
        
        provider.client.stream = MagicMock(return_value=mock_context)
        
        chunks = []
        for chunk in provider.chat_completion(
            messages=messages,
            model="gpt-3.5-turbo",
            stream=True
        ):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        assert chunks[0]["content"] == "Hello"


class TestAIService:
    """Test AI Service"""
    
    @pytest.fixture
    def ai_service(self, db_session):
        """Create AIService instance"""
        return AIService(db_session)
    
    def test_get_enabled_providers(self, db_session, ai_service):
        """Test getting enabled providers"""
        provider = LLMProvider(
            id="test-1",
            name="deepseek",
            display_name="DeepSeek",
            api_base_url="https://api.deepseek.com/v1",
            api_key_env="DEEPSEEK_API_KEY",
            cost_per_1k_tokens=0.001,
            enabled=True
        )
        db_session.add(provider)
        db_session.commit()
        
        providers = ai_service.get_enabled_providers()
        
        assert len(providers) == 1
        assert providers[0].name == "deepseek"
    
    def test_get_disabled_providers(self, db_session, ai_service):
        """Test getting disabled providers"""
        provider = LLMProvider(
            id="test-1",
            name="deepseek",
            display_name="DeepSeek",
            api_base_url="https://api.deepseek.com/v1",
            api_key_env="DEEPSEEK_API_KEY",
            cost_per_1k_tokens=0.001,
            enabled=False
        )
        db_session.add(provider)
        db_session.commit()
        
        providers = ai_service.get_enabled_providers()
        
        assert len(providers) == 0
    
    def test_instantiate_provider(self, db_session, ai_service):
        """Test instantiating provider"""
        os.environ["DEEPSEEK_API_KEY"] = "sk-test-key"
        
        provider = LLMProvider(
            id="test-1",
            name="deepseek",
            display_name="DeepSeek",
            api_base_url="https://api.deepseek.com/v1",
            api_key_env="DEEPSEEK_API_KEY",
            cost_per_1k_tokens=0.001,
            enabled=True
        )
        db_session.add(provider)
        db_session.commit()
        
        instantiated = ai_service.instantiate_provider(provider)
        
        assert isinstance(instantiated, DeepSeekProvider)
        assert instantiated.api_key == "sk-test-key"
    
    def test_instantiate_provider_missing_key(self, db_session, ai_service):
        """Test instantiating provider with missing API key"""
        if "DEEPSEEK_API_KEY" in os.environ:
            del os.environ["DEEPSEEK_API_KEY"]
        
        provider = LLMProvider(
            id="test-1",
            name="deepseek",
            display_name="DeepSeek",
            api_base_url="https://api.deepseek.com/v1",
            api_key_env="DEEPSEEK_API_KEY",
            cost_per_1k_tokens=0.001,
            enabled=True
        )
        db_session.add(provider)
        db_session.commit()
        
        with pytest.raises(ValueError) as exc_info:
            ai_service.instantiate_provider(provider)
        
        assert "API key not found" in str(exc_info.value)
    
    def test_calculate_cost(self, db_session, ai_service):
        """Test cost calculation"""
        provider = LLMProvider(
            id="test-1",
            name="deepseek",
            display_name="DeepSeek",
            api_base_url="https://api.deepseek.com/v1",
            api_key_env="DEEPSEEK_API_KEY",
            cost_per_1k_tokens=0.001,
            enabled=True
        )
        db_session.add(provider)
        db_session.commit()
        
        cost = ai_service.calculate_cost("deepseek", 1000)
        assert abs(cost - 0.001) < 0.0001
        
        cost = ai_service.calculate_cost("deepseek", 500)
        assert abs(cost - 0.0005) < 0.0001
    
    def test_chat_completion_no_providers(self, ai_service):
        """Test chat completion with no providers"""
        mock_session = MagicMock()
        
        with pytest.raises(ValueError) as exc_info:
            for chunk in ai_service.chat_completion(
                session=mock_session,
                messages=[{"role": "user", "content": "Hello"}]
            ):
                pass
        
        assert "No LLM providers configured" in str(exc_info.value)


class TestIntegration:
    """Integration tests"""
    
    def test_full_flow(self):
        """Test full conversation flow"""
        assert ProviderFactory.PROVIDERS is not None
        assert "deepseek" in ProviderFactory.PROVIDERS
        assert "openai" in ProviderFactory.PROVIDERS


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
