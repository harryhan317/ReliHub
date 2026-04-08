"""
Enhanced Integration tests for AI Service with LLM Provider.

Uses PostgreSQL test database via conftest.py fixtures.

Tests:
1. AISessionService - Session CRUD operations
2. AIMessageService - Message CRUD operations
3. AIService - Provider management and chat completion
4. Stream response handling
5. Cost calculation and billing
"""

import pytest
import os
import uuid
from unittest.mock import MagicMock, patch

from app.services.ai_service import AIService, AISessionService, AIMessageService
from app.services.llm_provider.factory import ProviderFactory
from app.services.llm_provider.openai_provider import OpenAIProvider
from app.services.llm_provider.deepseek_provider import DeepSeekProvider
from app.models.llm_provider import LLMProvider
from app.models.ai_session import AISession
from app.models.ai_message import AIMessage


@pytest.fixture
def sample_provider(db_session):
    provider = LLMProvider(
        id=str(uuid.uuid4()),
        name="deepseek",
        display_name="DeepSeek",
        api_base_url="https://api.deepseek.com/v1",
        api_key_env="DEEPSEEK_API_KEY",
        cost_per_1k_tokens=0.001,
        rate_limit_per_minute=60,
        enabled=True
    )
    db_session.add(provider)
    db_session.commit()
    return provider


@pytest.fixture
def disabled_provider(db_session):
    provider = LLMProvider(
        id=str(uuid.uuid4()),
        name="disabled_provider",
        display_name="Disabled Provider",
        api_base_url="https://api.disabled.com/v1",
        api_key_env="DISABLED_API_KEY",
        cost_per_1k_tokens=0.002,
        enabled=False
    )
    db_session.add(provider)
    db_session.commit()
    return provider


@pytest.fixture
def openai_provider(db_session):
    provider = LLMProvider(
        id=str(uuid.uuid4()),
        name="openai",
        display_name="OpenAI",
        api_base_url="https://api.openai.com/v1",
        api_key_env="OPENAI_API_KEY",
        cost_per_1k_tokens=0.002,
        enabled=True
    )
    db_session.add(provider)
    db_session.commit()
    return provider


class TestAISessionService:
    """Test AI Session Service"""
    
    def test_create_session(self, db_session):
        service = AISessionService(db_session)
        
        class MockRequest:
            title = "Test Session"
            model_type = "general"
        
        session = service.create_session("user-123", MockRequest())
        
        assert session is not None
        assert session.user_id == "user-123"
        assert session.title == "Test Session"
    
    def test_create_session_with_no_user(self, db_session):
        service = AISessionService(db_session)
        
        class MockRequest:
            title = "Guest Session"
            model_type = "general"
        
        session = service.create_session(None, MockRequest())
        
        assert session is not None
        assert session.user_id is None
        assert session.title == "Guest Session"
    
    def test_list_sessions_empty(self, db_session):
        service = AISessionService(db_session)
        
        sessions, total = service.list_sessions("user-123", page=1, page_size=20)
        
        assert sessions == []
        assert total == 0
    
    def test_get_session_not_found(self, db_session):
        service = AISessionService(db_session)
        
        session = service.get_session("non-existent-id", "user-123")
        
        assert session is None


class TestAIMessageService:
    """Test AI Message Service"""
    
    def test_create_message(self, db_session):
        session_service = AISessionService(db_session)
        message_service = AIMessageService(db_session)
        
        class MockRequest:
            title = "Test Session"
            model_type = "general"
        
        session = session_service.create_session("user-123", MockRequest())
        
        message = message_service.create_message(
            session_id=session.id,
            content="Hello, AI!",
            role="user"
        )
        
        assert message is not None
        assert message.session_id == session.id
        assert message.content == "Hello, AI!"
        assert message.role == "user"
    
    def test_list_messages_empty(self, db_session):
        service = AIMessageService(db_session)
        
        messages, total = service.list_messages("session-123", page=1, page_size=50)
        
        assert messages == []
        assert total == 0


class TestAIServiceProviderManagement:
    """Test AI Service Provider Management"""
    
    def test_get_enabled_providers(self, db_session, sample_provider, disabled_provider):
        service = AIService(db_session)
        
        providers = service.get_enabled_providers()
        
        assert len(providers) == 1
        assert providers[0].name == "deepseek"
    
    def test_get_enabled_providers_empty(self, db_session):
        service = AIService(db_session)
        
        providers = service.get_enabled_providers()
        
        assert providers == []
    
    def test_get_provider_by_name(self, db_session, sample_provider):
        service = AIService(db_session)
        
        provider = service.get_provider_by_name("deepseek")
        
        assert provider is not None
        assert provider.name == "deepseek"
        assert provider.display_name == "DeepSeek"
    
    def test_get_provider_by_name_not_found(self, db_session):
        service = AIService(db_session)
        
        provider = service.get_provider_by_name("nonexistent")
        
        assert provider is None
    
    def test_get_provider_by_name_disabled(self, db_session, disabled_provider):
        service = AIService(db_session)
        
        provider = service.get_provider_by_name("disabled_provider")
        
        assert provider is None
    
    def test_instantiate_provider_deepseek(self, db_session, sample_provider):
        os.environ["DEEPSEEK_API_KEY"] = "sk-test-key"
        
        service = AIService(db_session)
        provider = service.instantiate_provider(sample_provider)
        
        assert isinstance(provider, DeepSeekProvider)
        assert provider.api_key == "sk-test-key"
        
        del os.environ["DEEPSEEK_API_KEY"]
    
    def test_instantiate_provider_openai(self, db_session, openai_provider):
        os.environ["OPENAI_API_KEY"] = "sk-openai-key"
        
        service = AIService(db_session)
        provider = service.instantiate_provider(openai_provider)
        
        assert isinstance(provider, OpenAIProvider)
        assert provider.api_key == "sk-openai-key"
        
        del os.environ["OPENAI_API_KEY"]
    
    def test_instantiate_provider_missing_key(self, db_session, sample_provider):
        if "DEEPSEEK_API_KEY" in os.environ:
            del os.environ["DEEPSEEK_API_KEY"]
        
        service = AIService(db_session)
        
        with pytest.raises(ValueError) as exc_info:
            service.instantiate_provider(sample_provider)
        
        assert "API key not found" in str(exc_info.value)
    
    def test_provider_cache(self, db_session, sample_provider):
        os.environ["DEEPSEEK_API_KEY"] = "sk-test-key"
        
        service = AIService(db_session)
        
        provider1 = service.instantiate_provider(sample_provider)
        provider2 = service.instantiate_provider(sample_provider)
        
        assert provider1 is provider2
        
        del os.environ["DEEPSEEK_API_KEY"]


class TestAIServiceCostCalculation:
    """Test AI Service Cost Calculation"""
    
    def test_calculate_cost_basic(self, db_session, sample_provider):
        service = AIService(db_session)
        
        cost = service.calculate_cost("deepseek", 1000)
        
        assert abs(cost - 0.001) < 0.0001
    
    def test_calculate_cost_fractional_tokens(self, db_session, sample_provider):
        service = AIService(db_session)
        
        cost = service.calculate_cost("deepseek", 500)
        
        assert abs(cost - 0.0005) < 0.0001
    
    def test_calculate_cost_zero_tokens(self, db_session, sample_provider):
        service = AIService(db_session)
        
        cost = service.calculate_cost("deepseek", 0)
        
        assert cost == 0.0
    
    def test_calculate_cost_large_tokens(self, db_session, sample_provider):
        service = AIService(db_session)
        
        cost = service.calculate_cost("deepseek", 100000)
        
        assert abs(cost - 0.1) < 0.0001
    
    def test_calculate_cost_unknown_provider(self, db_session):
        service = AIService(db_session)
        
        cost = service.calculate_cost("unknown", 1000)
        
        assert cost == 0.0


class TestAIServiceRateLimit:
    """Test AI Service Rate Limiting"""
    
    def test_check_rate_limit_allowed(self, db_session, sample_provider):
        service = AIService(db_session)
        
        result = service.check_rate_limit("deepseek", "user-123")
        
        assert result is True
    
    def test_check_rate_limit_no_user(self, db_session, sample_provider):
        service = AIService(db_session)
        
        result = service.check_rate_limit("deepseek", None)
        
        assert result is True


class TestAIServiceChatCompletion:
    """Test AI Service Chat Completion"""
    
    def test_chat_completion_no_providers(self, db_session):
        service = AIService(db_session)
        
        mock_session = MagicMock()
        
        with pytest.raises(ValueError) as exc_info:
            for _ in service.chat_completion(
                session=mock_session,
                messages=[{"role": "user", "content": "Hello"}]
            ):
                pass
        
        assert "No LLM providers configured" in str(exc_info.value)
    
    def test_chat_completion_provider_not_found(self, db_session, sample_provider):
        service = AIService(db_session)
        
        mock_session = MagicMock()
        
        with pytest.raises(ValueError) as exc_info:
            for _ in service.chat_completion(
                session=mock_session,
                messages=[{"role": "user", "content": "Hello"}],
                provider_name="nonexistent"
            ):
                pass
        
        assert "not found or disabled" in str(exc_info.value)
    
    def test_chat_completion_with_mocked_provider(self, db_session, sample_provider):
        os.environ["DEEPSEEK_API_KEY"] = "sk-test-key"
        
        service = AIService(db_session)
        
        mock_session = AISession(
            id=str(uuid.uuid4()),
            user_id="user-123",
            title="Test",
            total_tokens=0,
            total_cost=0.0
        )
        db_session.add(mock_session)
        db_session.commit()
        
        mock_provider = MagicMock()
        mock_provider.chat_completion.return_value = iter([
            {"content": "Hello", "finish_reason": None, "usage": {"total_tokens": 10}},
            {"content": "!", "finish_reason": "stop", "usage": {"total_tokens": 10}}
        ])
        mock_provider.get_models.return_value = [{"id": "deepseek-chat"}]
        
        service._provider_cache[sample_provider.id] = mock_provider
        
        chunks = list(service.chat_completion(
            session=mock_session,
            messages=[{"role": "user", "content": "Hi"}],
            stream=True
        ))
        
        assert len(chunks) == 2
        assert chunks[0]["content"] == "Hello"
        assert chunks[1]["content"] == "!"
        
        del os.environ["DEEPSEEK_API_KEY"]


class TestProviderFactory:
    """Test Provider Factory"""
    
    def test_get_deepseek_provider(self):
        provider = ProviderFactory.get_provider(
            provider_name="deepseek",
            api_key="sk-test",
            base_url="https://api.deepseek.com/v1"
        )
        
        assert isinstance(provider, DeepSeekProvider)
        assert provider.api_key == "sk-test"
    
    def test_get_openai_provider(self):
        provider = ProviderFactory.get_provider(
            provider_name="openai",
            api_key="sk-test",
            base_url="https://api.openai.com/v1"
        )
        
        assert isinstance(provider, OpenAIProvider)
        assert provider.api_key == "sk-test"
    
    def test_get_unsupported_provider(self):
        with pytest.raises(ValueError) as exc_info:
            ProviderFactory.get_provider(
                provider_name="unsupported",
                api_key="sk-test"
            )
        
        assert "Unsupported LLM provider" in str(exc_info.value)
    
    def test_registered_providers(self):
        assert "deepseek" in ProviderFactory.PROVIDERS
        assert "openai" in ProviderFactory.PROVIDERS


class TestOpenAIProvider:
    """Test OpenAI Provider"""
    
    def test_count_tokens(self):
        provider = OpenAIProvider(api_key="sk-test")
        
        messages = [
            {"role": "user", "content": "Hello, how are you?"}
        ]
        
        tokens = provider.count_tokens(messages)
        
        assert tokens > 0
    
    def test_count_tokens_empty(self):
        provider = OpenAIProvider(api_key="sk-test")
        
        tokens = provider.count_tokens([])
        
        assert tokens == 0
    
    def test_count_tokens_multilingual(self):
        provider = OpenAIProvider(api_key="sk-test")
        
        messages = [
            {"role": "user", "content": "你好，世界！Hello, World!"}
        ]
        
        tokens = provider.count_tokens(messages)
        
        assert tokens > 0
    
    def test_get_models(self):
        provider = OpenAIProvider(api_key="sk-test")
        
        models = provider.get_models()
        
        assert len(models) > 0
        model_ids = [m["id"] for m in models]
        assert "gpt-3.5-turbo" in model_ids
        assert "gpt-4" in model_ids
    
    def test_chat_completion_stream_mocked(self):
        provider = OpenAIProvider(api_key="sk-test")
        
        messages = [{"role": "user", "content": "Say hello"}]
        
        def mock_iter_lines():
            lines = [
                'data: {"choices": [{"delta": {"content": "Hello"}, "finish_reason": null}]}',
                'data: {"choices": [{"delta": {"content": "!"}, "finish_reason": "stop"}]}',
                'data: [DONE]'
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
        
        chunks = list(provider.chat_completion(
            messages=messages,
            model="gpt-3.5-turbo",
            stream=True
        ))
        
        assert len(chunks) >= 1
        assert "Hello" in chunks[0]["content"]


class TestDeepSeekProvider:
    """Test DeepSeek Provider"""
    
    def test_count_tokens(self):
        provider = DeepSeekProvider(api_key="sk-test")
        
        messages = [
            {"role": "user", "content": "你好，世界！"}
        ]
        
        tokens = provider.count_tokens(messages)
        
        assert tokens > 0
    
    def test_get_models(self):
        provider = DeepSeekProvider(api_key="sk-test")
        
        models = provider.get_models()
        
        assert len(models) > 0
        model_ids = [m["id"] for m in models]
        assert "deepseek-chat" in model_ids


class TestAISessionModel:
    """Test AI Session Model"""
    
    def test_create_session_model(self, db_session):
        session = AISession(
            id=str(uuid.uuid4()),
            user_id="user-123",
            title="Test Session",
            model_type="general",
            total_tokens=0,
            total_cost=0.0,
            total_turns=0
        )
        
        db_session.add(session)
        db_session.commit()
        
        assert session.id is not None
        assert session.user_id == "user-123"
        assert session.title == "Test Session"
    
    def test_session_default_values(self, db_session):
        session = AISession(
            id=str(uuid.uuid4()),
            user_id="user-123"
        )
        
        db_session.add(session)
        db_session.commit()
        
        assert session.model_type == "general"
        assert session.total_tokens == 0
        assert session.total_cost == 0.0
        assert session.total_turns == 0
        assert session.max_turns == 50
        assert session.max_tokens == 50000
        assert session.is_deleted == False


class TestAIMessageModel:
    """Test AI Message Model"""
    
    def test_create_message_model(self, db_session):
        session = AISession(
            id=str(uuid.uuid4()),
            user_id="user-123",
            title="Test Session"
        )
        db_session.add(session)
        db_session.commit()
        
        message = AIMessage(
            id=str(uuid.uuid4()),
            session_id=session.id,
            role="user",
            content="Hello, AI!",
            token_count=5
        )
        
        db_session.add(message)
        db_session.commit()
        
        assert message.id is not None
        assert message.session_id == session.id
        assert message.role == "user"
        assert message.content == "Hello, AI!"
    
    def test_message_default_values(self, db_session):
        session = AISession(
            id=str(uuid.uuid4()),
            user_id="user-123"
        )
        db_session.add(session)
        db_session.commit()
        
        message = AIMessage(
            id=str(uuid.uuid4()),
            session_id=session.id,
            role="user",
            content="Test"
        )
        
        db_session.add(message)
        db_session.commit()
        
        assert message.token_count == 0
        assert message.cost == 0.0
        assert message.has_attachment == False
        assert message.is_deleted == False


class TestLLMProviderModel:
    """Test LLM Provider Model"""
    
    def test_create_provider_model(self, db_session):
        provider = LLMProvider(
            id=str(uuid.uuid4()),
            name="test_provider",
            display_name="Test Provider",
            api_base_url="https://api.test.com/v1",
            api_key_env="TEST_API_KEY",
            cost_per_1k_tokens=0.001
        )
        
        db_session.add(provider)
        db_session.commit()
        
        assert provider.id is not None
        assert provider.name == "test_provider"
        assert provider.enabled == True
    
    def test_provider_default_values(self, db_session):
        provider = LLMProvider(
            id=str(uuid.uuid4()),
            name="test_provider2",
            display_name="Test Provider 2",
            api_base_url="https://api.test2.com/v1",
            api_key_env="TEST2_API_KEY",
            cost_per_1k_tokens=0.002
        )
        
        db_session.add(provider)
        db_session.commit()
        
        assert provider.enabled == True
        assert provider.rate_limit_per_minute == 60


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
