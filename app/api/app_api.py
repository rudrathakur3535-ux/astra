from fastapi import APIRouter
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter()

class HealthResponse(BaseModel):
    status: str = "online"
    service: str = "Astra AI OS Companion"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse()

@router.get("/status")
async def system_status():
    return {
        "status": "active",
        "subsystems": {
            "avatar": "operational",
            "brain": "operational",
            "memory": "operational",
            "security": "operational"
        }
    }
