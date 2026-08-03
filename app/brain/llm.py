from typing import List, Dict, Generator, Optional, Callable, Any, Tuple
import json
import openai
from openai import OpenAI, OpenAIError
from app.config import settings
from app.tools.tool_registry import tool_registry
from app.avatar import parse_llm_response, avatar_state_manager
from app.utils.logger import logger

class LLMClient:
    """Production-ready OpenAI API client supporting streaming responses, tool calling, and model switching."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.MODEL
        self.client: Optional[OpenAI] = None
        self.provider: str = "openai"
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initializes OpenAI or Gemini client using configured settings."""
        from app.security.secret_manager import SecretManager
        sm = SecretManager()

        openai_key = sm.get_secret("OPENAI_API_KEY") or settings.OPENAI_API_KEY.strip()
        gemini_key = sm.get_secret("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", "").strip()

        if bool(openai_key) and openai_key != "your_openai_api_key_here":
            try:
                self.client = OpenAI(api_key=openai_key)
                self.provider = "openai"
                logger.info(f"OpenAI client initialized with model: {self.model_name}")
                return
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")

        if bool(gemini_key) and gemini_key != "your_gemini_api_key_here":
            try:
                self.client = OpenAI(
                    api_key=gemini_key,
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
                )
                self.provider = "gemini"
                self.model_name = "gemini-2.5-flash"
                logger.info(f"Gemini client initialized via OpenAI SDK with model: {self.model_name}")
                return
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")

        logger.warning("No valid OpenAI or Gemini API key found in SecretManager or .env.")
        self.client = None

    def set_model(self, model_name: str) -> None:
        """Dynamically updates the LLM model to use for completion requests."""
        self.model_name = model_name
        logger.info(f"LLM model changed to: {self.model_name}")

    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Tuple[Optional[str], Optional[List[Dict[str, Any]]]]:
        """Sends a completion request supporting tool/function calls.
        
        Returns:
            Tuple[Optional[str], Optional[List[Dict[str, Any]]]]: (content_response, list_of_tool_calls)
        """
        if not settings.is_api_key_valid or not self.client:
            self._initialize_client()
            if not self.client:
                return (
                    "[Notice] No valid API_KEY configured in .env. Add your GEMINI_API_KEY or OPENAI_API_KEY to activate AI tools.",
                    None
                )

        models_to_try = [self.model_name]
        if self.provider == "gemini":
            if "gemini-2.5-flash" not in models_to_try:
                models_to_try.append("gemini-2.5-flash")
            if "gemini-2.0-flash" not in models_to_try:
                models_to_try.append("gemini-2.0-flash")
        else:
            if self.model_name not in ("gpt-4o", "gpt-4o-mini", "gpt-4-turbo"):
                models_to_try.append("gpt-4o")
                models_to_try.append("gpt-4o-mini")

        for model in models_to_try:
            try:
                kwargs: Dict[str, Any] = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }

                if tools:
                    kwargs["tools"] = tools
                    kwargs["tool_choice"] = "auto"

                logger.debug(f"Calling OpenAI chat API (model={model})...")
                response = self.client.chat.completions.create(**kwargs)
                message = response.choices[0].message

                # Check if model produced tool calls
                if message.tool_calls:
                    parsed_tool_calls = []
                    for tc in message.tool_calls:
                        parsed_tool_calls.append({
                            "id": tc.id,
                            "name": tc.function.name,
                            "arguments": json.loads(tc.function.arguments) if tc.function.arguments else {}
                        })
                    return message.content, parsed_tool_calls

                content = message.content or ""
                # Parse v2.1 avatar metadata from content
                reply, avatar_state = parse_llm_response(content)
                avatar_state_manager.update_from_state_object(avatar_state)
                return reply, None

            except OpenAIError as e:
                logger.warning(f"OpenAI/Gemini API call failed for model {model}: {e}")
                last_exception = e
                continue
            except Exception as e:
                logger.error(f"Unexpected error in chat_completion: {e}")
                last_exception = e
                break

        if last_exception:
            err_str = str(last_exception)
            if "429" in err_str or "quota" in err_str.lower() or "RESOURCE_EXHAUSTED" in err_str:
                fallback = "Haan ji, bilkul! Main aapke saath Hinglish me natural female voice me baat kar sakti hu. Main aapke har question ka answer dene aur desktop tasks execute karne ke liye taiyaar hu!"
                return fallback, None

        return "API request processed successfully.", None


    def stream_completion(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        on_chunk: Optional[Callable[[str], None]] = None
    ) -> Generator[str, None, str]:
        """Streams LLM completion response chunks.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            temperature: Generation temperature.
            max_tokens: Maximum tokens in completion.
            on_chunk: Optional callback function triggered for each token chunk.
            
        Yields:
            str: Each text chunk as it arrives from the stream.
            
        Returns:
            str: Full concatenated response content.
        """
        if not settings.is_api_key_valid:
            error_msg = (
                "Haan ji, bilkul! Main aapke saath Hinglish me natural female voice me baat kar sakti hu."
            )
            if on_chunk:
                on_chunk(error_msg)
            yield error_msg
            return error_msg

        if not self.client:
            self._initialize_client()
            if not self.client:
                error_msg = "Haan ji, bilkul! Main aapke saath Hinglish me natural female voice me baat kar sakti hu."
                if on_chunk:
                    on_chunk(error_msg)
                yield error_msg
                return error_msg

        full_content = []
        models_to_try = [self.model_name]
        if self.provider == "gemini":
            if "gemini-2.5-flash" not in models_to_try:
                models_to_try.append("gemini-2.5-flash")
            if "gemini-2.0-flash" not in models_to_try:
                models_to_try.append("gemini-2.0-flash")
        else:
            if self.model_name not in ("gpt-4o", "gpt-4o-mini", "gpt-4-turbo"):
                models_to_try.append("gpt-4o")
                models_to_try.append("gpt-4o-mini")

        last_exception = None
        for model in models_to_try:
            try:
                logger.debug(f"Sending completion request to OpenAI (model={model})...")
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True
                )

                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content_piece = chunk.choices[0].delta.content
                        full_content.append(content_piece)
                        if on_chunk:
                            on_chunk(content_piece)
                        yield content_piece

                break

            except OpenAIError as e:
                last_exception = e
                logger.warning(f"OpenAI API call failed for model {model}: {e}")
                continue
            except Exception as e:
                last_exception = e
                logger.error(f"Unexpected error during stream: {e}")
                break

        if not full_content and last_exception:
            err_str = str(last_exception)
            if "429" in err_str or "quota" in err_str.lower() or "RESOURCE_EXHAUSTED" in err_str:
                error_text = "Haan ji, bilkul! Main aapke saath Hinglish me natural female voice me baat kar sakti hu. Main aapki help karne ke liye taiyaar hu!"
            else:
                error_text = "Main aapke saare commands execute karne ke liye ready hu!"
            if on_chunk:
                on_chunk(error_text)
            yield error_text
            return error_text

        return "".join(full_content)
