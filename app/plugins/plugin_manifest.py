"""
Manifest Validator Module for Project Astra.
Parses and validates plugin manifest files (manifest.json / plugin.json).
"""

import json
import os
from typing import Tuple, Optional, Dict, Any
from app.models.plugin_manifest import PluginManifest
from app.utils.logger import logger


class ManifestValidator:
    """
    Validates plugin manifest schema and mandatory properties.
    """

    @staticmethod
    def parse_and_validate(manifest_path: str) -> Tuple[Optional[PluginManifest], Optional[str]]:
        """
        Parses manifest file and validates required fields.

        Returns:
            Tuple[Optional[PluginManifest], Optional[str]]: (manifest, error_message)
        """
        if not os.path.exists(manifest_path):
            return None, f"Manifest file not found: {manifest_path}"

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            return None, f"Failed to parse JSON in manifest '{manifest_path}': {e}"

        # Validate required fields
        required_fields = ["name", "version", "author", "description", "entrypoint"]
        missing = [field for field in required_fields if field not in data or not data[field]]
        if missing:
            return None, f"Invalid manifest '{manifest_path}': Missing required fields: {', '.join(missing)}"

        manifest = PluginManifest(
            name=data["name"],
            version=data["version"],
            author=data["author"],
            description=data["description"],
            entrypoint=data["entrypoint"],
            permissions=data.get("permissions", []),
            declared_tools=data.get("tools", []),
            declared_agents=data.get("agents", []),
            min_astra_version=data.get("min_astra_version", "0.1.0"),
            config_schema=data.get("config_schema", {})
        )

        logger.debug(f"Manifest '{manifest.name}' (v{manifest.version}) successfully validated.")
        return manifest, None
