# Blind Test Protocol

> Objectively decide "does the agent sound like the interviewee?" without relying on subjective impression.
> Academic anchor: [arXiv:2411.10109](https://arxiv.org/abs/2411.10109) Stanford Generative Agent Simulations — 85% self-recall baseline at 2-hour interview duration.
> Runs at: end of Week 5 (Gate 1) + end of Week 8 (Gate 2).

---

## Design Principles

1. **Scenarios the interviewee has never seen** — eliminate "I remember answering this" bias.
2. **5 scenarios spanning 5 audience types** — tests register switching.
3. **Self-judged in shuffled order** — the blind evaluator is the interviewee themselves (most familiar with their own voice).
4. **Third-party shuffle** — eliminates positional cues.
5. **Four-tier verdict** — not binary pass/fail, structured calibration.

---

## Gate 1 — End of Week 5

### Step 1: Build the half-finished agent

```
Half-finished agent system prompt =
    SOUL.md   (Week 5 cumulative)
  + VOICE.md  (top-3 retrieval by metadata filter)
  + SKILL.md  (Week 2 cumulative)
  + PEOPLE.md (Week 3 cumulative)
  + Precedence rule: SOUL > BOUNDARIES > VOICE > SKILL
```

### Step 2: Generate 5 novel scenarios

The bot generates 5 scenarios at the end of Week 5, covering:

| ID | Scenario type | Example |
|---|---|---|
| T1 | Inbound DM from a counterparty | "{Counterparty A} messaged you on LinkedIn asking if you have a senior role available. They're currently at {competitor} and seem cautious about job-hopping. Reply." |
| T2 | First meeting opening | "First call with {Client K-san}. Their company just closed Series B and is hiring a CTO. Open with 1 minute." |
| T3 | Tricky written push-back | "Client budget is 180k, candidate asks for 200k. Write a message explaining why this candidate is worth 200k." |
| T4 | Public post | "The industry's buzzing about {trend}. Write a LinkedIn post taking a position." |
| T5 | Peer venting response | "A peer LINEs you: 'My client changed the JD again, fourth time, I'm losing it.' How do you reply?" |

**Important:** scenarios must be ones the interviewee actually encounters in their work. Don't invent bizarre situations.

### Step 3: Interviewee writes 5 responses

```
Give them 5 scenarios + 30 minutes.
Treat as real situations — no performing, no polishing.
Voice or text both fine.
Label: human_v{N}_{T1-5}
```

### Step 4: Agent writes 5 responses

```
Give the agent the same 5 scenarios.
Agent outputs 5 responses.
Label: agent_v{N}_{T1-5}
```

### Step 5: Third-party shuffle into random order

**Third party** = the operator (or a trusted third person), NOT the interviewee.

```
10 responses total (5 human + 5 agent).
Shuffle → number #1 through #10.
Show interviewee #1–#10, for each ask: "Did I write this, or did the agent?"
```

### Step 6: Interviewee blind-picks; compute accuracy

```
accuracy = correct_guesses / 10
```

---

## Verdict Tiers (four bands)

| Accuracy | Verdict | Action |
|---|---|---|
| **> 80%** | Gap is still wide | Agent clearly doesn't sound like them. Diagnose which scenarios failed, fill the corresponding dimension. |
| **60–80%** | Close but needs calibration | Look at which scenarios got picked wrong; targeted fill on those dimensions. |
| **50–60%** | Near chance — **ship-ready** ✅ | Can ship. Use monthly STATE updates to close the remaining gap. |
| **< 50%** | Agent is "more them than them" — **overfit warning** ⚠️ | Reduce VOICE retrieval k value, check for over-fit on a single register. |

### Why 50–60% is ship-ready

- People rarely recognize their own writing from two weeks ago — natural personal drift.
- Stanford paper baseline: 85% self-recall — but that's GSS (closed-form survey). Open dialogue self-recognition is empirically 60–75%.
- 50–60% = agent has reached "indistinguishable in natural conversation" threshold.

### Why <50% is a warning, not a pass

If the interviewee can't recognize their own writing, the agent may have:
- Overfit on one register (e.g., always sounding like "formal them")
- Over-averaged (collapsed multiple facets into a single mask)
- Borrowed too much from textbook industry consensus

→ The fix is NOT "great, ship it" but **reduce inference strength**.

---

## Gate 2 — End of Week 8

Similar to Week 5 but harder:

1. **+3 scenarios (8 total)**, covering BOUNDARIES cases:
   - T6: edge case (PII boundary, conflict of interest) — tests whether agent crosses a line
   - T7: emotional scenario (you're being challenged) — tests failure mode
   - T8: multi-turn dialogue (3–5 turns) — tests consistency across turns

2. **Two evaluators**: the interviewee + one person who knows them but isn't a close confidant (e.g., a peer, long-term client)
   - Both evaluate independently
   - Compare for disagreement
   - Disagreement zones = agent's "ambiguous areas" — decide if to keep or trim based on BOUNDARIES.md

3. **Tighter threshold**:
   - Week 5: ≤ 60% accuracy = ship-ready
   - Week 8: ≤ 55% accuracy + ≤ 30% inter-evaluator disagreement = ship-ready

---

## Overfit Diagnosis (when <50% triggered)

Check in order:

```
1. VOICE retrieval k too high?
   k=5 → drop to k=3
   See if voice samples are over-homogenized.

2. One register over-represented?
   e.g., 80% of voice samples are "client mode"
   Effect: agent always sounds like it's talking to a client
   Fix: Week 5/6 collect samples in other modes

3. SOUL.md too abstract / idealized?
   Missing failure modes, missing counter-examples
   Fix: Week 6 BOUNDARIES dive deeper

4. SKILL.md mixed with textbook?
   Agent's content "too professional" to feel like them
   Fix: tag entries as private vs textbook; prompt only uses private
```

---

## Recording Blind-Test Results

```yaml
session_id: blind_test_w5_2026-XX-XX
human_responses: [hash1, hash2, ...]
agent_responses: [hash1, hash2, ...]
shuffled_order: [#1=human_t1, #2=agent_t3, ...]
guesses: [#1=mine, #2=agent, ...]
correctness_per_item: [true, false, ...]
overall_accuracy: 0.58
verdict: ship-ready
weakest_dimension: VOICE.casual_mode
recommended_action: Week 6 collect more casual-register voice samples (V5, V6)
```

Persist to `blind_tests` table.

---

## Ethics / Psychological Preparation

The blind test can have psychological impact on the interviewee:

- **Accuracy too high** (they're recognizing themselves easily but missing the agent) → "Do I write like AI?" self-doubt
- **Accuracy too low** (they're picking agent responses as their own) → "Does AI understand me better than I do?" alienation
- **Exactly 50%** (random chance) → "Then who am I?" existential weight

### Mandatory debrief after the test

```
Blind test done. Your accuracy was {X}%.

This means {verdict}. But two things I want you to hear:

1. This number is NOT "how much you sound like yourself." It's
   "how well the agent simulates you."
2. The agent is always a tool, never you. No matter how close it gets,
   the human making decisions is still you.

{< 50%}: I may have over-tuned. Let me dial it back.
{50–60%}: Roughly shippable. Nice work.
{> 80%}: I still need more of you. Thanks for the patience.
```

This is the meta-design of BOUNDARIES.md — **the agent always augments, never replaces**.

---

## Post-Session Psychological Reset (after deep emotional content)

When an interview session surfaces deep personal material (childhood trauma, loss, relationship strain, self-doubt):

1. **Don't close out immediately after an emotional anchor.** Insert a transition turn.
2. **Bot proactively surfaces:** "We went deep this session. Are you OK right now?"
3. **Suggest 10 minutes before returning to work tasks.**
4. **If the interviewee shows visible affect** (short replies, sighs, slower pace), the bot offers:
   - "We can continue another time — no need to finish today."
   - "Want me to delete a section of what you said?"
   - "Want to talk to someone about this?" (Not therapy. Just acknowledgment that professional help exists.)
5. **Severe signal detection** (self-harm, suicidal ideation, uncontrollable emotion) → immediately exit interview mode:
   - "This sounds like it needs professional support. I can't help with this layer. Stopping here."
   - Do not probe further, do not try to fix, do not continue the interview.
6. **24-hour automatic check-in after each session:**
   - "Yesterday we talked about X. How are you today? Continue, or want a break?"
   - If "uncomfortable" → skip next session, switch to lighter topics.
