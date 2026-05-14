# Memory Architecture

> How VirtualMe stores what it learns about you — and how the agent can learn from its own mistakes.
> Last updated: 2026-05-14

---

## Why this document exists

A persona-extraction pipeline that only stores transcripts is a fancy chat log. To produce an agent that meaningfully represents someone, the system needs four kinds of memory — not three, not five, and definitely not "just one big vector store".

This document defines those four layers, what they store, when they update, and how the default SQLite implementation can be upgraded to a self-hosted memory engine ([memory-hall](https://github.com/MakiDevelop/memory-hall)) for production deployments.

---

## The four layers

```
┌──────────────────────────────────────────────────────────────┐
│ L1 Episodic         what was said                            │
│   "I yelled at my manager when he questioned my judgment"    │
└──────────────────────────────────────────────────────────────┘
                          │ end-of-session extraction
                          ▼
┌──────────────────────────────────────────────────────────────┐
│ L2 Semantic         what we extracted                        │
│   (interviewee, value_anchor, "directness over deference")   │
│   triangulated when ≥3 different questions surface the same  │
└──────────────────────────────────────────────────────────────┘
                          │ weekly reflection pass
                          ▼
┌──────────────────────────────────────────────────────────────┐
│ L3 Reflective       what we noticed about our model          │
│   "SOUL says 'direct' but VOICE samples to clients are       │
│    diplomatic — this is register switching, not contradiction"│
└──────────────────────────────────────────────────────────────┘
                          │ post-ship agent feedback
                          ▼
┌──────────────────────────────────────────────────────────────┐
│ L4 Corrective       what went wrong, what changed            │
│   "She rejected my LinkedIn draft on 2026-06-02 because it   │
│    used 'we' instead of 'I' — never use plural pronouns"    │
└──────────────────────────────────────────────────────────────┘
```

Each layer feeds the one below it. Skipping a layer is not "minimalism" — it's a category mistake. A system without L3/L4 cannot meaningfully improve over time.

---

## L1 — Episodic Memory

**What:** raw interview turns. Every word the interviewee and bot exchanged.

**Schema (SQLite default)**:
```sql
turns (id, session_id, role, content, content_hash UNIQUE, voice_audio_path, ts)
sessions (id, interviewee_id, week, started_at, ended_at, status, energy_score)
redactions (id, turn_id, category, original, replacement, span_start, span_end)
```

**Update trigger:** every conversation turn.

**Privacy:** PII scrubbed via [`05-boundaries-and-pii.md`](05-boundaries-and-pii.md) §3 before storage. `redactions` table holds the operator-only un-redaction map, never enters outgoing prompts.

**Retention:** persisted for the interviewee's lifetime of using their agent. Hard-deletable on request.

---

## L2 — Semantic Memory

**What:** structured extractions of who the interviewee is.

Two sub-stores:
- **Anchors** — `(dimension, layer, content)` per [`01-interview-engine.md`](01-interview-engine.md). Dimensions are SOUL / VOICE / SKILL / PEOPLE / HISTORY / JOURNAL / BOUNDARIES / STATE.
- **Triples** — `(subject, relation, object)` for PPA retrieval per [`07-related-work.md`](07-related-work.md) §2 PPA.

**Schema (SQLite default)**:
```sql
anchors (id, interviewee_id, dimension, layer, content, triangulated, source_turn_ids, pii_tag)
persona_triples (id, interviewee_id, subject, relation, object, source_turn_ids, embedding BLOB)
```

**Update triggers:**
- End of each session — automatic triple extraction via [`session_lifecycle.py`](../src/virtualme/interview/session_lifecycle.py)
- During session — R1–R5 anchor extraction per [`01-interview-engine.md`](01-interview-engine.md) §3

**Triangulation rule:** an anchor becomes `triangulated=True` when it has appeared as the answer in **≥3 different question_ids** (NOT 3 turns — turns from the same probing thread don't count separately). See [issue #3](https://github.com/MakiDevelop/VirtualMe/issues/3) for current implementation gap.

**Production note:** L2 is where the system goes from "we have your words" to "we have a model of you." Quality of L2 is the bottleneck for agent fidelity. Spend extraction prompt-engineering effort here, not anywhere else.

---

## L3 — Reflective Memory

**What:** the system's own observations about its model.

This is where **self-learning** lives. Reflections capture:
- Contradictions between SOUL anchors and VOICE samples (often register switching, not contradictions)
- Patterns across sessions (e.g., "interviewee mentions burnout in 3/4 sessions where the topic comes up")
- Drift detection (this week's extractions don't match the model we had two weeks ago)
- Coverage holes (BOUNDARIES has only 2 entries — flag for next-session question selection)

**Schema (SQLite default)**:
```sql
-- NOT YET IMPLEMENTED — v0.5 scope
reflections (
    id INTEGER PRIMARY KEY,
    interviewee_id TEXT NOT NULL,
    reflection_type TEXT NOT NULL,  -- contradiction / drift / coverage_gap / pattern
    content TEXT NOT NULL,
    evidence_anchor_ids TEXT NOT NULL,  -- JSON array
    confidence REAL,
    requires_human_review BOOLEAN DEFAULT 1,
    resolution TEXT,  -- after human review: "register-switching" / "real contradiction" / "noise"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);
```

**Update triggers:**
- **Weekly reflection pass** — run at the end of each interview week, scans the past 7 days' L2 changes
- **Pre-blind-test pass** — Week 5 and Week 8, surfaces contradictions for the operator to review with the interviewee
- **Post-deployment pass** — after the agent ships, scans agent-mode interactions for drift

**Important: L3 entries are draft observations, not facts.** They require interviewee confirmation before becoming SOUL anchors. The mechanism is documented in [`05-boundaries-and-pii.md`](05-boundaries-and-pii.md) §6 Persona Update Protocol.

**Status:** ❌ not yet implemented (v0.5).

---

## L4 — Corrective Memory

**What:** what the agent got wrong, and what the interviewee taught it.

This is **self-reflection** that closes the loop:
- The agent drafts a message → interviewee reviews → interviewee says "this isn't quite me"
- That rejection contains a signal: which part is wrong, and ideally why
- L4 captures this signal so future drafts avoid the same mistake

**Schema (SQLite default)**:
```sql
-- NOT YET IMPLEMENTED — v0.5 scope
feedback (
    id INTEGER PRIMARY KEY,
    interviewee_id TEXT NOT NULL,
    agent_output TEXT NOT NULL,         -- what the agent generated
    rejected BOOLEAN NOT NULL,
    rejection_reason TEXT,              -- "tone too formal" / "wrong vocabulary" / "factual error"
    corrected_version TEXT,             -- if interviewee provided one
    extracted_lesson TEXT,              -- LLM-synthesized "what to learn from this"
    affected_dimension TEXT,            -- which L2 dimension this updates
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Update trigger:** agent-mode interaction with feedback signal. UI for capturing this is part of v0.5 ("not just a Slack 👍/👎 reaction — needs a 'why' field").

**Important: L4 entries directly modify L2.** A pattern of rejections on "tone too formal" triggers re-weighting of VOICE samples toward casual register. This is how the agent learns without fine-tuning.

**Status:** ❌ not yet implemented (v0.5+).

---

## Self-learning & self-reflection summary

| Capability | Layer | Status |
|---|---|---|
| Remember what was said | L1 | ✅ v0.4 (SQLite) |
| Extract structured persona | L2 | ✅ v0.4 (with [#3](https://github.com/MakiDevelop/VirtualMe/issues/3) bug + [#9](https://github.com/MakiDevelop/VirtualMe/issues/9) embedding gap) |
| Auto-extract triples at session end | L2 | ⚠️ partial — function exists ([#8](https://github.com/MakiDevelop/VirtualMe/issues/8)) |
| Detect coverage gaps to drive next question | L2 → bot | ✅ v0.4 |
| Notice contradictions between SOUL and VOICE | L3 | ❌ v0.5 |
| Detect cross-session drift in extracted model | L3 | ❌ v0.5 |
| Flag patterns across sessions for human review | L3 | ❌ v0.5 |
| Capture agent-mode rejections + learn from them | L4 | ❌ v0.5+ |
| Auto-adjust VOICE retrieval weighting from feedback | L4 → L2 | ❌ v0.6 |

The system can't truly **self-reflect** until L3 lands. It can't truly **self-correct** until L4 lands. Until then, it can extract and triangulate (which is already useful, but not the full vision).

---

## The default backend: SQLite

VirtualMe ships with SQLite as the default. Reasons:

- Zero infrastructure: one file, no service
- Local-first: data never leaves the operator's machine unless they explicitly export
- Hard delete is actually hard (overwrite the file, gone)
- Sufficient for a single interviewee's pipeline through v0.4

**SQLite supports L1 + L2 well. SQLite supports L3 + L4 awkwardly.**

The reasons L3/L4 are awkward in SQLite:
1. Reflection passes want hybrid search (BM25 + semantic) — SQLite has BM25 (FTS5) and can do vector via `sqlite-vec`, but you have to wire both
2. Provenance tracking — L3 needs to know which L2 entries triggered a reflection; SQLite has no native provenance model
3. Cross-session entity resolution — "the boss I mentioned in week 2 is the same boss I'm complaining about in week 5" — graph-like queries are painful in plain SQLite
4. Multi-agent writes (operator + interview bot + reflection cron) need careful locking

You can build all of this on SQLite. You just shouldn't unless you really enjoy reinventing memory engines.

---

## The recommended production backend: memory-hall

[memory-hall](https://github.com/MakiDevelop/memory-hall) is a self-hosted AI agent memory engine (Apache 2.0, SQLite + sqlite-vec + Ollama under the hood, CJK-native). It is **deliberately small** — exactly the same design ethic as VirtualMe.

Why memory-hall over rolling our own L3/L4:

| Capability | DIY SQLite | memory-hall |
|---|---|---|
| Hybrid BM25 + semantic search | Manual wiring | Built-in (RRF fusion) |
| Per-agent namespaces | Add column + filter | First-class concept |
| Provenance / upstream tracking | Hand-roll JSON arrays | `upstream_ids` + `provenance_tier` schema |
| HMAC-authenticated API | Build it yourself | Built-in (per [memory-hall docs](https://github.com/MakiDevelop/memory-hall)) |
| Entry types (episode / observation / fact / etc.) | Define your own enum | Already standardized |
| Embed model lifecycle (queue, retry, status) | Build the worker | Built-in (`embed_attempt_count`, `last_embed_error`) |
| CJK tokenization for BM25 | Default SQLite FTS5 fails on Chinese | Native handling |
| Dedup via content_hash | Add UNIQUE constraint | Built-in |

memory-hall isn't trying to be Pinecone or Weaviate. It's trying to be the boring, reliable memory layer behind small AI projects. That's exactly what VirtualMe needs.

### Mapping VirtualMe's 4 layers onto memory-hall

memory-hall's schema uses `(agent_id, namespace, type, content)`. VirtualMe maps cleanly:

| VirtualMe Layer | memhall agent_id | memhall namespace | memhall type |
|---|---|---|---|
| L1 Episode | `virtualme-bot` | `project:virtualme:<interviewee_id>` | `episode` |
| L2 Triple (raw) | `virtualme-extractor` | `project:virtualme:<interviewee_id>` | `observation` |
| L2 Anchor (triangulated) | `virtualme-extractor` | `project:virtualme:<interviewee_id>` | `fact` |
| L3 Reflection | `virtualme-reflector` | `project:virtualme:<interviewee_id>` | `note` |
| L4 Feedback | `virtualme-agent` | `project:virtualme:<interviewee_id>` | `experiment` |
| Blind test result | `virtualme-evaluator` | `project:virtualme:<interviewee_id>` | `experiment` |

Each `agent_id` corresponds to a logical role within VirtualMe. memhall tracks which role wrote which entry, which gives audit + filtering for free.

### Crucially: L2 `fact` entries link upstream to L2 `observation` entries

memhall's `upstream_ids` field lets us encode triangulation natively:
```json
{
  "agent_id": "virtualme-extractor",
  "namespace": "project:virtualme:alice",
  "type": "fact",
  "content": "Alice values directness over deference",
  "upstream_ids": ["obs-2026-05-20-1", "obs-2026-05-22-3", "obs-2026-06-01-7"],
  "provenance_tier": "human_confirmed"
}
```

Three different observations from three different sessions → one triangulated fact. The provenance is queryable, falsifiable, and auditable. SQLite can do this but you have to build the indices yourself.

### Integration interface

Both backends implement the same Protocol:

```python
# src/virtualme/storage/interface.py (v0.5 scope)
class MemoryBackend(Protocol):
    async def save_episode(self, interviewee_id: str, turn: Turn) -> str: ...
    async def save_observation(self, triple: PersonaTriple, source_session_id: int) -> str: ...
    async def save_fact(self, content: str, upstream_observation_ids: list[str]) -> str: ...
    async def save_reflection(self, reflection: Reflection) -> str: ...
    async def save_feedback(self, feedback: Feedback) -> str: ...
    async def search(self, query: str, namespace: str, types: list[str], k: int) -> list[Entry]: ...
    async def hard_delete(self, namespace: str) -> int: ...
```

Two implementations:
- `storage/sqlite_backend.py` — wraps existing `db.py`
- `storage/memhall_backend.py` — HTTP client to memhall, uses `MH_API_TOKEN` for auth

Operator picks via env var:
```
# .env
VIRTUALME_BACKEND=sqlite                          # default
# or:
VIRTUALME_BACKEND=memory-hall
VIRTUALME_MEMHALL_ENDPOINT=http://localhost:9100
VIRTUALME_MEMHALL_TOKEN_FILE=~/.config/memhall/token
```

### Honest limitation of the dual-backend approach

- **L3 + L4 are no-ops on the SQLite backend** — calling `save_reflection()` on SQLite stores the row but no reflection pass actually runs against it. The interface accepts the writes; the analysis logic only runs against memhall.
- This is a feature, not a bug. SQLite is for "just want to try VirtualMe on myself for a week". memhall is for "actually running the 8-week pipeline with the full reflection loop."
- The README will make this distinction loud and clear, so people don't think they're getting self-reflection for free with `pip install virtualme`.

---

## Why this isn't just "use Mem0"

Open issue [#5](https://github.com/MakiDevelop/VirtualMe/issues/5) tracks evaluating Mem0 as a backend. Mem0 (Apache 2.0, 48K stars) has its strengths:
- Excellent LOCOMO benchmark numbers
- Mature SDK
- YC-backed, active development

But Mem0 is designed for **chat agents accumulating memory over time**. It's optimized for "remember what the user told you yesterday." VirtualMe's needs are slightly different:
- We're not just accumulating; we're **extracting structured persona artifacts** with explicit provenance
- We need **roles** (extractor / reflector / evaluator / agent) writing to the same namespace, with attribution
- We need **CJK-native** tokenization (a meaningful share of likely VirtualMe users speak Mandarin / Cantonese / Japanese / Korean)
- We need to **own the storage format** so operators can grep, export, version-control, and reason about their own data

memory-hall hits all four. Mem0 would require us to layer adapters on top.

If a contributor wants to add a Mem0 backend alongside memhall, that's welcome. The MemoryBackend Protocol is designed for that. But the recommended path is memhall.

---

## v0.5 implementation plan

1. **Define `MemoryBackend` Protocol** — `src/virtualme/storage/interface.py`
2. **Refactor existing `db.py` to implement Protocol** as `sqlite_backend.py` (no behavior change)
3. **Implement `memhall_backend.py`** — HTTP client with HMAC auth, retries, exponential backoff
4. **Add L3 `reflections` table** + weekly reflection pass cron job stub
5. **Add L4 `feedback` table** + minimal capture endpoint
6. **Add `VIRTUALME_BACKEND` config** with the two options
7. **Integration test** — same `process_turn` flow runs identically against both backends

Tracked as [issue #5](https://github.com/MakiDevelop/VirtualMe/issues/5) (expanded scope).

---

## Open design questions (for v0.5 design session)

1. **L3 reflection cadence**: weekly (calendar-based), every-N-turns (volume-based), or on-demand? Trade-off is freshness vs noise.
2. **L4 feedback UI**: minimum viable is a CLI command (`virtualme feedback --reject "draft text" --reason "tone too formal"`). Better is a 1-click hook in messaging client. Best is automatic detection (user edits the draft significantly → signal extracted). v0.5 ships CLI; v0.6 explores messaging hook.
3. **Cross-interviewee privacy**: memhall namespaces are per-interviewee — `project:virtualme:alice` and `project:virtualme:bob` are isolated. Operators running multiple interviewees should be aware that misconfigured namespaces would mix data. v0.5 adds a `validate_namespace_isolation()` startup check.
4. **Forgetting**: should L1 episodes auto-expire after the 8-week extraction window if the operator chooses? Reduces blast radius if the DB file leaks. v0.6 question, default = no auto-forget.

---

## TL;DR

- VirtualMe needs 4 memory layers; v0.4 has 2 (L1 / L2). L3 (self-reflection) and L4 (self-correction) are v0.5+.
- Default backend is SQLite — simple, local, friction-free.
- Recommended production backend is [memory-hall](https://github.com/MakiDevelop/memory-hall) — handles hybrid search + provenance + multi-agent attribution out of the box.
- Both backends implement the same `MemoryBackend` Protocol (v0.5).
- SQLite is for trying VirtualMe on yourself. memhall is for running real 8-week pipelines that actually self-reflect.
