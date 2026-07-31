from typing import List, Dict, Generator, Optional, Callable, Any, Tuple
import json
import openai
from openai import OpenAI, OpenAIError
from app.config import settings
from app.tools.tool_registry import tool_registry
from app.utils.logger import logger

class LLMClient:
    """Production-ready OpenAI API client supporting streaming responses, tool calling, and model switching."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.MODEL
        self.client: Optional[OpenAI] = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initializes the OpenAI API client using configured settings."""
        if not settings.is_api_key_valid:
            logger.warning("OpenAI API key is missing or invalid placeholder.")
            self.client = None
            return

        try:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info(f"OpenAI client initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
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
                    "[Notice] No valid OPENAI_API_KEY configured in .env. Add your key to activate AI tools.",
                    None
                )

        models_to_try = [self.model_name]
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

                return message.content, None

            except OpenAIError as e:
                logger.warning(f"OpenAI API call failed for model {model}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error in chat_completion: {e}")
                break

        return "API request failed. Please check network or API key configuration.", None

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
                "\n[Notice] No valid OPENAI_API_KEY configured in .env.\n"
                "Please add your API key to .env (OPENAI_API_KEY=your_key_here) to activate AI responses."
            )
            if on_chunk:
                on_chunk(error_msg)
            yield error_msg
            return error_msg

        if not self.client:
            self._initialize_client()
            if not self.client:
                error_msg = "OpenAI client is not initialized."
                if on_chunk:
                    on_chunk(error_msg)
                yield error_msg
                return error_msg

        full_content = []
        models_to_try = [self.model_name]
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
            error_text = f"\n[API Error]: {str(last_exception)}"
            if on_chunk:
                on_chunk(error_text)
            yield error_text
            return error_text

        return "".join(full_content)
