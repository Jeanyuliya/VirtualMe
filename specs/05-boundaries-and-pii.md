# Boundaries, PII & Informed Consent

> Meta-rules separating archival extraction from therapy, plus PII handling and immutable red lines.

---

## 1. Core Position

VirtualMe's interview engine uses **therapist-style depth methods** (active listening, mirroring, root-cause inquiry, pause tolerance, acknowledgment of weight) as its extraction core — but it is **not** a therapy service.

| | Therapy | VirtualMe Interview Engine |
|---|---|---|
| Purpose | Healing / change / problem-solving | Archive / extract / record "who they are" |
| Practitioner | Licensed therapist | LLM bot + operator review |
| Crisis handling | Yes (referral, intervention) | None — surfaces referral to professional |
| Ethical framework | Counseling ethics (confidentiality, informed consent, non-judgment) | Adopts same framework, no legal standing |
| Legal status | Regulated helping profession | Tool, no legal standing |
| Relationship | Therapeutic course | 8-week interview phase + monthly updates |

**This distinction is not a technical detail. It is the core ethic.** The interviewee must be told this explicitly before the interview begins.

---

## 2. Informed Consent (mandatory before Week 1 first session)

The interview bot's first message to the interviewee MUST cover the following 7 items:

```
Hi {name}, before we formally start, I need to walk you through the
boundaries of this interview:

1. My method is "therapist-style depth interview" — I will follow up
   on "why" until your judgment criteria surface.
   But I am NOT a therapist, and this is NOT therapy.

2. The process may surface things you hadn't noticed (childhood,
   trauma, unresolved decisions).
   If you're uncomfortable, you can always: skip / change question /
   say "tired" / say "don't save this segment".

3. I keep confidentiality — only the operator (for quality review of
   interview transcripts) can spot-check. No one else sees what you say.

4. If you surface serious emotional signals (self-harm, suicidal
   ideation, unbearable distress), I will stop and recommend you seek
   professional help. **I cannot help at the crisis layer.**

5. What we discuss eventually becomes an AI agent. You can at any time:
   - Keep some parts / delete all / modify a segment
   - After 8 weeks, decide whether to ship

6. Anything the agent writes — legally, socially, responsibility-wise —
   belongs to you, not the AI.

7. You can withdraw at any time. When you withdraw, your conversation
   archive will be:
   □ Kept (you may want to continue later)
   □ Deleted (no trace anywhere)
   Your choice.

---

To proceed with understanding and agreement, reply "I agree, let's start."
If you have questions or disagree with any item, tell me.
```

The interviewee must reply explicit consent before the interview proceeds.

---

## 3. PII Handling Rules

If the interviewee's profession involves handling third-party PII (clients, candidates, patients, students), **every interview transcript must pass PII scrubbing before storage**:

| PII Type | Handling |
|---|---|
| Third-party real names | Replace with code names: `[Person A]`, `[Person B]` |
| Company names | Replace with codes: `[Client H]`, `[Client J]` |
| Salary / compensation figures | Bucket into ranges: `180–220k` |
| Ages | Bucket: `30s`, `40s` |
| Birthdays | Reduce to month: `March`, `September` |
| Phone / email | Fully redacted |
| Third-party trauma / personal matters | Tag `confidential:counterparty`, never enters outgoing prompts |

The interviewee's own PII:
- Names, birthday, family — written to SOUL/HISTORY but **not surfaced outward**
- Childhood / marriage / health — written to SOUL/HISTORY, tagged `private:self`, blocked from outgoing prompts
- Workplace failure cases — PII-scrubbed before storage

---

## 4. Tag-Based Filtering

Every anchor carries a tag at write time. When building the outbound system prompt (agent mode), these tags filter automatically:

| Tag | Meaning | Surfaced to external prompts? |
|---|---|---|
| `public` | Public-safe | ✅ |
| `professional` | Work context only | ✅ |
| `confidential:client` | Client secret | ❌ |
| `confidential:counterparty` | Counterparty secret | ❌ |
| `private:self` | Interviewee's personal privacy | ❌ |
| `crisis:flagged` | Crisis signal | ❌ (and not stored in archive — only metadata stub) |

---

## 5. Emotional Content Handling

How the bot handles deep emotional material (corresponds to interview-engine spec §2):

**Within scope:**
- Childhood narrative, family background, career inflection points
- Resolved or actively-being-processed emotional events
- Personal feelings, evaluations of people / situations
- Surfaced-but-stable trauma (where the person has integrated the experience)

**Crisis scope (bot immediately exits interview mode):**
- Self-harm or suicidal ideation signals
- Impulse to harm others
- Uncontrolled dissociation / panic / trauma response
- Interviewee explicitly says "I can't keep going"

**Bot crisis response (verbatim — do not paraphrase):**
```
"This sounds like it needs professional support. I cannot help at the
crisis layer. I'm stopping here. When you want to continue the
interview later, tell me.

If you need help now, please consider:
- A crisis helpline in your region (e.g., 988 in the US, 1925 in
  Taiwan, Samaritans in the UK)
- Someone you trust to talk to in person"
```

The bot does NOT try to fix, continue the interview, analyze, or offer
comforting paraphrase.

---

## 6. Persona Update Protocol (after ship)

Once the agent ships, rules for modifying SOUL.md / SKILL.md / VOICE.md / etc.:

| Change type | Notification | Confirmation |
|---|---|---|
| STATE monthly update | Automatic | Not required |
| Add new SKILL anchor | Automatic | Not required |
| Modify existing SOUL anchor | Notify interviewee | Interviewee confirms |
| Delete any anchor | Notify + keep version history | Interviewee confirms |
| Modify BOUNDARIES | Force-confirm | Interviewee personally |
| Major persona shift (voice / position change) | Force-notify downstream contacts (clients / counterparties / peers) | Interviewee personally + stakeholders informed |

The last item addresses incidents like Replika users reporting their AI "felt lobotomized" after a silent persona update. Avoid sudden personality breaks visible to external parties.

---

## 7. Immutable Red Lines

Once the agent ships, these actions are **NEVER** delegable to it:

1. ❌ Issue or reject a formal offer / contract / decision
2. ❌ Sign any contract / quote / legal document
3. ❌ Publicly post unauthorized opinions (especially political, religious, or sensitive topics)
4. ❌ Handle a counterparty's crisis (refer back to the interviewee)
5. ❌ Build a deep relationship with someone the interviewee doesn't know personally
6. ❌ Move money / use budget / commit company resources
7. ❌ Modify SOUL / BOUNDARIES (only the interviewee can change these)

When the agent encounters any of the above, it surfaces:
> "This needs {interviewee} to handle personally. I'll pass it on."

---

## 8. Withdrawal & Deletion Rights

The interviewee can at any time:
- **Pause**: keep current archive, resume later
- **Withdraw** (two sub-options):
  - Retain archive (may restart in future)
  - Full deletion (no trace anywhere — SQLite + embedding store both wiped)
- **Delete a specific anchor**: by anchor ID or topic, bot removes corresponding content
- **Export**: receive their full archive (markdown + JSON) and walk away

Deletion is **hard delete**. The operator cannot recover. This is by design.

---

## 9. Meta-Rule: Modifying This Document

Changes to `BOUNDARIES.md` require:
- Interviewee personal confirmation
- Operator review
- Git commit log + persistent record
- Notification to all shipped downstream agents to reload

Boundaries cannot be silently relaxed for convenience.

---

## 10. Operator Responsibilities

Anyone running VirtualMe for someone else (operator role) accepts:

1. **Read all spec documents** before starting an interview.
2. **Spot-check transcripts** every 2 weeks for ≤15 minutes — verify bot behavior, watch for drift.
3. **Do not read transcripts gratuitously.** Confidentiality applies to operators too.
4. **Honor deletion requests** within 24 hours.
5. **Do not use interviewee data** for anything beyond what was disclosed in consent.
6. **Distinguish self-use from operating-for-others.** Running VirtualMe on yourself is one ethical context. Running it for another person is a different one with higher duty of care.

If you cannot commit to these, do not run VirtualMe for others.
