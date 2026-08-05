import pytest
from app.avatar.avatar_enums import ExpressionEnum, GestureEnum, VisemeEnum
from app.avatar.avatar_state_manager import AvatarStateManager
from app.avatar.response_parser import ResponseParser

def test_response_parser_tags():
    raw_llm_text = "[HAPPY] [GESTURE:WAVE] Hello! I am Astra, your AI companion."
    clean_text, expr, gesture, visemes = ResponseParser.parse_llm_response(raw_llm_text)
    
    assert clean_text == "Hello! I am Astra, your AI companion."
    assert expr == ExpressionEnum.HAPPY
    assert gesture == GestureEnum.WAVE
    assert len(visemes) > 0

def test_avatar_state_manager_websocket_payload():
    manager = AvatarStateManager()
    manager.set_expression(ExpressionEnum.SMILE)
    manager.set_gesture(GestureEnum.EXPLAIN)
    
    payload = manager.to_websocket_payload()
    assert payload["type"] == "avatar_state_update"
    assert payload["data"]["expression"] == "smile"
    assert payload["data"]["gesture"] == "explain"
