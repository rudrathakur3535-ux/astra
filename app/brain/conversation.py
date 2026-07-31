from typing import List, Dict, Any, Optional
from app.brain.prompts import get_system_prompt
from app.config import settings
from app.utils.logger import logger

class ConversationManager:
    """Manages active conversation context, message history, and memory buffers."""

    def __init__(self, user_name: Optional[str] = None, max_history_messages: int = 40):
        self.user_name = user_name or settings.USER_NAME
        self.max_history_messages = max_history_messages
        self._history: List[Dict[str, str]] = []
        self._initialize_system_prompt()

    def _initialize_system_prompt(self) -> None:
        """Initializes system prompt as the foundational message in history."""
        system_content = get_system_prompt(self.user_name)
        self._history = [{"role": "system", "content": system_content}]
        logger.debug(f"Initialized conversation manager for user: {self.user_name}")

    def add_user_message(self, content: str) -> None:
        """Adds a user message to the conversation history."""
        self._history.append({"role": "user", "content": content})
        self._trim_history()

    def add_assistant_message(self, content: str) -> None:
        """Adds an assistant response message to the conversation history."""
        self._history.append({"role": "assistant", "content": content})
        self._trim_history()

    def get_messages(self) -> List[Dict[str, str]]:
        """Returns the full message list formatted for LLM API calls."""
        return list(self._history)

    def clear(self) -> None:
        """Clears all conversation history while preserving system prompt."""
        self._initialize_system_prompt()
        logger.info("Conversation history cleared.")

    def get_user_messages_count(self) -> int:
        """Returns the count of non-system messages in history."""
        return sum(1 for msg in self._history if msg["role"] != "system")

    def get_formatted_history(self) -> List[Dict[str, str]]:
        """Returns user and assistant messages for displaying history."""
        return [msg for msg in self._history if msg["role"] != "system"]

    def _trim_history(self) -> None:
        """Trims old messages if history exceeds max_history_messages, keeping system prompt."""
        system_msgs = [msg for msg in self._history if msg["role"] == "system"]
        chat_msgs = [msg for msg in self._history if msg["role"] != "system"]

        if len(chat_msgs) > self.max_history_messages:
            chat_msgs = chat_msgs[-self.max_history_messages:]
            self._history = system_msgs + chat_msgs
            logger.debug(f"Trimmed history to last {self.max_history_messages} chat messages.")
