# LLM Providers

VirtualMe can select the LLM backend through environment variables.

## Anthropic Claude

Default provider:

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxx
```

Default model tiers:

```env
VIRTUALME_MODEL_FAST=claude-haiku-4-5
VIRTUALME_MODEL_STANDARD=claude-sonnet-4-6
VIRTUALME_MODEL_DEEP=claude-opus-4-7
```

## Google Gemini

Use a Google AI Studio key:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_google_ai_studio_key
```

`GOOGLE_API_KEY` is also accepted as an alias for `GEMINI_API_KEY`.

Default model tiers:

```env
VIRTUALME_MODEL_FAST=gemini-2.5-flash
VIRTUALME_MODEL_STANDARD=gemini-2.5-pro
VIRTUALME_MODEL_DEEP=gemini-2.5-pro
```

## Notes

- Existing interview code still receives Anthropic-shaped responses with `response.content[0].text`.
- BYOK remains Claude-key oriented for now. Keep `VIRTUALME_BYOK_ENABLED=false` when running Gemini unless BYOK is expanded to support provider-specific keys.
- If Google changes model names or quota rules, override the tier variables instead of editing code.
