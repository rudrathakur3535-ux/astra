import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    """Pydantic model representing a structured tool invocation request."""
    tool_name: str = Field(..., description="Name of the registered tool to invoke")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Key-value arguments for tool execution")
    call_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique invocation call ID")
