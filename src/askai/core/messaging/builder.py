"""
Message building and processing logic.
Handles construction of messages for AI interaction based on various inputs.
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple
from askai.utils import (get_piped_input, get_file_input, build_format_instruction,
                   encode_file_to_base64, generate_output_format_template)
from askai.utils.helpers import fetch_url_content


# ============================================================================
# CONSTANTS
# ============================================================================

# Map file extensions to MIME types for image processing
MIME_TYPE_MAP = {
    "jpg": "jpeg",
    "jpeg": "jpeg",
    "png": "png",
    "gif": "gif",
    "webp": "webp",
    "bmp": "bmp"
}


class MessageBuilder:
    """Builds messages for AI interaction from various input sources."""

    def __init__(self, pattern_manager: Any, logger: Any) -> None:
        """Initialize MessageBuilder.

        Args:
            pattern_manager: Pattern manager instance
            logger: Logger instance
        """
        self.pattern_manager = pattern_manager
        self.logger = logger

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type from file extension.

        Args:
            file_path: Path to the file

        Returns:
            MIME type string (defaults to 'jpeg' if unknown)
        """
        file_ext = os.path.splitext(file_path)[1].lower().replace(".", "")
        return MIME_TYPE_MAP.get(file_ext or "jpeg", "jpeg")

    def _create_image_multimodal_message(
        self,
        question: str,
        image_data: str,
        mime_type: str
    ) -> Dict[str, Any]:
        """Create a multimodal message with image content.

        Args:
            question: User question about the image
            image_data: Base64-encoded image data or URL
            mime_type: MIME type (e.g., 'jpeg', 'png')

        Returns:
            Message dictionary with multimodal content
        """
        # Check if it's a URL or base64 data
        if image_data.startswith(('http://', 'https://')):
            image_url = image_data
        else:
            image_url = f"data:image/{mime_type};base64,{image_data}"

        return {
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {
                    "type": "image_url",
                    "image_url": {"url": image_url}
                }
            ]
        }

    def _create_pdf_multimodal_message(
        self,
        question: str,
        pdf_data: str,
        filename: str
    ) -> Dict[str, Any]:
        """Create a multimodal message with PDF content.

        Args:
            question: User question about the PDF
            pdf_data: Base64-encoded PDF data or URL
            filename: PDF filename

        Returns:
            Message dictionary with multimodal content
        """
        # Check if it's a URL or base64 data
        if pdf_data.startswith(('http://', 'https://')):
            file_data = pdf_data
        else:
            file_data = f"data:application/pdf;base64,{pdf_data}"

        return {
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {
                    "type": "file",
                    "file": {
                        "filename": filename,
                        "file_data": file_data
                    }
                }
            ]
        }

    def _encode_image_file(
        self,
        image_path: str,
        question: Optional[str],
        messages: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Encode image file and add to messages.

        Args:
            image_path: Path to the image file
            question: Optional user question (will be consumed if provided)
            messages: Message list to append to

        Returns:
            None if question was consumed, original question otherwise
        """
        self.logger.info(json.dumps({
            "log_message": "Processing image file",
            "image_path": image_path
        }))

        mime_type = self._get_mime_type(image_path)
        image_base64 = encode_file_to_base64(image_path)

        if image_base64:
            user_question = question or "Please analyze and describe this image in detail."
            message = self._create_image_multimodal_message(user_question, image_base64, mime_type)
            messages.append(message)

            self.logger.debug(json.dumps({
                "log_message": "Created multimodal message for image",
                "mime_type": mime_type
            }))
            return None  # Question consumed

        return question

    def _encode_pdf_file(
        self,
        pdf_path: str,
        question: Optional[str],
        messages: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Encode PDF file and add to messages.

        Args:
            pdf_path: Path to the PDF file
            question: Optional user question (will be consumed if provided)
            messages: Message list to append to

        Returns:
            None if question was consumed, original question otherwise
        """
        pdf_filename = os.path.basename(pdf_path)
        file_ext = os.path.splitext(pdf_filename)[1].lower()

        self.logger.debug(json.dumps({
            "log_message": "Processing PDF file",
            "pdf_path": pdf_path,
            "extension": file_ext
        }))

        # Handle non-PDF files as text
        if file_ext != '.pdf':
            self.logger.warning(json.dumps({
                "log_message": "File does not have .pdf extension, treating as text file",
                "file_path": pdf_path
            }))

            file_content = get_file_input(pdf_path)
            if file_content:
                messages.append({
                    "role": "system",
                    "content": f"The file content of {pdf_filename} to work with:\n{file_content}"
                })
                return question or "Please analyze and summarize the content of this file."
            return question

        # Encode actual PDF file
        pdf_base64 = encode_file_to_base64(pdf_path)
        if not pdf_base64:
            self.logger.warning("Failed to encode PDF file")
            return question

        user_question = question or "Please analyze and summarize the content of this PDF."

        try:
            message = self._create_pdf_multimodal_message(user_question, pdf_base64, pdf_filename)
            messages.append(message)

            # Add fallback note
            messages.append({
                "role": "system",
                "content": ("Note: If you're unable to access the PDF content directly, "
                          "please inform the user that the PDF could not be processed, "
                          "and ask them to try extracting the text manually.")
            })

            self.logger.debug(json.dumps({
                "log_message": "Created multimodal message for PDF",
                "filename": pdf_filename
            }))
            return None  # Question consumed

        except Exception as e:
            self.logger.error(json.dumps({
                "log_message": "Error creating PDF message format",
                "error": str(e)
            }))

            messages.append({
                "role": "user",
                "content": user_question
            })
            messages.append({
                "role": "system",
                "content": (f"The user attempted to upload a PDF file named '{pdf_filename}', "
                          f"but it couldn't be processed. Please inform them that PDF processing "
                          f"may require PyPDF2 to be installed or the PDF may not be compatible.")
            })
            return None  # Question consumed

    # ========================================================================
    # PUBLIC METHODS
    # ========================================================================

    def build_messages(
        self,
        *,
        question: Optional[str] = None,
        file_input: Optional[str] = None,
        pattern_id: Optional[str] = None,
        pattern_input: Optional[Dict[str, Any]] = None,
        response_format: str = "rawtext",
        url: Optional[str] = None,
        image: Optional[str] = None,
        pdf: Optional[str] = None,
        image_url: Optional[str] = None,
        pdf_url: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
        # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """Build the message list for OpenRouter.

        Args:
            question: Optional user question
            file_input: Optional path to input file
            pattern_id: Optional pattern ID to use
            pattern_input: Optional pattern inputs as dict
            response_format: Response format (rawtext, json, or md)
            url: Optional URL to analyze/summarize
            image: Optional path to image file
            pdf: Optional path to PDF file
            image_url: Optional URL to an image
            pdf_url: Optional URL to a PDF file
            model_name: Optional model name for model-specific instructions

        Returns:
            Tuple of (messages list, resolved_pattern_id) or (None, None) on error
        """
        messages = []
        resolved_pattern_id = pattern_id

        # Handle piped input from terminal
        if context := get_piped_input():
            self.logger.info(json.dumps({"log_message": "Piped input received"}))
            messages.append({
                "role": "system",
                "content": f"Previous terminal output:\n{context}"
            })

        # Handle input file content
        if file_input and (file_content := get_file_input(file_input)):
            self.logger.info(json.dumps({
                "log_message": "Input file read successfully",
                "file_path": file_input
            }))
            messages.append({
                "role": "system",
                "content": f"The file content of {file_input} to work with:\n{file_content}"
            })

        # Handle URL input - fetch content and add to messages
        if url:
            self.logger.info(json.dumps({
                "log_message": "URL provided for analysis",
                "url": url
            }))

            url_content, error = fetch_url_content(url)

            if url_content:
                self.logger.info(json.dumps({
                    "log_message": "URL content fetched successfully",
                    "content_length": len(url_content)
                }))
                messages.append({
                    "role": "system",
                    "content": f"The content from URL {url}:\n{url_content}"
                })
                # If no question provided, default to summarization
                if not question:
                    question = "Please analyze and summarize the content from the provided URL"
            else:
                self.logger.error(json.dumps({
                    "log_message": "Failed to fetch URL content",
                    "url": url,
                    "error": error
                }))
                # Fallback to asking AI to reason about the URL
                if not question:
                    question = (f"Please analyze and summarize what you know about this URL: {url} "
                              f"(Note: Content could not be fetched due to: {error})")
                else:
                    question = (f"Please analyze this URL: {url} "
                              f"(Note: Content could not be fetched due to: {error})\n\n"
                              f"Question: {question}")

        # Handle image input - convert to base64 for multimodal message
        if image:
            question = self._encode_image_file(image, question, messages)

        # Handle image URL input
        if image_url:
            self.logger.info(json.dumps({
                "log_message": "Image URL provided for analysis",
                "image_url": image_url
            }))

            user_question = question or "Please analyze and describe this image in detail."
            message = self._create_image_multimodal_message(user_question, image_url, "jpeg")
            messages.append(message)
            question = None  # Mark question as consumed

            self.logger.debug(json.dumps({
                "log_message": "Created multimodal message for image URL"
            }))

        # Handle PDF input - encode as base64
        if pdf:
            question = self._encode_pdf_file(pdf, question, messages)

        # Handle PDF URL input
        if pdf_url:
            self.logger.info(json.dumps({
                "log_message": "PDF URL provided for analysis",
                "pdf_url": pdf_url
            }))

            # Extract filename from URL
            pdf_filename = pdf_url.split('/')[-1]
            if not pdf_filename or not pdf_filename.lower().endswith('.pdf'):
                pdf_filename = "document.pdf"

            user_question = question or "Please analyze and summarize the content of this PDF."

            try:
                message = self._create_pdf_multimodal_message(user_question, pdf_url, pdf_filename)
                messages.append(message)

                # Add fallback note
                messages.append({
                    "role": "system",
                    "content": ("Note: If you're unable to access the PDF content directly, please inform the user "
                              "that the PDF could not be processed, and ask them to try using a different PDF URL "
                              "or downloading the PDF first.")
                })

                question = None  # Mark question as consumed

                self.logger.debug(json.dumps({
                    "log_message": "Created multimodal message for PDF URL"
                }))
            except Exception as e:
                self.logger.error(json.dumps({
                    "log_message": "Error creating PDF URL message format",
                    "error": str(e)
                }))

                messages.append({
                    "role": "user",
                    "content": user_question
                })
                messages.append({
                    "role": "system",
                    "content": (f"The user attempted to provide a PDF URL '{pdf_url}', but it couldn't be processed. "
                              f"Please inform them that the PDF URL may not be valid or directly accessible.")
                })
                question = None  # Mark question as consumed

        # Add pattern-specific context if specified
        if pattern_id is not None:
            resolved_pattern_id = self._handle_pattern_context(
                pattern_id, pattern_input, messages
            )
            if resolved_pattern_id is None:
                return None, None

        # Add format instructions
        if pattern_id is None: # Only if no pattern is used -> question logic
            messages.append({
                "role": "system",
                "content": build_format_instruction(response_format, model_name)
            })

        # Add user question if provided
        if question:
            messages.append({
                "role": "user",
                "content": question
            })

        return messages, resolved_pattern_id

    def _handle_pattern_context(
        self,
        pattern_id: str,
        pattern_input: Optional[Dict[str, Any]],
        messages: List[Dict[str, Any]]
    ) -> Optional[str]:
        # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """Handle pattern-specific context and add to messages."""
        # Handle pattern selection if no specific ID was provided
        if pattern_id == 'new':
            resolved_pattern_id = self.pattern_manager.select_pattern()
            if resolved_pattern_id is None:
                print("Pattern selection cancelled.")
                return None
        else:
            resolved_pattern_id = pattern_id

        self.logger.info(json.dumps({
            "log_message": "Pattern used",
            "pattern": resolved_pattern_id
        }))

        pattern_data = self.pattern_manager.get_pattern_content(resolved_pattern_id)
        if pattern_data is None:
            print(f"Pattern '{resolved_pattern_id}' does not exist")
            return None

        # Get and validate pattern data
        pattern_inputs = self.pattern_manager.process_pattern_inputs(
            pattern_id=resolved_pattern_id,
            input_values=pattern_input
        )
        if pattern_inputs is None:
            return None

        # Add pattern prompt content (purpose and functionality only)
        pattern_prompt = pattern_data['prompt_content']
        messages.append({
            "role": "system",
            "content": pattern_prompt
        })

        # Check for special file inputs and handle them specially
        image_file_input = None
        pdf_file_input = None
        image_base64 = None
        structured_inputs = dict(pattern_inputs)  # Make a copy to modify

        # Check if there are any special inputs to handle (image_file, pdf_file, image_url, pdf_url)
        for input_def in pattern_data.get('inputs', []):
            # Handle image files
            if input_def.input_type.value == "image_file" and input_def.name in pattern_inputs:
                image_file_input = pattern_inputs[input_def.name]
                structured_inputs.pop(input_def.name, None)

                if image_file_input is not None:
                    self.logger.info(json.dumps({
                        "log_message": "Processing image_file from pattern input",
                        "image_path": image_file_input
                    }))

                    mime_type = self._get_mime_type(image_file_input)
                    image_base64 = encode_file_to_base64(image_file_input)

                    if image_base64:
                        user_question = "Please analyze this image based on the provided inputs."
                        message = self._create_image_multimodal_message(
                            user_question, image_base64, mime_type
                        )
                        messages.append(message)

                        self.logger.debug(json.dumps({
                            "log_message": "Created multimodal message for pattern image input"
                        }))

            # Handle PDF files
            elif input_def.input_type.value == "pdf_file" and input_def.name in pattern_inputs:
                pdf_file_input = pattern_inputs[input_def.name]
                structured_inputs.pop(input_def.name, None)

                if pdf_file_input is not None:
                    self.logger.info(json.dumps({
                        "log_message": "Processing pdf_file from pattern input",
                        "pdf_path": pdf_file_input
                    }))

                    pdf_filename = os.path.basename(pdf_file_input)
                    pdf_base64 = encode_file_to_base64(pdf_file_input)

                    if pdf_base64:
                        user_question = "Please analyze this PDF document based on the provided inputs."
                        message = self._create_pdf_multimodal_message(
                            user_question, pdf_base64, pdf_filename
                        )
                        messages.append(message)

                        self.logger.debug(json.dumps({
                            "log_message": "Created multimodal message for pattern PDF input"
                        }))

            # Handle PDF URL inputs from pattern
            elif input_def.name == "pdf_url" and input_def.name in pattern_inputs:
                pdf_url = pattern_inputs[input_def.name]
                structured_inputs.pop(input_def.name, None)

                if pdf_url is not None:
                    self.logger.info(json.dumps({
                        "log_message": "Processing pdf_url from pattern input",
                        "pdf_url": pdf_url
                    }))

                    try:
                        pdf_filename = pdf_url.split('/')[-1]
                        if not pdf_filename.lower().endswith('.pdf'):
                            pdf_filename += '.pdf'

                        user_question = "Please analyze and summarize this PDF document based on the provided inputs."
                        message = self._create_pdf_multimodal_message(user_question, pdf_url, pdf_filename)
                        messages.append(message)

                        self.logger.debug(json.dumps({
                            "log_message": "Created multimodal message for pattern PDF URL input"
                        }))

                    except Exception as e:
                        self.logger.error(json.dumps({
                            "log_message": "Error processing PDF URL from pattern input",
                            "error": str(e)
                        }))

            # Handle image URL inputs from pattern
            elif input_def.name == "image_url" and input_def.name in pattern_inputs:
                image_url = pattern_inputs[input_def.name]
                structured_inputs.pop(input_def.name, None)

                if image_url is not None:
                    self.logger.info(json.dumps({
                        "log_message": "Processing image_url from pattern input",
                        "image_url": image_url
                    }))

                    try:
                        user_question = "Please analyze and describe this image based on the provided inputs."
                        message = self._create_image_multimodal_message(user_question, image_url, "jpeg")
                        messages.append(message)

                        self.logger.debug(json.dumps({
                            "log_message": "Created multimodal message for pattern image URL input"
                        }))

                    except Exception as e:
                        self.logger.error(json.dumps({
                            "log_message": "Error processing image URL from pattern input",
                            "error": str(e)
                        }))

        # If there are inputs (excluding handled image_file), provide them in a structured way
        if structured_inputs:
            messages.append({
                "role": "system",
                "content": "Available inputs:\n" + json.dumps(structured_inputs, indent=2)
            })

        # If there are output definitions, generate a dynamic output format template
        if pattern_outputs := pattern_data.get('outputs'):
            # First check if the pattern has its own format_instructions
            custom_format = None
            config = pattern_data.get('configuration')
            if config and hasattr(config, 'format_instructions') and config.format_instructions:
                custom_format = config.format_instructions

            # If no custom format, generate one dynamically
            if not custom_format:
                custom_format = generate_output_format_template(pattern_outputs)

            # Add the format instructions to the messages
            if custom_format:
                messages.append({
                    "role": "system",
                    "content": custom_format
                })
            else:
                # Fallback to basic output spec if generation fails
                output_spec = {
                    output.name: {
                        "description": output.description,
                        "type": output.output_type.value,
                        "required": output.required,
                        "schema": output.schema if hasattr(output, 'schema') else None
                    } for output in pattern_outputs
                }
                messages.append({
                    "role": "system",
                    "content": "Required output format:\n" + json.dumps(output_spec, indent=2)
                })

        return resolved_pattern_id
