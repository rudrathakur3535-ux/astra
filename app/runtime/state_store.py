"""
State Store Module for Project Astra.
Implements RuntimePort providing persistent SQLite / JSON storage for workflow states and checkpoints.
"""

import os
import json
import sqlite3
from typing import List, Optional, Dict, Any

from app.ports.runtime_port import RuntimePort
from app.models.execution_state import ExecutionState, ExecutionStatus
from app.models.execution_checkpoint import ExecutionCheckpoint
from app.utils.logger import logger


class StateStore(RuntimePort):
    """
    SQLite persistent state store for workflow execution states and checkpoints.
    """

    def __init__(self, db_path: str = "app/database/runtime_state.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initializes SQLite database tables for states and checkpoints."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS execution_states (
                        workflow_id TEXT PRIMARY KEY,
                        goal_description TEXT,
                        status TEXT,
                        total_steps INTEGER,
                        completed_steps INTEGER,
                        current_step_id TEXT,
                        completed_step_ids TEXT,
                        failed_step_ids TEXT,
                        error_message TEXT,
                        start_time REAL,
                        end_time REAL,
                        metadata TEXT
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS execution_checkpoints (
                        checkpoint_id TEXT PRIMARY KEY,
                        workflow_id TEXT,
                        step_id TEXT,
                        step_index INTEGER,
                        step_result_data TEXT,
                        context_snapshot TEXT,
                        created_at REAL
                    )
                """)
                conn.commit()
            logger.debug(f"StateStore initialized at '{self.db_path}'")
        except Exception as e:
            logger.error(f"Failed to initialize StateStore DB: {e}")

    def save_state(self, state: ExecutionState) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO execution_states (
                        workflow_id, goal_description, status, total_steps, completed_steps,
                        current_step_id, completed_step_ids, failed_step_ids, error_message,
                        start_time, end_time, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    state.workflow_id,
                    state.goal_description,
                    state.status.value if isinstance(state.status, ExecutionStatus) else state.status,
                    state.total_steps,
                    state.completed_steps,
                    state.current_step_id,
                    json.dumps(state.completed_step_ids),
                    json.dumps(state.failed_step_ids),
                    state.error_message,
                    state.start_time,
                    state.end_time,
                    json.dumps(state.metadata)
                ))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save execution state for '{state.workflow_id}': {e}")
            return False

    def get_state(self, workflow_id: str) -> Optional[ExecutionState]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM execution_states WHERE workflow_id = ?", (workflow_id,))
                row = cursor.fetchone()
                if not row:
                    return None

                return ExecutionState(
                    workflow_id=row[0],
                    goal_description=row[1] or "",
                    status=ExecutionStatus(row[2]),
                    total_steps=row[3] or 0,
                    completed_steps=row[4] or 0,
                    current_step_id=row[5],
                    completed_step_ids=json.loads(row[6]) if row[6] else [],
                    failed_step_ids=json.loads(row[7]) if row[7] else [],
                    error_message=row[8],
                    start_time=row[9] or 0.0,
                    end_time=row[10],
                    metadata=json.loads(row[11]) if row[11] else {}
                )
        except Exception as e:
            logger.error(f"Failed to get execution state for '{workflow_id}': {e}")
            return None

    def save_checkpoint(self, checkpoint: ExecutionCheckpoint) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO execution_checkpoints (
                        checkpoint_id, workflow_id, step_id, step_index,
                        step_result_data, context_snapshot, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    checkpoint.checkpoint_id,
                    checkpoint.workflow_id,
                    checkpoint.step_id,
                    checkpoint.step_index,
                    json.dumps(checkpoint.step_result_data),
                    json.dumps(checkpoint.context_snapshot),
                    checkpoint.created_at
                ))
                conn.commit()
            logger.info(f"Saved checkpoint '{checkpoint.checkpoint_id[:8]}' for workflow '{checkpoint.workflow_id[:8]}'")
            return True
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            return False

    def get_latest_checkpoint(self, workflow_id: str) -> Optional[ExecutionCheckpoint]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM execution_checkpoints
                    WHERE workflow_id = ?
                    ORDER BY step_index DESC, created_at DESC LIMIT 1
                """, (workflow_id,))
                row = cursor.fetchone()
                if not row:
                    return None

                return ExecutionCheckpoint(
                    checkpoint_id=row[0],
                    workflow_id=row[1],
                    step_id=row[2],
                    step_index=row[3],
                    step_result_data=json.loads(row[4]) if row[4] else {},
                    context_snapshot=json.loads(row[5]) if row[5] else {},
                    created_at=row[6]
                )
        except Exception as e:
            logger.error(f"Failed to get latest checkpoint for '{workflow_id}': {e}")
            return None

    def list_checkpoints(self, workflow_id: str) -> List[ExecutionCheckpoint]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM execution_checkpoints
                    WHERE workflow_id = ?
                    ORDER BY step_index ASC
                """, (workflow_id,))
                rows = cursor.fetchall()
                checkpoints = []
                for row in rows:
                    checkpoints.append(ExecutionCheckpoint(
                        checkpoint_id=row[0],
                        workflow_id=row[1],
                        step_id=row[2],
                        step_index=row[3],
                        step_result_data=json.loads(row[4]) if row[4] else {},
                        context_snapshot=json.loads(row[5]) if row[5] else {},
                        created_at=row[6]
                    ))
                return checkpoints
        except Exception as e:
            logger.error(f"Failed to list checkpoints for '{workflow_id}': {e}")
            return []

    def list_all_workflows(self) -> List[ExecutionState]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM execution_states ORDER BY start_time DESC")
                rows = cursor.fetchall()
                states = []
                for row in rows:
                    states.append(ExecutionState(
                        workflow_id=row[0],
                        goal_description=row[1] or "",
                        status=ExecutionStatus(row[2]),
                        total_steps=row[3] or 0,
                        completed_steps=row[4] or 0,
                        current_step_id=row[5],
                        completed_step_ids=json.loads(row[6]) if row[6] else [],
                        failed_step_ids=json.loads(row[7]) if row[7] else [],
                        error_message=row[8],
                        start_time=row[9] or 0.0,
                        end_time=row[10],
                        metadata=json.loads(row[11]) if row[11] else {}
                    ))
                return states
        except Exception as e:
            logger.error(f"Failed to list all workflows: {e}")
            return []
