"""Central model-tier registry.

Each interview-engine LLM call selects a model by tier rather than a hardcoded
string. Tiers are environment-overridable so the whole pipeline can be
re-pointed to a supported provider without touching call sites.
"""

from __future__ import annotations

import os
from typing import Any

_PROVIDER = os.getenv("VIRTUALME_LLM_PROVIDER", os.getenv("LLM_PROVIDER", "anthropic")).lower()

_DEFAULT_MODELS = {
    "anthropic": {
        "fast": "claude-haiku-4-5",
        "standard": "claude-sonnet-4-6",
        "deep": "claude-opus-4-7",
    },
    "gemini": {
        "fast": "gemini-2.5-flash",
        "standard": "gemini-2.5-pro",
        "deep": "gemini-2.5-pro",
    },
}

_provider_defaults = _DEFAULT_MODELS.get(_PROVIDER, _DEFAULT_MODELS["anthropic"])
MODEL_FAST = os.getenv("VIRTUALME_MODEL_FAST", _provider_defaults["fast"])
MODEL_STANDARD = os.getenv("VIRTUALME_MODEL_STANDARD", _provider_defaults["standard"])
MODEL_DEEP = os.getenv("VIRTUALME_MODEL_DEEP", _provider_defaults["deep"])

_NO_TEMPERATURE_MODELS = {"claude-opus-4-7"}


async def create_message(client: Any, **kwargs: Any) -> Any:
    """Central message creation wrapper.

    Adapters may expose ``create_message`` directly. Plain Anthropic clients keep
    using ``client.messages.create``.
    """
    if kwargs.get("model") in _NO_TEMPERATURE_MODELS:
        kwargs.pop("temperature", None)
    if hasattr(client, "create_message"):
        return await client.create_message(**kwargs)
    return await client.messages.create(**kwargs)
