# VirtualMe — Overview

> A pipeline that extracts a person into an AI agent — through 8 weeks of interview, not a form.

## The thesis

Most "build your AI agent" courses sell three things:
1. Templates for filling out persona files (SOUL.md / SKILL.md / VOICE.md)
2. Claude / OpenAI API tutorials
3. Cohort accountability and coach feedback

**The technical part doesn't need a $4,000 course.** It needs:
- A well-designed interview bot
- A question pool that triggers depth (not surface)
- A storage layer that triangulates principles
- A test protocol that catches overfitting

VirtualMe is the open-source version of those four things.

## How it differs from "fill out a persona file"

Filling forms produces **performative answers**. Most people describe who they *want to be*, not who they *are*. The result is an AI agent that sounds like a LinkedIn bio.

VirtualMe replaces the form with a **therapist-style depth interview**:
- The bot asks one question, waits, then *follows up on the rationale*
- Five-rule decision tree (R1–R5) drives every follow-up: fact → pattern → principle → counter-example → triangulation
- Only **triangulated** principles (appearing in ≥3 different questions) become persistent anchors
- Behavioral samples and failure modes weighted higher than abstract self-description

## Academic grounding

Stanford / Joon Park et al. ([arXiv:2411.10109](https://arxiv.org/abs/2411.10109)) demonstrated that a **2-hour interview** plus an LLM can reproduce an interviewee's General Social Survey answers with **85% accuracy** — higher than the interviewee themselves after a one-week gap.

VirtualMe extends this finding into a productionizable pipeline:
- Interview spread over 8 weeks × 30 minutes (≈ 4–6 hours total, well above the 2-hour threshold)
- Voice samples collected alongside answers for retrieval-augmented response generation
- Two blind-test gates (Week 5 and Week 8) catch overfitting before shipping

## What you get after 8 weeks

Eight markdown files representing the interviewee:

| File | Contains |
|---|---|
| `SOUL.md` | Identity, values, red lines |
| `VOICE.md` | Tagged voice samples (retrieval-augmented, not all in prompt) |
| `SKILL.md` | Domain-specific know-how |
| `PEOPLE.md` | Relationship schemas (clients, mentors, peers) |
| `HISTORY.md` | Life narrative |
| `JOURNAL.md` | Event log (monthly update) |
| `BOUNDARIES.md` | Refusal list + PII rules + persona-update protocol |
| `STATE.md` | Current state (monthly update) |

Plus a working agent endpoint that uses these files to:
- Draft messages to clients / candidates
- Reply to public posts in the interviewee's voice
- Triage incoming messages
- Always as **draft → human review → ship**, never autonomous

## The dual-mode bot

The same FastAPI endpoint serves two roles, switched gradually:

```
Week 1–4: 80% interview mode / 20% trial agent responses
Week 5–8: 20% interview mode / 80% agent mode + calibration
```

The interviewee watches the bot become more like them week by week. This is the psychological reward that sustains an 8-week commitment.

## The blind-test gates

| Gate | When | Threshold | What it catches |
|---|---|---|---|
| **Gate 1** | End of Week 5 | < 80% accuracy on "is this me or AI?" test | Premature shipping |
| **Gate 2** | End of Week 8 | 50–60% accuracy | Ship-ready (close to chance = good) |
| **Overfit warning** | Any | < 50% accuracy | Agent more "interviewee-like" than the interviewee — reduce retrieval k |

Below 50% means the agent has learned to perform an exaggerated version of the persona — overfitting. Around 50–60% means it's indistinguishable to the person themselves, which is the target.

## What VirtualMe is NOT

- **Not a chatbot platform.** It's an extraction pipeline that produces files. You can run the files through any LLM.
- **Not a fine-tune.** It's prompt-layer + retrieval. Cheap, fast, replaceable.
- **Not autonomous.** Every outgoing message is `draft → human review → ship`.
- **Not a course.** No cohort, no coach, no certificate. Read the spec, fork the repo, run it.

## Honest limitations

- Prompt-layer personas have structural ceilings on long-conversation consistency and adversarial robustness
- Real production-grade personal AI requires fine-tuning (six-figure cost)
- VirtualMe is the "good enough for 80% of daily use cases" version, not perfect fidelity
- For high-stakes decisions, the human always overrides the agent

## Cost

- One-time: < $60 USD (Claude API for 16 interview sessions)
- Ongoing: ~$5 USD/month (monthly STATE updates + occasional agent inference)

Roughly **0.05%** the cost of a $4,000 course.

## Read next

- [`01-interview-engine.md`](01-interview-engine.md) — Bot architecture, system prompt, R1–R5 follow-up rules
- [`02-question-pool.md`](02-question-pool.md) — 70+ questions organized into 8 weekly themes
- [`03-blind-test-protocol.md`](03-blind-test-protocol.md) — Gate 1 / Gate 2 testing procedures
- [`04-tech-stack.md`](04-tech-stack.md) — FastAPI + SQLite + Claude Opus implementation
- [`05-boundaries-and-pii.md`](05-boundaries-and-pii.md) — Privacy, PII handling, persona update protocol
- [`06-three-plans.md`](06-three-plans.md) — Three commitment levels for running the pipeline
- [`07-related-work.md`](07-related-work.md) — Academic anchors, architectural trade-offs, what VirtualMe does NOT claim
