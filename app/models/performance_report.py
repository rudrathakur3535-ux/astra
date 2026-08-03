"""
Performance Report Model for Project Astra OS.
Aggregates benchmark results, hardware snapshots, and optimization recommendations.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import time
from app.models.benchmark_result import BenchmarkResult
from app.models.resource_snapshot import ResourceSnapshot


@dataclass
class PerformanceReport:
    report_id: str
    benchmarks: Dict[str, BenchmarkResult] = field(default_factory=dict)
    resource_snapshot: Optional[ResourceSnapshot] = None
    recommendations: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "benchmarks": {k: v.to_dict() for k, v in self.benchmarks.items()},
            "resource_snapshot": self.resource_snapshot.to_dict() if self.resource_snapshot else None,
            "recommendations": self.recommendations,
            "created_at": self.created_at
        }
