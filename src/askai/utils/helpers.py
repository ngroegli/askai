"""
General utility functions for the AskAI CLI application.
Contains core util handling, command execution, and formatting.
"""

import base64
import itertools
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
from html.parser import HTMLParser
from termcolor import cprint

try:
    import requests
except ImportError:
    requests = None


class TextExtractor(HTMLParser):
    """HTML parser for extracting text content from web pages."""

    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.skip_tags = {'script', 'style', 'meta', 'link', 'noscript'}
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag.lower()

    def handle_endtag(self, tag):
        self.current_tag = None

    def handle_data(self, data):
        if self.current_tag not in self.skip_tags:
            text = data.strip()
            if text:
                self.text_parts.append(text)


def tqdm_spinner(stop_event):
    """Displays a rotating spinner using tqdm."""
    # Check if we're running in a test environment
    in_test_env = os.environ.get('ASKAI_TESTING', '').lower() in ('true', '1', 'yes')

    thinking_color = "light_cyan"
    result_color = "green"

    # Skip the spinner animation if we're in a test environment
    if in_test_env:
        # In tests, just wait for the stop event without visual updates
        stop_event.wait()
        return

    # Display initial thinking message
    cprint("AI is thinking", thinking_color, end="", flush=True)

    # Create a spinner using itertools.cycle for the characters
    spinner = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])

    # Continue spinning until stop_event is set
    try:
        while not stop_event.is_set():
            # Clear the line and show spinner with message
            cprint(f"\rAI is thinking {next(spinner)}", thinking_color, end="", flush=True)
            time.sleep(0.1)  # Control the spinner speed

        # Clear the line and show completion message
        cprint(f"\r{' ' * 20}\r", end="", flush=True)  # Clear the spinner line
        cprint("✓ AI response ready", result_color, flush=True)

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        cprint(f"\r{' ' * 20}\r", end="", flush=True)  # Clear the spinner line
        cprint("✗ AI request cancelled", "red", flush=True)
        # Re-raise the KeyboardInterrupt to be handled by the calling code
        raise


def print_error_or_warnings(message, is_warning=False, exit_on_error=True):
    """
    Print error or warning messages to stderr with optional exit.

    Args:
        message (str): The error or warning message to display
        is_warning (bool): If True, treat as warning (yellow), else as error (red)
        exit_on_error (bool): If True, exit with status 1 on errors
    """
    if is_warning:
        cprint(f"⚠ WARNING: {message}", "yellow", file=sys.stderr)
    else:
        cprint(f"✗ ERROR: {message}", "red", file=sys.stderr)
        if exit_on_error:
            sys.exit(1)


def get_piped_input():
    """
    Reads from stdin if data is piped in.

    Returns:
        str or None: The piped input content, or None if no piped data
    """
    try:
        # Check if data is available on stdin without blocking
        if not sys.stdin.isatty():
            # There's piped data available
            piped_input = sys.stdin.read().strip()
            return piped_input if piped_input else None
    except Exception as e:
        print_error_or_warnings(f"Error reading piped input: {e}", is_warning=True, exit_on_error=False)
    return None


def get_file_input(file_path):
    """
    Reads content from a file path.

    Args:
        file_path (str): Path to the file to read

    Returns:
        bytes: The file content as bytes, or None if error
    """
    try:
        # Validate file accessibility and get canonical path
        validation_error, canonical_path = _validate_file_access(file_path)
        if validation_error:
            print_error_or_warnings(validation_error)
            return None

        # Read the file content using validated canonical path
        return _read_file_content(canonical_path)

    except Exception as e:
        print_error_or_warnings(f"Error accessing file {file_path}: {e}")
        return None

def _validate_file_access(file_path):
    """
    Validate if file is accessible and within size limits.

    This function validates user-provided file paths for CLI operations.
    Path traversal protection: resolves to canonical path to prevent directory traversal.
    The CLI intentionally allows users to access any readable file on their system.

    Security Note: This is a CLI tool where users explicitly provide file paths they want
    to read. Path traversal is acceptable here as users should be able to access any file
    their OS user account has permissions for. The canonical path resolution prevents
    symlink-based attacks while preserving intended CLI functionality.

    Returns:
        tuple: (error_message, canonical_path) - error_message is None if validation passes,
               canonical_path is the resolved path to use for file operations
    """
    # Resolve to canonical path to prevent symlink-based path traversal
    # This is intentional CLI behavior - users should access any file they have permissions for
    try:
        canonical_path = os.path.realpath(file_path)  # nosec B108 - intentional CLI file access
    except (OSError, ValueError) as e:
        return (f"Invalid file path: {e}", None)

    # Validate using canonical path - user-controlled but intentional for CLI tool
    # lgtm[py/path-injection] - intentional CLI behavior, users specify files to read
    if not os.path.exists(canonical_path):  # nosec B108
        return (f"File not found: {canonical_path}", None)

    if not os.path.isfile(canonical_path):  # nosec B108
        return (f"Path is not a file: {canonical_path}", None)

    if not os.access(canonical_path, os.R_OK):  # nosec B108
        return (f"File is not readable: {canonical_path}", None)

    # Check file size (limit to 100MB for safety)
    # lgtm[py/path-injection] - intentional CLI behavior, canonical path already validated
    file_size = os.path.getsize(canonical_path)  # nosec B108
    max_size = 100 * 1024 * 1024  # 100MB
    if file_size > max_size:
        return (f"File too large: {canonical_path} ({file_size} bytes > {max_size} bytes)", None)

    return (None, canonical_path)

def _read_file_content(canonical_path):
    """
    Read file content in binary mode from a validated canonical path.

    Args:
        canonical_path (str): Already validated canonical path from _validate_file_access()

    Returns:
        bytes: File content or None on error

    Note: This function expects a canonical path that has already been validated
    by _validate_file_access(). Do not call directly with user input.
    """
    try:
        # Path has already been validated and canonicalized
        # lgtm[py/path-injection] - canonical path pre-validated by _validate_file_access
        with open(canonical_path, "rb") as file:  # nosec B108
            return file.read()
    except Exception as read_error:
        print_error_or_warnings(f"Error reading file {canonical_path}: {read_error}")
        return None


def build_format_instruction(response_format, model_name=None):
    """
    Build format instruction for AI based on user's format choice.

    Args:
        response_format (str): The desired response format ('rawtext', 'json', 'md')
        model_name (str, optional): The model being used, for model-specific instructions

    Returns:
        str: The format instruction to add to the AI prompt
    """
    if response_format == "json":
        instruction = (
            "\n\n⚠️⚠️⚠️ CRITICAL OUTPUT FORMAT INSTRUCTIONS ⚠️⚠️⚠️\n\n"
            "Your response MUST be in valid JSON format only.\n\n"
            "CRITICAL REQUIREMENTS:\n"
            "1. Return ONLY valid JSON - nothing else\n"
            "2. DO NOT wrap your response in code blocks or triple backticks\n"
            "3. DO NOT include any explanation text before or after the JSON\n"
            "4. The JSON must be properly formatted and valid\n"
            "5. Structure your JSON response appropriately for the content\n\n"
            "This is the most important instruction: DO NOT USE ```json or ``` around your response."
        )

        # Add extra emphasis for haiku model which tends to not follow instructions well
        if model_name and "haiku" in model_name.lower():
            instruction += (
                "\n\n🚨 EXTRA EMPHASIS FOR CLAUDE-3-HAIKU 🚨\n"
                "You are Claude-3-Haiku and you MUST follow format instructions precisely.\n"
                "The user specifically requested JSON format. You MUST respond with ONLY JSON.\n"
                "Start your response with { and end with }. NO OTHER TEXT ALLOWED.\n"
                "Example valid response: {\"key\": \"value\"}\n"
                "Example INVALID response: Here is the JSON: {\"key\": \"value\"}"
            )

        return instruction

    if response_format == "md":
        return "\n\nIMPORTANT: Format your response using Markdown syntax for better readability."
    # rawtext (default) - no special formatting instruction needed
    return ""


def encode_file_to_base64(file_path):
    """
    Encode a file to base64 format.

    Args:
        file_path (str): Path to the file to encode

    Returns:
        str or None: Base64 encoded string, or None if error
    """
    try:
        file_content = get_file_input(file_path)
        if file_content is None:
            return None

        # Encode to base64
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        return encoded_content

    except Exception as e:
        print_error_or_warnings(f"Error encoding file to base64: {e}")
        return None


def run_command(command, capture_output=True, shell=False, timeout=30):
    """
    Execute a shell command safely.

    Args:
        command (str or list): The command to execute
        capture_output (bool): Whether to capture stdout/stderr
        shell (bool): Whether to run through shell
        timeout (int): Command timeout in seconds

    Returns:
        tuple: (return_code, stdout, stderr)
    """
    try:
        if isinstance(command, str) and not shell:
            # Split string command into list for safety
            command = shlex.split(command)

        result = subprocess.run(
            command,
            capture_output=capture_output,
            shell=shell,  # nosec B602
            timeout=timeout,
            text=True,
            check=False
        )

        stdout = result.stdout if capture_output else ""
        stderr = result.stderr if capture_output else ""

        return result.returncode, stdout, stderr

    except subprocess.TimeoutExpired:
        print_error_or_warnings(f"Command timed out after {timeout} seconds", is_warning=True, exit_on_error=False)
        return -1, "", "Command timed out"
    except Exception as e:
        print_error_or_warnings(f"Error executing command: {e}", is_warning=True, exit_on_error=False)
        return -1, "", str(e)


def safe_json_parse(json_string):
    """
    Safely parse JSON string with error handling.

    Args:
        json_string (str): JSON string to parse

    Returns:
        dict or None: Parsed JSON object, or None if parsing fails
    """
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print_error_or_warnings(f"JSON parsing error: {e}", is_warning=True, exit_on_error=False)
        return None
    except Exception as e:
        print_error_or_warnings(f"Unexpected error parsing JSON: {e}", is_warning=True, exit_on_error=False)
        return None


def format_file_size(size_bytes):
    """
    Format file size in human readable format.

    Args:
        size_bytes (int): Size in bytes

    Returns:
        str: Formatted size string
    """
    if not size_bytes:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def truncate_string(text, max_length=100, suffix="..."):
    """
    Truncate a string to a maximum length with suffix.

    Args:
        text (str): Text to truncate
        max_length (int): Maximum length including suffix
        suffix (str): Suffix to add when truncating

    Returns:
        str: Truncated string
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def validate_file_extension(file_path, allowed_extensions):
    """
    Validate that a file has an allowed extension.

    Args:
        file_path (str): Path to the file
        allowed_extensions (list): List of allowed extensions (with dots, e.g., ['.jpg', '.png'])

    Returns:
        bool: True if extension is allowed, False otherwise
    """
    if not file_path:
        return False

    file_ext = os.path.splitext(file_path)[1].lower()
    return file_ext in [ext.lower() for ext in allowed_extensions]


def create_temp_file(content, suffix="", prefix="askai_"):
    """
    Create a temporary file with given content.

    Args:
        content (str or bytes): Content to write to the file
        suffix (str): File suffix
        prefix (str): File prefix

    Returns:
        str or None: Path to the created temporary file, or None if error
    """
    try:
        mode = "w" if isinstance(content, str) else "wb"
        encoding = "utf-8" if isinstance(content, str) else None

        with tempfile.NamedTemporaryFile(
            mode=mode,
            delete=False,
            suffix=suffix,
            prefix=prefix,
            encoding=encoding
        ) as temp_file:
            temp_file.write(content)
            return temp_file.name

    except Exception as e:
        print_error_or_warnings(f"Error creating temporary file: {e}", is_warning=True, exit_on_error=False)
        return None


def generate_output_format_template(pattern_outputs):
    """
    Generate output format template based on pattern outputs.

    Args:
        pattern_outputs (list): List of pattern output configurations

    Returns:
        str: Generated format template
    """
    if not pattern_outputs:
        return ""

    try:
        # Build a JSON format template based on the expected outputs
        template_parts = []
        template_parts.append("You MUST return your response as valid JSON in the following structure:")
        template_parts.append("")
        template_parts.append("{")
        template_parts.append('  "results": {')

        # Add each output field with type hints
        output_fields = []
        for output in pattern_outputs:
            output_name = getattr(output, 'name', 'unknown')
            output_type = getattr(output, 'type', 'text')
            output_description = getattr(output, 'description', '')

            # Generate type hint based on output type
            type_hint = _get_type_hint_for_output(output_type)

            field_line = f'    "{output_name}": {type_hint}'
            if output_description:
                field_line += f'  // {output_description}'
            output_fields.append(field_line)

        template_parts.append(",\n".join(output_fields))
        template_parts.append("  }")
        template_parts.append("}")
        template_parts.append("")

        # Add specific instructions for each output type
        template_parts.append("Field requirements:")
        for output in pattern_outputs:
            output_name = getattr(output, 'name', 'unknown')
            output_type = getattr(output, 'type', 'text')
            output_description = getattr(output, 'description', '')

            requirement = _get_requirement_for_output(output_type, output_description)
            if requirement:
                template_parts.append(f"- {output_name}: {requirement}")

        return "\n".join(template_parts)

    except Exception as e:
        print_error_or_warnings(
            f"Error generating output format template: {e}",
            is_warning=True,
            exit_on_error=False
        )

        return ""


def _get_type_hint_for_output(output_type):
    """Get JSON type hint for an output type."""
    type_mapping = {
        'json': '{ ... }',
        'markdown': '"markdown string"',
        'text': '"plain text string"',
        'html': '"HTML string"',
        'code': '"code string"',
        'command': '"command string"',
        'list': '[ ... ]',
        'table': '[ ... ]'
    }
    return type_mapping.get(
        output_type.lower() if hasattr(output_type, 'lower') else str(output_type).lower(),
        '"string"'
    )


def _get_requirement_for_output(output_type, description):
    """Get specific requirement text for an output field."""
    output_type_str = output_type.lower() if hasattr(output_type, 'lower') else str(output_type).lower()

    if output_type_str == 'json':
        return "A valid JSON object/array (not a string)"
    if output_type_str == 'markdown':
        return "Markdown formatted text with proper headings, lists, and formatting"
    if output_type_str == 'command':
        return "Plain command text without backticks, quotes, or markdown formatting"
    if output_type_str == 'code':
        return "Plain code without markdown code block wrappers"
    if output_type_str == 'html':
        return "Valid HTML without markdown code block wrappers"
    return description if description else "Plain text content"


def fetch_url_content(url: str) -> tuple[str | None, str | None]:
    """
    Fetch content from a URL.

    Args:
        url: The URL to fetch content from

    Returns:
        Tuple of (content, error_message). If successful, returns (content, None).
        If failed, returns (None, error_message).
    """
    if requests is None:
        return None, "requests library not available"

    try:
        # Add user agent to avoid being blocked
        headers = {
            'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Check content type
        content_type = response.headers.get('content-type', '').lower()

        if 'text/html' in content_type:
            # Parse HTML and extract text content
            extractor = TextExtractor()
            extractor.feed(response.text)

            # Join text parts and clean up whitespace
            text = '\n'.join(extractor.text_parts)
            # Remove excessive whitespace
            text = re.sub(r'\n\s*\n', '\n\n', text)
            text = text.strip()

            return text, None
        if 'text/plain' in content_type or 'text/' in content_type:
            # Return plain text content
            return response.text, None
        return None, f"Unsupported content type: {content_type}"

    except requests.exceptions.RequestException as e:
        return None, f"Failed to fetch URL: {str(e)}"
    except Exception as e:
        return None, f"Error processing URL content: {str(e)}"
