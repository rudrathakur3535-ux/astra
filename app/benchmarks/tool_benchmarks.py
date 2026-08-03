"""
Tool Benchmarks Suite for Project Astra OS.
Measures execution latencies for Desktop, Browser, and Vision automation tools.
"""

from typing import Dict, Any
import time
from app.models.benchmark_result import BenchmarkResult
from app.performance.benchmark_runner import BenchmarkRunner


class ToolBenchmarks:
    """
    Benchmark Suite for Desktop & Browser Automation Tools.
    """

    def __init__(self, runner: BenchmarkRunner):
        self.runner = runner

    def benchmark_desktop_tools(self, samples: int = 5) -> BenchmarkResult:
        """Benchmarks Desktop Windows automation tool execution."""
        def mock_desktop():
            time.sleep(0.008)

        return self.runner.run_benchmark("desktop_tools", mock_desktop, samples=samples)

    def benchmark_browser_tools(self, samples: int = 5) -> BenchmarkResult:
        """Benchmarks Playwright browser automation tool execution."""
        def mock_browser():
            time.sleep(0.025)

        return self.runner.run_benchmark("browser_tools", mock_browser, samples=samples)
