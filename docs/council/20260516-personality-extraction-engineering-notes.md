# Personality Extraction Engineering Notes

## Query

Maki asked to research how "extraction" should be practiced in engineering, explicitly meaning **Personality Extraction**, not generic information extraction.

## Initial Finding

The engineering unit should not be a raw quote, a summary sentence, or a Big Five / MBTI label.

For VirtualMe, the practical extraction unit should be closer to:

> A reusable, evidence-backed decision mechanism: under condition C, the person tends to protect value V by choosing action A over B, sacrificing tradeoff T, unless exception E applies.

This points to a mechanism-first schema. The eight dimensions can remain useful as artifact routes, but they should not be the primary synthesis frame.

## Why Current Snapshot Failed

Current Phase A-3 output is mostly:

```text
anchor -> lightly wrapped hypothesis
```

That is extractive summary. It does not create a new reusable construct.

Useful personality extraction needs an intermediate ladder:

```text
raw utterance
-> meaning unit
-> code
-> focused code
-> construct hypothesis
-> decision mechanism
-> falsifier
-> blind-test probe
```

## Engineering Principles

### 1. Schema before synthesis

Do not ask an LLM to "summarize this person." Define target fields first:

- condition / trigger
- protected value
- preferred action
- rejected action
- tradeoff axis
- exception rule
- voice implication
- evidence
- rival explanation
- falsifier
- confidence reason
- blind-test probe

### 2. Evidence spans are mandatory

Every construct must link back to source turns / source questions / anchor ids.

Evidence should be shown as support, not used as the main output. If the output reads like the evidence sentence, it failed extraction.

### 3. Confidence is not only count

Confidence should consider:

- source diversity: different questions / contexts
- pressure diversity: normal case vs high-stakes case
- counterexample coverage
- exception clarity
- repeated behavior vs one-time story
- whether the construct predicts a new scenario

### 4. Falsifiability is required

Each extracted mechanism needs a statement of what would make it wrong.

Example:

```text
If Maki repeatedly accepts vague handoffs in important projects just to preserve harmony, the "operational evidence as trust signal" pattern is wrong.
```

### 5. Mini blind test should test mechanism first

First test:

- what decision is made
- what value is protected
- what tradeoff is accepted
- where the exception lies

Only after mechanism matches should the system test exact wording / register.

## Eight-Dimension Question

The eight dimensions may still be useful as output shelves:

- `SOUL`: durable values / identity
- `VOICE`: expression layer
- `SKILL`: domain operating method
- `PEOPLE`: trust and relationship schemas
- `HISTORY`: formative evidence
- `JOURNAL`: reflection and change over time
- `BOUNDARIES`: refusal / authorization
- `STATE`: current context

But they are risky as the extraction frame because they encourage filling buckets.

Open council question:

> Should extraction be mechanism-first, then routed into dimensions for export?

Likely answer: yes.

## Sources To Use In Council

- Stanford KBP / slot filling: structured extraction fills target slots from text, with relation extraction as a core task.
- Stanford OpenIE: open extraction can produce relation tuples without predefined schema, but VirtualMe likely needs schema-guided extraction to be auditable.
- OpenAI Structured Outputs: schema-constrained extraction from unstructured text is practical for deterministic downstream workflows.
- Braun & Clarke thematic analysis: themes are patterns of shared meaning, not merely repeated words.
- Grounded theory: constant comparison, memoing, theoretical sampling, and saturation are relevant for moving from incidents to constructs.
- Computational personality assessment literature: personality inferred from digital traces requires reliability, validity, ground truth criteria, privacy, and interpretability.
- Automatic personality detection surveys: text can support personality recognition, but trait classification is not the same as building a useful personal agent policy.

## Proposed Next Artifact

Introduce `ConstructCard` before `SOUL-lite`:

```text
construct_id
title
dimensions
raw_anchor_ids
meaning_units
codes
mechanism
decision_rule
protected_value
tradeoff_axis
trigger_contexts
exception_rule
rival_explanations
falsifier
missing_evidence
confidence
confidence_reason
blind_test_probe
feedback_route
```

Then generate:

- `construct-cards.md`
- `SOUL-lite.md` from cards
- `mini-blind-test.md` from card probes
- `feedback-routing.md` from missing evidence / falsifiers

## Minimal Engineering Slice

Do not build the full research system.

Next slice:

1. Add deterministic `ConstructCard` model.
2. Add rule-based synthesis for the five known anchor families:
   - triangle constraints
   - direct conflict / project invalidity
   - handoff seriousness
   - emotional-blackmail negotiation
   - attacker's motive is not important
3. Render `construct-cards.md`.
4. Render `SOUL-lite.md` from construct cards, with raw hypotheses demoted to appendix.
5. Add tests that fail if synthesized text is too close to raw anchors.

## Anti-Patterns

- More polished anchor wrapper.
- More interview questions without a declared missing-evidence target.
- Big Five / MBTI as primary output.
- Free-form LLM persona essay.
- Runtime agent work before snapshot quality passes human review.
