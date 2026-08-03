"""
Benchmark Runner Engine for Project Astra OS.
Runs performance benchmarks across subsystems (agents, tools, memory, RAG, providers, workflows).
"""

from typing import Dict, List, Any, Callable
import time
from app.models.benchmark_result import BenchmarkResult
from app.performance.latency_analyzer import LatencyAnalyzer


class BenchmarkRunner:
    """
    Benchmark Suite Execution Harness.
    """

    def __init__(self):
        self.analyzer = LatencyAnalyzer()

    def run_benchmark(self, subsystem_name: str, target_fn: Callable[[], Any], samples: int = 10) -> BenchmarkResult:
        """
        Executes target function N times and analyzes latency distributions.
        """
        latencies = []
        for _ in range(samples):
            start = time.time()
            try:
                target_fn()
            except Exception:
                pass
            elapsed = (time.time() - start) * 1000.0
            latencies.append(elapsed)

        stats = self.analyzer.analyze_latencies(latencies)

        return BenchmarkResult(
            benchmark_id=f"bm-{subsystem_name}-{int(time.time())}",
            subsystem=subsystem_name,
            sample_count=samples,
            avg_latency_ms=stats["avg"],
            p50_latency_ms=stats["p50"],
            p95_latency_ms=stats["p95"],
            p99_latency_ms=stats["p99"],
            ops_per_sec=stats["ops_per_sec"]
        )
