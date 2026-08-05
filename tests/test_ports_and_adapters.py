import pytest
from app.models.memory_record import MemoryRecord, MemoryType
from app.adapters.sqlite_adapter import SQLiteMemoryAdapter
from app.adapters.ollama_adapter import OllamaLLMAdapter
from app.adapters.mock_voice_adapter import MockSTTAdapter, MockTTSAdapter

@pytest.mark.asyncio
async def test_sqlite_memory_adapter():
    adapter = SQLiteMemoryAdapter(db_path=":memory:")
    record = MemoryRecord(
        memory_type=MemoryType.WORKING,
        content="User likes competitive programming on Codeforces.",
        metadata={"platform": "Codeforces"}
    )
    
    record_id = await adapter.store(record)
    assert record_id == record.record_id

    results = await adapter.query("Codeforces", memory_type=MemoryType.WORKING)
    assert len(results) == 1
    assert results[0].content == record.content
    assert results[0].metadata["platform"] == "Codeforces"

    cleared = await adapter.clear_working_memory()
    assert cleared is True

    results_after = await adapter.query("Codeforces", memory_type=MemoryType.WORKING)
    assert len(results_after) == 0

@pytest.mark.asyncio
async def test_ollama_llm_adapter():
    adapter = OllamaLLMAdapter(model_name="llama3")
    response = await adapter.generate_response("Hello Astra", system_prompt="Be concise.")
    assert "Astra Response:" in response
    assert "Be concise." in response

    chunks = []
    async for chunk in adapter.stream_response("Hello Astra"):
        chunks.append(chunk)
    assert len(chunks) > 0

@pytest.mark.asyncio
async def test_mock_voice_adapters():
    stt = MockSTTAdapter()
    text = await stt.transcribe_audio(b"fake_audio")
    assert text == "Hello Astra, status check."

    tts = MockTTSAdapter()
    audio_chunks = []
    async for chunk in tts.synthesize_speech_stream("Test speech"):
        audio_chunks.append(chunk)
    assert len(audio_chunks) > 0
