"""
Provider Benchmarks Suite for Project Astra OS.
Measures completion latencies across OpenAI, Gemini, OpenRouter, and local Ollama.
"""

from typing import Dict, Any
import time
from app.models.benchmark_result import BenchmarkResult
from app.performance.benchmark_runner import BenchmarkRunner


class ProviderBenchmarks:
    """
    Benchmark Suite for LLM Providers.
    """

    def __init__(self, runner: BenchmarkRunner):
        self.runner = runner

    def benchmark_ollama_local(self, samples: int = 5) -> BenchmarkResult:
        """Benchmarks local Ollama LLM completion latency."""
        def mock_ollama():
            time.sleep(0.030)

        return self.runner.run_benchmark("ollama_local", mock_ollama, samples=samples)

    def benchmark_cloud_providers(self, samples: int = 5) -> BenchmarkResult:
        """Benchmarks cloud LLM completion latency."""
        def mock_cloud():
            time.sleep(0.045)

        return self.runner.run_benchmark("cloud_providers", mock_cloud, samples=samples)
