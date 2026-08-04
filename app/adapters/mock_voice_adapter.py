from typing import AsyncGenerator
from app.ports.provider_port import BaseSTTProviderPort, BaseTTSProviderPort

class MockSTTAdapter(BaseSTTProviderPort):
    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        return "Hello Astra, status check."

class MockTTSAdapter(BaseTTSProviderPort):
    async def synthesize_speech_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        yield f"Audio chunk for: {text}".encode("utf-8")
