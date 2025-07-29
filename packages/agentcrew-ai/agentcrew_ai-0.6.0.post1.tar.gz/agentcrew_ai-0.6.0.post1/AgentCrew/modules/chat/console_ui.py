import asyncio
import sys
import time
import pyperclip
import re
import threading
import random
import itertools
from typing import Dict, Any, List
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from rich.live import Live
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
import AgentCrew

from AgentCrew.modules.agents.base import MessageType
from AgentCrew.modules.chat.message_handler import MessageHandler, Observer
from AgentCrew.modules import logger
from AgentCrew.modules.chat.completers import ChatCompleter
from AgentCrew.modules.chat.constants import (
    YELLOW,
    GREEN,
    BLUE,
    RED,
    GRAY,
    RESET,
    BOLD,
    RICH_YELLOW,
    RICH_GRAY,
)

CODE_THEME = "lightbulb"


class ConsoleUI(Observer):
    """
    A console-based UI for the interactive chat that implements the Observer interface
    to receive updates from the MessageHandler.
    """

    def __init__(self, message_handler: MessageHandler):
        """
        Initialize the ConsoleUI.

        Args:
            message_handler: The MessageHandler instance that this UI will observe.
        """
        self.message_handler = message_handler
        self.message_handler.attach(self)

        self.console = Console()
        self.live = None  # Will be initialized during response streaming
        self._last_ctrl_c_time = 0
        self.latest_assistant_response = ""
        self.session_cost = 0.0
        self._live_text_data = ""
        self._loading_stop_event = None
        self._loading_thread = None

        # Set up key bindings
        self.kb = self._setup_key_bindings()

    def listen(self, event: str, data: Any = None):
        """
        Update method required by the Observer interface. Handles events from the MessageHandler.

        Args:
            event: The type of event that occurred.
            data: The data associated with the event.
        """

        if event == "thinking_started":
            self.stop_loading_animation()  # Stop loading on first chunk
            self.display_thinking_started(data)  # data is agent_name
        elif event == "thinking_chunk":
            self.display_thinking_chunk(data)  # data is the thinking chunk
        elif event == "response_chunk":
            self.stop_loading_animation()  # Stop loading on first chunk
            _, assistant_response = data
            self.update_live_display(assistant_response)  # data is the response chunk
        elif event == "tool_use":
            self.stop_loading_animation()  # Stop loading on first chunk
            self.display_tool_use(data)  # data is the tool use object
        elif event == "tool_result":
            pass
            # self.display_tool_result(data)  # data is dict with tool_use and tool_result
        elif event == "tool_error":
            self.display_tool_error(data)  # data is dict with tool_use and error
        elif event == "tool_confirmation_required":
            self.stop_loading_animation()  # Stop loading on first chunk
            self.display_tool_confirmation_request(
                data
            )  # data is the tool use with confirmation ID
        elif event == "tool_denied":
            self.display_tool_denied(data)  # data is the tool use that was denied
        elif event == "response_completed":
            # pass
            self.finish_response(data)  # data is the complete response
        elif event == "error":
            self.display_error(data)  # data is the error message or dict
        elif event == "clear_requested":
            self.display_message(f"{YELLOW}{BOLD}🎮 Chat history cleared.{RESET}")
        elif event == "exit_requested":
            self.display_message(
                f"{YELLOW}{BOLD}🎮 Ending chat session. Goodbye!{RESET}"
            )
            sys.exit(0)
        elif event == "copy_requested":
            self.copy_to_clipboard(data)  # data is the text to copy
        elif event == "debug_requested":
            self.display_debug_info(data)  # data is the debug information
        elif event == "think_budget_set":
            self.display_message(
                f"{YELLOW}Thinking budget set to {data} tokens.{RESET}"
            )
        elif event == "models_listed":
            self.display_models(data)  # data is dict of models by provider
        elif event == "model_changed":
            self.display_message(
                f"{YELLOW}Switched to {data['name']} ({data['id']}){RESET}"
            )
        elif event == "agents_listed":
            self.display_agents(data)  # data is dict of agent info
        elif event == "agent_changed":
            self.display_message(f"{YELLOW}Switched to {data} agent{RESET}")
        elif event == "agent_changed_by_transfer":
            self.display_message(
                f"{YELLOW}Transfered to {data['agent_name'] if 'agent_name' in data else 'other'} agent{RESET}"
            )
        elif event == "agent_continue":
            self.display_message(f"\n{GREEN}{BOLD}🤖 {data.upper()}:{RESET}")
        elif event == "jump_performed":
            self.display_message(
                f"{YELLOW}{BOLD}🕰️ Jumping to turn {data['turn_number']}...{RESET}\n"
                f"{YELLOW}Conversation rewound to: {data['preview']}{RESET}"
            )
        elif event == "thinking_completed":
            self.console.print("\n")
            self.display_divider()
        elif event == "file_processed":
            self.stop_loading_animation()  # Stop loading on first chunk
            self.display_message(f"{YELLOW}Processed file: {data['file_path']}{RESET}")
        elif event == "consolidation_completed":
            self.display_consolidation_result(data)
        elif event == "conversations_listed":
            self.display_conversations(data)  # data is list of conversation metadata
        elif event == "conversation_loaded":
            self.display_message(
                f"{YELLOW}Loaded conversation: {data.get('id', 'N/A')}{RESET}"
            )
        elif event == "conversation_saved":
            logger.info(f"Conversation saved: {data.get('id', 'N/A')}")
            # self.display_message(
            #     f"{YELLOW}Conversation saved: {data.get('id', 'N/A')}{RESET}"
            # )
        elif event == "clear_requested":
            self.session_cost = 0.0
        elif event == "update_token_usage":
            self._calculate_token_usage(data["input_tokens"], data["output_tokens"])

    def display_thinking_started(self, agent_name: str):
        """Display the start of the thinking process."""
        self.console.print(
            Text(f"\n💭 {agent_name.upper()}'s thinking process:", style=RICH_YELLOW)
        )

    def _loading_animation(self, stop_event):
        """Display a loading animation in the terminal."""
        spinner = itertools.cycle(["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"])
        fun_words = [
            "Pondering",
            "Cogitating",
            "Ruminating",
            "Contemplating",
            "Brainstorming",
            "Calculating",
            "Processing",
            "Analyzing",
            "Deciphering",
            "Meditating",
            "Daydreaming",
            "Scheming",
            "Brewing",
            "Conjuring",
            "Inventing",
            "Imagining",
        ]
        fun_word = random.choice(fun_words)

        with Live(
            "", console=self.console, auto_refresh=True, refresh_per_second=10
        ) as live:
            while not stop_event.is_set():
                live.update(f"{fun_word} {next(spinner)}")
                time.sleep(0.1)  # Control animation speed

    def start_loading_animation(self):
        """Start the loading animation."""
        if self._loading_thread and self._loading_thread.is_alive():
            return  # Already running

        self._loading_stop_event = threading.Event()
        self._loading_thread = threading.Thread(
            target=self._loading_animation, args=(self._loading_stop_event,)
        )
        self._loading_thread.daemon = True
        self._loading_thread.start()

    def stop_loading_animation(self):
        """Stop the loading animation."""
        if self._loading_stop_event:
            if self.console._live:
                self.console._live.update("")
                self.console._live.stop()
            self._loading_stop_event.set()
        if self._loading_thread and self._loading_thread.is_alive():
            self._loading_thread.join(timeout=0.5)
        self._loading_stop_event = None
        self._loading_thread = None

    def display_thinking_chunk(self, chunk: str):
        """Display a chunk of the thinking process."""
        self.console.print(Text(chunk, style=RICH_GRAY), end="", soft_wrap=True)

    def update_live_display(self, chunk: str):
        """Update the live display with a new chunk of the response."""
        if not self.live:
            self.start_streaming_response(self.message_handler.agent.name)

        updated_text = chunk

        self._live_text_data = updated_text

        # Only show the last part that fits in the console
        lines = updated_text.split("\n")
        height_limit = (
            self.console.size.height - 10
        )  # leave some space for other elements
        if len(lines) > height_limit:
            lines = lines[-height_limit:]

        if self.live:
            self.live.update(Markdown("\n".join(lines), code_theme=CODE_THEME))

    def display_tool_use(self, tool_use: Dict):
        """Display information about a tool being used."""
        self.finish_live_update()

        # Tool icons mapping
        tool_icons = {
            "web_search": "🔍",
            "fetch_webpage": "🌐",
            "transfer": "↗️",
            "adapt": "🧠",
            "retrieve_memory": "💭",
            "forget_memory_topic": "🗑️",
            "analyze_repo": "📂",
            "read_file": "📄",
        }

        # Get tool icon or default
        tool_icon = tool_icons.get(tool_use["name"], "🔧")

        # Display tool header with better formatting
        print(
            f"\n{YELLOW}┌───── {tool_icon} Tool: {BOLD}{tool_use['name']}{RESET}{YELLOW} ─────{RESET}"
        )

        # Format tool input parameters
        if isinstance(tool_use.get("input"), dict):
            print(f"{YELLOW}│ Parameters:{RESET}")
            for key, value in tool_use["input"].items():
                # Format value based on type
                if isinstance(value, dict) or isinstance(value, list):
                    import json

                    formatted_value = json.dumps(value, indent=2)
                    # Add indentation to all lines after the first
                    formatted_value = formatted_value.replace(
                        "\n", f"\n{YELLOW}│ {RESET}    "
                    )
                    print(f"{YELLOW}│ • {BLUE}{key}{RESET}: {formatted_value}")
                else:
                    print(f"{YELLOW}│ • {BLUE}{key}{RESET}: {value}")
        else:
            print(f"{YELLOW}│ Input: {RESET}{tool_use.get('input', '')}")

        print(f"{YELLOW}└{RESET}")

    def display_tool_result(self, data: Dict):
        """Display the result of a tool execution."""
        tool_use = data["tool_use"]
        tool_result = data["tool_result"]

        # Tool icons mapping
        tool_icons = {
            "web_search": "🔍",
            "fetch_webpage": "🌐",
            "transfer": "↗️",
            "adapt": "🧠",
            "retrieve_memory": "💭",
            "forget_memory_topic": "🗑️",
            "analyze_repo": "📂",
            "read_file": "📄",
        }

        # Get tool icon or default
        tool_icon = tool_icons.get(tool_use["name"], "🔧")

        # Display tool result with better formatting
        print(
            f"\n{GREEN}┌───── {tool_icon} Tool Result: {BOLD}{tool_use['name']}{RESET}{GREEN} ─────{RESET}"
        )

        # Format the result based on type
        result_str = str(tool_result)
        # If result is very long, try to format it
        if len(result_str) > 500:
            print(f"{GREEN}│ {RESET}{result_str[:500]}...")
            print(
                f"{GREEN}│ {RESET}(Output truncated, total length: {len(result_str)} characters)"
            )
        else:
            # Split by lines to add prefixes
            for line in result_str.split("\n"):
                print(f"{GREEN}│ {RESET}{line}")

        print(f"{GREEN}└{RESET}")

    def display_tool_error(self, data: Dict):
        """Display an error that occurred during tool execution."""
        self.finish_live_update()
        tool_use = data["tool_use"]
        error = data["error"]

        # Tool icons mapping
        tool_icons = {
            "web_search": "🔍",
            "fetch_webpage": "🌐",
            "transfer": "↗️",
            "adapt": "🧠",
            "retrieve_memory": "💭",
            "forget_memory_topic": "🗑️",
            "analyze_repo": "📂",
            "read_file": "📄",
        }

        # Get tool icon or default
        tool_icon = tool_icons.get(tool_use["name"], "🔧")

        # Display tool error with better formatting
        print(
            f"\n{RED}┌───── {tool_icon} Tool Error: {BOLD}{tool_use['name']}{RESET}{RED} ─────{RESET}"
        )
        print(f"{RED}│ {RESET}{error}")
        print(f"{RED}└{RESET}")

    def display_tool_confirmation_request(self, tool_info):
        """Display tool confirmation request and get user response."""
        self.finish_live_update()

        tool_use = tool_info.copy()
        confirmation_id = tool_use.pop("confirmation_id")

        print(f"\n{YELLOW}🔧 Tool execution requires your permission:{RESET}")
        print(f"{YELLOW}Tool: {tool_use['name']}{RESET}")

        # Display tool parameters
        if isinstance(tool_use["input"], dict):
            print(f"{YELLOW}Parameters:{RESET}")
            for key, value in tool_use["input"].items():
                print(f"  - {key}: {value}")
        else:
            print(f"{YELLOW}Input: {tool_use['input']}{RESET}")

        # Get user response
        while True:
            response = input(
                f"\n{YELLOW}Allow this tool to run? [y]es/[n]o/[all] future calls: {RESET}"
            ).lower()

            if response in ["y", "yes"]:
                self.message_handler.resolve_tool_confirmation(
                    confirmation_id, {"action": "approve"}
                )
                break
            elif response in ["n", "no"]:
                self.message_handler.resolve_tool_confirmation(
                    confirmation_id, {"action": "deny"}
                )
                break
            elif response in ["all", "a"]:
                self.message_handler.resolve_tool_confirmation(
                    confirmation_id, {"action": "approve_all"}
                )
                print(
                    f"{YELLOW}✓ Approved all future calls to '{tool_use['name']}' for this session.{RESET}"
                )
                break
            else:
                print(f"{YELLOW}Please enter 'y', 'n', or 'all'.{RESET}")

    def display_tool_denied(self, data):
        """Display information about a denied tool execution."""
        tool_use = data["tool_use"]
        print(f"\n{RED}❌ Tool execution denied: {tool_use['name']}{RESET}")

    def finish_live_update(self):
        """stop the live update display."""
        if self.live:
            self.console.print(self.live.get_renderable())
            self.live.update("")
            self.live.stop()
            self.live = None

    def finish_response(self, response: str):
        """Finalize and display the complete response."""
        if self.live:
            self.live.update("")
            self.live.stop()
            self.live = None

        # Replace \n with two spaces followed by \n for proper Markdown line breaks
        markdown_formatted_response = response.replace("\n", "  \n")
        self.console.print(Markdown(markdown_formatted_response, code_theme=CODE_THEME))

        # Store the latest response
        self.latest_assistant_response = response

    def display_error(self, error):
        """Display an error message."""
        self.stop_loading_animation()  # Stop loading on error
        if isinstance(error, dict):
            print(f"\n{RED}❌ Error: {error['message']}{RESET}")
            if "traceback" in error:
                print(f"{GRAY}{error['traceback']}{RESET}")
        else:
            print(f"\n{RED}❌ Error: {error}{RESET}")
        if self.live:
            self.live.update("")
            self.live.stop()
            self.live = None

    def display_message(self, message: str):
        """Display a generic message."""
        print(message)

    def display_divider(self):
        """Display a divider line."""
        divider = "─" * self.console.size.width
        print(divider)

    def copy_to_clipboard(self, text: str):
        """Copy text to clipboard and show confirmation."""
        if text:
            pyperclip.copy(text)
            print(f"\n{YELLOW}✓ Text copied to clipboard!{RESET}")
        else:
            print(f"\n{YELLOW}! No text to copy.{RESET}")

    def display_debug_info(self, debug_info):
        """Display debug information."""
        import json

        print(f"{YELLOW}Current messages:{RESET}")
        try:
            self.console.print(json.dumps(debug_info, indent=2))
        except Exception:
            print(debug_info)

    def display_models(self, models_by_provider: Dict):
        """Display available models grouped by provider."""
        print(f"{YELLOW}Available models:{RESET}")
        for provider, models in models_by_provider.items():
            print(f"\n{YELLOW}{provider.capitalize()} models:{RESET}")
            for model in models:
                current = " (current)" if model["current"] else ""
                print(f"  - {model['id']}: {model['name']}{current}")
                print(f"    {model['description']}")
                print(f"    Capabilities: {', '.join(model['capabilities'])}")

    def display_agents(self, agents_info: Dict):
        """Display available agents."""
        print(f"{YELLOW}Current agent: {agents_info['current']}{RESET}")
        print(f"{YELLOW}Available agents:{RESET}")

        for agent_name, agent_data in agents_info["available"].items():
            current = " (current)" if agent_data["current"] else ""
            print(f"  - {agent_name}{current}: {agent_data['description']}")

    def display_conversations(self, conversations: List[Dict[str, Any]]):
        """Display available conversations."""
        if not conversations:
            print(f"{YELLOW}No saved conversations found.{RESET}")
            return

        print(f"{YELLOW}Available conversations:{RESET}")
        for i, convo in enumerate(conversations[:30], 1):
            # Format timestamp for better readability
            timestamp = convo.get("timestamp", "Unknown")
            if isinstance(timestamp, (int, float)):
                from datetime import datetime

                timestamp = datetime.fromtimestamp(timestamp).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            title = convo.get("title", "Untitled")
            convo_id = convo.get("id", "unknown")

            # Display conversation with index for easy selection
            print(f"  {i}. {title} [{convo_id}]")
            print(f"     Created: {timestamp}")

            # Show a preview if available
            if "preview" in convo:
                print(f"     Preview: {convo['preview']}")
            print()

    def handle_load_conversation(self, load_arg: str):
        """
        Handle loading a conversation by number or ID.

        Args:
            load_arg: Either a conversation number (from the list) or a conversation ID
        """
        # First check if we have a list of conversations cached
        if not hasattr(self, "_cached_conversations"):
            # If not, get the list first
            self._cached_conversations = self.message_handler.list_conversations()

        try:
            # Check if the argument is a number (index in the list)
            if load_arg.isdigit():
                index = int(load_arg) - 1  # Convert to 0-based index
                if 0 <= index < len(self._cached_conversations):
                    convo_id = self._cached_conversations[index].get("id")
                    if convo_id:
                        print(f"{YELLOW}Loading conversation #{load_arg}...{RESET}")
                        messages = self.message_handler.load_conversation(convo_id)
                        if messages:
                            self.display_loaded_conversation(messages)
                        return
                print(
                    f"{RED}Invalid conversation number. Use '/list' to see available conversations.{RESET}"
                )
            else:
                # Assume it's a conversation ID
                print(f"{YELLOW}Loading conversation with ID: {load_arg}...{RESET}")
                messages = self.message_handler.load_conversation(load_arg)
                if messages:
                    self.display_loaded_conversation(messages)
        except Exception as e:
            print(f"{RED}Error loading conversation: {str(e)}{RESET}")

    def display_consolidation_result(self, result: Dict[str, Any]):
        """
        Display information about a consolidation operation.

        Args:
            result: Dictionary containing consolidation results
        """
        print(f"\n{YELLOW}🔄 Conversation Consolidated:{RESET}")
        print(f"  • {result['messages_consolidated']} messages summarized")
        print(f"  • {result['messages_preserved']} recent messages preserved")
        print(
            f"  • ~{result['original_token_count'] - result['consolidated_token_count']} tokens saved"
        )
        self.display_loaded_conversation(self.message_handler.streamline_messages)

    def display_loaded_conversation(self, messages):
        """Display all messages from a loaded conversation.

        Args:
            messages: List of message dictionaries from the loaded conversation
        """
        print(f"\n{YELLOW}Displaying conversation history:{RESET}")
        self.display_divider()

        last_consolidated_idx = 0

        for i, msg in reversed(list(enumerate(messages))):
            if msg.get("role") == "consolidated":
                last_consolidated_idx = i
                break

        # Display each message in the conversation
        for msg in messages[last_consolidated_idx:]:
            role = msg.get("role")
            if role == "user":
                print(f"\n{BLUE}{BOLD}👤 YOU:{RESET}")
                content = self._extract_message_content(msg)
                print(content)
                self.display_divider()
            elif role == "assistant":
                agent_name = self.message_handler.agent.name
                print(f"\n{GREEN}{BOLD}🤖 {agent_name.upper()}:{RESET}")
                content = self._extract_message_content(msg)
                # Format as markdown for better display
                self.console.print(Markdown(content, code_theme=CODE_THEME))
                self.display_divider()
                if "tool_calls" in msg:
                    for tool_call in msg["tool_calls"]:
                        self.display_tool_use(tool_call)
                self.display_divider()
            elif role == "consolidated":
                print(f"\n{YELLOW}📝 CONVERSATION SUMMARY:{RESET}")
                content = self._extract_message_content(msg)

                # Display metadata if available
                metadata = msg.get("metadata", {})
                if metadata:
                    consolidated_count = metadata.get(
                        "messages_consolidated", "unknown"
                    )
                    token_savings = metadata.get(
                        "original_token_count", 0
                    ) - metadata.get("consolidated_token_count", 0)
                    print(
                        f"{YELLOW}({consolidated_count} messages consolidated, ~{token_savings} tokens saved){RESET}"
                    )

                # Format the summary with markdown
                self.console.print(Markdown(content, code_theme=CODE_THEME))
                self.display_divider()

        print(f"{YELLOW}End of conversation history{RESET}\n")

    def _extract_message_content(self, message):
        """Extract the content from a message, handling different formats.

        Args:
            message: A message dictionary

        Returns:
            The extracted content as a string
        """
        content = message.get("content", "")

        # Handle different content structures
        if isinstance(content, str):
            pass
        elif isinstance(content, list) and content:
            # For content in the format of a list of content parts
            result = []
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        result.append(item.get("text", ""))
                    # Handle other content types if needed
            return "\n".join(result)

        content = re.sub(
            r"(?:```(?:json)?)?\s*<user_context_summary>.*?</user_context_summary>\s*(?:```)?",
            "",
            str(content),
            flags=re.DOTALL | re.IGNORECASE,
        )
        return str(content)

    def get_user_input(self, conversation_turns=None):
        """
        Get multiline input from the user with support for command history.

        Args:
            conversation_turns: Optional list of conversation turns for completions.

        Returns:
            The user input as a string.
        """
        print(f"\n{BLUE}{BOLD}👤 YOU:{RESET}")
        print(
            f"{YELLOW}🤖 "
            f"{self.message_handler.agent.name} 🧠 {self.message_handler.agent.get_model()}\n"
            f"(Press Enter for new line, Ctrl+S to submit, Up/Down for history)"
            f"{RESET}"
        )

        session = PromptSession(
            key_bindings=self.kb,
            completer=ChatCompleter(
                conversation_turns or self.message_handler.conversation_turns
            ),
        )

        try:
            user_input = session.prompt("> ")
            # Reset history position after submission
            self.message_handler.history_manager.reset_position()
            self.display_divider()
            return user_input
        except KeyboardInterrupt:
            # This should not be reached with our custom handler, but keep as fallback
            print(
                f"\n{YELLOW}{BOLD}🎮 Chat interrupted. Press Ctrl+C again to exit.{RESET}"
            )
            return ""  # Return empty string to continue the chat

    def start_streaming_response(self, agent_name: str):
        """
        Start streaming the assistant's response.

        Args:
            agent_name: The name of the agent providing the response.
        """
        print(f"\n{GREEN}{BOLD}🤖 {agent_name.upper()}:{RESET}")
        self.live = Live(
            "", console=self.console, refresh_per_second=24, vertical_overflow="crop"
        )
        self.live.start()

    def _setup_key_bindings(self):
        """Set up key bindings for multiline input."""
        kb = KeyBindings()

        @kb.add(Keys.ControlS)
        def _(event):
            """Submit on Ctrl+S."""
            if event.current_buffer.text.strip():
                event.current_buffer.validate_and_handle()

        @kb.add(Keys.Enter)
        def _(event):
            """Insert newline on Enter."""
            event.current_buffer.insert_text("\n")

        @kb.add("escape", "c")  # Alt+C
        def _(event):
            """Copy latest assistant response to clipboard."""
            self.copy_to_clipboard(self.latest_assistant_response)
            print("> ", end="")

        @kb.add(Keys.ControlC)
        def _(event):
            """Handle Ctrl+C with confirmation for exit."""
            current_time = time.time()
            if (
                hasattr(self, "_last_ctrl_c_time")
                and current_time - self._last_ctrl_c_time < 1
            ):
                print(f"\n{YELLOW}{BOLD}🎮 Confirmed exit. Goodbye!{RESET}")
                sys.exit(0)
            else:
                self._last_ctrl_c_time = current_time
                print(f"\n{YELLOW}Press Ctrl+C again within 1 seconds to exit.{RESET}")
                print("> ", end="")

        @kb.add(Keys.Up)
        def _(event):
            """Navigate to previous history entry."""
            buffer = event.current_buffer
            document = buffer.document

            # Check if cursor is at the first line's start
            cursor_position = document.cursor_position
            if document.cursor_position_row == 0 and cursor_position <= len(
                document.current_line
            ):
                # Get previous history entry
                prev_entry = self.message_handler.history_manager.get_previous()
                if prev_entry is not None:
                    # Replace current text with history entry
                    buffer.text = prev_entry
                    # Move cursor to end of text
                    buffer.cursor_position = len(prev_entry)
            else:
                # Regular up arrow behavior - move cursor up
                buffer.cursor_up()

        @kb.add(Keys.Down)
        def _(event):
            """Navigate to next history entry if cursor is at last line."""
            buffer = event.current_buffer
            document = buffer.document

            # Check if cursor is at the last line
            if document.cursor_position_row == document.line_count - 1:
                # Get next history entry
                next_entry = self.message_handler.history_manager.get_next()
                if next_entry is not None:
                    # Replace current text with history entry
                    buffer.text = next_entry
                    # Move cursor to end of text
                    buffer.cursor_position = len(next_entry)
            else:
                # Regular down arrow behavior - move cursor down
                buffer.cursor_down()

        return kb

    def print_welcome_message(self):
        """Print the welcome message for the chat."""
        # Get version information
        version = getattr(AgentCrew, "__version__", "Unknown")

        welcome_messages = [
            f"\n{YELLOW}{BOLD}🎮 Welcome to AgentCrew v{version} interactive chat!{RESET}",
            f"{YELLOW}Press Ctrl+C twice to exit.{RESET}",
            f"{YELLOW}Type 'exit' or 'quit' to end the session.{RESET}",
            f"{YELLOW}Use '/file <file_path>' to include a file in your message.{RESET}",
            f"{YELLOW}Use '/clear' to clear the conversation history.{RESET}",
            f"{YELLOW}Use '/think <budget>' to enable Claude's thinking mode (min 1024 tokens).{RESET}",
            f"{YELLOW}Use '/think 0' to disable thinking mode.{RESET}",
            f"{YELLOW}Use '/model [model_id]' to switch models or list available models.{RESET}",
            f"{YELLOW}Use '/jump <turn_number>' to rewind the conversation to a previous turn.{RESET}",
            f"{YELLOW}Use '/copy' to copy the latest assistant response to clipboard.{RESET}",
            f"{YELLOW}Press Alt/Meta+C to copy the latest assistant response.{RESET}",
            f"{YELLOW}Use Up/Down arrow keys to navigate through command history.{RESET}",
            f"{YELLOW}Use '/agent [agent_name]' to switch agents or list available agents.{RESET}",
            f"{YELLOW}Use '/list' to list saved conversations.{RESET}",
            f"{YELLOW}Use '/load <id>' or '/load <number>' to load a conversation.{RESET}",
            f"{YELLOW}Use '/consolidate [count]' to summarize older messages (default: 10 recent messages preserved).{RESET}",
            f"{YELLOW}Tool calls require confirmation before execution.{RESET}",
            f"{YELLOW}Use 'y' to approve once, 'n' to deny, 'all' to approve future calls to the same tool.{RESET}",
        ]

        for message in welcome_messages:
            print(message)
        self.display_divider()

    def display_token_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        total_cost: float,
        session_cost: float,
    ):
        """Display token usage and cost information."""
        print("\n")
        self.display_divider()
        print(
            f"{YELLOW}📊 Token Usage: Input: {input_tokens:,} | Output: {output_tokens:,} | "
            f"Total: {input_tokens + output_tokens:,} | Cost: ${total_cost:.4f} | Total: {session_cost:.4f}{RESET}"
        )
        self.display_divider()

    def _calculate_token_usage(self, input_tokens: int, output_tokens: int):
        total_cost = self.message_handler.agent.calculate_usage_cost(
            input_tokens, output_tokens
        )
        self.session_cost += total_cost
        return total_cost

    def start(self):
        self.print_welcome_message()

        self.session_cost = 0.0
        self._cached_conversations = []  # Add this to cache conversation list

        while True:
            try:
                # Get user input
                self.stop_loading_animation()  # Stop if any
                user_input = self.get_user_input()

                # Handle list command directly
                if user_input.strip() == "/list":
                    self._cached_conversations = (
                        self.message_handler.list_conversations()
                    )
                    self.display_conversations(self._cached_conversations)
                    continue

                # Handle load command directly
                if user_input.strip().startswith("/load "):
                    load_arg = user_input.strip()[
                        6:
                    ].strip()  # Extract argument after "/load "
                    if load_arg:
                        self.handle_load_conversation(load_arg)
                    else:
                        print(
                            f"{YELLOW}Usage: /load <conversation_id> or /load <number>{RESET}"
                        )
                    continue

                # Start loading animation while waiting for response
                if not user_input.startswith("/") or user_input.startswith("/file "):
                    self.start_loading_animation()

                # Process user input and commands
                # self.start_streaming_response(self.message_handler.agent_name)
                should_exit, was_cleared = asyncio.run(
                    self.message_handler.process_user_input(user_input)
                )

                # Exit if requested
                if should_exit:
                    break

                # Skip to next iteration if messages were cleared
                if was_cleared:
                    continue

                # Skip to next iteration if no messages to process
                if not self.message_handler.agent.history:
                    continue

                # Get assistant response
                assistant_response, input_tokens, output_tokens = asyncio.run(
                    self.message_handler.get_assistant_response()
                )

                # Ensure loading animation is stopped
                self.stop_loading_animation()

                total_cost = self._calculate_token_usage(input_tokens, output_tokens)

                if assistant_response:
                    # Calculate and display token usage
                    self.display_token_usage(
                        input_tokens, output_tokens, total_cost, self.session_cost
                    )
            except KeyboardInterrupt:
                self.stop_loading_animation()  # Stop loading on interrupt
                self.message_handler.stop_streaming = True
                # Display whatever text was generated so far
                if self.live:
                    last_response = self._live_text_data
                    self.message_handler._messages_append(
                        self.message_handler.agent.format_message(
                            MessageType.Assistant, {"message": last_response}
                        )
                    )
                    self.live.stop()
                    self.live = None
                self.display_message(
                    f"{YELLOW}Message streaming stopped by user.{RESET}"
                )
