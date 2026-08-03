"""
Hexagonal Adapters Package for Project Astra OS.
"""

from app.adapters.sqlite_adapter import SQLiteAdapter
from app.adapters.chromadb_adapter import ChromaDBAdapter
from app.adapters.chromadb_knowledge_adapter import ChromaDBKnowledgeAdapter
from app.adapters.filesystem_adapter import FilesystemAdapter
from app.adapters.gmail_adapter import GmailAdapter
from app.adapters.calendar_adapter import CalendarAdapter
from app.adapters.notification_adapter import NotificationAdapter
from app.adapters.playwright_adapter import PlaywrightAdapter
from app.adapters.ollama_adapter import OllamaAdapter
from app.adapters.mcp_adapter import MCPAdapter

__all__ = [
    "SQLiteAdapter",
    "ChromaDBAdapter",
    "ChromaDBKnowledgeAdapter",
    "FilesystemAdapter",
    "GmailAdapter",
    "CalendarAdapter",
    "NotificationAdapter",
    "PlaywrightAdapter",
    "OllamaAdapter",
    "MCPAdapter"
]
