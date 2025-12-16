"""
AI interaction and model configuration handling.
Manages AI response generation and model configuration logic.
"""

import json
import threading
from typing import Any, Dict, List, Optional
from askai.utils import tqdm_spinner, load_config
from .models import ModelConfiguration, ModelProvider, ModelConfigurationBuilder
from .openrouter import OpenRouterClient



class AIService:
    """Handles AI interaction and model configuration."""

    def __init__(self, logger):
        self.logger = logger

    def get_model_configuration(
        self,
        model_name: Optional[str],
        config: Dict[str, Any],
        pattern_data: Optional[Dict[str, Any]] = None
    ) -> ModelConfiguration:
        """Get model configuration based on priority: Config > Pattern > CLI args.

        Uses ModelConfigurationBuilder to properly apply defaults from:
        1. Config file (user's global preferences)
        2. Pattern configuration (pattern-specific overrides)
        3. CLI arguments (user overrides)

        Args:
            model_name: Optional model name from CLI
            config: Global configuration
            pattern_data: Optional pattern data containing pattern-specific configuration

        Returns:
            The configured ModelConfiguration instance
        """
        # Start with config file defaults
        builder = ModelConfigurationBuilder(config).from_config_defaults()

        # Determine provider and model_name
        provider = ModelProvider.OPENROUTER
        final_model_name = config.get("default_model", "")

        # Priority 1: Pattern configuration
        if pattern_data:
            pattern_config = pattern_data.get('configuration')

            if pattern_config:
                # Check if we have a pre-built ModelConfiguration object
                if hasattr(pattern_config, 'model') and pattern_config.model:
                    model_config = pattern_config.model
                    self.logger.info(json.dumps({
                        "log_message": "Using model configuration from pattern",
                        "model_name": model_config.model_name,
                        "provider": model_config.provider.value if model_config.provider else 'openrouter'
                    }))
                    return model_config

                # Handle dictionary format with pattern overrides
                if isinstance(pattern_config, dict):
                    if 'model' in pattern_config:
                        model_data = pattern_config['model']
                        if isinstance(model_data, dict):
                            # Apply pattern's model config
                            builder.from_pattern(model_data)
                            if 'provider' in model_data:
                                provider = model_data['provider']
                            if 'model_name' in model_data:
                                final_model_name = model_data['model_name']
                            self.logger.info("Applied model configuration from pattern dict")

        # Priority 2: Explicit model name from CLI
        if model_name:
            final_model_name = model_name
            self.logger.info(json.dumps({
                "log_message": "Using explicit model from CLI",
                "model": model_name
            }))

        # Build the final configuration
        model_config = builder.build(provider=provider, model_name=final_model_name)

        # Get provider value for logging
        provider_value = (
            model_config.provider.value
            if isinstance(model_config.provider, ModelProvider)
            else str(model_config.provider)
        )

        self.logger.info(json.dumps({
            "log_message": "Built model configuration",
            "model_name": model_config.model_name,
            "provider": provider_value,
            "temperature": model_config.temperature,
            "max_tokens": model_config.max_tokens,
            "web_search": model_config.web_search,
            "web_plugin": model_config.web_plugin
        }))

        return model_config

    def get_ai_response(
        self,
        messages: List[Dict[str, Any]],
        model_name: Optional[str] = None,
        *,
        pattern_id: Optional[str] = None,
        debug: bool = False,
        pattern_manager: Any = None,
        enable_url_search: bool = False
    ) -> Dict[str, Any]:
        # pylint: disable=too-many-locals
        """Get response from AI model with progress spinner.

        Args:
            messages: List of message dictionaries
            model_name: Optional model name to override default
            pattern_id: Optional pattern ID to get pattern-specific configuration
            debug: Whether to enable debug mode
            pattern_manager: PatternManager instance for accessing pattern data
            enable_url_search: Whether to enable web search for URL analysis

        Returns:
            Response dictionary from the AI model
        """
        stop_spinner = threading.Event()
        spinner = threading.Thread(target=tqdm_spinner, args=(stop_spinner,))
        spinner.start()

        try:
            self.logger.info(json.dumps({"log_message": "Messages sending to ai"}))

            # Get configuration from the proper source
            config = load_config()
            pattern_data = None
            if pattern_id and pattern_manager is not None:
                pattern_data = pattern_manager.get_pattern_content(pattern_id)

                # The format instructions are now generated dynamically from output definitions
                # and consistently handled by the output handler, so no special validators are needed here

            model_config = self.get_model_configuration(model_name, config, pattern_data)

            # Determine web search configuration
            web_search_options = None
            web_plugin_config = None

            # Priority 1: System-specific web search configuration
            if hasattr(model_config, 'get_web_search_options'):
                web_search_options = model_config.get_web_search_options()

            if hasattr(model_config, 'get_web_plugin_config'):
                web_plugin_config = model_config.get_web_plugin_config()

            # Priority 2: Global configuration or URL search override
            if web_search_options is None and web_plugin_config is None:
                web_config = config.get('web_search', {})

                # Enable web search only when explicitly requested for URL input
                # Global 'enabled' setting just configures defaults but doesn't auto-enable
                if enable_url_search:
                    if web_config.get('method', 'plugin') == 'plugin':
                        web_plugin_config = {
                            "max_results": web_config.get('max_results', 5)
                        }
                        if web_config.get('search_prompt'):
                            web_plugin_config["search_prompt"] = web_config['search_prompt']
                    else:
                        web_search_options = {
                            "search_context_size": web_config.get('context_size', 'medium')
                        }

            # Create OpenRouter client and get response
            openrouter_client = OpenRouterClient(config=config, logger=self.logger)
            response = openrouter_client.request_completion(
                messages=messages,
                model_config=model_config,
                debug=debug,
                web_search_options=web_search_options,
                web_plugin_config=web_plugin_config
            )

            self.logger.debug(json.dumps({
                "log_message": "Response from ai",
                "response": str(response)
            }))
            self.logger.info(json.dumps({"log_message": "Response received from ai"}))
            return response
        finally:
            stop_spinner.set()
            spinner.join()
