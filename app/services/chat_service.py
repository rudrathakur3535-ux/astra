from typing import Generator, Optional, Callable, Dict, Any
from app.brain.conversation import ConversationManager
from app.brain.llm import LLMClient
from app.config import settings
from app.utils.logger import logger

class ChatService:
    """Service layer coordinating conversation state, system commands, and LLM streaming."""

    def __init__(self, user_name: Optional[str] = None):
        self.user_name = user_name or settings.USER_NAME
        self.conversation = ConversationManager(user_name=self.user_name)
        self.llm_client = LLMClient()
        logger.info(f"ChatService initialized for user: {self.user_name}")

    def process_user_input(
        self,
        user_input: str,
        on_chunk: Optional[Callable[[str], None]] = None
    ) -> Optional[Generator[str, None, None]]:
        """Processes user input string, handles slash commands, or routes to LLM stream.
        
        Args:
            user_input: Raw user input text.
            on_chunk: Callback function for streaming text chunks.
            
        Returns:
            Generator yielding text chunks if sending to LLM, or None if command handled.
        """
        trimmed_input = user_input.strip()
        if not trimmed_input:
            return None

        # Add user input to conversation history
        self.conversation.add_user_message(trimmed_input)
        logger.info(f"User message received ({len(trimmed_input)} chars)")

        # Prepare messages context for LLM
        messages = self.conversation.get_messages()

        def stream_wrapper() -> Generator[str, None, None]:
            full_response_parts = []
            try:
                for chunk in self.llm_client.stream_completion(
                    messages=messages,
                    on_chunk=on_chunk
                ):
                    full_response_parts.append(chunk)
                    yield chunk

                full_response = "".join(full_response_parts)
                # Store assistant's full response into conversation memory
                if full_response.strip():
                    self.conversation.add_assistant_message(full_response)
                    logger.info(f"Assistant response stored ({len(full_response)} chars)")

            except Exception as e:
                logger.error(f"Error during message stream processing: {e}")
                error_msg = f"\n[System Error]: {e}"
                if on_chunk:
                    on_chunk(error_msg)
                yield error_msg

        return stream_wrapper()

    def execute_command(self, command_str: str) -> Dict[str, Any]:
        """Executes system slash commands.
        
        Supported commands:
            /help: Show help menu
            /clear: Clear conversation context
            /history: Show conversation history
            /model [name]: View or change active LLM model
            /exit: Exit Astra
            
        Returns:
            Dict containing status and command result message.
        """
        cmd_parts = command_str.strip().split(maxsplit=1)
        command = cmd_parts[0].lower()
        arg = cmd_parts[1].strip() if len(cmd_parts) > 1 else ""

        if command in ("/exit", "/quit"):
            return {"action": "exit", "message": f"Goodbye {self.user_name}."}

        elif command == "/clear":
            self.conversation.clear()
            return {"action": "clear", "message": "Conversation history cleared."}

        elif command == "/history":
            history = self.conversation.get_formatted_history()
            if not history:
                return {"action": "history", "message": "No conversation history yet."}
            return {"action": "history", "history": history}

        elif command == "/model":
            if arg:
                self.llm_client.set_model(arg)
                return {"action": "model", "message": f"Model switched to: [bold cyan]{arg}[/bold cyan]"}
            else:
                return {"action": "model", "message": f"Current active model: [bold cyan]{self.llm_client.model_name}[/bold cyan]"}

        elif command == "/help":
            help_text = (
                "[bold cyan]Available Astra Commands:[/bold cyan]\n"
                "  [green]/clear[/green]   - Clear active conversation memory\n"
                "  [green]/history[/green] - View session conversation history\n"
                "  [green]/model[/green]   - View or switch active LLM model (e.g. /model gpt-4o)\n"
                "  [green]/help[/green]    - Show this help menu\n"
                "  [green]/exit[/green]    - Exit Project Astra"
            )
            return {"action": "help", "message": help_text}

        else:
            return {"action": "unknown", "message": f"Unknown command: '{command}'. Type /help for available commands."}
