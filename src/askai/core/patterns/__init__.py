"""
Patterns package for Ask AI.

This package implements the pattern system for configuring AI prompts,
managing inputs and outputs, and specialized use cases through predefined templates.
"""
from .configuration import (
    PatternConfiguration,
    PatternPurpose,
    PatternFunctionality
)
from .inputs import PatternInput, InputType
from .outputs import PatternOutput
from .manager import PatternManager
from .processor import PatternProcessor

__all__ = [
    'PatternConfiguration',
    'PatternPurpose',
    'PatternFunctionality',
    'PatternInput',
    'InputType',
    'PatternOutput',
    'PatternManager',
    'PatternProcessor'
]
