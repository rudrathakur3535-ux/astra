"""
Plugin Sandbox Module for Project Astra.
Enforces security permission boundaries for third-party plugins.
"""

from typing import List, Dict, Any, Optional, Tuple
from app.models.plugin_info import PluginInfo
from app.models.plugin_permission import PluginPermission
from app.utils.logger import logger


class PluginSandbox:
    """
    Security sandbox verifying permission requirements before enabling plugin execution.
    """

    KNOWN_PERMISSIONS = {
        "network": "Access external HTTP/network resources",
        "filesystem": "Read/write local workspace files",
        "desktop": "Launch apps and manage OS windows",
        "browser": "Control Playwright web browser",
        "email": "Read and draft emails",
        "microphone": "Access audio input stream"
    }

    def verify_permissions(self, info: PluginInfo, granted_permissions: Optional[List[str]] = None) -> Tuple[bool, List[PluginPermission]]:
        """
        Verifies plugin requested permissions against granted permission list.

        Returns:
            Tuple[bool, List[PluginPermission]]: (all_granted, permission_status_list)
        """
        granted_set = set(granted_permissions or info.permissions)
        perm_objects: List[PluginPermission] = []
        all_granted = True

        for req in info.permissions:
            desc = self.KNOWN_PERMISSIONS.get(req, f"Custom permission '{req}'")
            is_ok = req in granted_set
            if not is_ok:
                all_granted = False

            perm_objects.append(PluginPermission(
                name=req,
                description=desc,
                is_granted=is_ok,
                reason=None if is_ok else f"Permission '{req}' was not approved by user."
            ))

        if not all_granted:
            logger.warning(f"[PluginSandbox] Plugin '{info.name}' has unapproved permissions.")
        else:
            logger.info(f"[PluginSandbox] Plugin '{info.name}' permissions verified cleanly.")

        return all_granted, perm_objects
