"""
Configuration module for Ask AI application.
Handles loading of user configuration from YAML files.
Supports proper ~/.askai directory structure with initialization and setup wizard.
"""

# Standard library imports
import os
import sys
import tempfile
from typing import Optional, Dict, Any

# Third-party imports
import yaml

# ============================================================================
# CONSTANTS
# ============================================================================

# Boolean response patterns
TRUE_VALUES = {'y', 'yes', 'true', '1'}
FALSE_VALUES = {'n', 'no', 'false', '0'}

# Placeholder patterns that indicate required fields
PLACEHOLDER_PATTERNS = [
    'your_api_key_here',
    'your_key_here',
    'your_url_here',
    'your-api-key',
    'enter_',
    'add_your_',
    'replace_this',
]

# Default configuration values
DEFAULT_CONFIG = {
    'log_path': '~/.askai/logs/askai.log',
    'chat': {'storage_path': '~/.askai/chats'},
    'patterns': {'private_patterns_path': ''},
    'interface': {
        'default_mode': 'cli',
        'tui_features': {
            'enabled': True,
            'auto_fallback': True,
            'theme': 'dark',
            'animations': True,
            'preview_pane': True,
            'search_highlight': True
        }
    }
}

# Test configuration values
TEST_DUMMY_VALUES = {'https://test.api.com', 'test-key', 'test-model'}

# Configuration paths
ASKAI_DIR = os.path.expanduser("~/.askai")
CONFIG_PATH = os.path.join(ASKAI_DIR, "config.yml")
CHATS_DIR = os.path.join(ASKAI_DIR, "chats")
LOGS_DIR = os.path.join(ASKAI_DIR, "logs")

# Test paths
TEST_DIR = os.path.join(ASKAI_DIR, "test")
TEST_CONFIG_PATH = os.path.join(TEST_DIR, "config.yml")
TEST_CHATS_DIR = os.path.join(TEST_DIR, "chats")
TEST_LOGS_DIR = os.path.join(TEST_DIR, "logs")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _get_boolean_input(prompt: str, default: bool) -> bool:
    """
    Get boolean input from user with validation.

    Args:
        prompt: The question to display to the user
        default: The default boolean value

    Returns:
        The user's boolean choice
    """
    default_str = 'y' if default else 'n'
    full_prompt = f"{prompt} (y/n, default: {default_str}): "

    while True:
        user_input = input(full_prompt).strip().lower()
        if not user_input:
            return default
        if user_input in TRUE_VALUES:
            return True
        if user_input in FALSE_VALUES:
            return False
        print("Please enter y/n")

def _get_numeric_input(prompt: str, default: Any, value_type: type) -> Any:
    """
    Get numeric input from user with validation.

    Args:
        prompt: The question to display to the user
        default: The default numeric value
        value_type: The type to convert to (int or float)

    Returns:
        The user's numeric input or default
    """
    full_prompt = f"{prompt} (default: {default}): "

    while True:
        user_input = input(full_prompt).strip()
        if not user_input:
            return default
        try:
            return value_type(user_input)
        except ValueError:
            print("Please enter a valid number")

def _get_string_input(prompt: str, default: Optional[str] = None,
                      required: bool = False) -> Optional[str]:
    """
    Get string input from user with optional requirement.

    Args:
        prompt: The question to display to the user
        default: The default string value (None if required)
        required: Whether the input is required

    Returns:
        The user's string input, default, or None
    """
    if required:
        full_prompt = f"{prompt} (required): "
        while True:
            user_input = input(full_prompt).strip()
            if user_input:
                return user_input
            print("This setting is required. Please provide a value.")
    else:
        if default is not None:
            full_prompt = f"{prompt} (default: '{default}'): "
        else:
            full_prompt = f"{prompt}: "
        user_input = input(full_prompt).strip()
        return user_input if user_input else default

# ============================================================================
# ENVIRONMENT DETECTION
# ============================================================================

def is_test_environment() -> bool:
    """
    Check if we're running in a test environment.

    Returns:
        True if ASKAI_TESTING environment variable is set
    """
    return os.environ.get('ASKAI_TESTING', '').lower() in TRUE_VALUES

# ============================================================================
# DIRECTORY MANAGEMENT
# ============================================================================

def create_directory_structure(test_mode: bool = False) -> bool:
    """
    Create the ~/.askai directory structure.

    Args:
        test_mode: If True, create test subdirectories instead

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create main directories
        os.makedirs(ASKAI_DIR, exist_ok=True)
        os.makedirs(CHATS_DIR, exist_ok=True)
        os.makedirs(LOGS_DIR, exist_ok=True)

        if test_mode:
            # Create test directories
            os.makedirs(TEST_DIR, exist_ok=True)
            os.makedirs(TEST_CHATS_DIR, exist_ok=True)
            os.makedirs(TEST_LOGS_DIR, exist_ok=True)

        return True
    except Exception as e:
        print(f"Error creating directory structure: {str(e)}")
        return False

# ============================================================================
# CONFIGURATION TEMPLATE
# ============================================================================

def load_config_template() -> Optional[Dict[str, Any]]:
    """
    Load the config template from config/config_example.yml

    Returns:
        The template configuration with metadata, or None on error
    """
    try:
        # Get the path to config_example.yml relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        template_path = os.path.join(project_root, "config", "config_example.yml")

        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Config template not found at {template_path}")

        with open(template_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing config template: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error loading config template: {e}")
        return None

def is_placeholder_value(value: Any) -> bool:
    """
    Determine if a value is a placeholder that needs user input.

    Args:
        value: The value to check

    Returns:
        True if it's a placeholder, False if it's a default
    """
    if isinstance(value, str):
        value_lower = value.lower()
        return any(pattern in value_lower for pattern in PLACEHOLDER_PATTERNS)

    return False

# ============================================================================
# SETUP WIZARD
# ============================================================================

def get_user_input_for_setting(key: str, value: Any, path: str = "",
                               depth: int = 0) -> Any:
    """
    Get user input for a specific configuration setting.

    Args:
        key: The configuration key
        value: The current/default value
        path: The nested path to this setting
        depth: The nesting depth

    Returns:
        The user's input or the default value
    """
    indent = "  " * depth
    full_key = f"{path}.{key}" if path else key

    # Handle different types of values
    if isinstance(value, dict):
        print(f"{indent}[{key.upper()} SETTINGS]")
        result = {}
        for sub_key, sub_value in value.items():
            result[sub_key] = get_user_input_for_setting(sub_key, sub_value, full_key, depth + 1)
        return result

    if isinstance(value, list):
        # For lists, just return the default for now
        return value

    if value is None:
        # Handle null values
        return _get_string_input(f"{indent}{key}", default=None, required=False)

    if isinstance(value, bool):
        # Handle boolean values
        return _get_boolean_input(f"{indent}{key}", default=value)

    if isinstance(value, (int, float)):
        # Handle numeric values
        return _get_numeric_input(f"{indent}{key}", default=value, value_type=type(value))

    # Handle string values
    is_required = is_placeholder_value(value)
    return _get_string_input(f"{indent}{key}", default=None if is_required else value,
                           required=is_required)

def _apply_default_paths(template: Dict[str, Any]) -> None:
    """
    Apply default paths to configuration template.

    Args:
        template: The configuration template to modify in-place
    """
    if 'log_path' in template:
        template['log_path'] = DEFAULT_CONFIG['log_path']
    if 'chat' in template and 'storage_path' in template['chat']:
        template['chat']['storage_path'] = DEFAULT_CONFIG['chat']['storage_path']
    if 'patterns' in template and 'private_patterns_path' in template['patterns']:
        if not template['patterns']['private_patterns_path']:
            template['patterns']['private_patterns_path'] = DEFAULT_CONFIG['patterns']['private_patterns_path']

def _ensure_interface_config(template: Dict[str, Any]) -> None:
    """
    Ensure interface configuration exists with sensible defaults.

    Args:
        template: The configuration template to modify in-place
    """
    if 'interface' not in template:
        template['interface'] = DEFAULT_CONFIG['interface']

def run_dynamic_setup_wizard() -> Optional[Dict[str, Any]]:
    """
    Run a dynamic setup wizard based on the config template.

    Returns:
        The created configuration, or None on error
    """
    print("\n" + "="*60)
    print("           Welcome to AskAI Setup Wizard")
    print("="*60)
    print("\nThis wizard will help you set up your AskAI configuration.")
    print("You can change these settings later by editing ~/.askai/config.yml")
    print("\nPress Enter to accept default values, or type a new value to override.")
    print("Required fields (placeholders) must be filled in.\n")

    # Load the configuration template
    template = load_config_template()
    if not template:
        print("Error: Could not load configuration template.")
        print("Please ensure config/config_example.yml exists in the project.")
        return None

    # Update template with defaults
    _apply_default_paths(template)
    _ensure_interface_config(template)

    # Process the configuration interactively
    config = {}

    # Group settings for better organization
    core_settings = ['api_key', 'default_model', 'default_vision_model', 'default_pdf_model', 'base_url']

    print("CORE SETTINGS:")
    print("-" * 15)
    for key in core_settings:
        if key in template:
            config[key] = get_user_input_for_setting(key, template[key])

    print("\nOTHER SETTINGS:")
    print("-" * 15)
    for key, value in template.items():
        if key not in core_settings:
            config[key] = get_user_input_for_setting(key, value)

    print("\n" + "="*60)
    print("           Setup Complete!")
    print("="*60)
    print(f"Configuration will be saved to: {CONFIG_PATH}")
    print("You can edit this file later to modify settings.")

    return config

# ============================================================================
# TEST CONFIGURATION
# ============================================================================

def create_test_config_from_production() -> bool:
    """
    Create a test configuration file by copying the production config.
    Modifies paths to use test-specific directories to avoid conflicts.

    Returns:
        True if config was created successfully, False otherwise
    """
    try:
        if not os.path.exists(CONFIG_PATH):
            print(f"Error: Production config file not found at {CONFIG_PATH}")
            return False

        # Ensure test directory exists
        create_directory_structure(test_mode=True)

        # Load and modify the production config
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # Modify paths for testing
        if 'log_path' in config:
            config['log_path'] = "~/.askai/test/logs/askai_test.log"

        if 'patterns' in config and 'private_patterns_path' in config['patterns']:
            # For testing, remove private patterns path to avoid creating non-existent directories
            # Private patterns are optional, so tests can run without them
            config['patterns']['private_patterns_path'] = None

        if 'chat' in config and 'storage_path' in config['chat']:
            config['chat']['storage_path'] = "~/.askai/test/chats"

        # Write the modified test config
        with open(TEST_CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)

        print(f"Test configuration created at {TEST_CONFIG_PATH}")
        print("Modified settings for testing:")
        print(f"  - Log path: {config.get('log_path', 'unchanged')}")
        print(f"  - Chat storage: {config['chat']['storage_path']}")
        print("  - Private patterns: disabled for testing")

        return True

    except yaml.YAMLError as e:
        print(f"Error parsing config file: {e}")
        return False
    except IOError as e:
        print(f"Error reading/writing config file: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error creating test config: {e}")
        return False

# ============================================================================
# SETUP ORCHESTRATION
# ============================================================================

def ensure_askai_setup() -> bool:
    """
    Ensure that AskAI is properly set up. Run setup wizard if needed.

    Returns:
        True if setup is complete, False if user chose to exit
    """
    # Safety check: In test environment, always return True immediately
    if is_test_environment():
        return True

    # Ensure directory structure
    if not _ensure_directory_structure():
        return False

    # Ensure configuration file
    return _ensure_configuration_file()

def _ensure_directory_structure() -> bool:
    """
    Ensure the AskAI directory structure exists.

    Returns:
        True if structure exists or was created, False if user declined
    """
    if os.path.exists(ASKAI_DIR):
        return True

    print("\n" + "="*60)
    print("           AskAI First Time Setup")
    print("="*60)
    print(f"\nAskAI needs to create its directory structure at: {ASKAI_DIR}")
    print("This will include directories for configuration, chats, and logs.")

    if _get_boolean_input("\nWould you like to create the AskAI directory structure?", default=True):
        if not create_directory_structure():
            print("Failed to create directory structure.")
            return False
        return True

    print("AskAI requires the directory structure to function. Exiting.")
    return False

def _ensure_configuration_file() -> bool:
    """
    Ensure the configuration file exists.

    Returns:
        True if config exists or was created, False otherwise
    """
    config_path = TEST_CONFIG_PATH if is_test_environment() else CONFIG_PATH

    if os.path.exists(config_path):
        return True

    # Handle test environment
    if is_test_environment():
        return _setup_test_configuration()

    # Handle production environment
    return _setup_production_configuration()

def _setup_test_configuration() -> bool:
    """
    Set up configuration in test environment.

    Returns:
        True if test config was created, False otherwise
    """
    if os.path.exists(CONFIG_PATH):
        print("Test configuration not found. Creating automatically from production config...")
        create_directory_structure(test_mode=True)
        return create_test_config_from_production()

    print("Production configuration not found. Please run setup in production mode first.")
    return False

def _setup_production_configuration() -> bool:
    """
    Set up configuration in production environment.

    Returns:
        True if config was created and saved, False otherwise
    """
    config = run_dynamic_setup_wizard()

    if not config:
        print("Setup wizard failed. Cannot continue without configuration.")
        return False

    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
        print("Configuration saved successfully!")
        return True
    except IOError as e:
        print(f"Error saving configuration: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error saving configuration: {e}")
        return False

# ============================================================================
# CONFIGURATION LOADING
# ============================================================================

def get_config_path() -> str:
    """
    Get the appropriate configuration file path based on environment.

    Returns:
        Path to the configuration file to use
    """
    return TEST_CONFIG_PATH if is_test_environment() else CONFIG_PATH

def _load_test_config() -> Optional[Dict[str, Any]]:
    """
    Load test configuration with fallback to production config.

    Returns:
        Configuration dictionary or None if not available
    """
    # First, try to load test configuration if it exists
    if os.path.exists(TEST_CONFIG_PATH):
        try:
            with open(TEST_CONFIG_PATH, "r", encoding="utf-8") as f:
                test_config = yaml.safe_load(f)
                # Check if this is a dummy config
                if (test_config.get('base_url') not in TEST_DUMMY_VALUES and
                    test_config.get('api_key') not in TEST_DUMMY_VALUES):
                    return test_config
        except Exception as e:
            print(f"Warning: Could not load test config: {e}")

    # If test config doesn't exist or has dummy values, check for production config
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                prod_config = yaml.safe_load(f)
                # Use production config but modify paths for testing
                temp_dir = tempfile.gettempdir()
                prod_config['enable_logging'] = False
                prod_config['log_path'] = os.path.join(temp_dir, 'test.log')
                prod_config['log_level'] = 'ERROR'
                if 'chat' in prod_config:
                    prod_config['chat']['storage_path'] = os.path.join(temp_dir, 'test-chats')
                if 'interface' in prod_config and 'tui_features' in prod_config['interface']:
                    prod_config['interface']['tui_features']['enabled'] = False
                    prod_config['interface']['tui_features']['animations'] = False
                return prod_config
        except Exception as e:
            print(f"Warning: Could not load production config for testing: {e}")

    return None

def _get_minimal_test_config() -> Dict[str, Any]:
    """
    Get minimal test configuration as last resort.

    Returns:
        Minimal configuration dictionary for testing
    """
    print("Warning: Using minimal test configuration. Integration tests may fail.")
    temp_dir = tempfile.gettempdir()
    return {
        'api_key': 'test-key',
        'default_model': 'test-model',
        'base_url': 'https://test.api.com',
        'enable_logging': False,
        'log_path': os.path.join(temp_dir, 'test.log'),
        'log_level': 'ERROR',
        'patterns': {'private_patterns_path': ''},
        'web_search': {
            'enabled': False,
            'method': 'plugin',
            'max_results': 5
        },
        'chat': {
            'storage_path': os.path.join(temp_dir, 'test-chats'),
            'max_history': 10
        },
        'interface': {
            'default_mode': 'cli',
            'tui_features': {
                'enabled': False,
                'auto_fallback': True,
                'theme': 'dark',
                'animations': False
            }
        }
    }

def load_config() -> Dict[str, Any]:
    """
    Load and parse the YAML configuration file.
    Automatically ensures setup is complete and uses appropriate config for environment.

    Returns:
        The parsed configuration as a dictionary

    Raises:
        SystemExit: If setup is incomplete or configuration cannot be loaded
    """
    # In test environment, use test configuration with fallbacks
    if is_test_environment():
        config = _load_test_config()
        if config:
            return config
        return _get_minimal_test_config()

    # Ensure AskAI is properly set up
    if not ensure_askai_setup():
        sys.exit(1)

    config_path = get_config_path()

    if not os.path.exists(config_path):
        print(f"Configuration file not found at {config_path}")
        sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error parsing configuration file: {e}")
        sys.exit(1)
    except IOError as e:
        print(f"Error reading configuration file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error loading configuration: {e}")
        sys.exit(1)


# ============================================================================
# INTERFACE CONFIGURATION
# ============================================================================

def get_interface_mode(config: Optional[Dict[str, Any]] = None) -> str:
    """
    Get the configured default interface mode.

    Args:
        config: Configuration dict. If None, loads from file.

    Returns:
        'cli' or 'tui' based on configuration
    """
    if config is None:
        config = load_config()

    return config.get('interface', {}).get('default_mode', 'cli')


def get_tui_features(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get TUI feature configuration.

    Args:
        config: Configuration dict. If None, loads from file.

    Returns:
        TUI features configuration with defaults
    """
    if config is None:
        config = load_config()

    defaults = DEFAULT_CONFIG['interface']['tui_features'].copy()
    tui_config = config.get('interface', {}).get('tui_features', {})

    # Merge defaults with user configuration
    defaults.update(tui_config)
    return defaults


def is_tui_enabled(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Check if TUI functionality is enabled in configuration.

    Args:
        config: Configuration dict. If None, loads from file.

    Returns:
        True if TUI is enabled
    """
    tui_features = get_tui_features(config)
    return tui_features.get('enabled', True)


def should_auto_fallback_to_cli(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Check if auto-fallback to CLI is enabled when TUI fails.

    Args:
        config: Configuration dict. If None, loads from file.

    Returns:
        True if auto-fallback is enabled
    """
    tui_features = get_tui_features(config)
    return tui_features.get('auto_fallback', True)
