import time
import json
from typing import Dict, Any, Union
from app.models.tool_request import ToolRequest
from app.models.tool_response import ToolResponse
from app.tools.tool_registry import ToolRegistry, tool_registry
from app.security.permissions import permission_manager
from app.utils.logger import logger

class ToolRouter:
    """Tool Router validating, authorizing, and executing structured tool invocations."""

    def __init__(self, registry: Optional[ToolRegistry] = None):
        self.registry = registry or tool_registry

    def execute(self, request_input: Union[ToolRequest, Dict[str, Any], str]) -> ToolResponse:
        """Executes a tool request securely and returns a structured ToolResponse.
        
        Args:
            request_input: ToolRequest model, dict, or JSON string.
            
        Returns:
            ToolResponse object.
        """
        start_time = time.time()

        # Parse request input into ToolRequest object
        try:
            if isinstance(request_input, str):
                parsed = json.loads(request_input)
                request = ToolRequest(**parsed)
            elif isinstance(request_input, dict):
                request = ToolRequest(**request_input)
            elif isinstance(request_input, ToolRequest):
                request = request_input
            else:
                raise ValueError(f"Invalid tool request input format: {type(request_input)}")
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000.0
            logger.error(f"Failed to parse tool request: {e}")
            return ToolResponse(
                success=False,
                tool_name="unknown",
                error_message=f"Invalid tool request schema: {e}",
                execution_time_ms=elapsed
            )

        tool_name = request.tool_name
        arguments = request.arguments

        logger.info(f"Routing tool request '{tool_name}' with args: {arguments}")

        # Look up tool in registry
        tool = self.registry.get_tool(tool_name)
        if not tool:
            elapsed = (time.time() - start_time) * 1000.0
            error_msg = f"Tool '{tool_name}' is not registered in ToolRegistry."
            logger.error(error_msg)
            return ToolResponse(
                success=False,
                tool_name=tool_name,
                error_message=error_msg,
                execution_time_ms=elapsed
            )

        # Permission authorization check
        if tool.requires_permission:
            authorized = permission_manager.check_permission(tool_name, arguments)
            if not authorized:
                elapsed = (time.time() - start_time) * 1000.0
                error_msg = f"Permission denied for executing tool '{tool_name}'."
                logger.warning(error_msg)
                return ToolResponse(
                    success=False,
                    tool_name=tool_name,
                    error_message=error_msg,
                    execution_time_ms=elapsed
                )

        # Execute tool
        try:
            response = tool.execute(**arguments)
            elapsed = (time.time() - start_time) * 1000.0
            response.execution_time_ms = elapsed
            logger.info(f"Tool '{tool_name}' executed in {elapsed:.2f}ms (Success: {response.success})")
            return response
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000.0
            logger.error(f"Unexpected error executing tool '{tool_name}': {e}", exc_info=True)
            return ToolResponse(
                success=False,
                tool_name=tool_name,
                error_message=f"Execution error: {e}",
                execution_time_ms=elapsed
            )

tool_router = ToolRouter()
