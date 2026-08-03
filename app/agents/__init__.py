"""
Agents Package for Project Astra.
Subsystem orchestrating ManagerAgent and 7 Specialist Agents (Research, Browser, Coding, Memory, Vision, Desktop, Communication).
"""

from app.agents.base_agent import BaseAgent
from app.agents.manager_agent import ManagerAgent
from app.agents.research_agent import ResearchAgent
from app.agents.browser_agent import BrowserAgent
from app.agents.coding_agent import CodingAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.vision_agent import VisionAgent
from app.agents.desktop_agent import DesktopAgent
from app.agents.communication_agent import CommunicationAgent
from app.orchestrator.agent_registry import agent_registry


def register_default_agents() -> None:
    """Registers default specialist agents into AgentRegistry."""
    agent_registry.register(ManagerAgent())
    agent_registry.register(ResearchAgent())
    agent_registry.register(BrowserAgent())
    agent_registry.register(CodingAgent())
    agent_registry.register(MemoryAgent())
    agent_registry.register(VisionAgent())
    agent_registry.register(DesktopAgent())
    agent_registry.register(CommunicationAgent())


# Auto-register agents on package import
register_default_agents()

__all__ = [
    "BaseAgent",
    "ManagerAgent",
    "ResearchAgent",
    "BrowserAgent",
    "CodingAgent",
    "MemoryAgent",
    "VisionAgent",
    "DesktopAgent",
    "CommunicationAgent",
    "register_default_agents"
]
