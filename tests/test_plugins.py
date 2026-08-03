"""
Unit tests for Day 13 Plugin SDK & Extension Platform.
Tests ManifestValidator, PluginSandbox, PluginLoader, PluginRegistry, PluginManager, BasePlugin, and PluginAPI.
"""

import os
import json
import pytest
from typing import List, Dict, Any

from app.models.plugin_info import PluginInfo, PluginStatus
from app.models.plugin_manifest import PluginManifest
from app.plugins.plugin_manifest import ManifestValidator
from app.plugins.plugin_sandbox import PluginSandbox
from app.plugins.plugin_registry import PluginRegistry
from app.plugins.plugin_manager import PluginManager
from app.sdk.base_plugin import BasePlugin
from app.sdk.plugin_api import PluginAPI


@pytest.fixture
def mock_plugin_dir(tmp_path):
    plugin_folder = tmp_path / "SpotifyPlugin"
    plugin_folder.mkdir()

    manifest_file = plugin_folder / "plugin.json"
    manifest_data = {
        "name": "Spotify Plugin",
        "version": "1.0.0",
        "author": "Rudra",
        "description": "Mock Spotify Music Control Plugin",
        "entrypoint": "main.py",
        "permissions": ["network", "desktop"],
        "tools": ["spotify.play", "spotify.pause"]
    }
    manifest_file.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

    code_file = plugin_folder / "main.py"
    code_content = """
from app.sdk.base_plugin import BasePlugin
from typing import List, Dict, Any

class SpotifyPlugin(BasePlugin):
    async def on_load(self) -> bool:
        return True

    async def register_tools(self) -> List[Dict[str, Any]]:
        return [{
            "name": "spotify.play",
            "func": lambda: "Playing music",
            "description": "Plays music on Spotify"
        }]

    async def on_unload(self) -> bool:
        return True
"""
    code_file.write_text(code_content, encoding="utf-8")
    return str(tmp_path)


class TestManifestValidatorAndSandbox:
    def test_manifest_validation(self, mock_plugin_dir):
        manifest_path = os.path.join(mock_plugin_dir, "SpotifyPlugin", "plugin.json")
        manifest, err = ManifestValidator.parse_and_validate(manifest_path)

        assert manifest is not None
        assert err is None
        assert manifest.name == "Spotify Plugin"
        assert manifest.version == "1.0.0"
        assert "network" in manifest.permissions

    def test_invalid_manifest(self, tmp_path):
        bad_manifest = tmp_path / "plugin.json"
        bad_manifest.write_text(json.dumps({"name": "Bad Plugin"}), encoding="utf-8")

        manifest, err = ManifestValidator.parse_and_validate(str(bad_manifest))
        assert manifest is None
        assert "Missing required fields" in err

    def test_permission_sandbox_verification(self):
        sandbox = PluginSandbox()
        info = PluginInfo(
            name="TestPlugin",
            version="1.0.0",
            author="Dev",
            description="Test",
            entrypoint="main.py",
            install_path="/tmp",
            permissions=["network", "filesystem"]
        )

        # Unapproved
        ok1, perms1 = sandbox.verify_permissions(info, granted_permissions=["network"])
        assert ok1 is False

        # Approved
        ok2, perms2 = sandbox.verify_permissions(info, granted_permissions=["network", "filesystem"])
        assert ok2 is True


class TestPluginRegistryAndManager:
    @pytest.mark.asyncio
    async def test_plugin_discovery_and_lifecycle(self, mock_plugin_dir):
        manager = PluginManager(plugins_dir=mock_plugin_dir)

        # 1. Discover plugins
        discovered = manager.discover_plugins()
        assert len(discovered) == 1
        assert discovered[0].name == "Spotify Plugin"

        # 2. Load plugin with permissions
        loaded_ok, err = await manager.load_plugin("Spotify Plugin", granted_permissions=["network", "desktop"])
        assert loaded_ok is True
        assert err is None

        # 3. Verify registry status
        info = manager.registry.get_info("Spotify Plugin")
        assert info is not None
        assert info.status == PluginStatus.LOADED

        # 4. Hot reload
        reloaded_ok, r_err = await manager.hot_reload_plugin("Spotify Plugin", granted_permissions=["network", "desktop"])
        assert reloaded_ok is True
        assert r_err is None

        # 5. Unload plugin
        unloaded_ok, u_err = await manager.unload_plugin("Spotify Plugin")
        assert unloaded_ok is True
        assert info.status == PluginStatus.UNLOADED
