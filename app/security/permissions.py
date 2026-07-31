from typing import Optional, Callable, Dict, Any
from app.utils.logger import logger

class PermissionManager:
    """Permission Manager governing safety and user confirmation guards for OS tools."""

    def __init__(self):
        # High risk action types requiring explicit confirmation
        self.sensitive_actions = {
            "delete_folder",
            "delete_file",
            "kill_process",
            "run_terminal_command"
        }
        self._prompt_callback: Optional[Callable[[str, Dict[str, Any]], bool]] = None

    def set_prompt_callback(self, callback: Callable[[str, Dict[str, Any]], bool]) -> None:
        """Sets the UI callback function used to ask the user for confirmation."""
        self._prompt_callback = callback

    def check_permission(self, action_name: str, arguments: Dict[str, Any]) -> bool:
        """Checks whether the requested tool execution is authorized.
        
        Args:
            action_name: Name of the tool or action.
            arguments: Execution parameters.
            
        Returns:
            bool: True if authorized, False if rejected by permission policy.
        """
        if action_name in self.sensitive_actions:
            logger.warning(f"Sensitive action requested: '{action_name}' with args {arguments}")
            if self._prompt_callback:
                approved = self._prompt_callback(action_name, arguments)
                if not approved:
                    logger.info(f"User denied permission for action '{action_name}'")
                    return False
                logger.info(f"User granted permission for action '{action_name}'")
                return True
            else:
                logger.warning(f"No permission prompt callback registered. Denying sensitive action '{action_name}' by default.")
                return False

        return True

permission_manager = PermissionManager()
