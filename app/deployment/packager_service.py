"""
Packager & Installer Service for Project Astra OS.
Evaluates build configs and generates installer specs for Windows, macOS, and Linux.
"""

from typing import Dict, Any, List
from app.models.deployment_manifest import TargetPlatform, DeploymentManifest


class PackagerService:
    """
    Builds and evaluates desktop installer configuration specs.
    """

    BUILD_CONFIGS: Dict[TargetPlatform, Dict[str, Any]] = {
        TargetPlatform.WINDOWS: {
            "installer_type": "NSIS (.exe) / MSI",
            "artifact_name": "AstraSetup-1.0.0.exe",
            "shortcut": True,
            "one_click": False,
            "allow_to_change_installation_directory": True
        },
        TargetPlatform.MACOS: {
            "installer_type": "DMG",
            "artifact_name": "Astra-1.0.0.dmg",
            "background_image": "assets/dmg_background.png",
            "codesign": True
        },
        TargetPlatform.LINUX: {
            "installer_type": "AppImage / DEB",
            "artifact_name": "Astra-1.0.0.AppImage",
            "category": "Utility"
        }
    }

    def generate_installer_spec(self, platform: TargetPlatform = TargetPlatform.WINDOWS) -> Dict[str, Any]:
        """
        Returns installer build spec for target platform.
        """
        spec = self.BUILD_CONFIGS.get(platform, self.BUILD_CONFIGS[TargetPlatform.WINDOWS])
        return {
            "app_name": "Project Astra OS",
            "target_platform": platform.value if hasattr(platform, "value") else str(platform),
            "installer_config": spec,
            "bundled_services": [
                "FastAPI Backend Runtime",
                "Electron Desktop Shell",
                "SQLite Vector & Relational Storage",
                "ChromaDB Vector Adapter"
            ]
        }
