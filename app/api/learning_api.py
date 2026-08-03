"""
FastAPI Router for Adaptive Intelligence & Learning Engine in Project Astra OS.
"""

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from app.services.learning_service import LearningService

router = APIRouter(prefix="/api/learning", tags=["learning"])

_learning_service_instance: Optional[LearningService] = None


def get_learning_service() -> LearningService:
    global _learning_service_instance
    if _learning_service_instance is None:
        _learning_service_instance = LearningService()
    return _learning_service_instance


class PreferenceUpdateRequest(BaseModel):
    key: str
    value: Any


class ActionLogRequest(BaseModel):
    action_logs: List[Dict[str, Any]]


class FeedbackRequest(BaseModel):
    feedback_type: str = "preference_correction"
    message: str


@router.get("/habits", response_class=JSONResponse)
async def list_habits():
    """Lists all detected user habits and routines."""
    svc = get_learning_service()
    return {"habits": [h.to_dict() for h in svc.habit_detector.get_habits()]}


@router.delete("/habits/{habit_id}", response_class=JSONResponse)
async def delete_habit(habit_id: str):
    """Deletes a learned habit (privacy compliance)."""
    svc = get_learning_service()
    deleted = svc.habit_detector.delete_habit(habit_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Habit '{habit_id}' not found.")
    return {"status": "deleted", "habit_id": habit_id}


@router.get("/preferences", response_class=JSONResponse)
async def get_preferences():
    """Returns learned user preferences."""
    svc = get_learning_service()
    return {"preferences": svc.preference_engine.get_all_preferences()}


@router.post("/preferences", response_class=JSONResponse)
async def update_preference(req: PreferenceUpdateRequest):
    """Updates a learned user preference."""
    svc = get_learning_service()
    svc.preference_engine.set_preference(req.key, req.value)
    return {"status": "updated", "key": req.key, "value": req.value}


@router.get("/recommendations", response_class=JSONResponse)
async def get_recommendations():
    """Returns proactive workflow recommendations."""
    svc = get_learning_service()
    return {"recommendations": [r.to_dict() for r in svc.recommendation_engine.get_pending_recommendations()]}


@router.post("/recommendations/accept", response_class=JSONResponse)
async def accept_recommendation(recommendation_id: str = Body(..., embed=True)):
    """Accepts a proactive workflow recommendation."""
    svc = get_learning_service()
    accepted = svc.recommendation_engine.accept_recommendation(recommendation_id)
    if not accepted:
        raise HTTPException(status_code=404, detail=f"Recommendation '{recommendation_id}' not found.")
    return {"status": "accepted", "recommendation_id": recommendation_id}


@router.get("/knowledge-graph", response_class=JSONResponse)
async def get_knowledge_graph():
    """Returns Personal Knowledge Graph summary (nodes and relationship edges)."""
    svc = get_learning_service()
    return svc.knowledge_graph.get_graph_summary()


@router.post("/process-actions", response_class=JSONResponse)
async def process_user_actions(req: ActionLogRequest):
    """Processes user action logs to learn habits and update suggestions."""
    svc = get_learning_service()
    return svc.record_user_actions_and_learn(req.action_logs)


@router.post("/feedback", response_class=JSONResponse)
async def submit_feedback(req: FeedbackRequest):
    """Submits feedback or explicit correction signals to tune preferences."""
    svc = get_learning_service()
    return svc.feedback_analyzer.analyze_feedback_signal(req.feedback_type, req.message)


@router.post("/reset", response_class=JSONResponse)
async def reset_learning_data():
    """Full Privacy Reset: Wipes all learned habits, preferences, and personal knowledge graph nodes."""
    svc = get_learning_service()
    return svc.reset_all_learning_data()
