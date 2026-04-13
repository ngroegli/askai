"""
Pattern display utilities for Ask AI.

This module provides functions for displaying pattern information and
presenting interactive pattern selection menus to the user.
"""

from typing import List, Optional, Dict, Any


def display_pattern(pattern_manager, pattern_id: str) -> None:
    """Display the content of a pattern file.

    Args:
        pattern_manager: PatternManager instance to fetch pattern data from
        pattern_id: The pattern identifier
    """
    content = pattern_manager.get_pattern_content(pattern_id)
    if content is None:
        raise ValueError(f"Pattern '{pattern_id}' does not exist")

    # Display pattern metadata in a user-friendly format
    print("\n" + "=" * 70)
    # Keep a clear header and also show an explicit Name field for compatibility
    print(f"Pattern: {content['configuration'].purpose.name}")
    # Some consumers/tests expect an explicit 'Name:' label — include it
    print(f"Name: {content['configuration'].purpose.name}")
    print("=" * 70)

    # Get and display tags
    tags = pattern_manager.get_tags_for_pattern(pattern_id)
    if tags:
        print(f"\nTags: {', '.join(tags)}")

    print(f"\nID: {pattern_id}")
    print(f"Source: {content['source']}")

    print("\nDescription:")
    print(content['configuration'].purpose.description)

    # Display inputs
    if content['inputs']:
        print("\nInputs:")
        for inp in content['inputs']:
            required_str = " (required)" if inp.required else " (optional)"
            print(f"  • {inp.name}{required_str}")
            print(f"    Type: {inp.input_type.value}")
            print(f"    Description: {inp.description}")

    # Display outputs
    if content['outputs']:
        print("\nOutputs:")
        for out in content['outputs']:
            print(f"  • {out.name}")
            print(f"    Type: {out.output_type.value}")
            print(f"    Description: {out.description}")

    # Display model configuration
    print("\nModel Configuration:")
    print(f"  Provider: {content['configuration'].model.provider.value}")
    print(f"  Model: {content['configuration'].model.model_name}")
    print(f"  Temperature: {content['configuration'].model.temperature}")
    print(f"  Max Tokens: {content['configuration'].model.max_tokens}")

    print("\n" + "=" * 70)


def select_pattern(
    pattern_manager,
    tags: Optional[List[str]] = None
) -> Optional[str]:
    """Display an interactive pattern selection menu.

    Args:
        pattern_manager: PatternManager instance to fetch pattern list from
        tags: Optional list of tags to filter patterns by

    Returns:
        Optional[str]: Selected pattern ID or None if selection cancelled
    """
    patterns: List[Dict[str, Any]] = pattern_manager.list_patterns(tags=tags)

    if not patterns:
        if tags:
            print(f"No pattern files found matching tags: {', '.join(tags)}")
        else:
            print("No pattern files found.")
        return None

    if tags:
        print(f"\nPatterns matching tags: {', '.join(tags)}")
    else:
        print("\nAvailable patterns:")
    print("-" * 70)

    # Display patterns with index
    for i, pattern in enumerate(patterns, 1):
        source_indicator = "🔒" if pattern.get('is_private', False) else "📦"
        print(f"{i}. {pattern['name']} {source_indicator}")
        print(f"   ID: {pattern['pattern_id']} ({pattern.get('source', 'built-in')})")
        if pattern.get('tags'):
            print(f"   Tags: {', '.join(pattern['tags'])}")
        print("-" * 70)

    print("\nOptions:")
    print(f"1-{len(patterns)}. Select pattern")
    print("q. Quit")
    print("\n🔒 = Private pattern, 📦 = Built-in pattern")

    while True:
        choice = input(f"\nEnter your choice (1-{len(patterns)} or q): ").lower()

        if choice == 'q':
            return None

        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(patterns):
                return patterns[choice_num - 1]['pattern_id']
            print(f"Please enter a number between 1 and {len(patterns)}")
        except ValueError:
            print("Please enter a valid number or 'q' to quit")
