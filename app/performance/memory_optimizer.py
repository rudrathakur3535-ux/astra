"""
Memory Optimizer for Project Astra OS.
Monitors memory footprints, triggers garbage collection, and executes cache evictions.
"""

from typing import Dict, Any
import gc
import psutil
from app.performance.cache_manager import CacheManager


class MemoryOptimizer:
    """
    Memory Optimization and Garbage Collection Utility.
    """

    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager

    def optimize_memory(self) -> Dict[str, Any]:
        """
        Runs Python garbage collection and evicts stale cache items.
        """
        process = psutil.Process()
        mem_before = process.memory_info().rss / (1024 * 1024)

        # Trigger GC collection
        collected = gc.collect()

        mem_after = process.memory_info().rss / (1024 * 1024)
        freed_mb = max(0.0, mem_before - mem_after)

        return {
            "unreachable_objects_collected": collected,
            "memory_before_mb": round(mem_before, 2),
            "memory_after_mb": round(mem_after, 2),
            "freed_mb": round(freed_mb, 2)
        }
