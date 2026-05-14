# Related Work

> Where VirtualMe sits in the literature and the wider personal-AI design space.

This document references only **academic / open-source / standardized work**. It deliberately avoids naming or comparing against specific commercial products — those move too fast and naming them dates the document. Operators wanting a current commercial-product comparison should run their own scan when they read this.

---

## 1. Foundational paper

### Stanford Generative Agent Simulations (Park et al., 2024)

[arXiv:2411.10109](https://arxiv.org/abs/2411.10109) — "Generative Agent Simulations of 1,000 People"

**Headline finding:** a 2-hour qualitative interview, transformed into an LLM agent prompt, reproduces the interviewee's answers to the General Social Survey with ~85% normalized accuracy — within 1.7 percentage points of how accurately the interviewee themselves replicates their own answers two weeks later.

**Why this matters for VirtualMe:**

- The 2-hour threshold is a floor, not a ceiling. VirtualMe spreads interviews over 8 weeks × 30 min = 4–6 hours total, well above floor.
- The paper's method is single-pass interview → single agent. VirtualMe extends this with progressive prototype rebuilds every 2 weeks and two blind-test gates.
- The accuracy benchmark (~85%) is on closed-form survey questions. Open-form dialogue self-recognition is empirically lower (60–75%) — which is why VirtualMe's blind test target is 50–60%, not 85%.

### Earlier predecessor: Generative Agents (Park et al., 2023)

[arXiv:2304.03442](https://arxiv.org/abs/2304.03442) — "Generative Agents: Interactive Simulacra of Human Behavior"

The 25-agent Smallville simulation. Demonstrated that LLM agents with persistent memory + reflection + planning produce believable social behavior. Not about extracting specific individuals — but established the architectural primitives (memory stream, reflection, planning) that personal AI agent systems iterate on.

---

## 2. Two architectural paths for personal AI agents

### Path A: prompt-layer + retrieval (VirtualMe's path)

**How it works:** the LLM stays untouched. A system prompt describes the persona (SOUL.md). Voice samples sit in an embedding store, retrieved at inference time and injected into prompts on a per-query basis.

**Trade-offs:**
| Pros | Cons |
|---|---|
| ~$10s/month operating cost | Structural ceiling on adversarial robustness |
| Provider-portable (switch LLM with same files) | Long-context drift on extended conversations |
| Immediately editable by humans (markdown) | Cannot deeply internalize voice — only retrieve |
| No training data leakage | Token cost scales with retrieval k |

### Path B: fine-tune

**How it works:** train the model itself on the interviewee's voice/persona. The persona becomes weights, not prompts.

**Trade-offs:**
| Pros | Cons |
|---|---|
| Internalized voice — no retrieval needed | Six-figure cost (training + ops) |
| Better long-context consistency | Provider-locked (training on Provider X → stuck) |
| Harder to drift in adversarial inputs | Hard to edit (need re-tune to fix) |
| | Training data persists in weights (deletion harder) |

### Why VirtualMe chose Path A

- Cost: 100× cheaper for the same daily use case
- Sovereignty: markdown files travel with the interviewee; weights don't
- Editability: BOUNDARIES.md changes today, takes effect tonight
- Honesty: prompt-layer's ceiling is acknowledged in the spec, not hidden

For interviewees whose Path A blind-test fails (Week 8 accuracy still >70%), the natural next step is Path B fine-tune using the accumulated archive as training data. VirtualMe explicitly **does not implement Path B** — but the artifacts (SOUL.md / VOICE.md / SKILL.md) are exactly the data a Path B trainer would need.

---

## 3. The interview-as-extraction lineage

Treating qualitative interview as a method for extracting cognitive structure is older than LLMs:

- **Cognitive task analysis** (Crandall et al., 2006) — structured interview methodology for capturing tacit expert knowledge. The R1–R5 follow-up rules in VirtualMe are a simplified, LLM-mediated variant of this tradition.
- **Therapist active-listening protocols** (Rogers, 1957 client-centered framework) — mirroring, pause tolerance, acknowledgment of weight. Adopted in interview-engine spec §2, but explicitly bounded: VirtualMe is archival extraction, not therapy (see [`05-boundaries-and-pii.md`](05-boundaries-and-pii.md) §1).
- **The "5 whys" tradition** (Sakichi Toyoda, Toyota Production System, ~1930s) — root-cause inquiry by repeated probing. R2 (pattern → principle) is a softened 5-whys.

The Stanford 2024 result above is roughly the first time an LLM has been shown to operationalize these older interview traditions into an automatable pipeline.

---

## 4. Adjacent design questions

### Persona update protocol

A persistent personal AI must survive the interviewee changing over time. Two failure modes:

1. **Stale persona** — agent represents the interviewee from 18 months ago, getting feedback from people who haven't realized
2. **Silent persona shift** — operator updates the persona without telling external contacts; the agent suddenly sounds different to people who've been talking to it

VirtualMe handles this in [`05-boundaries-and-pii.md`](05-boundaries-and-pii.md) §6: any persona-affecting change is logged, version-controlled, and requires interviewee confirmation. Major shifts (tone / public position) require notification to known contacts.

### Evaluation is genuinely hard

The wider field hasn't converged on how to evaluate "does this agent sound like the person?" Common proposals:

- **Self-recognition** (the interviewee judges blind samples) — VirtualMe's chosen method
- **Peer recognition** (people who know the interviewee judge blind samples)
- **GSS-style closed-form benchmarks** — Park 2024's approach
- **Task-completion** (give agent a task the interviewee has done, compare output)

VirtualMe uses self-recognition primarily, with peer-recognition as a Week 8 secondary signal. We do not claim this is the only valid method — only that it produces actionable shipping decisions.

### Long-conversation drift

Even with good retrieval, prompt-layer agents drift over long conversations: the model gradually defaults to its base distribution rather than the persona. Mitigations VirtualMe applies:

- Re-inject identity anchor every N turns
- Cap session length (25 min dialogue per session)
- Force human review on outgoing content (no autonomous multi-turn outbound)

Whether this is enough depends on the use case. For "draft messages and review" — yes, sufficient. For "have a 3-hour autonomous customer call" — no, do not use VirtualMe.

---

## 5. What VirtualMe does NOT claim

To be honest about scope:

- ❌ We do NOT claim VirtualMe is the best architecture. Path B may be better for high-fidelity use cases.
- ❌ We do NOT claim 8 weeks is the optimal interview length. It's a balance between depth and dropout risk for the use cases we've tested.
- ❌ We do NOT claim 50–60% blind-test accuracy is the universal ship threshold. It's our chosen calibration for "draft → human review → ship" use cases; high-autonomy use cases need higher.
- ❌ We do NOT claim the question pool covers all professions. The 8 pillars (SOUL/VOICE/SKILL/PEOPLE/HISTORY/JOURNAL/BOUNDARIES/STATE) generalize well, but specific weeks (especially SKILL) need profession customization (see [`02-question-pool.md`](02-question-pool.md)).

---

## 6. Reading list

If you want to think deeper about the design space:

- Park et al. 2024 (arXiv:2411.10109) — interview-based generative agents
- Park et al. 2023 (arXiv:2304.03442) — generative agents architecture
- Crandall, Klein, & Hoffman (2006) — *Working Minds: A Practitioner's Guide to Cognitive Task Analysis*
- Anthropic's prompt caching documentation — for cost optimization
- Rogers, C.R. (1957) — *The Necessary and Sufficient Conditions of Therapeutic Personality Change*
- OWASP LLM Top 10 — when designing BOUNDARIES.md threat model

---

## 7. If you build something better

Open an issue or PR. The point of MIT-licensing this repo is so that better designs can build on these primitives without re-deriving them. The spec is the contribution, not the code.
