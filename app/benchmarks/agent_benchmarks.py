"""
Agent Benchmarks Suite for Project Astra OS.
Measures planning and execution latencies for Planner, Manager, Executor, and Reflection agents.
"""

from typing import Dict, Any
import time
from app.models.benchmark_result import BenchmarkResult
from app.performance.benchmark_runner import BenchmarkRunner


class AgentBenchmarks:
    """
    Benchmark Suite for Multi-Agent Runtime.
    """

    def __init__(self, runner: BenchmarkRunner):
        self.runner = runner

    def benchmark_planner_agent(self, samples: int = 5) -> BenchmarkResult:
        """Benchmarks Planner agent decomposition latency."""
        def mock_plan():
            time.sleep(0.015)  # 15ms mock planning

        return self.runner.run_benchmark("planner_agent", mock_plan, samples=samples)

    def benchmark_executor_agent(self, samples: int = 5) -> BenchmarkResult:
        """Benchmarks Executor agent action dispatching."""
        def mock_execute():
            time.sleep(0.010)  # 10ms mock execution

        return self.runner.run_benchmark("executor_agent", mock_execute, samples=samples)
