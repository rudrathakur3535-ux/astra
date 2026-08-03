"""
Prompt Optimizer for Project Astra OS.
Tracks historical execution success rates and tunes agent prompt structures.
"""

from typing import Dict, Any, Optional


class PromptOptimizer:
    """
    Agent Prompt Performance Optimization Engine.
    """

    def __init__(self):
        self._history: Dict[str, Dict[str, int]] = {}

    def record_prompt_outcome(self, task_type: str, prompt_template: str, is_success: bool) -> None:
        if task_type not in self._history:
            self._history[task_type] = {"success": 0, "failure": 0}
        if is_success:
            self._history[task_type]["success"] += 1
        else:
            self._history[task_type]["failure"] += 1

    def optimize_system_prompt(self, base_prompt: str, task_type: str) -> str:
        """
        Appends optimization guidelines based on success stats.
        """
        stats = self._history.get(task_type, {"success": 1, "failure": 0})
        total = stats["success"] + stats["failure"]
        success_rate = (stats["success"] / total) * 100.0 if total > 0 else 100.0

        if success_rate < 80.0:
            return f"{base_prompt}\n\n[Optimization Hint: Be explicit and verify tool preconditions before execution.]"
        return base_prompt
