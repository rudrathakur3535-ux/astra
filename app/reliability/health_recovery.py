"""
Health Recovery & Checkpoint Engine for Project Astra OS.
Persists runtime checkpoints and restores active workflow states after crashes or restarts.
"""

from typing import Dict, Any, Optional
import os
import json
import time


class HealthRecoveryEngine:
    """
    Checkpoint Recovery Manager.
    """

    def __init__(self, checkpoint_path: str = "app/database/runtime_checkpoint.json"):
        self.checkpoint_path = checkpoint_path
        os.makedirs(os.path.dirname(self.checkpoint_path), exist_ok=True)

    def save_checkpoint(self, state_payload: Dict[str, Any]) -> bool:
        """Saves runtime state checkpoint to disk."""
        data = {
            "saved_at": time.time(),
            "state": state_payload
        }
        try:
            with open(self.checkpoint_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False

    def recover_last_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Recovers and loads previous runtime state checkpoint."""
        if not os.path.exists(self.checkpoint_path):
            return None
        try:
            with open(self.checkpoint_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("state")
        except Exception:
            return None
