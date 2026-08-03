"""
FastAPI Avatar API & Real-Time WebSocket Router for Project Astra OS (v2.1 Enterprise Spec).
Provides REST endpoints and WebSocket state streaming for the interactive 2D animated avatar.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Body
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import asyncio
import json
import os

from app.avatar import (
    avatar_state_manager,
    AstraEmotion,
    AstraOutfit,
    AstraGesture,
    AstraEyeFocus,
    AstraGesturePriority,
)
from app.utils.logger import logger

router = APIRouter(prefix="/avatar", tags=["avatar"])


@router.get("/view", response_class=HTMLResponse)
async def render_avatar_view():
    """Renders the standalone interactive 2D avatar canvas page."""
    html_path = os.path.join(os.path.dirname(__file__), "..", "avatar", "renderer", "avatar_renderer.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Avatar renderer page not found</h1>")


class EyeTargetRequest(BaseModel):
    x: float = Field(..., ge=0.0, le=1.0, description="Normalized cursor X coordinate (0.0 - 1.0)")
    y: float = Field(..., ge=0.0, le=1.0, description="Normalized cursor Y coordinate (0.0 - 1.0)")


class ToggleStateRequest(BaseModel):
    active: bool = Field(..., description="Active flag boolean")


class MouthOpennessRequest(BaseModel):
    openness: float = Field(..., ge=0.0, le=1.0, description="Normalized mouth openness (0.0 - 1.0)")


class ManualStateRequest(BaseModel):
    emotion: Optional[str] = None
    emotion_strength: Optional[float] = None
    outfit_mode: Optional[str] = None
    gesture: Optional[str] = None
    gesture_priority: Optional[str] = None
    gesture_duration: Optional[float] = None
    eye_focus: Optional[str] = None
    reply_text: Optional[str] = None


@router.get("/state", response_class=JSONResponse)
async def get_avatar_state():
    """Returns the current visual state of the Astra avatar."""
    return avatar_state_manager.get_state_dict()


@router.post("/eye-target", response_class=JSONResponse)
async def update_eye_target(req: EyeTargetRequest):
    """Updates pupil tracking target based on cursor position."""
    avatar_state_manager.update_eye_target(req.x, req.y)
    return {"status": "ok", "eye_target": [req.x, req.y]}


@router.post("/speaking", response_class=JSONResponse)
async def set_speaking(req: ToggleStateRequest):
    """Toggles speaking state for lip-sync animation."""
    avatar_state_manager.set_speaking(req.active)
    return {"status": "ok", "is_speaking": req.active}


@router.post("/listening", response_class=JSONResponse)
async def set_listening(req: ToggleStateRequest):
    """Toggles listening state for microphone reaction animation."""
    avatar_state_manager.set_listening(req.active)
    return {"status": "ok", "is_listening": req.active}


@router.post("/mouth", response_class=JSONResponse)
async def set_mouth_openness(req: MouthOpennessRequest):
    """Sets mouth openness amplitude for voice lip-sync."""
    avatar_state_manager.update_mouth_openness(req.openness)
    return {"status": "ok", "mouth_openness": req.openness}


@router.post("/state/manual", response_class=JSONResponse)
async def update_state_manually(req: ManualStateRequest):
    """Allows manual override of character state for testing/demo purposes."""
    current = avatar_state_manager.get_current_state()

    emotion = AstraEmotion.from_string(req.emotion) if req.emotion else current.emotion
    outfit = AstraOutfit.from_string(req.outfit_mode) if req.outfit_mode else current.outfit_mode
    gesture = AstraGesture.from_string(req.gesture) if req.gesture else current.gesture
    eye_focus = AstraEyeFocus.from_string(req.eye_focus) if req.eye_focus else current.eye_focus
    gesture_priority = AstraGesturePriority.from_string(req.gesture_priority) if req.gesture_priority else current.gesture_priority

    str_val = req.emotion_strength if req.emotion_strength is not None else current.emotion_strength
    dur_val = req.gesture_duration if req.gesture_duration is not None else current.gesture_duration
    reply = req.reply_text if req.reply_text is not None else current.reply_text

    updated = avatar_state_manager.update_from_response(
        reply_text=reply,
        emotion=emotion,
        emotion_strength=str_val,
        outfit_mode=outfit,
        gesture=gesture,
        gesture_priority=gesture_priority,
        gesture_duration=dur_val,
        eye_focus=eye_focus,
    )
    return {"status": "updated", "state": updated.to_dict()}


@router.get("/history", response_class=JSONResponse)
async def get_state_history():
    """Returns recent state transitions log."""
    return {"history": avatar_state_manager.get_history()}


@router.websocket("/ws/state")
async def websocket_avatar_state(websocket: WebSocket):
    """
    Real-Time WebSocket streaming endpoint for Avatar Renderers (2D/Live2D/3D).
    Pushes state updates whenever character state changes.
    """
    await websocket.accept()
    logger.info("Avatar WebSocket client connected")

    queue = avatar_state_manager.subscribe()
    try:
        initial_state = avatar_state_manager.get_state_dict()
        await websocket.send_text(json.dumps(initial_state))

        while True:
            state_dict = await queue.get()
            await websocket.send_text(json.dumps(state_dict))

    except WebSocketDisconnect:
        logger.info("Avatar WebSocket client disconnected")
    except Exception as e:
        logger.error(f"Error in Avatar WebSocket stream: {e}")
        try:
            await websocket.close()
        except Exception:
            pass
    finally:
        avatar_state_manager.unsubscribe(queue)
