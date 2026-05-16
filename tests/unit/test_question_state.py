from virtualme.storage.db import DB


async def test_record_question_state_roundtrip(tmp_path):
    db = DB(str(tmp_path / "virtualme.db"))
    await db.init()

    await db.record_question_asked("u1", "Q1", week=1)
    await db.record_question_asked("u1", "Q1", week=1)
    await db.record_question_answered("u1", "Q1", week=1, depth="principle")
    await db.record_question_answered("u1", "Q2", week=1, depth="fact")
    await db.record_question_probe("u1", "Q1", week=1)
    await db.record_question_probe("u1", "Q1", week=1)
    assert await db.record_question_non_answer("u1", "Q1", week=1) == 1
    assert await db.record_question_non_answer("u1", "Q1", week=1) == 2
    await db.reset_question_non_answer("u1", "Q1")

    async with db._connect() as conn:
        q1 = await (
            await conn.execute(
                """
                SELECT asked_count, answered_depth, probe_count, non_answer_count
                FROM question_state
                WHERE interviewee_id = ? AND question_id = ?
                """,
                ("u1", "Q1"),
            )
        ).fetchone()
        q2 = await (
            await conn.execute(
                """
                SELECT asked_count, answered_depth, probe_count, non_answer_count
                FROM question_state
                WHERE interviewee_id = ? AND question_id = ?
                """,
                ("u1", "Q2"),
            )
        ).fetchone()

    assert q1 == (2, "principle", 2, 0)
    assert q2 == (0, "fact", 0, 0)
    assert await db.get_probe_count("u1", "Q1") == 2
    assert await db.get_probe_count("u1", "Q2") == 0
    assert await db.load_asked_question_ids("u1") == {"Q1"}
