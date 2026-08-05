from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import asyncio

from app.avatar.avatar_state_manager import avatar_state_manager
from app.avatar.avatar_enums import AstraEmotion, AstraOutfit, AstraGesture, AstraEyeFocus, AstraGesturePriority

router = APIRouter(prefix="/avatar", tags=["Avatar"])

class ManualStateRequest(BaseModel):
    emotion: Optional[str] = None
    emotion_strength: Optional[float] = None
    outfit_mode: Optional[str] = None
    gesture: Optional[str] = None
    gesture_priority: Optional[str] = None
    gesture_duration: Optional[float] = None
    eye_focus: Optional[str] = None
    reply_text: Optional[str] = None

class AvatarConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                self.disconnect(connection)

manager = AvatarConnectionManager()

@router.get("/state", response_class=JSONResponse)
async def get_avatar_state():
    """Returns the current visual state of the Astra avatar."""
    return avatar_state_manager.get_state_dict()

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
    return {"status": "success", "state": updated.to_dict()}

ws_router = APIRouter()

@ws_router.websocket("/ws/avatar")
@router.websocket("/ws/avatar")
async def avatar_websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data_text = await websocket.receive_text()
            data = json.loads(data_text)
            
            # Respond to incoming client commands/pings
            await websocket.send_text(json.dumps({
                "type": "avatar_ack",
                "received": data
            }))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

