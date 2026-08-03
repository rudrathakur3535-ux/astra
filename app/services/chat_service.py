import json
from typing import Generator, Optional, Callable, Dict, Any, List
from app.brain.conversation import ConversationManager
from app.brain.llm import LLMClient
from app.tools import tool_registry, tool_router
from app.models.tool_request import ToolRequest
from app.voice import AudioManager, VoiceState
from app.avatar import avatar_state_manager
from app.config import settings
from app.utils.logger import logger

class ChatService:
    """Service layer coordinating conversation state, system commands, tool calling, and Voice Subsystem."""

    def __init__(self, user_name: Optional[str] = None):
        self.user_name = user_name or settings.USER_NAME
        self.conversation = ConversationManager(user_name=self.user_name)
        self.llm_client = LLMClient()
        self.audio_manager = AudioManager()

        # Connect audio manager to chat service processor
        self.audio_manager.set_chat_processor(self.get_response_sync)
        logger.info(f"ChatService initialized for user: {self.user_name}")

    def process_user_input(
        self,
        user_input: str,
        on_chunk: Optional[Callable[[str], None]] = None
    ) -> Optional[Generator[str, None, None]]:
        """Processes user input string, handles slash commands, tool execution, and LLM output.
        
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

        def stream_wrapper() -> Generator[str, None, None]:
            avatar_state_manager.set_thinking(True)
            messages = self.conversation.get_messages()
            tools_schema = tool_registry.get_openai_tools_schema()

            # 1. Check if query requires tool calls
            content, tool_calls = self.llm_client.chat_completion(messages=messages, tools=tools_schema)
            avatar_state_manager.set_thinking(False)

            if tool_calls:
                # Add assistant message with tool calls to memory
                self.conversation._history.append({
                    "role": "assistant",
                    "content": content,
                    "tool_calls": [
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": {
                                "name": tc["name"],
                                "arguments": json.dumps(tc["arguments"])
                            }
                        } for tc in tool_calls
                    ]
                })

                # Execute each tool call securely via ToolRouter
                for tc in tool_calls:
                    tool_name = tc["name"]
                    arguments = tc["arguments"]
                    call_id = tc["id"]

                    status_msg = f"\n[bold yellow]⚡ [Executing Desktop Tool]: {tool_name}({arguments})[/bold yellow]\n"
                    if on_chunk:
                        on_chunk(status_msg)
                    yield status_msg

                    request = ToolRequest(tool_name=tool_name, arguments=arguments, call_id=call_id)
                    tool_response = tool_router.execute(request)

                    # Append tool execution result back to conversation context
                    tool_result_content = json.dumps({
                        "success": tool_response.success,
                        "data": tool_response.data,
                        "error": tool_response.error_message
                    })

                    self.conversation._history.append({
                        "role": "tool",
                        "tool_call_id": call_id,
                        "content": tool_result_content
                    })

                # Stream final synthesized assistant response
                updated_messages = self.conversation.get_messages()
                full_parts = []
                for chunk in self.llm_client.stream_completion(messages=updated_messages, on_chunk=on_chunk):
                    full_parts.append(chunk)
                    yield chunk

                full_response = "".join(full_parts)
                if full_response.strip():
                    self.conversation.add_assistant_message(full_response)

            else:
                # Direct streaming response without tool calling
                if content and not settings.is_api_key_valid:
                    if on_chunk:
                        on_chunk(content)
                    yield content
                    self.conversation.add_assistant_message(content)
                else:
                    full_parts = []
                    for chunk in self.llm_client.stream_completion(messages=messages, on_chunk=on_chunk):
                        full_parts.append(chunk)
                        yield chunk

                    full_response = "".join(full_parts)
                    if full_response.strip():
                        self.conversation.add_assistant_message(full_response)

        return stream_wrapper()

    def get_response_sync(self, user_input: str) -> str:
        """Synchronous wrapper to get LLM response string for voice output."""
        stream = self.process_user_input(user_input)
        if not stream:
            return ""
        return "".join(list(stream))

    def execute_command(self, command_str: str) -> Dict[str, Any]:
        """Executes system slash commands.
        
        Supported commands:
            /tools: List all registered desktop tools
            /help: Show help menu
            /clear: Clear conversation context
            /history: Show conversation history
            /model [name]: View or change active LLM model
            /voice [on|off|status]: Toggle or check voice mode
            /exit: Exit Astra
            
        Returns:
            Dict containing status and command result message.
        """
        cmd_parts = command_str.strip().split(maxsplit=1)
        command = cmd_parts[0].lower()
        arg = cmd_parts[1].strip() if len(cmd_parts) > 1 else ""

        if command in ("/exit", "/quit"):
            self.audio_manager.stop()
            return {"action": "exit", "message": f"Goodbye {self.user_name}."}

        elif command == "/tools":
            tools = tool_registry.list_tools()
            tools_fmt = "\n".join([f"  • [bold cyan]{t}[/bold cyan]: {tool_registry.get_tool(t).description}" for t in tools])
            return {"action": "tools", "message": f"[bold yellow]Registered Desktop Tools ({len(tools)}):[/bold yellow]\n{tools_fmt}"}

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

        elif command == "/voice":
            if arg.lower() == "on":
                self.audio_manager.start()
                return {"action": "voice", "message": "Voice Subsystem [bold green]ACTIVATED[/bold green] (Listening for 'Hey Astra')."}
            elif arg.lower() == "off":
                self.audio_manager.stop()
                return {"action": "voice", "message": "Voice Subsystem [bold red]DEACTIVATED[/bold red]."}
            else:
                status_str = "ACTIVE" if self.audio_manager._running else "INACTIVE"
                return {"action": "voice", "message": f"Voice Subsystem Status: [bold yellow]{status_str}[/bold yellow]"}

        elif command == "/help":
            help_text = (
                "[bold cyan]Available Astra Commands:[/bold cyan]\n"
                "  [green]/tools[/green]         - List all registered desktop & system tools\n"
                "  [green]/voice on|off[/green] - Turn background microphone & voice engine on/off\n"
                "  [green]/clear[/green]         - Clear active conversation memory\n"
                "  [green]/history[/green]       - View session conversation history\n"
                "  [green]/model[/green]         - View or switch active LLM model (e.g. /model gpt-4o)\n"
                "  [green]/help[/green]          - Show this help menu\n"
                "  [green]/exit[/green]          - Exit Project Astra"
            )
            return {"action": "help", "message": help_text}

        else:
            return {"action": "unknown", "message": f"Unknown command: '{command}'. Type /help for available commands."}
