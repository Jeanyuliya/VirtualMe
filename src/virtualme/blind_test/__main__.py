from __future__ import annotations

import argparse
import asyncio

from virtualme.config import Settings, sqlite_path
from virtualme.interview.blind_test import (
    compute_accuracy,
    parse_results,
    recommended_action,
    verdict_for_accuracy,
)
from virtualme.storage.db import DB


async def main() -> None:
    parser = argparse.ArgumentParser(description="Record a VirtualMe blind-test result.")
    parser.add_argument("--interviewee", default="local")
    parser.add_argument("--week", type=int, required=True)
    parser.add_argument("--results", required=True, help="Comma-separated results, e.g. T1=1,T2=0")
    parser.add_argument("--db", default=None)
    parser.add_argument("--weakest", default=None)
    parser.add_argument("--action", default=None)
    args = parser.parse_args()

    results = parse_results(args.results)
    accuracy = compute_accuracy(results)
    verdict = verdict_for_accuracy(accuracy)
    database_url = args.db if args.db is not None else Settings().database_url
    db = DB(sqlite_path(database_url))
    await db.init()
    blind_test_id = await db.save_blind_test(
        interviewee_id=args.interviewee,
        week=args.week,
        correctness_per_item=results,
        overall_accuracy=accuracy,
        verdict=verdict,
        weakest_dimension=args.weakest,
        recommended_action=args.action or recommended_action(verdict),
    )

    print(
        f"blind_test_id={blind_test_id} "
        f"interviewee={args.interviewee} "
        f"week={args.week} "
        f"accuracy={accuracy:.2f} "
        f"verdict={verdict}"
    )


if __name__ == "__main__":
    asyncio.run(main())
