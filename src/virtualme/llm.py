"""LLM provider abstraction for VirtualMe.

The interview engine expects Anthropic-style responses with
``response.content[0].text``. Provider adapters normalize other vendors to that
small shape so call sites can stay focused on interview behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from anthropic import AsyncAnthropic

from virtualme.config import Settings


@dataclass
class LLMTextBlock:
    text: str


@dataclass
class LLMMessageResponse:
    content: list[LLMTextBlock]


class LLMProviderError(RuntimeError):
    """Raised when provider configuration or SDK setup is invalid."""


class GeminiClient:
    """Small adapter that exposes a ``create_message`` method.

    It accepts the subset of Anthropic ``messages.create`` kwargs used by this
    project and returns an Anthropic-shaped response.
    """

    provider = "gemini"

    def __init__(self, api_key: str):
        try:
            from google import genai
        except ImportError as exc:  # pragma: no cover - depends on optional runtime install
            raise LLMProviderError(
                "Gemini provider requires the google-genai package. "
                "Install project dependencies again after updating pyproject.toml."
            ) from exc

        self._client = genai.Client(api_key=api_key)

    async def create_message(self, **kwargs: Any) -> LLMMessageResponse:
        try:
            from google.genai import types
        except ImportError as exc:  # pragma: no cover - depends on optional runtime install
            raise LLMProviderError("Gemini provider requires google-genai.") from exc

        system = kwargs.get("system")
        messages = kwargs.get("messages", [])
        contents = [self._to_gemini_content(message) for message in messages]

        config_kwargs: dict[str, Any] = {}
        if kwargs.get("max_tokens") is not None:
            config_kwargs["max_output_tokens"] = kwargs["max_tokens"]
        if kwargs.get("temperature") is not None:
            config_kwargs["temperature"] = kwargs["temperature"]
        if system:
            config_kwargs["system_instruction"] = system

        response = await self._client.aio.models.generate_content(
            model=kwargs["model"],
            contents=contents,
            config=types.GenerateContentConfig(**config_kwargs),
        )
        return LLMMessageResponse(content=[LLMTextBlock(text=response.text or "")])

    def _to_gemini_content(self, message: dict[str, Any]) -> Any:
        role = "model" if message.get("role") == "assistant" else "user"
        text = self._content_to_text(message.get("content", ""))
        return {"role": role, "parts": [{"text": text}]}

    def _content_to_text(self, content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
                else:
                    parts.append(str(item))
            return "\n".join(part for part in parts if part)
        return str(content)


def _secret_value(secret: Any | None) -> str | None:
    if secret is None:
        return None
    return secret.get_secret_value()


def build_llm_client(settings: Settings, api_key: str | None = None) -> Any:
    """Build the configured LLM client.

    ``api_key`` is kept for BYOK-style callers that pass a per-user key.
    """
    provider = settings.llm_provider.lower().strip()
    if provider == "anthropic":
        key = api_key or _secret_value(settings.anthropic_api_key)
        if not key:
            raise LLMProviderError("ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic.")
        return AsyncAnthropic(api_key=key, max_retries=4)

    if provider == "gemini":
        key = api_key or _secret_value(settings.gemini_api_key)
        if not key:
            raise LLMProviderError(
                "GEMINI_API_KEY or GOOGLE_API_KEY is required when LLM_PROVIDER=gemini."
            )
        return GeminiClient(api_key=key)

    raise LLMProviderError(f"Unsupported LLM_PROVIDER: {settings.llm_provider!r}")
