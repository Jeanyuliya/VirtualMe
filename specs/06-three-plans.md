# Three Commitment Levels

> VirtualMe is the spec + reference implementation. How you actually run it depends on your commitment level.

---

## Plan A — Self-Run (free, you own everything)

**For:** developers / people comfortable with Python + LLM APIs / curious tinkerers

**Cost:** ~$50 in API spending + your time

**What you do:**
1. Fork the repo
2. Read `specs/00-overview.md` → `specs/01-interview-engine.md` → `specs/02-question-pool.md`
3. Customize `src/virtualme/data/question-pool.yaml` for your domain (substitute the placeholders)
4. Run `python -m virtualme.cli --interviewee yourself` for Phase 0 verification
5. Wire your messaging platform of choice (LINE / Telegram / Discord)
6. Run the 8-week pipeline on yourself

**What you get:**
- A working personal agent
- Eight markdown files representing you
- Full ownership of your data (it never leaves your machine)
- All the code, all the prompts, all the question pool

**What this is NOT:**
- Not "weekend coding". The interview is 8 weeks long.
- Not zero-effort. Customizing the question pool for your domain matters.
- Not "guaranteed to feel like you". Blind test verifies this; if it fails, you iterate.

---

## Plan B — Operator-Run (you find someone to run it for someone else)

**For:** operators (technical) running VirtualMe for an interviewee (non-technical)

**Cost:** operator absorbs technical setup; interviewee absorbs ~10 hours of conversation time over 8 weeks

**What the operator does:**
1. Read all spec docs, including [`05-boundaries-and-pii.md`](05-boundaries-and-pii.md) in full
2. Get **explicit informed consent** from the interviewee (the 7-item script in §2)
3. Customize question pool for the interviewee's domain
4. Run infrastructure (deploy, monitor, back up)
5. Spot-check transcripts every 2 weeks (≤15 min per check, watching for drift / bot misbehavior)
6. Conduct blind test gates at Week 5 and Week 8
7. Hand off the final artifact (8 markdown files + agent endpoint)

**What the interviewee does:**
1. Sign informed consent (`05-boundaries-and-pii.md` §2)
2. Chat with the bot 1–2× per week × 30 min, for 8 weeks
3. Participate in blind tests at Week 5 and Week 8
4. Decide whether to ship at end of Week 8

**Operator responsibilities (non-negotiable):**
- Honor deletion requests within 24 hours
- Do not read transcripts gratuitously
- Do not use interviewee data for anything outside what was disclosed in consent
- Distinguish self-use from operating-for-others — duty of care is higher when running for someone else

**Read first:** [`05-boundaries-and-pii.md`](05-boundaries-and-pii.md) §10 Operator Responsibilities.

---

## Plan C — Cohort / Workshop (someone runs a group)

**For:** people who want to gather a small group and run VirtualMe together

**Cost:** group decides on facilitator compensation, infrastructure cost split, etc.

**What's different from Plan A/B:**
- Shared learning, but **NOT shared data** — each interviewee has their own SQLite DB
- Facilitator helps with question pool customization across domains
- Optional shared retrospective at Week 4 and Week 8 (people share what they learned about themselves, not the raw archive)
- No certificate, no graduation, no LinkedIn badge — this isn't a course, it's a co-working group on a shared project

**Hard rules for cohort mode:**
- No interviewee's archive is ever shared with the group
- The facilitator does not become a coach / therapist — facilitator stays in operator role
- Anyone can drop out at any week without justification — peer pressure is forbidden

---

## What VirtualMe is NOT Selling

- ❌ A SaaS — no hosted version, no signup, no subscription
- ❌ A course — no curriculum, no instructor, no certificate
- ❌ A cohort program with coach attention — you can DIY a Plan C with friends, but the repo doesn't sell that
- ❌ Done-for-you setup — the repo is BYO (build your own)

If those things are what you want, there are courses for that — many of them excellent. VirtualMe is for people who want to **read the spec, fork the repo, and build their own**.

---

## Cost Comparison

| Path | Setup time | Cost | Outcome |
|---|---|---|---|
| Public courses (representative pricing) | Fixed schedule | $1,500–4,000 | Persona files + API tutorial + cohort |
| **VirtualMe Plan A** (self-run) | ~2 days setup + 8 weeks interview | ~$50 in API calls | Working agent + 8 markdown files |
| **VirtualMe Plan B** (operator-run) | Operator's setup time | ~$50–80 API for one pipeline | Same as Plan A, but interviewee doesn't touch the technical side |
| **VirtualMe Plan C** (cohort) | Group decides | Group decides | Each member has their own agent |

Cost ratio: VirtualMe Plan A is roughly **1% of a $4,000 course**. The trade-off is doing your own setup.

---

## How to Decide

- **You're technical and just want to try this on yourself** → Plan A
- **You want to give this to a non-technical friend / family member / client** → Plan B
- **You want to do this with a group of friends** → Plan C
- **You want someone else to do everything for you** → not in scope here; look elsewhere
