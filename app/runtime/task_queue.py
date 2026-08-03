"""
Task Queue Module for Project Astra.
Priority and FIFO queue managing ready-to-run workflow step tasks.
"""

import asyncio
from typing import Optional, List, Any
from app.models.agent_task import AgentTask
from app.utils.logger import logger


class TaskQueue:
    """
    Async queue for buffering ready tasks for the runtime scheduler.
    """

    def __init__(self):
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._pending_tasks: List[AgentTask] = []

    def push(self, task: AgentTask) -> None:
        """Pushes a task into the queue."""
        priority_val = task.priority.value if hasattr(task.priority, "value") else 1
        # Use priority_val ascending (higher priority first: 0 > 1 > 2)
        self._queue.put_nowait((priority_val, task))
        self._pending_tasks.append(task)
        logger.debug(f"[TaskQueue] Queued task '{task.task_id[:8]}' with priority {priority_val}")

    async def pop(self) -> AgentTask:
        """Pops highest priority task from the queue."""
        priority_val, task = await self._queue.get()
        if task in self._pending_tasks:
            self._pending_tasks.remove(task)
        return task

    def qsize(self) -> int:
        return len(self._pending_tasks)

    def is_empty(self) -> bool:
        return len(self._pending_tasks) == 0
