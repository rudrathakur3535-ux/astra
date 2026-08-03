"""
Checkpoint Manager Module for Project Astra.
Manages workflow state snapshots to guarantee crash recovery after restarts.
"""

from typing import Optional, List, Dict, Any
from app.ports.runtime_port import RuntimePort
from app.models.execution_checkpoint import ExecutionCheckpoint
from app.models.execution_state import ExecutionState
from app.utils.logger import logger


class CheckpointManager:
    """
    Manages workflow state checkpointing and crash recovery.
    """

    def __init__(self, port: RuntimePort):
        self.port = port

    def create_checkpoint(
        self,
        workflow_id: str,
        step_id: str,
        step_index: int,
        step_result_data: Dict[str, Any],
        context_snapshot: Dict[str, Any]
    ) -> ExecutionCheckpoint:
        """
        Creates and persists a new workflow checkpoint.
        """
        checkpoint = ExecutionCheckpoint(
            workflow_id=workflow_id,
            step_id=step_id,
            step_index=step_index,
            step_result_data=step_result_data,
            context_snapshot=context_snapshot
        )
        self.port.save_checkpoint(checkpoint)
        logger.info(f"[CheckpointManager] Created checkpoint for step {step_index} ('{step_id}') in workflow '{workflow_id[:8]}'")
        return checkpoint

    def get_latest_checkpoint(self, workflow_id: str) -> Optional[ExecutionCheckpoint]:
        """Retrieves latest saved checkpoint."""
        return self.port.get_latest_checkpoint(workflow_id)

    def recover_workflow_context(self, workflow_id: str) -> Dict[str, Any]:
        """
        Reconstructs shared context data from the latest saved checkpoint.
        """
        cp = self.get_latest_checkpoint(workflow_id)
        if not cp:
            logger.warning(f"[CheckpointManager] No checkpoint found for crash recovery of workflow '{workflow_id}'")
            return {}

        logger.info(f"[CheckpointManager] Recovered workflow '{workflow_id[:8]}' context from step_index={cp.step_index}")
        return cp.context_snapshot
