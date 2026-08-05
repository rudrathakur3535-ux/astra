import pytest
from app.brain.conversation import ConversationManager
from app.brain.llm import BrainLLM
from app.adapters.ollama_adapter import OllamaLLMAdapter
from app.adapters.sqlite_adapter import SQLiteMemoryAdapter
from app.memory.memory_manager import MemoryManager
from app.models.memory_record import MemoryType

def test_conversation_manager():
    conv = ConversationManager(max_history_turns=2)
    conv.add_message("user", "Hello 1")
    conv.add_message("assistant", "Hi 1")
    conv.add_message("user", "Hello 2")
    conv.add_message("assistant", "Hi 2")
    conv.add_message("user", "Hello 3")
    conv.add_message("assistant", "Hi 3")

    messages = conv.get_messages()
    assert len(messages) == 4
    assert messages[-1]["content"] == "Hi 3"

@pytest.mark.asyncio
async def test_brain_and_memory_integration():
    memory_adapter = SQLiteMemoryAdapter(db_path=":memory:")
    memory_mgr = MemoryManager(memory_adapter)

    await memory_mgr.add_memory("User studies B.Tech CS at KIET.", memory_type=MemoryType.SEMANTIC)
    context = await memory_mgr.recall_context("KIET")

    assert "KIET" in context

    llm_adapter = OllamaLLMAdapter(model_name="llama3")
    brain = BrainLLM(provider=llm_adapter)

    response = await brain.process_user_query("Where do I study?", memory_context=context)
    assert "Astra Response:" in response
    assert "KIET" in response
