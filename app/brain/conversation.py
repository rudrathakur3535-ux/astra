from typing import List, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class Message(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ConversationManager:
    def __init__(self, max_history_turns: int = 10):
        self.max_history_turns = max_history_turns
        self.history: List[Message] = []

    def add_message(self, role: str, content: str) -> Message:
        msg = Message(role=role, content=content)
        self.history.append(msg)
        self.trim_history()
        return msg

    def trim_history(self) -> None:
        if len(self.history) > self.max_history_turns * 2:
            self.history = self.history[-(self.max_history_turns * 2):]

    def get_messages(self) -> List[Dict[str, str]]:
        return [{"role": m.role, "content": m.content} for m in self.history]
