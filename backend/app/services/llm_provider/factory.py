"""
LLM Provider Factory

Dynamically loads and instantiates LLM providers based on configuration.
"""

import importlib
import logging
from typing import Dict, Type

from app.services.llm_provider.base import LLMProvider

logger = logging.getLogger(__name__)


class ProviderFactory:
    """
    Factory for creating LLM Provider instances.
    
    Usage:
        factory = ProviderFactory()
        provider = factory.get_provider("deepseek", api_key="sk-xxx")
    """
    
    # Provider mapping: name -> module.class
    PROVIDERS: Dict[str, Dict[str, str]] = {
        "deepseek": {
            "module": "app.services.llm_provider.deepseek_provider",
            "class": "DeepSeekProvider"
        },
        "openai": {
            "module": "app.services.llm_provider.openai_provider",
            "class": "OpenAIProvider"
        },
        "claude": {
            "module": "app.services.llm_provider.claude_provider",
            "class": "ClaudeProvider"
        },
        "moonshot": {
            "module": "app.services.llm_provider.moonshot_provider",
            "class": "MoonshotProvider"
        }
    }
    
    # Cache for loaded provider classes
    _loaded_classes: Dict[str, Type[LLMProvider]] = {}
    
    @classmethod
    def get_provider(
        cls,
        provider_name: str,
        api_key: str,
        base_url: str = None,
        **kwargs
    ) -> LLMProvider:
        """
        Get a provider instance by name.
        
        Args:
            provider_name: Name of the provider (e.g., 'deepseek', 'openai')
            api_key: API key for the provider
            base_url: Optional custom base URL
            **kwargs: Additional provider-specific arguments
            
        Returns:
            LLMProvider instance
            
        Raises:
            ValueError: If provider name is not supported
        """
        if provider_name not in cls.PROVIDERS:
            raise ValueError(
                f"Unsupported LLM provider: {provider_name}. "
                f"Supported providers: {list(cls.PROVIDERS.keys())}"
            )
        
        provider_config = cls.PROVIDERS[provider_name]
        module_name = provider_config["module"]
        class_name = provider_config["class"]
        
        # Load and cache the provider class
        if class_name not in cls._loaded_classes:
            try:
                module = importlib.import_module(module_name)
                provider_class = getattr(module, class_name)
                cls._loaded_classes[class_name] = provider_class
                logger.info(f"Loaded provider: {class_name} from {module_name}")
            except ImportError as e:
                logger.error(f"Failed to import provider {class_name}: {e}")
                raise ValueError(f"Provider {provider_name} module not found")
        
        provider_class = cls._loaded_classes[class_name]
        
        # Instantiate provider
        if base_url:
            return provider_class(api_key=api_key, base_url=base_url, **kwargs)
        else:
            return provider_class(api_key=api_key, **kwargs)
    
    @classmethod
    def register_provider(
        cls,
        name: str,
        module: str,
        class_name: str
    ):
        """
        Register a new provider dynamically.
        
        Args:
            name: Provider name (e.g., 'custom')
            module: Module path (e.g., 'app.services.llm_provider.custom_provider')
            class_name: Class name (e.g., 'CustomProvider')
        """
        cls.PROVIDERS[name] = {
            "module": module,
            "class": class_name
        }
        logger.info(f"Registered new provider: {name}")
    
    @classmethod
    def get_available_providers(cls) -> list:
        """
        Get list of available provider names.
        
        Returns:
            List of provider names
        """
        return list(cls.PROVIDERS.keys())
