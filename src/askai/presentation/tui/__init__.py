"""
TUI (Terminal User Interface) components for AskAI using Textual framework.

This module provides modern, interactive terminal interfaces for pattern management,
chat browsing, and other AskAI features. It gracefully falls back to the traditional
CLI interface when the terminal is incompatible.
"""

import os
import sys

import textual  # noqa: F401 # pylint: disable=unused-import # type: ignore[reportUnusedImport]

# Module-level constants for TUI availability
TEXTUAL_AVAILABLE = True  # Used by other modules to check TUI support


def is_tui_available() -> bool:
    """Check if TUI can be used in the current environment."""

    # Check if we're in a terminal
    if not os.isatty(sys.stdout.fileno()):
        return False

    # Check environment variable override
    if os.environ.get('ASKAI_NO_TUI', '').lower() in ['1', 'true']:
        return False

    # Check terminal capabilities
    term = os.environ.get('TERM', '')
    if term in ['dumb', '']:
        return False

    return True


def get_tui_config() -> dict:
    """Get TUI configuration settings."""
    return {
        'theme': os.environ.get('ASKAI_TUI_THEME', 'dark'),
        'keybindings': {
            'search': ['ctrl+f', '/'],
            'quit': ['ctrl+q', 'q'],
            'select': ['enter'],
            'back': ['escape'],
        },
        'features': {
            'live_preview': True,
            'fuzzy_search': True,
            'syntax_highlighting': True,
        }
    }


# Export public API
__all__ = ['TEXTUAL_AVAILABLE', 'is_tui_available', 'get_tui_config']
