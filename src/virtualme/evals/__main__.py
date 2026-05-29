from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from virtualme.config import Settings
from virtualme.evals.harness import load_fixtures, render_scorecard, run_eval
from virtualme.llm import build_llm_client


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run VirtualMe engine evaluation fixtures.")
    parser.add_argument("--fixtures", default=None)
    parser.add_argument("--with-llm", action="store_true")
    parser.add_argument("--out", type=Path, default=Path("./exports/evals"))
    args = parser.parse_args()

    cases = load_fixtures(args.fixtures)
    claude = None
    if args.with_llm:
        settings = Settings()
        claude = build_llm_client(settings)

    report = await run_eval(cases, claude=claude)
    args.out.mkdir(parents=True, exist_ok=True)
    scorecard_path = args.out / "scorecard.md"
    scorecard_path.write_text(render_scorecard(report), encoding="utf-8")

    summary = f"rule_accuracy={report.rule_accuracy:.2%}"
    if report.depth_accuracy is not None:
        summary = f"{summary} depth_accuracy={report.depth_accuracy:.2%}"
    print(f"{summary} cases={len(report.results)} scorecard={scorecard_path}")


if __name__ == "__main__":
    asyncio.run(main())
