"""
Pattern processing orchestration.
Handles pattern-based question processing separate from general question flow.
"""

import json
from typing import Optional, Tuple, List, Dict, Any

from askai.core.ai import AIService
from askai.core.messaging import MessageBuilder
from askai.core.patterns import PatternManager
from askai.output import OutputCoordinator


class PatternProcessor:
    """Handles pattern-based question processing."""

    def __init__(self, config: Dict[str, Any], logger, base_path: str):
        """
        Initialize the pattern processor.

        Args:
            config: Application configuration dictionary
            logger: Logger instance
            base_path: Base path for pattern directories
        """
        self.config = config
        self.logger = logger
        self.base_path = base_path

        # Initialize required components
        self.pattern_manager = PatternManager(base_path, config)
        self.message_builder = MessageBuilder(self.pattern_manager, logger)
        self.ai_service = AIService(logger)
        self.output_handler = OutputCoordinator()

    def process_pattern(self, args) -> Optional[Tuple[str, List[str]]]:
        """
        Process a pattern-based request.

        Args:
            args: Parsed command line arguments

        Returns:
            Tuple of (formatted_output, created_files) or None if cancelled
        """
        # Build messages for pattern
        messages, resolved_pattern_id = self.message_builder.build_messages(
            question=None,
            file_input=None,
            pattern_id=args.use_pattern,
            pattern_input=args.pattern_input,
            response_format="rawtext",
            url=None,
            image=None,
            pdf=None,
            image_url=None,
            pdf_url=None,
            model_name=getattr(args, 'model', None)
        )

        # Check if message building was cancelled
        if messages is None:
            self.logger.info(json.dumps({
                "log_message": "Pattern input collection cancelled by user"
            }))
            return None

        self.logger.debug(json.dumps({
            "log_message": "Pattern messages content",
            "messages": messages
        }))

        # Get AI response
        response = self.ai_service.get_ai_response(
            messages=messages,
            model_name=None,
            pattern_id=resolved_pattern_id,
            debug=args.debug,
            pattern_manager=self.pattern_manager,
            enable_url_search=False
        )

        # Process and normalize response
        response = self._normalize_response(response)

        # Process pattern output
        formatted_output, created_files = self.pattern_manager.process_pattern_response(
            resolved_pattern_id,
            response,
            self.output_handler
        )

        # Execute pending operations (commands, file creation)
        additional_files = self.output_handler.execute_pending_operations()
        all_created_files = (created_files or []) + additional_files

        return formatted_output, all_created_files

    def _normalize_response(self, response: Any) -> Any:
        """
        Normalize JSON response if it contains nested results.

        Args:
            response: Raw AI response

        Returns:
            Normalized response
        """
        try:
            if isinstance(response, dict) and 'content' in response:
                content = response['content']
                if isinstance(content, str) and content.strip().startswith('{'):
                    parsed_json = self._try_parse_results_json(content)
                    if parsed_json is not None:
                        return parsed_json
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            self.logger.debug("Error normalizing response: %s", str(e))
        return response

    def _try_parse_results_json(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Try to parse content as JSON with results field.

        Args:
            content: String content to parse

        Returns:
            Parsed JSON dict if successful and contains 'results', None otherwise
        """
        try:
            parsed_json = json.loads(content)
            if isinstance(parsed_json, dict) and 'results' in parsed_json:
                self.logger.debug("Found direct JSON with results in content")
                return parsed_json
        except json.JSONDecodeError:
            self.logger.debug("Content is not valid JSON")
        return None
