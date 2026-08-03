"""
Progress Tracker Module for Project Astra.
Calculates execution progress percentages, visual ASCII progress bars, and ETA metrics.
"""

from typing import Dict, Any
from app.models.execution_state import ExecutionState
from app.utils.logger import logger


class ProgressTracker:
    """
    Computes visual and numeric execution progress metrics for workflows.
    """

    @staticmethod
    def render_progress_bar(completed: int, total: int, width: int = 10) -> str:
        """
        Renders visual progress bar.
        Example: [████████░░] 80% (4/5 steps complete)
        """
        if total <= 0:
            return "[░░░░░░░░░░] 0%"

        pct = min(completed / total, 1.0)
        filled = int(round(width * pct))
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {int(pct * 100)}% ({completed}/{total} steps complete)"

    @classmethod
    def get_progress_summary(cls, state: ExecutionState) -> Dict[str, Any]:
        """Returns structured progress summary dictionary."""
        bar = cls.render_progress_bar(state.completed_steps, state.total_steps)
        return {
            "workflow_id": state.workflow_id,
            "status": state.status.value if hasattr(state.status, "value") else state.status,
            "completed_steps": state.completed_steps,
            "total_steps": state.total_steps,
            "progress_percentage": state.progress_percentage,
            "progress_bar": bar
        }
