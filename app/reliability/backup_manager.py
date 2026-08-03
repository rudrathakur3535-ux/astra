"""
Backup Manager for Project Astra OS.
Automates backups for SQLite databases, Chroma indexes, and configuration files.
"""

from typing import Dict, Any, List, Optional
import os
import shutil
import time


class BackupManager:
    """
    Automates local backup creation and archival.
    """

    def __init__(self, backup_dir: str = "app/database/backups"):
        self.backup_dir = backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_backup(self, source_path: str, backup_name: str) -> Dict[str, Any]:
        """Creates timestamped backup of target file/directory."""
        if not os.path.exists(source_path):
            return {"status": "error", "error": f"Source path '{source_path}' does not exist."}

        timestamp_str = int(time.time())
        dest_name = f"{backup_name}_{timestamp_str}"
        dest_path = os.path.join(self.backup_dir, dest_name)

        try:
            if os.path.isdir(source_path):
                shutil.copytree(source_path, dest_path)
            else:
                shutil.copy2(source_path, dest_path)

            return {
                "status": "success",
                "backup_path": dest_path,
                "created_at": time.time()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
