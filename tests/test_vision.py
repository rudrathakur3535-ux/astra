"""
Unit tests for Day 6 Visual Perception Subsystem.
"""

import os
import pytest
from PIL import Image
import numpy as np

from app.vision.capture import ScreenCapturer
from app.vision.processor import ImageProcessor
from app.vision.vision_service import VisionService
from app.tools.vision.vision_tools import (
    CaptureScreenTool,
    AnalyzeScreenTool,
    CaptureRegionTool
)
from app.tools.tool_registry import tool_registry


@pytest.fixture
def dummy_image():
    """Returns a dummy 200x200 RGB PIL Image for testing."""
    return Image.new("RGB", (200, 200), color="blue")


class TestScreenCapturer:
    def test_screen_capture_conversions(self, dummy_image):
        capturer = ScreenCapturer(output_dir="app/logs/test_screenshots")
        cv_img = capturer.to_opencv(dummy_image)
        assert isinstance(cv_img, np.ndarray)
        assert cv_img.shape == (200, 200, 3)

        b64_str = capturer.to_base64(dummy_image)
        assert isinstance(b64_str, str)
        assert len(b64_str) > 0

    def test_save_capture(self, dummy_image, tmp_path):
        capturer = ScreenCapturer(output_dir=str(tmp_path))
        filepath = capturer.save_capture(dummy_image, filename_prefix="test_save")
        assert os.path.exists(filepath)
        assert filepath.endswith(".png")


class TestImageProcessor:
    def test_resize_max_dimension(self):
        processor = ImageProcessor()
        large_img = Image.new("RGB", (2000, 1000), color="red")
        resized = processor.resize_max_dimension(large_img, max_dim=1000)
        assert resized.width == 1000
        assert resized.height == 500

    def test_draw_bounding_boxes(self, dummy_image):
        processor = ImageProcessor()
        boxes = [{"bbox": (10, 10, 50, 50), "label": "Target"}]
        annotated = processor.draw_bounding_boxes(dummy_image, boxes)
        assert annotated.size == dummy_image.size

    def test_draw_grid_overlay(self, dummy_image):
        processor = ImageProcessor()
        grid_img = processor.draw_grid_overlay(dummy_image, rows=2, cols=2)
        assert grid_img.size == dummy_image.size


class TestVisionService:
    def test_capture_and_encode_screen(self):
        service = VisionService()
        result = service.capture_and_encode_screen(save_to_disk=False)
        assert "base64_image" in result
        assert "width" in result
        assert "height" in result
        assert isinstance(result["base64_image"], str)


class TestVisionTools:
    def test_capture_screen_tool(self):
        tool = CaptureScreenTool()
        assert tool.name == "vision.capture_screen"
        response = tool.execute(grid_overlay=False)
        assert response.success is True
        assert "filepath" in response.data

    def test_analyze_screen_tool(self):
        tool = AnalyzeScreenTool()
        assert tool.name == "vision.analyze_screen"
        response = tool.execute(max_dimension=512)
        assert response.success is True
        assert "base64_image" in response.data

    def test_tool_registry_contains_vision_tools(self):
        registered = tool_registry.list_tools()
        assert "vision.capture_screen" in registered
        assert "vision.analyze_screen" in registered
        assert "vision.capture_region" in registered
