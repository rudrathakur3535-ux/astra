"""
Latency Analyzer for Project Astra OS.
Calculates statistical distributions (P50, P95, P99) and identifies performance bottlenecks.
"""

from typing import List, Dict, Any
import numpy as np


class LatencyAnalyzer:
    """
    Statistical Latency Distribution Engine.
    """

    def analyze_latencies(self, latencies_ms: List[float]) -> Dict[str, float]:
        """
        Calculates P50, P95, P99, average latency, and throughput stats.
        """
        if not latencies_ms:
            return {"avg": 0.0, "p50": 0.0, "p95": 0.0, "p99": 0.0, "ops_per_sec": 0.0}

        sorted_l = sorted(latencies_ms)
        n = len(sorted_l)
        avg_l = sum(sorted_l) / n
        p50 = sorted_l[int(n * 0.50)]
        p95 = sorted_l[int(n * 0.95)] if n >= 20 else sorted_l[-1]
        p99 = sorted_l[int(n * 0.99)] if n >= 100 else sorted_l[-1]

        ops_sec = (1000.0 / avg_l) if avg_l > 0 else 0.0

        return {
            "avg": avg_l,
            "p50": p50,
            "p95": p95,
            "p99": p99,
            "ops_per_sec": ops_sec
        }
