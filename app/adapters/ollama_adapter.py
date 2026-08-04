from typing import AsyncGenerator, Optional
from app.ports.provider_port import BaseLLMProviderPort

class OllamaLLMAdapter(BaseLLMProviderPort):
    def __init__(self, model_name: str = "llama3"):
        self.model_name = model_name

    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        prefix = f"[{system_prompt}] " if system_prompt else ""
        return f"{prefix}Astra Response: Processed '{prompt}' via {self.model_name}."

    async def stream_response(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        response = await self.generate_response(prompt, system_prompt)
        for word in response.split():
            yield word + " "

# Alias for backwards compatibility
OllamaAdapter = OllamaLLMAdapter
