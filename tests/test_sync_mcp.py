"""
Comprehensive Unit & Integration Test Suite for Cloud Sync, Local AI & MCP Platform.
"""

import pytest
import time
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.models.device import DeviceNode, DeviceStatus
from app.models.sync_event import SyncEvent
from app.models.provider_status import ProviderStatus, ProviderState
from app.models.mcp_resource import MCPResource

from app.adapters.ollama_adapter import OllamaAdapter
from app.adapters.mcp_adapter import MCPAdapter

from app.providers.provider_router import ProviderRouter
from app.providers.provider_selector import ProviderSelector
from app.providers.provider_health import ProviderHealthMonitor

from app.sync.device_registry import DeviceRegistry
from app.sync.offline_queue import OfflineQueue
from app.sync.conflict_resolver import ConflictResolver, ConflictStrategy
from app.sync.sync_service import SyncService
from app.sync.sync_manager import SyncManager

from app.mcp.mcp_client import MCPClient
from app.mcp.mcp_server import MCPServer
from app.mcp.mcp_registry import MCPRegistry
from app.mcp.mcp_router import MCPRouter

from app.api.sync_mcp_api import router as sync_mcp_router


class TestAIProviderRouting:
    """Tests provider routing, smart selection, and failover."""

    def test_provider_router_dispatch(self):
        router = ProviderRouter()
        res = router.route_completion("openai", "Hello AI")
        assert res["provider"] == "openai"
        assert "OpenAI Output" in res["text"]

    def test_provider_selector_logic(self):
        router = ProviderRouter()
        selector = ProviderSelector(provider_router=router)

        # Offline / Privacy -> Ollama
        assert selector.select_provider(is_online=False) == "ollama"
        assert selector.select_provider(requires_privacy=True) == "ollama"

        # Task types
        assert selector.select_provider(task_type="fast_answer") == "gemini"
        assert selector.select_provider(task_type="deep_reasoning") == "openai"

    def test_ollama_adapter_fallback(self):
        adapter = OllamaAdapter(base_url="http://localhost:99999")  # Unreachable port
        res = adapter.generate_completion("Test prompt")
        assert res["provider"] == "ollama"
        assert "Ollama Offline Local Output" in res["text"]

        embedding = adapter.generate_embedding("Test text")
        assert len(embedding) == 384

        status = adapter.get_status()
        assert status.state == ProviderState.OFFLINE


class TestSyncSubsystem:
    """Tests multi-device sync, offline queueing, and conflict resolution."""

    def test_device_registry(self):
        registry = DeviceRegistry("Test-Laptop")
        node = registry.register_device("Test-Mobile", platform="Android")
        assert node.device_name == "Test-Mobile"
        assert len(registry.list_devices()) == 2

    def test_offline_queue_flushing(self):
        queue = OfflineQueue()
        event = SyncEvent("dev-1", "chat", "chat-100", {"msg": "Hello"})
        queue.enqueue(event)
        assert queue.size() == 1

        flushed = queue.flush()
        assert len(flushed) == 1
        assert queue.size() == 0

    def test_conflict_resolution(self):
        resolver = ConflictResolver()
        ev_local = SyncEvent("dev-1", "settings", "theme", {"theme": "light"}, timestamp=100.0)
        ev_remote = SyncEvent("dev-2", "settings", "theme", {"theme": "dark"}, timestamp=200.0)

        # Latest wins -> ev_remote
        win = resolver.resolve(ev_local, ev_remote, strategy=ConflictStrategy.LATEST_WINS)
        assert win.payload["theme"] == "dark"

        # Merge -> combines keys
        ev1 = SyncEvent("dev-1", "settings", "s1", {"a": 1}, timestamp=100.0)
        ev2 = SyncEvent("dev-2", "settings", "s1", {"b": 2}, timestamp=200.0)
        merged = resolver.resolve(ev1, ev2, strategy=ConflictStrategy.MERGE)
        assert merged.payload["a"] == 1
        assert merged.payload["b"] == 2

    def test_sync_manager(self):
        sm = SyncManager("Master-Node")
        res_online = sm.sync_entity("chat", "c-1", {"text": "Hi"}, is_online=True)
        assert res_online["status"] == "synced"

        res_offline = sm.sync_entity("chat", "c-2", {"text": "Offline msg"}, is_online=False)
        assert res_offline["status"] == "queued_offline"

        reconnect_res = sm.sync_on_reconnect()
        assert reconnect_res["flushed_events"] == 1


class TestMCPEngine:
    """Tests Model Context Protocol client, server, registry, and routing."""

    def test_mcp_client_and_registry(self):
        client = MCPClient()
        client.connect_server("github")
        tools = client.discover_tools("github")
        assert len(tools) >= 1

        registry = MCPRegistry(client=client)
        resources = registry.list_all_resources()
        assert len(resources) >= 1

    def test_mcp_router_execution(self):
        registry = MCPRegistry()
        m_router = MCPRouter(registry=registry)
        res = m_router.route_tool_call("github", "github_search", {"query": "Astra OS"})
        assert res["status"] == "success"
        assert res["server_name"] == "github"

    def test_mcp_internal_server(self):
        server = MCPServer("astra-internal")
        tools = server.list_exposed_tools()
        assert len(tools) >= 2

        res = server.handle_request("astra_code_analysis", {"path": "main.py"})
        assert res["status"] == "success"


class TestSyncMCPAPIEndpoints:
    """Tests FastAPI Sync & MCP Router REST endpoints."""

    def setup_method(self):
        self.app = FastAPI()
        self.app.include_router(sync_mcp_router)
        self.client = TestClient(self.app)

    def test_sync_push_endpoint(self):
        res = self.client.post("/api/sync/push", json={
            "entity_type": "memory",
            "entity_id": "mem-1",
            "payload": {"key": "val"}
        })
        assert res.status_code == 200
        assert res.json()["status"] == "synced"

    def test_devices_endpoint(self):
        res = self.client.get("/api/devices")
        assert res.status_code == 200
        assert len(res.json()["devices"]) >= 1

    def test_providers_status_endpoint(self):
        res = self.client.get("/api/providers/status")
        assert res.status_code == 200
        assert "openai" in res.json()
        assert "ollama" in res.json()

    def test_providers_select_endpoint(self):
        res = self.client.post("/api/providers/select", json={"requires_privacy": True})
        assert res.status_code == 200
        assert res.json()["selected_provider"] == "ollama"

    def test_mcp_call_endpoint(self):
        res = self.client.post("/api/mcp/call", json={
            "server_name": "notion",
            "tool_name": "search_pages",
            "arguments": {"query": "notes"}
        })
        assert res.status_code == 200
        assert res.json()["status"] == "success"
