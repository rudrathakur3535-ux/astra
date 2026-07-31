from typing import Dict, Any
import psutil
from app.tools.base_tool import BaseTool
from app.models.tool_response import ToolResponse
from app.utils.logger import logger

class GetSystemInfoTool(BaseTool):
    """Tool to inspect RAM usage, CPU percent, disk space, and running desktop processes."""

    @property
    def name(self) -> str:
        return "get_system_info"

    @property
    def description(self) -> str:
        return "Returns current RAM memory usage, CPU percentage, disk space, and running process statistics."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
        }

    def execute(self) -> ToolResponse:
        try:
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            cpu_percent = psutil.cpu_percent(interval=0.1)

            # Get top 5 memory consuming processes
            top_processes = []
            for proc in sorted(psutil.process_iter(['pid', 'name', 'memory_percent']), key=lambda p: p.info['memory_percent'] or 0, reverse=True)[:5]:
                try:
                    top_processes.append(f"{proc.info['name']} ({proc.info['memory_percent']:.1f}%)")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            info_data = {
                "ram_percent": mem.percent,
                "ram_used_gb": round(mem.used / (1024**3), 2),
                "ram_total_gb": round(mem.total / (1024**3), 2),
                "cpu_percent": cpu_percent,
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "top_processes": top_processes
            }

            logger.info("Retrieved system info metrics.")
            return ToolResponse(
                success=True,
                tool_name=self.name,
                data=info_data
            )

        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return ToolResponse(
                success=False,
                tool_name=self.name,
                error_message=f"Could not retrieve system information: {e}"
            )
