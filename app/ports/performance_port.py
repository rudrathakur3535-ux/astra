"""
Performance Port Interface for Project Astra OS (Hexagonal Architecture).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.models.benchmark_result import BenchmarkResult
from app.models.resource_snapshot import ResourceSnapshot


class PerformancePort(ABC):
    """
    Abstract Hexagonal Port interface for Performance and Reliability Adapters.
    """

    @abstractmethod
    def run_benchmark(self, subsystem_name: str, samples: int = 10) -> BenchmarkResult:
        """Executes performance benchmark suite."""
        pass

    @abstractmethod
    def get_resource_snapshot(self) -> ResourceSnapshot:
        """Harvests hardware resource metrics."""
        pass
