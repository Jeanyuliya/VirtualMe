from __future__ import annotations

from virtualme.storage.db import Verdict


def parse_results(raw: str) -> dict[str, bool]:
    results: dict[str, bool] = {}
    pairs = [item.strip() for item in raw.split(",") if item.strip()]
    if not pairs:
        raise ValueError("--results must contain at least one item, e.g. T1=1")

    for pair in pairs:
        key, separator, value = pair.partition("=")
        key = key.strip()
        value = value.strip()
        if not key or separator != "=":
            raise ValueError(f"invalid result {pair!r}; expected KEY=0 or KEY=1")
        if key in results:
            raise ValueError(f"duplicate result key {key!r}")
        if value == "1":
            results[key] = True
        elif value == "0":
            results[key] = False
        else:
            raise ValueError(f"invalid result value {value!r}; expected 0 or 1")
    return results


def compute_accuracy(results: dict[str, bool]) -> float:
    if not results:
        raise ValueError("results must contain at least one item")
    return sum(1 for value in results.values() if value) / len(results)


def verdict_for_accuracy(accuracy: float) -> Verdict:
    if accuracy < 0.5:
        return Verdict.OVERFIT_WARNING
    if accuracy <= 0.6:
        return Verdict.SHIP_READY
    return Verdict.NEEDS_WORK


def recommended_action(verdict: Verdict) -> str:
    if verdict == Verdict.OVERFIT_WARNING:
        return "Check for overfit: reduce voice retrieval strength and inspect register balance."
    if verdict == Verdict.SHIP_READY:
        return "Ship-ready threshold reached; continue with monthly STATE updates."
    return "Calibrate weak scenarios and collect targeted anchors before shipping."
