import aiosqlite
from pydantic import ValidationError

from virtualme.blind_test.__main__ import main
from virtualme.interview.blind_test import compute_accuracy, parse_results, verdict_for_accuracy
from virtualme.storage.db import DB, Verdict


def test_parse_results_accepts_comma_separated_keyed_values():
    assert parse_results("T1=1,T2=0, T3=1") == {"T1": True, "T2": False, "T3": True}


def test_parse_results_rejects_invalid_values():
    try:
        parse_results("T1=1,T2=maybe")
    except ValueError as exc:
        assert "expected 0 or 1" in str(exc)
    else:
        raise AssertionError("invalid blind-test results should fail")


def test_parse_results_rejects_duplicate_keys():
    try:
        parse_results("T1=1,T1=0")
    except ValueError as exc:
        assert "duplicate result key" in str(exc)
    else:
        raise AssertionError("duplicate blind-test result keys should fail")


def test_verdict_thresholds_are_inclusive_for_ship_band():
    assert verdict_for_accuracy(0.4) == Verdict.OVERFIT_WARNING
    assert verdict_for_accuracy(0.5) == Verdict.SHIP_READY
    assert verdict_for_accuracy(0.6) == Verdict.SHIP_READY
    assert verdict_for_accuracy(0.7) == Verdict.NEEDS_WORK


def test_compute_accuracy_uses_correct_items_over_total():
    assert compute_accuracy({"T1": True, "T2": False, "T3": True}) == 2 / 3


async def test_save_blind_test_persists_result(tmp_path):
    db = DB(str(tmp_path / "virtualme.db"))
    await db.init()

    blind_test_id = await db.save_blind_test(
        interviewee_id="u1",
        week=5,
        correctness_per_item={"T1": True, "T2": False, "T3": True},
        overall_accuracy=2 / 3,
        verdict=Verdict.NEEDS_WORK,
        weakest_dimension="VOICE.casual_mode",
        recommended_action="collect more casual voice samples",
    )

    assert blind_test_id > 0
    async with aiosqlite.connect(db.path) as conn:
        row = await (
            await conn.execute(
                """
                SELECT correctness_per_item, overall_accuracy, verdict,
                       weakest_dimension, recommended_action
                FROM blind_tests
                WHERE id = ?
                """,
                (blind_test_id,),
            )
        ).fetchone()

    assert row == (
        '{"T1": true, "T2": false, "T3": true}',
        2 / 3,
        "needs-work",
        "VOICE.casual_mode",
        "collect more casual voice samples",
    )


async def test_blind_test_cli_with_explicit_db_does_not_require_api_key(tmp_path, monkeypatch):
    db_path = tmp_path / "virtualme.db"
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(
        "sys.argv",
        [
            "virtualme.blind_test",
            "--db",
            f"sqlite:///{db_path}",
            "--interviewee",
            "local",
            "--week",
            "5",
            "--results",
            "T1=1,T2=0,T3=1,T4=0,T5=1",
        ],
    )

    try:
        await main()
    except ValidationError as exc:
        raise AssertionError("explicit --db blind test should not require Settings") from exc

    async with aiosqlite.connect(db_path) as conn:
        row = await (
            await conn.execute(
                """
                SELECT overall_accuracy, verdict
                FROM blind_tests
                WHERE interviewee_id = 'local'
                """
            )
        ).fetchone()

    assert row == (0.6, "ship-ready")
