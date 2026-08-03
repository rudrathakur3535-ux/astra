"""
AI Provider Router for Project Astra OS.
Dispatches requests across OpenAI, Gemini, OpenRouter, and Ollama.
"""

from typing import Dict, Any, Optional, List
from app.ports.provider_port import ProviderPort
from app.adapters.ollama_adapter import OllamaAdapter
from app.models.provider_status import ProviderStatus, ProviderState


class MockCloudProviderAdapter(ProviderPort):
    """Fallback adapter for OpenAI / Gemini cloud providers in test environment."""

    def __init__(self, provider_name: str, latency: float = 120.0):
        self.name = provider_name
        self.latency = latency

    def generate_completion(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        return {
            "text": f"[{self.name} Output for: '{prompt}']",
            "provider": self.name.lower(),
            "model": kwargs.get("model", "default"),
            "latency_ms": self.latency,
            "usage": {"prompt_tokens": 10, "completion_tokens": 20}
        }

    def generate_embedding(self, text: str) -> List[float]:
        return [0.1] * 384

    def get_status(self) -> ProviderStatus:
        return ProviderStatus(
            provider_name=self.name,
            state=ProviderState.HEALTHY,
            latency_ms=self.latency,
            is_local=False,
            privacy_rating="encrypted_cloud"
        )


class ProviderRouter:
    """
    Router dispatching LLM requests across OpenAI, Gemini, OpenRouter, and Ollama.
    """

    def __init__(self):
        self._providers: Dict[str, ProviderPort] = {
            "openai": MockCloudProviderAdapter("OpenAI", latency=180.0),
            "gemini": MockCloudProviderAdapter("Gemini", latency=110.0),
            "openrouter": MockCloudProviderAdapter("OpenRouter", latency=220.0),
            "ollama": OllamaAdapter()
        }

    def register_provider(self, name: str, adapter: ProviderPort) -> None:
        """Registers a provider adapter."""
        self._providers[name.lower()] = adapter

    def get_provider(self, name: str) -> Optional[ProviderPort]:
        """Retrieves a provider by name."""
        return self._providers.get(name.lower())

    def list_providers(self) -> List[str]:
        """Lists registered provider names."""
        return list(self._providers.keys())

    def route_completion(self, provider_name: str, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Routes completion to requested provider, with automatic failover if primary fails.
        """
        primary = self.get_provider(provider_name)
        if primary:
            try:
                res = primary.generate_completion(prompt, system_prompt, **kwargs)
                if res and res.get("text"):
                    return res
            except Exception:
                pass

        # Automatic Failover: Try local Ollama, then Gemini, then OpenAI
        for fallback_name in ["ollama", "gemini", "openai"]:
            if fallback_name != provider_name.lower():
                fallback = self.get_provider(fallback_name)
                if fallback:
                    try:
                        res = fallback.generate_completion(prompt, system_prompt, **kwargs)
                        res["failover_from"] = provider_name
                        return res
                    except Exception:
                        continue

        return {"text": f"[Error: All AI Providers failed for prompt '{prompt}']", "provider": "none"}
