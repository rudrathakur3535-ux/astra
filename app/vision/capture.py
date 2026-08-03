"""
Screen Capture Module for Project Astra.
Handles full-screen and region-of-interest (ROI) captures, image conversions, and base64 encoding.
"""

import base64
import io
import os
import time
from typing import Optional, Tuple, Union
from PIL import Image, ImageGrab
import numpy as np

from app.utils.logger import logger


class ScreenCapturer:
    """
    Captures primary desktop screen or specific rectangular regions.
    """

    def __init__(self, output_dir: str = "app/logs/screenshots"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def capture_full_screen(self) -> Image.Image:
        """
        Captures the full desktop screen.

        Returns:
            PIL.Image.Image: The captured screen image.
        """
        try:
            image = ImageGrab.grab(all_screens=False)
            logger.debug(f"Full screen captured. Size: {image.size}")
            return image
        except Exception as e:
            logger.warning(f"Native screen grab failed ({e}). Returning fallback screenshot.")
            return Image.new("RGB", (1920, 1080), color=(30, 30, 30))

    def capture_region(self, bbox: Tuple[int, int, int, int]) -> Image.Image:
        """
        Captures a specific region of interest (ROI) on screen.

        Args:
            bbox: Tuple of (left, top, right, bottom) pixel coordinates.

        Returns:
            PIL.Image.Image: The cropped region image.
        """
        try:
            image = ImageGrab.grab(bbox=bbox)
            logger.debug(f"Region captured. Bounding Box: {bbox}, Size: {image.size}")
            return image
        except Exception as e:
            logger.error(f"Failed to capture region {bbox}: {e}", exc_info=True)
            raise RuntimeError(f"Region capture failed: {e}") from e

    @staticmethod
    def to_opencv(image: Image.Image) -> np.ndarray:
        """
        Converts a PIL Image to OpenCV BGR numpy array format.
        """
        rgb_array = np.array(image.convert("RGB"))
        # RGB to BGR
        return rgb_array[:, :, ::-1].copy()

    @staticmethod
    def to_base64(image: Image.Image, format: str = "PNG") -> str:
        """
        Converts a PIL Image to a base64 encoded string for LLM payloads.
        """
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return encoded

    def save_capture(self, image: Image.Image, filename_prefix: str = "capture") -> str:
        """
        Saves a PIL Image to the screenshots directory with a timestamped filename.

        Returns:
            str: Absolute file path to saved image.
        """
        timestamp = int(time.time())
        filename = f"{filename_prefix}_{timestamp}.png"
        filepath = os.path.abspath(os.path.join(self.output_dir, filename))
        image.save(filepath, format="PNG")
        logger.info(f"Saved screen capture to {filepath}")
        return filepath
