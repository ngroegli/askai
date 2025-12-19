#!/usr/bin/env python3
"""
Simplified Tabbed TUI Application using component-based architecture.
Each tab is now a separate, reusable component.
"""

from pathlib import Path
from textual.app import App
from textual.widgets import Header, Footer, TabbedContent, TabPane

# Import our components from parent's components directory
# pylint: disable=import-error
from ..components import QuestionTab, PatternTab, ChatTab, ModelTab, CreditsTab

TEXTUAL_AVAILABLE = True


class TabbedTUIApp(App):  # pylint: disable=too-many-instance-attributes
    """Simplified tabbed TUI application using components."""

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("f1", "help", "Help"),
        ("f2", "focus_question", "Question"),
        ("f3", "focus_patterns", "Patterns"),
        ("f4", "focus_chats", "Chats"),
        ("f5", "focus_models", "Models"),
        ("f6", "focus_credits", "Credits"),
    ]

    # Load CSS from external file
    CSS_PATH = Path(__file__).parent / "styles.tcss"

    def __init__(self, pattern_manager=None, chat_manager=None, question_processor=None):
        super().__init__()
        self.pattern_manager = pattern_manager
        self.chat_manager = chat_manager
        self.question_processor = question_processor

        # Component instances
        self.question_tab = None
        self.pattern_tab = None
        self.chat_tab = None
        self.model_tab = None
        self.credits_tab = None

    def compose(self):
        """Compose the main application layout."""
        yield Header()

        with TabbedContent(initial="question-tab"):
            # Question Builder Tab
            with TabPane("Question Builder", id="question-tab"):
                self.question_tab = QuestionTab(
                    question_processor=self.question_processor,
                    id="question-component"
                )
                yield self.question_tab

            # Pattern Browser Tab
            with TabPane("Pattern Browser", id="pattern-tab"):
                self.pattern_tab = PatternTab(
                    pattern_manager=self.pattern_manager,
                    id="pattern-component"
                )
                yield self.pattern_tab

            # Chat Browser Tab
            with TabPane("Chat Browser", id="chat-tab"):
                self.chat_tab = ChatTab(
                    chat_manager=self.chat_manager,
                    id="chat-component"
                )
                yield self.chat_tab

            # Model Browser Tab
            with TabPane("Model Browser", id="model-tab"):
                self.model_tab = ModelTab(id="model-component")
                yield self.model_tab

            # Credits Tab
            with TabPane("Credits", id="credits-tab"):
                self.credits_tab = CreditsTab(id="credits-component")
                yield self.credits_tab

        yield Footer()

    async def on_mount(self) -> None:
        """Called when the app mounts."""
        self.title = "AskAI - Interactive Terminal UI"
        self.sub_title = "Question Builder | Pattern Browser | Chat Manager | Model Browser | Credits"

        # Initialize all component tabs
        if hasattr(self, 'question_tab') and self.question_tab:
            await self.question_tab.initialize()
        if hasattr(self, 'pattern_tab') and self.pattern_tab:
            await self.pattern_tab.initialize()
        if hasattr(self, 'chat_tab') and self.chat_tab:
            await self.chat_tab.initialize()
        if hasattr(self, 'model_tab') and self.model_tab:
            await self.model_tab.initialize()
        if hasattr(self, 'credits_tab') and self.credits_tab:
            await self.credits_tab.initialize()

    # Message handlers for component interactions
    async def on_question_tab_question_submitted(self, event) -> None:
        """Handle question submission from QuestionTab."""
        question_data = event.question_data

        try:
            if not self.question_processor:
                return

            # Create a simple args object from question_data
            class SimpleArgs:  # pylint: disable=too-few-public-methods,too-many-instance-attributes
                """Simple arguments container for question processing."""

                def __init__(self, question_data):
                    self.question = question_data['question']
                    self.file_input = question_data['file_input'] if question_data['file_input'] else None
                    self.url = question_data['url'] if question_data['url'] else None
                    self.format = question_data['format']
                    self.model = question_data['model'] if question_data['model'] else None
                    self.output = None
                    self.debug = False
                    # These are not supported in TUI yet, but needed for compatibility
                    self.image = None
                    self.pdf = None
                    self.image_url = None
                    self.pdf_url = None
                    self.persistent_chat = None

            args = SimpleArgs(question_data)

            # Process the question
            response = self.question_processor.process_question(args)

            if response and response.content:
                # Display the answer
                if self.question_tab:
                    self.question_tab.display_answer(response.content)

        except Exception as e:
            if self.question_tab:
                self.question_tab.display_answer(f"Error: {str(e)}")

    # Key binding actions
    def action_focus_question(self) -> None:
        """Focus the question tab."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "question-tab"

    def action_focus_patterns(self) -> None:
        """Focus the patterns tab."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "pattern-tab"

    def action_focus_chats(self) -> None:
        """Focus the chats tab."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "chat-tab"

    def action_focus_models(self) -> None:
        """Focus the models tab."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "model-tab"

    def action_focus_credits(self) -> None:
        """Focus the credits tab."""
        tabs = self.query_one(TabbedContent)
        tabs.active = "credits-tab"

    def action_help(self) -> None:
        """Show help information."""
        help_text = """
**AskAI Interactive TUI Help**

**Navigation:**
• F1: Show this help
• F2: Switch to Question Builder
• F3: Switch to Pattern Browser
• F4: Switch to Chat Browser
• F5: Switch to Model Browser
• F6: Switch to Credits
• Ctrl+Q: Quit application

**Tabs:**
• Question Builder: Create and submit questions to AI
• Pattern Browser: Browse and use AI patterns
• Chat Browser: Manage chat history
• Model Browser: Browse and select AI models
• Credits: Monitor OpenRouter credit balance and usage

**Question Builder:**
• Enter your question in the main text area
• Optionally add file input, URL, or specify format
• Click "Ask AI" to submit your question
• Use "Clear" to reset the form

**Pattern Browser:**
• Browse available patterns in the left panel
• Select a pattern to view details in the right panel
• Provide JSON input if the pattern requires it
• Click "Use Pattern" to execute

**Chat Browser:**
• View all your chat sessions
• Create new chats or delete existing ones
• Select a chat to view details

**Model Browser:**
• Browse available AI models
• Search for specific models
• View model details, pricing, and capabilities
• Check your OpenRouter credits
"""

        # For now, just log the help - in a real implementation you'd create a help screen
        self.log(help_text)


def run_tabbed_tui(pattern_manager=None, chat_manager=None, question_processor=None):
    """
    Run the tabbed TUI application.

    Args:
        pattern_manager: Pattern manager instance
        chat_manager: Chat manager instance
        question_processor: Question processor instance

    Returns:
        Any result from the TUI interaction
    """
    try:
        app = TabbedTUIApp(
            pattern_manager=pattern_manager,
            chat_manager=chat_manager,
            question_processor=question_processor
        )
        return app.run()
    except Exception as e:
        print(f"TUI application failed: {e}")
        return None
    except KeyboardInterrupt:
        print("\nTUI application interrupted by user")
        return None
