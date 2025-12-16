"""
Model configuration classes for AI services.

This module contains the classes needed to configure AI models,
including provider definitions and model parameters.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from enum import Enum


class ModelProvider(Enum):
    """
    Enumeration of supported AI model providers.

    Defines the different AI service providers that can be used
    for generating responses and processing queries.
    """
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    CUSTOM = "custom"


@dataclass
class ModelConfiguration:  # pylint: disable=too-few-public-methods
    """
    Configuration for an AI model with customizable parameters.

    This class holds the complete configuration for an AI model, including
    the provider, model name, and various generation parameters that control
    the behavior of the AI responses.
    """
    provider: Union[str, ModelProvider]
    model_name: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    custom_parameters: Optional[Dict[str, Any]] = None
    web_search: bool = False
    web_search_context: str = "medium"  # low, medium, high
    web_plugin: bool = False
    web_max_results: int = 5
    web_search_prompt: Optional[str] = None

    def __post_init__(self):
        """Convert provider to ModelProvider enum if it's a string."""
        # Handle the provider conversion safely
        if hasattr(self.provider, 'value'):
            # Already a ModelProvider enum
            provider_str = self.provider.value.lower()  # type: ignore
        else:
            # Convert to string first
            provider_str = str(self.provider).lower()
        try:
            self.provider = ModelProvider(provider_str)
        except ValueError:
            for p in ModelProvider:
                if p.value.lower() == provider_str:
                    self.provider = p
                    break
            else:
                self.provider = ModelProvider.OPENROUTER

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelConfiguration':
        """Create a ModelConfiguration instance from a dictionary."""
        return cls(
            provider=data.get('provider', 'openrouter'),
            model_name=data.get('model_name') or "",
            temperature=data.get('temperature', 0.7),
            max_tokens=data.get('max_tokens'),
            stop_sequences=data.get('stop_sequences'),
            custom_parameters=data.get('custom_parameters'),
            web_search=data.get('web_search', False),
            web_search_context=data.get('web_search_context', 'medium'),
            web_plugin=data.get('web_plugin', False),
            web_max_results=data.get('web_max_results', 5),
            web_search_prompt=data.get('web_search_prompt')
        )

    def get_web_search_options(self):
        """Get web search options for non-plugin search."""
        if self.web_search:
            return {"search_context_size": self.web_search_context}
        return None

    def get_web_plugin_config(self) -> Optional[Dict[str, Any]]:
        """Get web plugin configuration."""
        if self.web_plugin:
            config: Dict[str, Any] = {"max_results": self.web_max_results}
            if self.web_search_prompt:
                config["search_prompt"] = self.web_search_prompt
            return config
        return None
