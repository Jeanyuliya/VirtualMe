# Question Pool — 8 Weeks × 8 Dimensions

> The bot's internal question pool. **The interviewee never sees this list.** The bot picks 1–3 questions per session based on Question Selection algorithm (see [`01-interview-engine.md`](01-interview-engine.md) §4).

## Design Principles (Phase 0 Validated)

Phase 0 validation showed:
- **Round 1 (textbook questions: "how's work" / "recent investments" / "what did you write on LinkedIn"):** 0/5 pass on "does this sound like me?"
- **Round 2 (SOUL-activating depth questions: "burn the boat moment" / "your son got bullied and didn't tell you, why" / "why do you recommend tragedies" / "if you disappeared for a month what would remain" / "PMP framework paradox"):** ≥3/5 pass

**The differentiator is not the system prompt. It's the questions.** Textbook questions let any LLM fake a generic answer with no SOUL anchor surface. Depth questions force anchor surface.

Concrete principles enforced by this pool:
1. **Behavioral samples > abstract self-description.** ("Tell me about a time you X" > "Are you X?")
2. **Counter-examples > positive examples.** ("When would you break this rule?" > "What's your rule?")
3. **Rationale probing is mandatory.** Every question has a `rationale_probe` field.
4. **Triangulation required.** Only principles surfaced in ≥3 different questions become SOUL anchors.

---

## Domain Customization

Some questions are **profession-agnostic** (HISTORY, SOUL, BOUNDARIES, STATE — universal human questions). Others are **profession-specific** (SKILL — depends on what the interviewee does).

The pool below shows:
- **HISTORY / SOUL / BOUNDARIES / STATE / VOICE collection prompts**: Use as-is across professions.
- **SKILL**: Templated with `{domain_object}` and `{domain_role}` placeholders. Substitute for the interviewee's profession.
- **PEOPLE**: Profession-agnostic structure; the interviewee fills in their own relationship types.

Three example SKILL domain substitutions are at the bottom:
- Sales / Headhunter
- Software engineer
- Product manager

The question YAML at [`question-pool.yaml`](../src/virtualme/data/question-pool.yaml) ships with the agnostic version. Operators fork and customize.

---

## Week 1 — HISTORY (target: 30–40 anchors)

Each question expects: **fact** (what happened, when) → **pattern** (is this typical) → **principle** (why does this matter to you).

| ID | Question | Rationale probe |
|---|---|---|
| H1 | Why did you enter this profession? What was the original spark? | If that spark hadn't happened, where would you be? |
| H2 | First moment in your career when you thought "I'm doing this right"? | What was your criterion for "doing it right"? |
| H3 | First moment when you thought "I shouldn't continue down this path"? How did you decide? | At that point, what tipped you toward staying / leaving? |
| H4 | Three people who influenced you most (mentor / client / peer / competitor) — what did each teach you? | One sentence from any of them you still remember? |
| H5 | Most regretted professional decision? What did you learn? | If you could redo it, what criterion would you use? |
| H6 | Most proud project? Why this one, not a more famous / lucrative one? | What does it mean to you? |
| H7 | A time you misjudged — recommended / decided wrong. Signals you had vs. hindsight signals? | What changed in your judgment process after? |
| H8 | Family background / childhood / education — how did they shape you for this work? *(optional)* | Which element shapes the current you most deeply? |
| H9 | Your 5-years-ago self looking at you now — what would surprise them? | Did you choose that change actively, or were you pushed? |
| H10 | If not this profession, what? Why? | Is that alternate path still alive in you? |

---

## Week 2 — SKILL (target: 40–50 anchors)

**Profession-agnostic template** (substitute `{domain_object}` and `{domain_role}` for the interviewee's field).

| ID | Question | Rationale probe |
|---|---|---|
| S1 | Your personal SOP for {core_task} — not the textbook version | Which step is your biggest divergence from peers? |
| S2 | Your opening move with {primary_counterparty} — how does it differ from peers? | What do you deliberately avoid in the opener? Why? |
| S3 | Three questions you always ask {decision_partner} that others don't | Beyond those three, what do you read non-verbally? |
| S4 | How do you tell when {counterparty} is genuine vs. going through the motions? | Were you ever fooled? How did you realize? |
| S5 | Strategy differences across {junior / mid / senior} levels of {counterparty} | Which level is hardest? Why? |
| S6 | Three industry consensus practices you disagree with | Why does everyone still do them? Have you been burned by avoiding them? |
| S7 | Five red flags + five green flags from your private checklist | Which one is self-taught, not in any textbook? |
| S8 | Three failure cases + root cause for each | Which one made you change your SOP? How? |

### Example substitutions

**Sales / Headhunter:**
- `{core_task}` = sourcing candidates
- `{primary_counterparty}` = candidate
- `{decision_partner}` = client (KO meeting)
- `{counterparty}` = client / candidate

**Software engineer:**
- `{core_task}` = breaking down a feature spec
- `{primary_counterparty}` = product manager
- `{decision_partner}` = tech lead (design review)
- `{counterparty}` = stakeholder

**Product manager:**
- `{core_task}` = killing a feature
- `{primary_counterparty}` = engineering lead
- `{decision_partner}` = exec sponsor
- `{counterparty}` = stakeholder

---

## Week 3 — PEOPLE (target: 10 person schemas)

**Schema** (six fields per person):
```yaml
person_alias: "Client K-san" / "Candidate A" / use code names
relationship_age: how long you've known each other
role: client / candidate / peer / mentor / competitor
interaction_mode: one sentence — how they treat you and how you treat them
private_notes: details outsiders wouldn't know (your private impression)
last_interaction: last touch + current status
```

The bot doesn't ask the interviewee to fill the schema directly. It uses these prompts to let people naturally surface:

| ID | Question | Rationale probe |
|---|---|---|
| P1 | Three counterparties who most often reach out to you in the past 3 years — one story each | What do they have in common? |
| P2 | Three counterparties you maintain (years-long) relationships with — one story each | Why do you maintain each? |
| P3 | The mentor / industry senior who most influenced you — one story | Do you want to become like them? |
| P4 | The competitor you most respect — one story | What can they do that you can't? |
| P5 | Two peers / partners / reports closest to you — one story each | What unspoken understanding do you have with them? |

---

## Week 4 — VOICE collection

Two-part: (A) retrieve existing artifacts, (B) record fresh samples.

### Part A — Retrieve existing artifacts (bot requests naturally, doesn't enumerate)

The bot asks at appropriate moments: "Can you send me a snippet of how you talk to X?" This naturally triggers:

- LINE / chat messages with counterparties (PII-scrubbed) — ≥10 snippets
- Emails to clients / collaborators — ≥5
- LinkedIn posts / comments — ≥5
- Pitch decks / slides — ≥2
- Internal messages (to peers / boss) — ≥5
- Podcast / talk transcripts where applicable

### Part B — Voice samples (7 scenario-based prompts)

The bot asks the interviewee to literally say (or type) something in their natural voice for each scenario:

| ID | Scenario |
|---|---|
| V1 | First contact opener with a senior {counterparty} — 30 seconds as if talking to them |
| V2 | Delivering bad news to a {primary_counterparty} (decision didn't go their way) |
| V3 | Pushing back on a {decision_partner} (budget / scope) |
| V4 | Telling someone "this isn't right for you" |
| V5 | Venting to a peer about a frustrating {counterparty} (LINE DM register) |
| V6 | Mentioning work to a friend / family member (most casual register) |
| V7 | Writing a public post (LinkedIn / Twitter register) about an industry trend |

Each sample auto-tagged with `[audience / mood / scenario / register]` and embedded into the voice sample store.

---

## Week 5 — SOUL (target: 10+ anchors + first blind test)

| ID | Question | Rationale probe |
|---|---|---|
| SO1 | Three adjectives you absolutely are + three you absolutely are not | The "not" three — has anyone ever misjudged you on these? |
| SO2 | Dilemma: counterparty A's constraint conflicts with counterparty B's expectation. How do you handle it? | Whose side do you lean toward? Why? |
| SO3 | Dilemma: someone you care about needs an outcome you don't think is right for them. What do you say? | How do you judge "right for them"? Tell them everything, or filter? |
| SO4 | A decision you made backfired and someone got hurt. Do you carry guilt? Why / why not? | Where does your responsibility end? |
| SO5 | Your private definition of "a good {domain_role}" — not the textbook one | One sentence. |
| SO6 | What makes you want to immediately disengage / leave the room? | Most recent instance? |
| SO7 | Your first reaction vs. second reaction when challenged / dismissed | Which is "really you"? |
| SO8 | Decisions: more gut or more data? Fast or slow? | Has this changed since you were younger? |
| SO9 | Deepest professional fear? | What does this fear make you avoid / pursue? |
| SO10 | Five years from now, how do you hope people describe your professional reputation? | How far is current you from that description? |

**End of Week 5: first blind test gate.** See [`03-blind-test-protocol.md`](03-blind-test-protocol.md).

---

## Week 6 — BOUNDARIES + Failure Modes (target: 8 anchors)

| ID | Question | Rationale probe |
|---|---|---|
| B1 | Three categories of {projects / engagements} you absolutely refuse | Ever taken one and regretted it? |
| B2 | Three categories of information you absolutely won't share | Under what conditions would you break this? |
| B3 | The kind of agent response that would most bother you | Why would that be a violation? |
| B4 | Two failure modes you slip into when stressed | Do others notice? |
| B5 | Two blind spots you know you have | Who told you? Do you agree? |
| B6 | What happens when someone really pisses you off (tone shift, behavior shift) | How would someone close to you know "she's really angry now"? |
| B7 | Topics you don't discuss (politics / religion / exes / former employers?) | Whom would you make exceptions for? |
| B8 | Red lines on agent-human division of labor — what must the human always do? | Why those specifically? |

---

## Week 7 — STATE setup + Triangulation Calibration

### STATE initialization

| ID | Question |
|---|---|
| T1 | Past 3 months' work focus + emotional baseline |
| T2 | This quarter's goals / what you care about right now |
| T3 | Recent energy level (1–10) + why |

### Triangulation calibration (bot surfaces its inferences)

| ID | Action |
|---|---|
| T4 | Bot lists 5 inferred "core values" from past 6 weeks of SOUL → interviewee confirms / corrects each |
| T5 | Bot surfaces contradictions between SOUL.md and actual VOICE samples → interviewee explains which is "really them" (e.g., SOUL says "I'm direct" but VOICE samples to clients are diplomatic → not contradiction, register switching → write to PEOPLE.md as "client mode") |
| T6 | Bot lists under-covered dimensions → interviewee ad-hoc fills (e.g., BOUNDARIES.md only has 2 entries → push to 5) |

---

## Week 8 — v1 Ship + Monthly STATE Cadence

### 8.1 Integration test (second blind test)

See [`03-blind-test-protocol.md`](03-blind-test-protocol.md). 50–60% accuracy = ship-ready.

### 8.2 Monthly STATE update ritual

15-minute catch-up session, bot initiates:
```
Hi {interviewee}, how was this month?
Updating STATE:
1. Did your work focus shift?
2. Any new red lines or revised ones?
3. Anything off about how the agent has been responding? Want to adjust?
```

### 8.3 Hand-off README

The interviewee receives the operating manual (see [`06-three-plans.md`](06-three-plans.md)).

---

## Appendix A — Coverage Checklist

Bot uses this at each week's end to verify "enough yet?":

```
SOUL:
  □ ≥3 triangulated values
  □ ≥3 triangulated red lines
  □ ≥2 dilemma trade-off positions
  □ ≥1 private definition of "good {domain_role}"

VOICE:
  □ ≥30 samples across ≥5 audience types
  □ Covers happy / neutral / stressed / angry moods
  □ Covers LINE / email / formal / casual registers

SKILL:
  □ ≥5 private know-how items (not textbook)
  □ ≥3 failure cases + root cause
  □ Differentiated strategies for at least 2 counterparty tiers

PEOPLE:
  □ ≥8 person schemas (varied roles)

HISTORY:
  □ ≥3 inflection events
  □ ≥2 mentor influences
  □ Childhood / education at least one entry (unless explicit refusal)

BOUNDARIES:
  □ ≥5 refusal / red lines
  □ ≥3 PII handling rules
  □ ≥1 persona update protocol

STATE:
  □ This quarter's goals
  □ Emotional baseline
  □ Monthly update cadence set
```

---

## Appendix B — Question Pool Iteration

The pool is living. The bot should log:
- Which questions get deep answers
- Which questions get shallow answers (rephrase needed)
- Which questions get skipped (try again?)
- Topics the interviewee surfaced that aren't in the pool (add for future interviewees)

Every 2 weeks, the operator reviews logs and adjusts the next 2 weeks' pool.
