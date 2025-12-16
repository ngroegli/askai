"""
Main entry point for the AskAI CLI application.
Orchestrates the different components to provide AI assistance via command line.
"""

# Standard library imports
import json
import os
import sys

# Add the src directory to the path when running the script directly
# This allows the script to work both when installed as a package and when run directly
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(script_dir)  # Go up from src/askai to src

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Local application imports - grouped by package
# pylint: disable=wrong-import-position
from askai.core.chat import ChatManager
from askai.core.patterns import PatternManager, PatternProcessor
from askai.core.questions import QuestionProcessor

from askai.utils import load_config, setup_logger, print_error_or_warnings

from askai.presentation.cli import CommandHandler
from askai.presentation.cli.parser import CLIParser
from askai.presentation.tui.apps.tabbed_tui_app import run_tabbed_tui

def display_help_fast():
    """
    Display help information with minimal imports.
    This function is optimized to avoid unnecessary imports when only help is needed.
    """
    cli_parser = CLIParser()
    cli_parser.parse_arguments()  # This will display help and exit

def main():  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    """Main entry point for the AskAI CLI application."""
    # Check if this is a help request (before any heavy initialization)
    # Use most efficient path for help commands
    if '-h' in sys.argv or '--help' in sys.argv:
        display_help_fast()
        return  # Exit after displaying help

    # Handle no parameters case - check default_mode config
    if len(sys.argv) == 1:
        try:
            config = load_config()
            interface_config = config.get('interface', {})
            default_mode = interface_config.get('default_mode', 'cli')

            if default_mode == 'tui':
                # Try to launch TUI mode
                try:
                    # Initialize minimal components for TUI
                    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    logger = setup_logger(config, False)

                    pattern_manager = PatternManager(base_path, config)
                    chat_manager = ChatManager(config, logger)
                    question_processor = QuestionProcessor(config, logger, base_path)

                    # Launch TUI
                    run_tabbed_tui(
                        pattern_manager=pattern_manager,
                        chat_manager=chat_manager,
                        question_processor=question_processor
                    )
                    return
                except Exception as e:
                    print(f"TUI mode failed: {e}. Falling back to CLI help.")
        except Exception:
            # If config loading fails, fall back to help
            pass

        # Show CLI help as fallback or if default_mode is cli
        display_help_fast()
        return

    # For non-help commands, initialize CLI parser first
    cli_parser = CLIParser()
    args = cli_parser.parse_arguments()

    # Now load configuration (needed for most commands)
    config = load_config()
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Setup logging
    logger = setup_logger(config, args.debug)
    logger.info(json.dumps({"log_message": "AskAI started and arguments parsed"}))

    # Initialize managers for command handling (lightweight operations)
    pattern_manager = PatternManager(base_path, config)
    chat_manager = ChatManager(config, logger)
    command_handler = CommandHandler(pattern_manager, chat_manager, logger)

    # Handle commands in priority order - interactive mode first, then patterns
    if command_handler.handle_interactive_mode(args):
        sys.exit(0)
    if command_handler.handle_pattern_commands(args):
        sys.exit(0)
    if command_handler.handle_chat_commands(args):
        sys.exit(0)
    if command_handler.handle_openrouter_commands(args):
        sys.exit(0)
    if command_handler.handle_config_commands(args):
        sys.exit(0)

    # Validate arguments
    cli_parser.validate_arguments(args, logger)

    # Determine which mode we're operating in: pattern mode or chat/question mode
    using_pattern = args.use_pattern is not None

    # Check if chat functionality is being used
    using_chat = args.persistent_chat is not None or args.view_chat is not None

    # Warn if trying to use both pattern and chat functionality together
    if using_pattern and using_chat:
        logger.warning(json.dumps({
            "log_message": "User attempted to use chat functionality with patterns"
        }))
        print_error_or_warnings(
            "Patterns and chat features are not compatible. Chat options (-pc, -vc) will be ignored.",
            is_warning=True, exit_on_error=False
        )
        # Force chat features to be disabled
        args.persistent_chat = None
        args.view_chat = None

    # Process based on mode
    if using_pattern:
        # === PATTERN MODE ===
        # Use the dedicated pattern processor
        pattern_processor = PatternProcessor(config, logger, base_path)
        formatted_output, created_files = pattern_processor.process_pattern(args)
    else:
        # === CHAT/QUESTION MODE ===
        # Use the dedicated question processor
        question_processor = QuestionProcessor(config, logger, base_path)
        response_obj = question_processor.process_question(args)

        # The question processor returns a QuestionResponse object
        formatted_output = response_obj.content
        created_files = response_obj.created_files

    # Print the formatted output for both pattern and non-pattern responses
    print(formatted_output)

    # Log created files
    if created_files:
        print(f"\nCreated output files: {', '.join(created_files)}")
        logger.info("Created output files: %s", ', '.join(created_files))


if __name__ == "__main__":
    main()
