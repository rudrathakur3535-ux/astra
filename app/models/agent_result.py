from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ExecutionMetrics(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    cost_usd: float = 0.0

class AgentResult(BaseModel):
    agent_name: str
    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    metrics: ExecutionMetrics = Field(default_factory=ExecutionMetrics)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
