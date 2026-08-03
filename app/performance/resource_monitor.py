"""
Real-Time Hardware & Runtime Resource Monitor for Project Astra OS.
Harvests CPU, RAM, Disk, active thread counts, and task queue depths.
"""

from typing import Dict, Any, Optional
import psutil
import threading
from app.models.resource_snapshot import ResourceSnapshot


class ResourceMonitor:
    """
    Real-time System Resource Monitoring Engine.
    """

    def harvest_snapshot(self, queue_size: int = 0) -> ResourceSnapshot:
        """
        Harvests real-time hardware resource snapshot.
        """
        cpu_p = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        active_threads = threading.active_count()

        return ResourceSnapshot(
            cpu_percent=cpu_p,
            ram_used_mb=mem.used / (1024 * 1024),
            ram_percent=mem.percent,
            disk_percent=disk.percent,
            active_threads=active_threads,
            queue_size=queue_size
        )
