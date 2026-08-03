"""
Load Tester Engine for Project Astra OS.
Simulates concurrent multi-agent workflows and heavy tool call load scenarios.
"""

from typing import Dict, Any, Callable, List
import concurrent.futures
import time


class LoadTester:
    """
    Stress Testing Utility.
    """

    def run_concurrent_load_test(self, task_fn: Callable[[], Any], concurrent_workers: int = 5, total_tasks: int = 20) -> Dict[str, Any]:
        """
        Executes concurrent load test using ThreadPoolExecutor.
        """
        start = time.time()
        success_count = 0
        failure_count = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_workers) as executor:
            futures = [executor.submit(task_fn) for _ in range(total_tasks)]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                    success_count += 1
                except Exception:
                    failure_count += 1

        total_time = time.time() - start
        throughput = total_tasks / total_time if total_time > 0 else 0.0

        return {
            "concurrent_workers": concurrent_workers,
            "total_tasks": total_tasks,
            "success_count": success_count,
            "failure_count": failure_count,
            "total_duration_sec": round(total_time, 2),
            "throughput_tasks_per_sec": round(throughput, 2)
        }
