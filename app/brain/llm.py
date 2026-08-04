from typing import Optional, AsyncGenerator
from app.ports.provider_port import BaseLLMProviderPort
from app.brain.conversation import ConversationManager
from app.brain.prompts import ASTRA_SYSTEM_PROMPT

class BrainLLM:
    def __init__(self, provider: BaseLLMProviderPort):
        self.provider = provider
        self.conversation = ConversationManager()

    async def process_user_query(self, user_input: str, memory_context: Optional[str] = None) -> str:
        self.conversation.add_message("user", user_input)
        
        system_prompt = ASTRA_SYSTEM_PROMPT
        if memory_context:
            system_prompt = system_prompt + "\n\n[RELEVANT USER MEMORY CONTEXT]\n" + memory_context

        response = await self.provider.generate_response(user_input, system_prompt=system_prompt)
        self.conversation.add_message("assistant", response)
        return response
