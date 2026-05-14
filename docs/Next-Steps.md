# VirtualMe Next Steps

Updated: 2026-05-14

This note captures the next pragmatic additions after the v0.5 stabilization pass. Keep each item as a small, independently testable slice.

## Current State

VirtualMe now has the minimum loop needed for local PoC validation:

- Packaged question pool loading.
- Anchor triangulation write-back.
- Advisory week progression.
- Session current-question tracking.
- Minimal markdown export.
- Minimal blind-test result recorder.
- Minimal blind-test preparation export.

Validation baseline:

- `.venv/bin/python -m pytest -q` -> 91 passed
- `.venv/bin/ruff check src tests` -> passed

## Recently Completed

### 1. Tiny blind-test preparation export

Build on the existing markdown exporter and blind-test recorder, but do not generate scenarios yet.

Target command:

```bash
python -m virtualme.blind_test.prepare \
  --db sqlite:///./data/virtualme.db \
  --interviewee local \
  --week 5 \
  --out ./exports/blind-test
```

Expected output:

- `instructions.md` with operator steps.
- `scorecard.md` with empty `T1..T5` rows for manual scoring.
- `persona-context.md` with the existing `principles.md` / anchor summary copied or referenced.

Why this is next:

- It helps another person run the current manual protocol without changing DB schema.
- It stays LLM-free.
- It does not require scenario generation, shuffle storage, or UI.

Acceptance criteria:

- Does not require `ANTHROPIC_API_KEY` when `--db` is provided. Done.
- Produces deterministic markdown files. Done.
- Has focused tests for generated file names and scorecard rows. Done.

This is implemented in `src/virtualme/blind_test/prepare.py`.

## Useful But Not Urgent

### 2. Store blind-test audit payload later

Only add this when manual testing shows the current `correctness_per_item` field is insufficient.

Likely future fields:

- scenario text
- human response hash
- agent response hash
- shuffled order
- evaluator id for Gate 2

Do this as a documented migration, not as a speculative schema change.

### 3. Persona summarizer

Needed before agent-generated blind-test responses become meaningful.

Minimum shape:

- Reads triangulated principles and selected voice anchors.
- Produces compact `SOUL`, `VOICE`, `SKILL`, `PEOPLE`, `BOUNDARIES` sections.
- Exports markdown first; avoid prompt/runtime integration until output quality is inspected.

### 4. CLI ergonomics

After one or two real blind-test runs, consider:

- `--results-file` only if copy-paste becomes annoying.
- clearer error examples for bad `Tn=0|1` input.
- README snippet for the current blind-test workflow.

## Defer

- Full scenario generation.
- Agent response generation.
- Shuffle orchestration.
- Gate 2 multi-evaluator workflow.
- Web UI.
- Configurable verdict thresholds.

These are not blockers for the next demo.
