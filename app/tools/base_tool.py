from abc import ABC, abstractmethod
from typing import Dict, Any
from app.models.tool_response import ToolResponse

class BaseTool(ABC):
    """Abstract Base Class for all Astra tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier name of the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable explanation of what the tool does."""
        pass

    @property
    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """JSON Schema dictionary defining required and optional parameters."""
        pass

    @property
    def requires_permission(self) -> bool:
        """Indicates whether this tool requires explicit user permission approval."""
        return False

    @abstractmethod
    def execute(self, **kwargs) -> ToolResponse:
        """Executes the tool with the provided validated keyword arguments.
        
        Returns:
            ToolResponse object containing execution data or error details.
        """
        pass

    def to_openai_schema(self) -> Dict[str, Any]:
        """Formats tool declaration into OpenAI API tool/function call format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema
            }
        }
