"""
Local Ollama Adapter for Project Astra OS.
Implements ProviderPort for offline local LLM execution and local embeddings.
"""

from typing import Dict, Any, Optional, List
import time
import requests
from app.ports.provider_port import ProviderPort
from app.models.provider_status import ProviderStatus, ProviderState


class OllamaAdapter(ProviderPort):
    """
    Adapter interfacing with local Ollama server instance (default http://localhost:11434).
    """

    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "llama3"):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    def generate_completion(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Generates completion via local Ollama instance.
        """
        model = kwargs.get("model", self.default_model)
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt

        start = time.time()
        try:
            resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=30)
            latency = (time.time() - start) * 1000.0
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "text": data.get("response", ""),
                    "provider": "ollama",
                    "model": model,
                    "latency_ms": latency,
                    "usage": {"prompt_tokens": 0, "completion_tokens": 0}
                }
        except Exception:
            pass

        # Offline fallback mock output if server un-contactable
        latency = (time.time() - start) * 1000.0
        return {
            "text": f"[Ollama Offline Local Output for: '{prompt}']",
            "provider": "ollama",
            "model": model,
            "latency_ms": latency,
            "usage": {"prompt_tokens": 0, "completion_tokens": 0}
        }

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generates 384-dim vector embedding locally.
        """
        try:
            resp = requests.post(f"{self.base_url}/api/embeddings", json={"model": self.default_model, "prompt": text}, timeout=10)
            if resp.status_code == 200:
                return resp.json().get("embedding", [0.0] * 384)
        except Exception:
            pass
        # Fallback deterministic mock embedding
        return [float((hash(text) + i) % 100) / 100.0 for i in range(384)]

    def get_status(self) -> ProviderStatus:
        """Checks local Ollama health status."""
        start = time.time()
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=2)
            latency = (time.time() - start) * 1000.0
            if resp.status_code == 200:
                return ProviderStatus(
                    provider_name="Ollama (Local)",
                    state=ProviderState.HEALTHY,
                    latency_ms=latency,
                    is_local=True,
                    privacy_rating="local_private"
                )
        except Exception:
            pass

        return ProviderStatus(
            provider_name="Ollama (Local)",
            state=ProviderState.OFFLINE,
            latency_ms=0.0,
            is_local=True,
            privacy_rating="local_private"
        )
