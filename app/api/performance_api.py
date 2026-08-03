"""
FastAPI Router for Performance, Reliability & Production Readiness in Project Astra OS.
"""

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from app.services.performance_service import PerformanceService

router = APIRouter(prefix="/api", tags=["performance_reliability"])

_performance_service_instance: Optional[PerformanceService] = None


def get_performance_service() -> PerformanceService:
    global _performance_service_instance
    if _performance_service_instance is None:
        _performance_service_instance = PerformanceService()
    return _performance_service_instance


class LoadTestRequest(BaseModel):
    workers: int = 5
    tasks: int = 20


@router.get("/performance/report", response_class=JSONResponse)
async def get_performance_report(samples: int = 5):
    """Returns comprehensive performance report with latency distributions & hardware snapshot."""
    svc = get_performance_service()
    report = svc.generate_performance_report(samples=samples)
    return report.to_dict()


@router.get("/performance/resources", response_class=JSONResponse)
async def get_resource_snapshot():
    """Returns real-time CPU, RAM, Disk, active threads, and task queue depth."""
    svc = get_performance_service()
    snapshot = svc.resource_monitor.harvest_snapshot()
    return snapshot.to_dict()


@router.post("/performance/load-test", response_class=JSONResponse)
async def run_load_test(req: LoadTestRequest):
    """Executes concurrent load test simulating heavy multi-agent workflow load."""
    svc = get_performance_service()
    return svc.run_load_test(workers=req.workers, tasks=req.tasks)


@router.get("/performance/cache", response_class=JSONResponse)
async def get_cache_stats():
    """Returns multi-tier LRU cache statistics."""
    svc = get_performance_service()
    return svc.cache_manager.get_stats()


@router.post("/performance/cache/clear", response_class=JSONResponse)
async def clear_cache():
    """Clears all multi-tier LRU caches."""
    svc = get_performance_service()
    svc.cache_manager.clear_all()
    return {"status": "cache_cleared"}


@router.get("/reliability/circuit-breakers", response_class=JSONResponse)
async def get_circuit_breakers():
    """Returns status of all registered AI provider Circuit Breakers."""
    svc = get_performance_service()
    return {
        name: cb.get_status() for name, cb in svc.circuit_breakers.items()
    }
