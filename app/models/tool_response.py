from typing import Any, Optional, Dict
from pydantic import BaseModel, Field

class ToolResponse(BaseModel):
    """Pydantic model representing a structured tool execution result."""
    success: bool = Field(..., description="Whether the tool execution succeeded")
    tool_name: str = Field(..., description="Name of the executed tool")
    data: Optional[Any] = Field(default=None, description="Data output returned by the tool")
    error_message: Optional[str] = Field(default=None, description="Error message if execution failed")
    execution_time_ms: float = Field(default=0.0, description="Execution duration in milliseconds")
