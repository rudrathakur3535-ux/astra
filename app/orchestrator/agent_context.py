"""
Agent Context Module for Project Astra.
Thread-safe shared memory context passed between specialist agents in a workflow.
"""

from typing import Dict, Any, Optional, List
import threading
from app.utils.logger import logger


class AgentContext:
    """
    Shared execution context holding global variables, task outputs, artifacts, and memory pointers.
    """

    def __init__(self, goal_description: str = "", event_bus: Optional[Any] = None):
        self.goal_description = goal_description
        self.event_bus = event_bus
        self._store: Dict[str, Any] = {}
        self._task_results: Dict[str, Any] = {}
        self._artifacts: List[str] = []
        self._lock = threading.Lock()

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._store[key] = value
            logger.debug(f"[AgentContext] Set key '{key}'")

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._store.get(key, default)

    def store_task_result(self, task_id: str, data: Any) -> None:
        with self._lock:
            self._task_results[task_id] = data

    def get_task_result(self, task_id: str) -> Optional[Any]:
        with self._lock:
            return self._task_results.get(task_id)

    def add_artifact(self, filepath: str) -> None:
        with self._lock:
            if filepath not in self._artifacts:
                self._artifacts.append(filepath)

    def list_artifacts(self) -> List[str]:
        with self._lock:
            return list(self._artifacts)

    def to_dict(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "goal_description": self.goal_description,
                "store": dict(self._store),
                "task_results": dict(self._task_results),
                "artifacts": list(self._artifacts)
            }
