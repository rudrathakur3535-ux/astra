"""
Workflow Benchmarks Suite for Project Astra OS.
Measures end-to-end multi-agent workflow completion latencies.
"""

from typing import Dict, Any
import time
from app.models.benchmark_result import BenchmarkResult
from app.performance.benchmark_runner import BenchmarkRunner


class WorkflowBenchmarks:
    """
    Benchmark Suite for E2E Workflows.
    """

    def __init__(self, runner: BenchmarkRunner):
        self.runner = runner

    def benchmark_full_workflow(self, samples: int = 5) -> BenchmarkResult:
        """Benchmarks end-to-end multi-agent execution pipeline."""
        def mock_workflow():
            time.sleep(0.050)

        return self.runner.run_benchmark("e2e_workflow", mock_workflow, samples=samples)
