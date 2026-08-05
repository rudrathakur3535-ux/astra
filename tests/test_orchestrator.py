import pytest
from app.adapters.ollama_adapter import OllamaLLMAdapter
from app.adapters.sqlite_adapter import SQLiteMemoryAdapter
from app.brain.llm import BrainLLM
from app.memory.memory_manager import MemoryManager
from app.orchestrator.orchestrator import AstraOrchestrator

@pytest.mark.asyncio
async def test_orchestrator_pipeline():
    memory_adapter = SQLiteMemoryAdapter(db_path=":memory:")
    memory_mgr = MemoryManager(memory_adapter)

    llm_adapter = OllamaLLMAdapter(model_name="llama3")
    brain = BrainLLM(provider=llm_adapter)

    orchestrator = AstraOrchestrator(brain=brain, memory_mgr=memory_mgr)

    published_events = []
    async def on_avatar_update(payload):
        published_events.append(payload)

    orchestrator.event_bus.subscribe("avatar_update", on_avatar_update)

    res = await orchestrator.handle_user_query("[HAPPY] [GESTURE:WAVE] Hello Astra, review my project!")
    
    assert "Astra Response:" in res["text"]
    assert res["expression"] == "happy"
    assert res["gesture"] == "wave"
    assert len(published_events) == 1
    assert published_events[0]["type"] == "avatar_state_update"
