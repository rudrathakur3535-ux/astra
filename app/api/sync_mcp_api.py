"""
FastAPI Router for Cloud Sync, AI Providers, and MCP Subsystems in Project Astra OS.
"""

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from app.sync.sync_manager import SyncManager
from app.providers.provider_router import ProviderRouter
from app.providers.provider_selector import ProviderSelector
from app.providers.provider_health import ProviderHealthMonitor
from app.mcp.mcp_registry import MCPRegistry
from app.mcp.mcp_router import MCPRouter

router = APIRouter(prefix="/api", tags=["sync_mcp_providers"])

# Global Singleton Instances
_sync_manager_instance: Optional[SyncManager] = None
_provider_router_instance: Optional[ProviderRouter] = None
_provider_selector_instance: Optional[ProviderSelector] = None
_mcp_registry_instance: Optional[MCPRegistry] = None
_mcp_router_instance: Optional[MCPRouter] = None


def get_sync_manager() -> SyncManager:
    global _sync_manager_instance
    if _sync_manager_instance is None:
        _sync_manager_instance = SyncManager()
    return _sync_manager_instance


def get_provider_router() -> ProviderRouter:
    global _provider_router_instance
    if _provider_router_instance is None:
        _provider_router_instance = ProviderRouter()
    return _provider_router_instance


def get_mcp_registry() -> MCPRegistry:
    global _mcp_registry_instance
    if _mcp_registry_instance is None:
        _mcp_registry_instance = MCPRegistry()
    return _mcp_registry_instance


def get_mcp_router() -> MCPRouter:
    global _mcp_router_instance
    if _mcp_router_instance is None:
        _mcp_router_instance = MCPRouter(registry=get_mcp_registry())
    return _mcp_router_instance


class SyncPushRequest(BaseModel):
    entity_type: str
    entity_id: str
    payload: Dict[str, Any]
    is_online: bool = True


class DeviceRegisterRequest(BaseModel):
    device_name: str
    platform: str = "Windows"
    ip_address: Optional[str] = "127.0.0.1"


class ProviderSelectRequest(BaseModel):
    task_type: str = "general"
    requires_privacy: bool = False
    is_online: bool = True
    user_preference: Optional[str] = None


class MCPCallRequest(BaseModel):
    server_name: str
    tool_name: str
    arguments: Dict[str, Any] = {}


@router.post("/sync/push", response_class=JSONResponse)
async def push_sync_event(req: SyncPushRequest):
    """Pushes a sync event update across device cluster."""
    sm = get_sync_manager()
    return sm.sync_entity(req.entity_type, req.entity_id, req.payload, is_online=req.is_online)


@router.get("/sync/summary", response_class=JSONResponse)
async def get_sync_summary():
    """Returns cluster device registry and sync statistics."""
    sm = get_sync_manager()
    return sm.get_sync_summary()


@router.post("/sync/reconnect", response_class=JSONResponse)
async def trigger_reconnect_sync():
    """Triggers auto-flush of queued offline sync events upon network reconnection."""
    sm = get_sync_manager()
    return sm.sync_on_reconnect()


@router.get("/devices", response_class=JSONResponse)
async def list_devices():
    """Lists all registered device cluster nodes."""
    sm = get_sync_manager()
    return {"devices": sm.registry.list_devices()}


@router.post("/devices/register", response_class=JSONResponse)
async def register_device(req: DeviceRegisterRequest):
    """Registers a new device node."""
    sm = get_sync_manager()
    node = sm.registry.register_device(req.device_name, req.platform, req.ip_address)
    return {"status": "registered", "device": node.to_dict()}


@router.get("/providers/status", response_class=JSONResponse)
async def get_providers_status():
    """Returns health and latency breakdown across OpenAI, Gemini, OpenRouter, and Ollama."""
    monitor = ProviderHealthMonitor(provider_router=get_provider_router())
    return monitor.check_all_providers()


@router.post("/providers/select", response_class=JSONResponse)
async def select_best_provider(req: ProviderSelectRequest):
    """Selects optimal AI provider based on network state, privacy policy, and task requirements."""
    selector = ProviderSelector(provider_router=get_provider_router())
    best = selector.select_provider(
        task_type=req.task_type,
        requires_privacy=req.requires_privacy,
        is_online=req.is_online,
        user_preference=req.user_preference
    )
    return {"selected_provider": best}


@router.get("/mcp/resources", response_class=JSONResponse)
async def list_mcp_resources():
    """Lists discovered MCP tools and resources across external servers."""
    registry = get_mcp_registry()
    return {"resources": registry.list_all_resources()}


@router.post("/mcp/call", response_class=JSONResponse)
async def call_mcp_tool(req: MCPCallRequest):
    """Routes a tool call request to specified MCP server."""
    router_inst = get_mcp_router()
    return router_inst.route_tool_call(req.server_name, req.tool_name, req.arguments)
