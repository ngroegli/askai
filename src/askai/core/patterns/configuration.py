"""
Configuration classes for defining AI patterns and their behavior.

This module contains the classes needed to configure AI interaction patterns,
including pattern purposes, functionalities, and pattern-specific configurations.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from askai.utils import print_error_or_warnings
from askai.core.ai.models import ModelConfiguration

@dataclass
class PatternPurpose:
    """
    Defines the purpose and intent of an interaction pattern.

    Contains a name and description that explain what the pattern
    is intended to accomplish and what problem it solves.
    """
    name: str
    description: str

    @classmethod
    def from_text(cls, name: str, description: str) -> 'PatternPurpose':
        """Create a PatternPurpose instance from text content."""
        return cls(
            name=name,
            description=description
        )

@dataclass
class PatternFunctionality:
    """
    Describes the specific capabilities of an interaction pattern.

    Contains a list of features that the pattern provides, allowing users
    to understand the full range of its functionality.
    """
    features: List[str]

    @classmethod
    def from_text(cls, content: str) -> 'PatternFunctionality':
        """Create a PatternFunctionality instance from markdown bullet points."""
        # Extract bullet points, removing empty lines and stripping whitespace
        features = [line.strip('* ').strip() for line in content.split('\n')
                   if line.strip().startswith('*')]
        return cls(features=features)

@dataclass
class PatternConfiguration:  # pylint: disable=too-many-instance-attributes
    """
    Complete configuration for an AI interaction pattern.

    Combines purpose, functionality, model configuration, and additional
    parameters to define how the AI should behave for a specific
    interaction pattern. This is the main configuration class that brings
    together all aspects of a pattern definition.
    """
    purpose: PatternPurpose
    functionality: PatternFunctionality
    model: Optional[ModelConfiguration] = None
    format_instructions: Optional[str] = None  # Custom formatting instructions for the AI
    example_conversation: Optional[List[Dict[str, str]]] = None  # Example interactions
    max_context_length: Optional[int] = None  # Maximum context length to maintain

    @classmethod
    def from_components(cls, purpose: PatternPurpose, functionality: PatternFunctionality,
                       *,
                       model_config: Optional[Dict[str, Any]] = None,
                       format_instructions: Optional[str] = None,
                       example_conversation: Optional[List[Dict[str, str]]] = None,
                       max_context_length: Optional[int] = None) -> 'PatternConfiguration':
        """Create a PatternConfiguration instance from its components."""
        model = None
        if model_config and 'model' in model_config:
            try:
                model = ModelConfiguration.from_dict(model_config['model'])
            except Exception as e:
                print_error_or_warnings(f"Error creating model configuration: {str(e)}")

        return cls(
            purpose=purpose,
            functionality=functionality,
            model=model,
            format_instructions=format_instructions,
            example_conversation=example_conversation,
            max_context_length=max_context_length
        )
