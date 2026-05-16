from virtualme.storage.db import DB


async def test_save_turn_preserves_repeated_content_in_same_session(tmp_path):
    db = DB(str(tmp_path / "virtualme.db"))
    await db.init()
    session = await db.get_or_create_session("u1", week=1)

    first = await db.save_turn(session.id, "user", "對")
    second = await db.save_turn(session.id, "user", "對")

    assert first.id != second.id
    assert first.content == second.content == "對"


async def test_get_last_assistant_content_returns_latest_assistant_turn(tmp_path):
    db = DB(str(tmp_path / "virtualme.db"))
    await db.init()
    session = await db.get_or_create_session("u1", week=1)

    assert await db.get_last_assistant_content(session.id) is None

    await db.save_turn(session.id, "user", "先回答")
    await db.save_turn(session.id, "assistant", "你昨天做了什麼？")  # noqa: RUF001
    await db.save_turn(session.id, "user", "後回答")
    await db.save_turn(session.id, "assistant", "可以給我一個例子嗎？")  # noqa: RUF001

    assert await db.get_last_assistant_content(session.id) == "可以給我一個例子嗎？"  # noqa: RUF001
