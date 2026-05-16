"""Tests for BW7 interview command detection (status query / re-talk)."""

from pydantic import SecretStr

from virtualme.config import Settings
from virtualme.interview.bot import process_turn
from virtualme.interview.commands import RetalkRequest, StatusQuery, detect_command
from virtualme.interview.question_selector import QuestionSelector
from virtualme.storage.db import DB, Dimension, Question

# --- detect_command pure tests -----------------------------------------------


def test_detect_status_query():
    assert isinstance(detect_command("現在在問什麼"), StatusQuery)
    assert isinstance(detect_command("我們收集到哪一塊了"), StatusQuery)
    assert isinstance(detect_command("which dimension are we on"), StatusQuery)


def test_detect_retalk_with_dimension():
    command = detect_command("我想重談人際關係")
    assert isinstance(command, RetalkRequest)
    assert command.dimension == Dimension.PEOPLE


def test_detect_retalk_without_dimension():
    command = detect_command("可以重談嗎")
    assert isinstance(command, RetalkRequest)
    assert command.dimension is None


def test_normal_answer_is_not_a_command():
    assert detect_command("When the migration started I preferred short questions.") is None
    assert detect_command("我覺得最近工作還算順利") is None


def test_long_answer_with_keyword_is_not_a_command():
    # A long storytelling answer that happens to contain "重談" must not trigger.
    long_answer = "重談 " + "這是一段很長的訪談回答內容描述當時的情境與感受" * 3
    assert len(long_answer) > 40
    assert detect_command(long_answer) is None


# --- process_turn integration ------------------------------------------------


async def _new_db(tmp_path) -> DB:
    db = DB(str(tmp_path / "virtualme.db"))
    await db.init()
    return db


async def test_process_turn_status_query_reports_current_dimension(tmp_path):
    db = await _new_db(tmp_path)
    selector = QuestionSelector(
        {1: [Question(id="Q1", week=1, dimension=Dimension.STATE, text="How has work been?")]}
    )
    settings = Settings(anthropic_api_key=SecretStr("k"))

    reply = await process_turn("u1", "現在在問什麼", object(), db, selector, settings)

    assert "近況" in reply  # STATE label
    turns = await db.load_session_turns(1)
    assert len(turns) == 2  # turn pair saved, no extraction
    assert await db.load_anchors_summary("u1") == {} or not await db.load_triples("u1")


async def test_process_turn_retalk_pins_dimension_question(tmp_path):
    db = await _new_db(tmp_path)
    selector = QuestionSelector(
        {
            1: [Question(id="Q1", week=1, dimension=Dimension.STATE, text="State question")],
            2: [Question(id="QV", week=2, dimension=Dimension.VOICE, text="Voice question here")],
        }
    )
    settings = Settings(anthropic_api_key=SecretStr("k"))

    reply = await process_turn("u1", "重談 語氣", object(), db, selector, settings)

    assert "語氣" in reply
    assert "Voice question here" in reply
    assert await db.get_current_question_id(1) == "QV"
