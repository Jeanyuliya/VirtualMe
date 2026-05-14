# Tech Stack

> Target: ~600 LoC Python. Lean by design.

## 1. Architecture

```
┌──────────────────────────────────┐
│ Interviewee (LINE / Telegram / CLI) │
└──────────────────────────────────┘
        │ text or voice
        ▼
┌──────────────────────────────────┐
│ Transport layer (webhook / CLI)  │
│ src/virtualme/transport/         │
└──────────────────────────────────┘
        │
        ├─ Voice → STT (your choice: Whisper / Gemini / external API)
        ├─ Load session state (SQLite)
        ├─ Question Selection (spec §4)
        ├─ Claude API call (Opus, dynamic system prompt)
        ├─ Apply follow-up rules R1–R5
        ├─ Update anchors / voice_samples
        ├─ Embed VOICE samples (your choice: bge-m3 / OpenAI / external)
        └─ Reply
```

## 2. Stack Choices

| Layer | Choice | Why |
|---|---|---|
| **Server** | FastAPI (Python) | Async-first, type-safe, ecosystem |
| **LLM** | Claude Opus (main interview reply) + Haiku/Sonnet (internal classification) | Don't downgrade the user-facing reply — interview quality matters. Internal helpers (depth classifier, anchor extractor) can use cheaper models. |
| **Speech-to-text** | Pluggable (default: stub) | Operator's choice — Whisper API, Gemini, AssemblyAI all fine |
| **Messaging platform** | LINE Bot SDK (Telegram trivially swappable) | Maximize interviewee adoption — use the platform they already check daily |
| **DB** | SQLite (aiosqlite) | Single-user scale doesn't need Postgres |
| **Embeddings** | Pluggable (1024-dim slot reserved) | bge-m3 recommended; any 1024-dim model works |
| **Vector search** | Inline numpy / sqlite-vss | No separate vector DB |
| **Deployment** | Self-hosted (any Linux box / Mac mini / VPS) | Conversation data stays local |
| **Webhook exposure** | ngrok / Cloudflare Tunnel / reverse proxy | Whatever the operator already uses |

## 3. SQLite Schema

See [`src/virtualme/storage/schema.sql`](../src/virtualme/storage/schema.sql) — six tables:

- `sessions` — week, energy, status
- `turns` — user/bot messages, content_hash UNIQUE for dedup
- `anchors` — dimension × layer × triangulated boolean
- `voice_samples` — content + metadata_json + 1024-dim embedding BLOB
- `question_state` — per-interviewee question asked count + depth
- `blind_tests` — Gate 1/2 results

## 4. Core Endpoint

See [`src/virtualme/main.py`](../src/virtualme/main.py). FastAPI app, three routes:
- `GET /healthz` — liveness
- `POST /webhook/line` — LINE message handler
- `POST /interview/turn` — direct API endpoint (for CLI / testing / non-LINE transport)

Bot orchestration: [`src/virtualme/interview/bot.py`](../src/virtualme/interview/bot.py) → `process_turn()`.

## 5. Claude API Settings — Tiered Model Routing

```python
# Main interview reply (user-facing) — use Opus
response = await claude.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    system=system_prompt,
    messages=messages,
    temperature=0.3,             # Lower than chatbot default — interview consistency matters
)

# Internal classification (depth evaluator: fact / pattern / principle) — use Haiku
classification = await claude.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=10,
    messages=[{"role": "user", "content": classify_prompt}],
)

# Internal extraction (anchor extractor) — Sonnet is a reasonable middle ground
extraction = await claude.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=512,
    messages=[{"role": "user", "content": extract_prompt}],
)
```

**Rule of thumb:**
- User-facing dialogue → Opus (quality matters)
- Structured classification / extraction → Haiku or Sonnet (cost matters)

**Prompt caching strongly recommended**: the system prompt (interview rules + accumulated anchors) is mostly stable across a session. Use Anthropic's prompt caching to drop input cost ~80%. See [Anthropic docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching).

## 6. VOICE Retrieval Pipeline (Week 4+)

```python
async def get_voice_context(user_query: str, current_scenario: dict) -> str:
    # 1. Infer current scenario metadata
    target_metadata = infer_scenario_metadata(user_query)
    # e.g. {audience: "candidate", register: "casual", mood: "friendly"}

    # 2. Metadata filter first, then embedding search
    filtered = sql_filter_by_metadata(target_metadata)

    # 3. Embed query + top-k retrieve
    query_embedding = await embed(user_query)
    top_k_samples = vector_search(query_embedding, filtered, k=3)

    # 4. Assemble into prompt
    return format_samples(top_k_samples)
```

**`k=3` is the starting point**. Reduce to 2 if blind test triggers overfit warning (see [`03-blind-test-protocol.md`](03-blind-test-protocol.md) §"Overfit Diagnosis").

## 7. Deployment Profile

### Self-hosted (recommended)

```
Location: any Linux box, Mac mini, or modest VPS
Service: virtualme-bot
Port: 8000 (internal)
Reverse proxy: Caddy / nginx / Cloudflare Tunnel
Process manager: systemd / launchd / supervisor
Logs: ./logs/virtualme.log (rotate daily)
DB: ./data/virtualme.db (back up nightly)
```

### Environment variables (see `.env.example`)

```bash
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-opus-4-7
LINE_CHANNEL_ACCESS_TOKEN=...  # optional
LINE_CHANNEL_SECRET=...        # optional
DATABASE_URL=sqlite:///./data/virtualme.db
SESSION_MAX_MINUTES=25
ENERGY_LOW_THRESHOLD=3
HOST=127.0.0.1
PORT=8000
```

### Minimum monitoring

```
1. /healthz returns 200
2. Daily log rotation
3. Claude API token usage → weekly digest (don't build a dashboard)
4. PII detection trigger log
5. Interviewee "skip / change / tired" reply count → operator review trigger
```

## 8. Phased Deployment

### Phase 0: Local CLI verification (1 day)

No LINE, pure CLI:
```bash
python -m virtualme.cli --interviewee test-user
```

Verify: Claude API works, system prompt loads, R1–R5 fires correctly. The operator should run themselves through one cycle as a smoke test.

### Phase 1: LINE Bot integration (1–2 days)

Wire LINE webhook, interviewee can chat with the bot. SQLite + STT integration.

### Phase 2: Voice Embedding (Week 4 of interview)

Wire embedding service + voice_samples table + retrieval pipeline.

### Phase 3: Agent mode (Week 5+ of interview)

System prompt switches from interview to representation. Blind test protocol starts.

## 9. Cost Estimate

### Claude API (Opus, with prompt caching)

- Per session: ~25 min × ~30 turns
- Cached input: ~3K tokens × 0.1× base rate
- Output: ~300 tokens
- Opus pricing: $15/M input, $75/M output (uncached); $1.50/M cached
- Per session ≈ $1.30 with caching, $2.00 without
- 8 weeks × 2 sessions/week = 16 sessions ≈ **$21–32**

### STT (optional)

- Whisper API: ~$0.006/min × 30 min × 16 = ~$3
- Gemini Flash audio: cheaper; OpenAI Whisper: middle

### Total: **< $50 USD one-time + $5/month** ongoing

Less than 1/80 the price of a $4,000 cohort course.

## 10. Hard Nots (what we don't build)

- ❌ Dashboard for the operator (the design ethic: don't build things you have to babysit)
- ❌ Multi-tenant — this is a personal pipeline, one interviewee per deployment
- ❌ Re-build STT — pick a vendor, treat it as commodity
- ❌ Re-build embedding service — same logic
- ❌ Auto fine-tune — ship the prompt-layer version first; fine-tune only if blind tests prove insufficient

## 11. Known Risks

| Risk | Mitigation |
|---|---|
| LINE webhook flaky | Retry + dead-letter log |
| Claude API rate limit | Token budget tracking + degraded mode (queue and reply later) |
| Persona drift over long sessions | Re-inject identity anchor every N turns |
| PII leaks into outgoing prompts | Tag-based filter (see [`05-boundaries-and-pii.md`](05-boundaries-and-pii.md) §4) + scrub on save |
| Operator forgets to back up | Cron job nightly to copy `data/virtualme.db` to backup location |
