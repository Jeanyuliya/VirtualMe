# Perplexity Max Brief: Personality Extraction Engineering

## Context

VirtualMe is an open-source pipeline that tries to extract a person into a portable AI agent through depth interviews, not forms.

Current product thesis:

- Interview over time, not one form.
- Extract behavioral anchors from dialogue.
- Produce owned markdown persona artifacts.
- Validate with blind tests and human correction.

Current artifact model uses eight dimensions:

1. `SOUL` - identity, values, red lines
2. `VOICE` - wording, register, message samples
3. `SKILL` - domain know-how, work method, decision process
4. `PEOPLE` - relationship schemas and trust models
5. `HISTORY` - life narrative and formative events
6. `JOURNAL` - reflection, self-correction, meaning-making
7. `BOUNDARIES` - refusal, authorization, PII, hard limits
8. `STATE` - current state and recent context

## Current Problem

Phase A-3 produced a Snapshot from interview anchors:

- `SOUL-lite.md`
- `mini-blind-test.md`
- `feedback-routing.md`

Maki's evaluation:

> It is very surface-level. It is almost all my original wording. The extraction cost is not high.

This means the system is doing extractive summary, not personality extraction.

Example raw anchors from the current production snapshot:

- Uses project triangle constraints to push back on unreasonable budget / scope / timeline.
- Does not avoid conflict; will directly state that project conditions do not hold.
- Treats handoff seriousness as a signal of whether someone is truly committed.
- Recognizes emotional-blackmail style negotiation as a pattern to defend against.
- Stops caring about the attacker's motive; treats it as part of human nature and moves on.

Current bad behavior:

- Raw anchor becomes a "hypothesis" with little abstraction.
- Top-level sketch mostly chooses one anchor per dimension.
- Mini blind test tests the anchor, not the underlying decision mechanism.

## Research Question

Please research and propose how to engineer **Personality Extraction**, not generic information extraction.

The target is not:

- generic summarization
- Big Five / MBTI classification
- resume-like persona writing
- "sounds like me" style imitation only

The target is:

> Given interview evidence, infer a person's reusable decision mechanisms: under what conditions they protect which value, trade off what, refuse what, make exceptions, and express the decision in what register.

## Questions To Answer

1. In engineering terms, what should "Personality Extraction" mean?
   - What is the unit of extraction?
   - Is it a trait, decision rule, mechanism, schema, construct, or something else?

2. What should the extraction ladder be?
   - Example ladder: raw utterance -> meaning unit -> code -> focused code -> construct -> decision mechanism -> falsifier.
   - Is this appropriate for personality extraction?
   - What should be added or removed?

3. How should VirtualMe avoid merely paraphrasing the user's original words?
   - What measurable gates can detect "raw wrapper" output?
   - How can we require abstraction without encouraging hallucination?

4. How should evidence and audit trail work?
   - What evidence must be attached to each inferred mechanism?
   - What counts as enough support?
   - How should rival explanations and disconfirming evidence be represented?

5. How should confidence work?
   - Current confidence is weak and mostly provenance-based.
   - Propose confidence criteria for personality extraction.
   - Include source diversity, pressure cases, counterexamples, and cross-context repetition.

6. Should the eight-dimension model be kept?
   - Do `SOUL / VOICE / SKILL / PEOPLE / HISTORY / JOURNAL / BOUNDARIES / STATE` help extraction?
   - Or do they force a form-filling mindset?
   - Should they be output artifact sections only, while extraction uses a different mechanism-first schema?
   - Should some dimensions be merged, demoted, or made optional?

7. What should the next Snapshot schema be?
   - Please propose a schema for `SynthesizedPattern` or equivalent.
   - It must support decision rule, protected value, tradeoff, trigger context, exception, falsifier, evidence, confidence reason, and blind-test probe.

8. How should mini blind tests validate personality extraction?
   - Should they test mechanism first, wording second?
   - What would a good blind-test item look like for the sample anchors above?

9. What should the next smallest engineering slice be?
   - Keep it implementable in an existing Python project with SQLite anchors.
   - Avoid building a huge research system.
   - Prefer something that can run offline and be reviewed by Maki.

## Desired Output Format

Please answer with:

1. A concise definition of Personality Extraction.
2. A proposed extraction pipeline.
3. A proposed schema.
4. A critique of the eight dimensions.
5. A concrete before/after using the sample anchors.
6. Anti-patterns to avoid.
7. A minimal engineering roadmap for the next 1-2 commits.
8. Sources / references used.

## Useful Reference Directions

Please prioritize sources from:

- computational personality assessment / personality computing
- automatic personality detection from text and its limitations
- qualitative coding / thematic analysis / grounded theory
- case formulation / construct formulation
- human-in-the-loop evaluation and audit trail methods

Avoid shallow SEO articles unless they point to useful primary sources.
