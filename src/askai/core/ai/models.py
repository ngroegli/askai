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

    Note: This is a pure data class. Default values should come from:
    1. Config file (config.yml) - user's global preferences
    2. Pattern file (pattern-specific overrides)
    3. Command-line arguments (user overrides)

    Use ModelConfigurationBuilder to create instances with proper defaults.
    """
    provider: Union[str, ModelProvider]
    model_name: str
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    custom_parameters: Optional[Dict[str, Any]] = None
    web_search: Optional[bool] = None
    web_search_context: Optional[str] = None  # low, medium, high
    web_plugin: Optional[bool] = None
    web_max_results: Optional[int] = None
    web_search_prompt: Optional[str] = None

    def __post_init__(self):
        """Convert provider to ModelProvider enum if it's a string."""
        if hasattr(self.provider, 'value'):
            provider_str = self.provider.value.lower()  # type: ignore
        else:
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
        """
        Create a ModelConfiguration instance from a dictionary.

        This method creates an instance with values from the dictionary,
        without applying any defaults. Use ModelConfigurationBuilder for
        proper default handling from config file and pattern overrides.

        Args:
            data: Dictionary containing model configuration values

        Returns:
            ModelConfiguration instance with values from dictionary
        """
        return cls(
            provider=data.get('provider', 'openrouter'),
            model_name=data.get('model_name', ''),
            temperature=data.get('temperature'),
            max_tokens=data.get('max_tokens'),
            stop_sequences=data.get('stop_sequences'),
            custom_parameters=data.get('custom_parameters'),
            web_search=data.get('web_search'),
            web_search_context=data.get('web_search_context'),
            web_plugin=data.get('web_plugin'),
            web_max_results=data.get('web_max_results'),
            web_search_prompt=data.get('web_search_prompt')
        )

    def get_web_search_options(self) -> Optional[Dict[str, str]]:
        """Get web search options for non-plugin search."""
        if self.web_search:
            return {"search_context_size": self.web_search_context or "medium"}
        return None

    def get_web_plugin_config(self) -> Optional[Dict[str, Any]]:
        """Get web plugin configuration."""
        if self.web_plugin:
            config: Dict[str, Any] = {"max_results": self.web_max_results or 5}
            if self.web_search_prompt:
                config["search_prompt"] = self.web_search_prompt
            return config
        return None


class ModelConfigurationBuilder:
    """
    Builder for creating ModelConfiguration instances with proper default handling.

    This builder applies defaults in the correct order:
    1. System defaults (hardcoded fallbacks)
    2. Config file defaults (user's global preferences)
    3. Pattern defaults (pattern-specific settings)
    4. User overrides (command-line arguments)

    Example:
        config = load_config()
        builder = ModelConfigurationBuilder(config)
        builder.from_config_defaults()
        builder.from_pattern(pattern_config)
        model_config = builder.build('openrouter', 'anthropic/claude-3.5-sonnet')
    """

    # System-level fallback defaults (used when nothing else is specified)
    SYSTEM_DEFAULTS = {
        'temperature': 0.7,
        'max_tokens': None,
        'web_search': False,
        'web_search_context': 'medium',
        'web_plugin': False,
        'web_max_results': 5,
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the builder with config file defaults.

        Args:
            config: Configuration dictionary from config.yml
        """
        self.config = config or {}
        self._values: Dict[str, Any] = {}

    def from_config_defaults(self) -> 'ModelConfigurationBuilder':
        """
        Apply defaults from config file.

        Returns:
            Self for method chaining
        """
        # Get web search config
        web_search_config = self.config.get('web_search', {})

        self._values.update({
            'temperature': self.config.get('temperature', self.SYSTEM_DEFAULTS['temperature']),
            'max_tokens': self.config.get('max_tokens', self.SYSTEM_DEFAULTS['max_tokens']),
            'web_search': web_search_config.get('enabled', self.SYSTEM_DEFAULTS['web_search']),
            'web_search_context': self.SYSTEM_DEFAULTS['web_search_context'],
            'web_plugin': web_search_config.get('method') == 'plugin',
            'web_max_results': web_search_config.get('max_results', self.SYSTEM_DEFAULTS['web_max_results']),
        })
        return self

    def from_pattern(self, pattern_config: Optional[Dict[str, Any]]) -> 'ModelConfigurationBuilder':
        """
        Apply overrides from pattern configuration.

        Args:
            pattern_config: Pattern's model_config section from pattern YAML

        Returns:
            Self for method chaining
        """
        if not pattern_config:
            return self

        # Only override values that are explicitly set in the pattern
        if 'temperature' in pattern_config:
            self._values['temperature'] = pattern_config['temperature']
        if 'max_tokens' in pattern_config:
            self._values['max_tokens'] = pattern_config['max_tokens']
        if 'stop_sequences' in pattern_config:
            self._values['stop_sequences'] = pattern_config['stop_sequences']
        if 'custom_parameters' in pattern_config:
            self._values['custom_parameters'] = pattern_config['custom_parameters']
        if 'web_search' in pattern_config:
            self._values['web_search'] = pattern_config['web_search']
        if 'web_search_context' in pattern_config:
            self._values['web_search_context'] = pattern_config['web_search_context']
        if 'web_plugin' in pattern_config:
            self._values['web_plugin'] = pattern_config['web_plugin']
        if 'web_max_results' in pattern_config:
            self._values['web_max_results'] = pattern_config['web_max_results']
        if 'web_search_prompt' in pattern_config:
            self._values['web_search_prompt'] = pattern_config['web_search_prompt']

        return self

    def from_user_args(self, **kwargs: Any) -> 'ModelConfigurationBuilder':
        """
        Apply overrides from user arguments (CLI or API).

        Args:
            **kwargs: Keyword arguments with user overrides
                (temperature, max_tokens, web_search, etc.)

        Returns:
            Self for method chaining
        """
        for key, value in kwargs.items():
            if value is not None and key in ['temperature', 'max_tokens', 'web_search',
                                              'web_search_context', 'web_plugin',
                                              'web_max_results', 'web_search_prompt',
                                              'stop_sequences', 'custom_parameters']:
                self._values[key] = value

        return self

    def build(self, provider: Union[str, ModelProvider], model_name: str) -> ModelConfiguration:
        """
        Build the final ModelConfiguration instance.

        Args:
            provider: The AI provider (e.g., 'openrouter', 'anthropic')
            model_name: The model name/identifier

        Returns:
            Fully configured ModelConfiguration instance
        """
        return ModelConfiguration(
            provider=provider,
            model_name=model_name,
            temperature=self._values.get('temperature'),
            max_tokens=self._values.get('max_tokens'),
            stop_sequences=self._values.get('stop_sequences'),
            custom_parameters=self._values.get('custom_parameters'),
            web_search=self._values.get('web_search'),
            web_search_context=self._values.get('web_search_context'),
            web_plugin=self._values.get('web_plugin'),
            web_max_results=self._values.get('web_max_results'),
            web_search_prompt=self._values.get('web_search_prompt'),
        )
