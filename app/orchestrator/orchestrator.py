from typing import Dict, Any
from app.brain.llm import BrainLLM
from app.avatar.avatar_state_manager import AvatarStateManager
from app.avatar.response_parser import ResponseParser
from app.memory.memory_manager import MemoryManager
from app.orchestrator.event_bus import EventBus
from app.agents.coding_agent import CodingAgent

class AstraOrchestrator:
    def __init__(self, brain: BrainLLM, memory_mgr: MemoryManager):
        self.brain = brain
        self.memory = memory_mgr
        self.avatar = AvatarStateManager()
        self.event_bus = EventBus()
        self.coding_agent = CodingAgent()

    async def handle_user_query(self, query: str) -> Dict[str, Any]:
        # 1. Recall memory context for query
        memory_context = await self.memory.recall_context(query)
        
        # 2. Process query via Brain LLM
        self.avatar.state.is_thinking = True
        raw_response = await self.brain.process_user_query(query, memory_context=memory_context)
        self.avatar.state.is_thinking = False

        # 3. Parse emotion & gesture tags for Avatar animation
        clean_text, expr, gesture, visemes = ResponseParser.parse_llm_response(raw_response)
        self.avatar.set_expression(expr)
        self.avatar.set_gesture(gesture)
        self.avatar.queue_visemes(visemes)

        # 4. Store user-assistant interaction in memory
        await self.memory.add_memory(f"User: {query} | Astra: {clean_text}")

        # 5. Broadcast WebSocket event payload
        payload = self.avatar.to_websocket_payload()
        payload["speech_text"] = clean_text
        await self.event_bus.publish("avatar_update", payload)

        return {
            "text": clean_text,
            "expression": expr.value if hasattr(expr, 'value') else str(expr),
            "gesture": gesture.value if hasattr(gesture, 'value') else str(gesture),
            "avatar_payload": payload
        }

# Alias for backwards compatibility
Orchestrator = AstraOrchestrator
