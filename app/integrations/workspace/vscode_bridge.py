"""
VS Code Extension Bridge & Tab Inspector for Project Astra OS.
Interfaces with open editor tabs and active workspace selections.
"""

from typing import Dict, List, Any, Optional


class VSCodeBridge:
    """
    Bridge connecting Astra OS to VS Code editor events and active tab state.
    """

    def __init__(self):
        self._open_files: List[str] = [
            "c:/Users/rudra/OneDrive/Desktop/astra/app/services/integration_service.py",
            "c:/Users/rudra/OneDrive/Desktop/astra/app/security/authentication.py"
        ]
        self._active_file: Optional[str] = "c:/Users/rudra/OneDrive/Desktop/astra/app/services/integration_service.py"

    def get_open_files(self) -> List[str]:
        """Returns list of open editor files."""
        return list(self._open_files)

    def get_active_file(self) -> Optional[str]:
        """Returns currently active open editor tab file."""
        return self._active_file

    def set_active_file(self, filepath: str) -> None:
        """Updates active file tab."""
        self._active_file = filepath
        if filepath not in self._open_files:
            self._open_files.append(filepath)
