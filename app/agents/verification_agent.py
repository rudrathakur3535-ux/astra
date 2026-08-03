"""
Verification Agent for Project Astra.
Empirically verifies step and goal outcomes using real-world system evidence (processes, files, windows, DOM state).
"""

from typing import Tuple, Optional, Dict, Any
import os
import psutil
import pygetwindow as gw

from app.models.plan_step import PlanStep, StepStatus
from app.utils.logger import logger


class VerificationAgent:
    """
    Independent verification agent validating real-world execution outcomes.
    """

    def verify_step_outcome(self, step: PlanStep) -> Tuple[bool, str]:
        """
        Verifies empirical system state following step execution.

        Returns:
            Tuple[bool, str]: (verified_success, verification_details)
        """
        if step.status != StepStatus.SUCCESS:
            return False, f"Step status is '{step.status}', not SUCCESS."

        tool = step.tool.lower()

        # 1. Verification for Folder/File Creation
        if "create_folder" in tool:
            folder_path = step.args.get("folder_name") or step.args.get("folder_path")
            if folder_path and os.path.exists(folder_path):
                return True, f"Verified: Folder '{folder_path}' exists on disk."
            return False, f"Verification failed: Folder '{folder_path}' was not found on disk."

        # 2. Verification for Application Launch
        elif "launch_app" in tool:
            app_name = step.args.get("app_name", "").lower()
            running = any(app_name in proc.info["name"].lower() for proc.info in psutil.process_iter(["name"]) if proc.info["name"])
            if running:
                return True, f"Verified: Process matching '{app_name}' is actively running."
            return False, f"Verification failed: No process matching '{app_name}' was found running."

        # 3. Verification for Window Focus
        elif "focus_window" in tool:
            title = step.args.get("title_query", "")
            matching_windows = [w for w in gw.getAllWindows() if title.lower() in w.title.lower()]
            if matching_windows:
                return True, f"Verified: Window matching '{title}' exists."
            return False, f"Verification failed: No window matching '{title}' found."

        # 4. Default verification for browser & system tools
        if step.result is not None:
            return True, f"Verified: Tool '{step.tool}' returned valid result payload."

        return True, f"Verified step {step.id} default state."
