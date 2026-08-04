from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional

class BaseLLMProviderPort(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        pass

    @abstractmethod
    async def stream_response(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        pass

class BaseSTTProviderPort(ABC):
    @abstractmethod
    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        pass

class BaseTTSProviderPort(ABC):
    @abstractmethod
    async def synthesize_speech_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        pass

# Aliases for backwards compatibility
ProviderPort = BaseLLMProviderPort
LLMProviderPort = BaseLLMProviderPort
STTProviderPort = BaseSTTProviderPort
TTSProviderPort = BaseTTSProviderPort
