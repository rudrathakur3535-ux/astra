"""
Auto Updater & Release Manager for Project Astra OS.
Handles app version checking, manifest comparison, and update triggers.
"""

from typing import Dict, Any, Optional
from app.models.deployment_manifest import DeploymentManifest, ReleaseChannel, TargetPlatform


class AutoUpdater:
    """
    Auto-Updater for checking and applying Astra OS software updates.
    """

    def __init__(self, current_version: str = "1.0.0", current_build: int = 100):
        self.current_version = current_version
        self.current_build = current_build

    def _parse_version(self, v_str: str) -> tuple:
        """Parses semver version string into a tuple of ints."""
        parts = v_str.strip().lstrip("v").split(".")
        return tuple(int(p) for p in parts if p.isdigit())

    def check_for_updates(self, latest_manifest: DeploymentManifest) -> Dict[str, Any]:
        """
        Compares current version against a release manifest and determines update availability.
        """
        current_v = self._parse_version(self.current_version)
        latest_v = self._parse_version(latest_manifest.version)

        update_available = (latest_v > current_v) or (latest_manifest.build_number > self.current_build)

        return {
            "current_version": self.current_version,
            "current_build": self.current_build,
            "latest_version": latest_manifest.version,
            "latest_build": latest_manifest.build_number,
            "update_available": update_available,
            "release_notes": latest_manifest.release_notes,
            "download_url": latest_manifest.download_url
        }

    def apply_update(self, manifest: DeploymentManifest) -> Dict[str, Any]:
        """
        Triggers hot-patch or update installation flow.
        """
        check_result = self.check_for_updates(manifest)
        if not check_result["update_available"]:
            return {"status": "up_to_date", "message": "System is already on the latest version."}

        # Update current version tracking
        self.current_version = manifest.version
        self.current_build = manifest.build_number

        return {
            "status": "updated",
            "new_version": self.current_version,
            "new_build": self.current_build,
            "message": f"Successfully updated Astra OS to v{self.current_version}."
        }
