"""
Workflow Learner for Project Astra OS.
Converts repeated habit sequences into automated workflow templates.
"""

from typing import Dict, List, Any, Optional
from app.models.habit import Habit


class WorkflowLearner:
    """
    Automated Workflow Generator from learned habits.
    """

    def learn_workflow_from_habit(self, habit: Habit) -> Dict[str, Any]:
        """
        Converts habit sequence into an executable workflow JSON template.
        """
        steps = [
            {"step_id": i + 1, "action": act, "target": "system"}
            for i, act in enumerate(habit.action_sequence)
        ]
        return {
            "workflow_id": f"wf-learned-{habit.habit_id}",
            "name": f"Automated Workflow: {habit.name}",
            "trigger": habit.trigger_context,
            "steps": steps,
            "auto_generated": True
        }
