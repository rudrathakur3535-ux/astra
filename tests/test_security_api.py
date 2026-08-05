import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.security.policy_engine import PolicyEngine
from app.models.security_event import RiskLevel
from app.api import app_router, avatar_router, avatar_ws_router

app = FastAPI()
app.include_router(app_router)
app.include_router(avatar_router)
app.include_router(avatar_ws_router)


@pytest.mark.asyncio
async def test_policy_engine_risk_validation():
    policy = PolicyEngine()
    
    critical_risk = await policy.validate_action("exec_shell_command", {})
    assert critical_risk == RiskLevel.CRITICAL

    high_risk = await policy.validate_action("write_file_contents", {})
    assert high_risk == RiskLevel.HIGH

    low_risk = await policy.validate_action("read_memory_record", {})
    assert low_risk == RiskLevel.LOW

def test_health_check_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["service"] == "Astra AI OS Companion"

def test_avatar_websocket_endpoint():
    client = TestClient(app)
    with client.websocket_connect("/ws/avatar") as websocket:
        websocket.send_json({"action": "ping"})
        data = websocket.receive_json()
        assert data["type"] == "avatar_ack"
        assert data["received"]["action"] == "ping"
