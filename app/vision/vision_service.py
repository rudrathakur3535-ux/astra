"""
Vision Service Module for Project Astra.
Provides high-level visual analysis APIs, screen inspection, and coordinate location helpers.
"""

from typing import Dict, Any, Optional, Tuple
import os

from app.vision.capture import ScreenCapturer
from app.vision.processor import ImageProcessor
from app.utils.logger import logger


class VisionService:
    """
    High-level visual perception manager for desktop screen understanding.
    """

    def __init__(self, capturer: Optional[ScreenCapturer] = None):
        self.capturer = capturer or ScreenCapturer()
        self.processor = ImageProcessor()

    def capture_and_encode_screen(
        self,
        max_dimension: int = 1024,
        save_to_disk: bool = True
    ) -> Dict[str, Any]:
        """
        Captures the current desktop screen, resizes for LLM optimization, and encodes as base64.

        Returns:
            Dict containing:
                - 'base64_image': Encoded PNG string
                - 'width': Image width
                - 'height': Image height
                - 'filepath': File path if saved to disk, else None
        """
        raw_image = self.capturer.capture_full_screen()
        processed_image = self.processor.resize_max_dimension(raw_image, max_dim=max_dimension)
        base64_str = self.capturer.to_base64(processed_image, format="PNG")

        filepath = None
        if save_to_disk:
            filepath = self.capturer.save_capture(raw_image, filename_prefix="astra_vision")

        return {
            "base64_image": base64_str,
            "width": processed_image.width,
            "height": processed_image.height,
            "filepath": filepath,
            "original_size": raw_image.size
        }

    def capture_region_and_encode(
        self,
        bbox: Tuple[int, int, int, int],
        max_dimension: int = 1024
    ) -> Dict[str, Any]:
        """
        Captures a specific screen region and returns base64 encoding.
        """
        raw_image = self.capturer.capture_region(bbox)
        processed_image = self.processor.resize_max_dimension(raw_image, max_dim=max_dimension)
        base64_str = self.capturer.to_base64(processed_image, format="PNG")

        return {
            "base64_image": base64_str,
            "width": processed_image.width,
            "height": processed_image.height,
            "bbox": bbox
        }

    def create_annotated_grid_capture(self, rows: int = 4, cols: int = 4) -> Dict[str, Any]:
        """
        Captures full screen and applies a coordinate grid overlay for quadrant target identification.
        """
        raw_image = self.capturer.capture_full_screen()
        grid_image = self.processor.draw_grid_overlay(raw_image, rows=rows, cols=cols)
        resized_grid = self.processor.resize_max_dimension(grid_image, max_dim=1024)
        base64_str = self.capturer.to_base64(resized_grid, format="PNG")

        filepath = self.capturer.save_capture(grid_image, filename_prefix="astra_grid")

        return {
            "base64_image": base64_str,
            "width": resized_grid.width,
            "height": resized_grid.height,
            "filepath": filepath,
            "rows": rows,
            "cols": cols
        }
