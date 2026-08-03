"""
Vision Tools Module for Project Astra.
Exposes screen capture, region capture, and grid annotation tools to Astra's tool registry.
"""

from typing import Dict, Any, Optional, Tuple
from app.tools.base_tool import BaseTool
from app.models.tool_response import ToolResponse
from app.vision.vision_service import VisionService
from app.utils.logger import logger


class CaptureScreenTool(BaseTool):
    """Tool to capture full desktop screen image or grid annotated image."""

    def __init__(self, vision_service: Optional[VisionService] = None):
        self.service = vision_service or VisionService()

    @property
    def name(self) -> str:
        return "vision.capture_screen"

    @property
    def description(self) -> str:
        return "Captures the full desktop screen image and saves it to disk. Can optionally overlay a coordinate grid."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "grid_overlay": {
                    "type": "boolean",
                    "description": "If true, draws a coordinate grid overlay on the image to locate UI sectors.",
                    "default": False
                },
                "rows": {
                    "type": "integer",
                    "description": "Number of grid rows if grid_overlay is true.",
                    "default": 4
                },
                "cols": {
                    "type": "integer",
                    "description": "Number of grid columns if grid_overlay is true.",
                    "default": 4
                }
            }
        }

    def execute(self, grid_overlay: bool = False, rows: int = 4, cols: int = 4) -> ToolResponse:
        try:
            if grid_overlay:
                result = self.service.create_annotated_grid_capture(rows=rows, cols=cols)
            else:
                result = self.service.capture_and_encode_screen(save_to_disk=True)

            logger.info(f"Captured screen image (grid_overlay={grid_overlay}). Saved to {result.get('filepath')}")

            return ToolResponse(
                success=True,
                tool_name=self.name,
                data={
                    "filepath": result.get("filepath"),
                    "width": result.get("width"),
                    "height": result.get("height"),
                    "grid_overlay": grid_overlay,
                    "message": f"Screen successfully captured and saved to {result.get('filepath')}"
                }
            )
        except Exception as e:
            logger.error(f"Failed to execute vision.capture_screen: {e}", exc_info=True)
            return ToolResponse(
                success=False,
                tool_name=self.name,
                error_message=f"Screen capture failed: {e}"
            )


class AnalyzeScreenTool(BaseTool):
    """Tool to prepare desktop screen base64 payload for visual model analysis."""

    def __init__(self, vision_service: Optional[VisionService] = None):
        self.service = vision_service or VisionService()

    @property
    def name(self) -> str:
        return "vision.analyze_screen"

    @property
    def description(self) -> str:
        return "Captures current desktop screen and returns base64 image payload ready for visual LLM perception analysis."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "max_dimension": {
                    "type": "integer",
                    "description": "Maximum width/height dimension to resize image for vision API token optimization.",
                    "default": 1024
                }
            }
        }

    def execute(self, max_dimension: int = 1024) -> ToolResponse:
        try:
            result = self.service.capture_and_encode_screen(max_dimension=max_dimension, save_to_disk=True)
            logger.info("Captured screen payload for vision analysis.")

            return ToolResponse(
                success=True,
                tool_name=self.name,
                data={
                    "base64_image": result.get("base64_image"),
                    "width": result.get("width"),
                    "height": result.get("height"),
                    "filepath": result.get("filepath"),
                    "message": "Screen captured and encoded as base64 payload for visual analysis."
                }
            )
        except Exception as e:
            logger.error(f"Failed to execute vision.analyze_screen: {e}", exc_info=True)
            return ToolResponse(
                success=False,
                tool_name=self.name,
                error_message=f"Screen analysis payload capture failed: {e}"
            )


class CaptureRegionTool(BaseTool):
    """Tool to capture a specific screen region by coordinates."""

    def __init__(self, vision_service: Optional[VisionService] = None):
        self.service = vision_service or VisionService()

    @property
    def name(self) -> str:
        return "vision.capture_region"

    @property
    def description(self) -> str:
        return "Captures a rectangular region of interest on the screen given left, top, right, bottom coordinates."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "left": {"type": "integer", "description": "Left X coordinate"},
                "top": {"type": "integer", "description": "Top Y coordinate"},
                "right": {"type": "integer", "description": "Right X coordinate"},
                "bottom": {"type": "integer", "description": "Bottom Y coordinate"}
            },
            "required": ["left", "top", "right", "bottom"]
        }

    def execute(self, left: int, top: int, right: int, bottom: int) -> ToolResponse:
        try:
            bbox = (left, top, right, bottom)
            result = self.service.capture_region_and_encode(bbox=bbox)

            logger.info(f"Captured region {bbox}")
            return ToolResponse(
                success=True,
                tool_name=self.name,
                data={
                    "base64_image": result.get("base64_image"),
                    "width": result.get("width"),
                    "height": result.get("height"),
                    "bbox": bbox,
                    "message": f"Successfully captured region {bbox}"
                }
            )
        except Exception as e:
            logger.error(f"Failed to capture region {left},{top},{right},{bottom}: {e}", exc_info=True)
            return ToolResponse(
                success=False,
                tool_name=self.name,
                error_message=f"Region capture failed: {e}"
            )
