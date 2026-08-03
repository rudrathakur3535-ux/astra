"""
Benchmark Result Model for Project Astra OS.
Captures performance metrics, latency percentiles (P50, P95, P99), and throughput.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import time


@dataclass
class BenchmarkResult:
    benchmark_id: str
    subsystem: str
    sample_count: int
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    ops_per_sec: float
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "benchmark_id": self.benchmark_id,
            "subsystem": self.subsystem,
            "sample_count": self.sample_count,
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "p50_latency_ms": round(self.p50_latency_ms, 2),
            "p95_latency_ms": round(self.p95_latency_ms, 2),
            "p99_latency_ms": round(self.p99_latency_ms, 2),
            "ops_per_sec": round(self.ops_per_sec, 2),
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }
