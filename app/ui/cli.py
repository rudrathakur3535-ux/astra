import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.theme import Theme

from app.config import settings
from app.services.chat_service import ChatService
from app.voice import VoiceState
from app.utils.logger import logger

# Custom Rich theme for Astra terminal UI
custom_theme = Theme({
    "astra.banner": "bold cyan",
    "astra.user": "bold green",
    "astra.assistant": "bold bright_magenta",
    "astra.voice": "bold yellow",
    "astra.system": "yellow",
    "astra.error": "bold red"
})

console = Console(theme=custom_theme)

class TerminalUI:
    """Terminal User Interface for Project Astra using Rich."""

    def __init__(self, chat_service: Optional[ChatService] = None):
        self.chat_service = chat_service or ChatService()
        self.user_name = self.chat_service.user_name

        # Register UI callbacks with audio manager
        self.chat_service.audio_manager.on_state_change = self._on_voice_state_change
        self.chat_service.audio_manager.on_transcript = self._on_voice_transcript

    def display_welcome_banner(self) -> None:
        """Renders the Astra startup banner in the terminal."""
        banner_content = (
            f"[bold cyan]Project Astra - Personal AI OS[/bold cyan]\n"
            f"[dim]Version 0.1.0 | Phase 1 (Day 3: Ears & Natural Voice Subsystem)[/dim]\n\n"
            f"Welcome back, [bold green]{self.user_name}[/bold green]!\n"
            f"[yellow]Voice Engine[/yellow]: Type [yellow]/voice on[/yellow] to enable continuous microphone listening ('Hey Astra').\n"
            f"Type your message to start chatting, or type [yellow]/help[/yellow] for available commands."
        )
        console.print(Panel(banner_content, border_style="cyan", expand=False))

    def run(self) -> None:
        """Starts the interactive terminal chat loop."""
        self.display_welcome_banner()

        while True:
            try:
                # Get input from user
                user_input = Prompt.ask(f"\n[astra.user]{self.user_name}[/astra.user]").strip()

                if not user_input:
                    continue

                # Handle slash commands
                if user_input.startswith("/"):
                    cmd_result = self.chat_service.execute_command(user_input)
                    action = cmd_result.get("action")

                    if action == "exit":
                        console.print(f"\n[astra.assistant]Astra:[/astra.assistant] {cmd_result['message']}\n")
                        break
                    elif action == "history":
                        self._render_history(cmd_result.get("history", []))
                    else:
                        console.print(f"\n[astra.system]{cmd_result['message']}[/astra.system]")
                    continue

                # Stream response from Astra
                console.print(f"\n[astra.assistant]Astra:[/astra.assistant] ", end="")
                
                stream = self.chat_service.process_user_input(user_input)
                if stream:
                    full_text = ""
                    for chunk in stream:
                        console.print(chunk, end="")
                        full_text += chunk
                    console.print()  # Newline after stream finishes

            except (KeyboardInterrupt, EOFError):
                self.chat_service.audio_manager.stop()
                console.print(f"\n\n[astra.assistant]Astra:[/astra.assistant] Goodbye {self.user_name}. Shutdown initiated.")
                logger.info("Terminal session ended by user signal.")
                break
            except Exception as e:
                console.print(f"\n[astra.error]An unexpected error occurred: {e}[/astra.error]")
                logger.error(f"UI Loop Exception: {e}", exc_info=True)

    def _on_voice_state_change(self, state: VoiceState) -> None:
        """Callback triggered when Voice Subsystem changes state."""
        state_messages = {
            VoiceState.LISTENING_FOR_WAKEWORD: "[astra.voice][Voice]: Listening for 'Hey Astra'...[/astra.voice]",
            VoiceState.RECORDING_USER_PROMPT: "[astra.voice][Voice]: Listening to your prompt...[/astra.voice]",
            VoiceState.PROCESSING_THOUGHTS: "[astra.voice][Voice]: Astra is thinking...[/astra.voice]",
            VoiceState.SPEAKING_RESPONSE: "[astra.voice][Voice]: Astra is speaking...[/astra.voice]",
            VoiceState.OFFLINE: "[astra.voice][Voice]: Voice engine offline.[/astra.voice]"
        }
        msg = state_messages.get(state)
        if msg:
            console.print(f"\n{msg}")

    def _on_voice_transcript(self, sender: str, transcript: str) -> None:
        """Callback triggered when Voice Subsystem transcribes audio."""
        if sender == "user":
            console.print(f"\n[astra.user][Voice] {self.user_name}:[/astra.user] {transcript}")
        elif sender == "assistant":
            console.print(f"[astra.assistant][Voice] Astra:[/astra.assistant] {transcript}")

    def _render_history(self, history: list) -> None:
        """Renders formatted session history in terminal."""
        if not history:
            console.print("[astra.system]No history to display.[/astra.system]")
            return

        console.print("\n[bold cyan]--- Session Conversation History ---[/bold cyan]")
        for msg in history:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                console.print(f"[astra.user]{self.user_name}:[/astra.user] {content}")
            elif role == "assistant":
                console.print(f"[astra.assistant]Astra:[/astra.assistant] {content}")
        console.print("[bold cyan]------------------------------------[/bold cyan]")
