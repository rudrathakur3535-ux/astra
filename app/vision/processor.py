"""
Image Processor Module for Project Astra.
Handles image scaling, compression, OpenCV annotations, grid overlays, and target bounding box highlights.
"""

from typing import List, Tuple, Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from app.utils.logger import logger


class ImageProcessor:
    """
    Processes screen capture images for visual AI model ingestion and user UI overlays.
    """

    @staticmethod
    def resize_max_dimension(image: Image.Image, max_dim: int = 1024) -> Image.Image:
        """
        Resizes an image maintaining aspect ratio so its maximum dimension does not exceed max_dim.
        Optimizes vision token costs for LLM APIs.
        """
        width, height = image.size
        if width <= max_dim and height <= max_dim:
            return image

        if width > height:
            new_w = max_dim
            new_h = int(height * (max_dim / width))
        else:
            new_h = max_dim
            new_w = int(width * (max_dim / height))

        resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        logger.debug(f"Resized image from {width}x{height} to {new_w}x{new_h}")
        return resized

    @staticmethod
    def draw_bounding_boxes(
        image: Image.Image,
        boxes: List[Dict[str, Any]],
        outline_color: str = "red",
        width: int = 3
    ) -> Image.Image:
        """
        Draws bounding box annotations on an image.

        Args:
            image: Source PIL Image.
            boxes: List of dicts containing 'bbox': (left, top, right, bottom) and optional 'label': str.
            outline_color: Color of rectangle.
            width: Thickness of rectangle line.

        Returns:
            PIL.Image.Image: Annotated image copy.
        """
        annotated = image.copy()
        draw = ImageDraw.Draw(annotated)

        for box in boxes:
            bbox = box.get("bbox")
            if not bbox or len(bbox) != 4:
                continue
            draw.rectangle(bbox, outline=outline_color, width=width)
            label = box.get("label")
            if label:
                draw.text((bbox[0] + 4, bbox[1] + 4), str(label), fill=outline_color)

        return annotated

    @staticmethod
    def draw_grid_overlay(
        image: Image.Image,
        rows: int = 4,
        cols: int = 4,
        line_color: str = "yellow",
        width: int = 2
    ) -> Image.Image:
        """
        Draws a labeled grid overlay across the image to assist LLMs in identifying screen quadrant coordinates.
        """
        annotated = image.copy()
        draw = ImageDraw.Draw(annotated)
        w, h = annotated.size

        row_h = h / rows
        col_w = w / cols

        # Draw vertical grid lines
        for c in range(1, cols):
            x = int(c * col_w)
            draw.line([(x, 0), (x, h)], fill=line_color, width=width)

        # Draw horizontal grid lines
        for r in range(1, rows):
            y = int(r * row_h)
            draw.line([(0, y), (w, y)], fill=line_color, width=width)

        # Draw sector labels
        for r in range(rows):
            for c in range(cols):
                label = f"({r},{c})"
                x = int(c * col_w + 10)
                y = int(r * row_h + 10)
                draw.text((x, y), label, fill=line_color)

        return annotated
