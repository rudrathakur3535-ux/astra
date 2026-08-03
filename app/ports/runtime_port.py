"""
Runtime Port Interface for Project Astra (Hexagonal Architecture).
Enforces strict decoupling between core runtime execution and state persistence / monitoring adapters.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.models.execution_state import ExecutionState
from app.models.execution_checkpoint import ExecutionCheckpoint


class RuntimePort(ABC):
    """
    Abstract Hexagonal Port interface for Astra Autonomous Execution Runtime Adapters.
    """

    @abstractmethod
    def save_state(self, state: ExecutionState) -> bool:
        """Persists workflow execution state."""
        pass

    @abstractmethod
    def get_state(self, workflow_id: str) -> Optional[ExecutionState]:
        """Retrieves workflow execution state."""
        pass

    @abstractmethod
    def save_checkpoint(self, checkpoint: ExecutionCheckpoint) -> bool:
        """Persists workflow execution checkpoint."""
        pass

    @abstractmethod
    def get_latest_checkpoint(self, workflow_id: str) -> Optional[ExecutionCheckpoint]:
        """Retrieves the latest saved checkpoint for a workflow."""
        pass

    @abstractmethod
    def list_checkpoints(self, workflow_id: str) -> List[ExecutionCheckpoint]:
        """Lists all checkpoints saved for a workflow in order."""
        pass

    @abstractmethod
    def list_all_workflows(self) -> List[ExecutionState]:
        """Lists all historical and active workflow executions."""
        pass
