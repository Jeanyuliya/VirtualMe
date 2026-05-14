import json

import aiosqlite
from pydantic import SecretStr

from virtualme.config import Settings
from virtualme.interview.bot import process_turn
from virtualme.storage.db import DB, Dimension, Question


class _Content:
    def __init__(self, text: str):
        self.text = text


class _Messages:
    def __init__(self, depth: str = "principle"):
        self.depth = depth
        self.depth_questions: list[str] = []

    async def create(self, **kwargs):
        max_tokens = kwargs["max_tokens"]
        prompt = kwargs["messages"][0]["content"]
        if max_tokens == 10:
            question = prompt.split("Question: ", 1)[1].split("\n", 1)[0]
            self.depth_questions.append(question)
            text = self.depth
        elif max_tokens == 500:
            question = prompt.split("Question: ", 1)[1].split("\n", 1)[0]
            text = json.dumps(
                [
                    {
                        "dimension": "SKILL" if "skill" in question.lower() else "STATE",
                        "layer": "principle",
                        "content": "directness over deference",
                    }
                ]
            )
        elif max_tokens == 80:
            text = "Could you give me one concrete example?"
        else:
            text = "OK"
        return type("Response", (), {"content": [_Content(text)]})


class _Claude:
    def __init__(self, depth: str = "principle"):
        self.messages = _Messages(depth)


class _FixedSelector:
    def __init__(self, next_question: Question | None):
        self.question_pool = {
            1: [
                Question(
                    id="Q1",
                    week=1,
                    dimension=Dimension.STATE,
                    text="How has work been?",
                ),
                Question(
                    id="Q2",
                    week=1,
                    dimension=Dimension.SKILL,
                    text="What skill matters most?",
                ),
            ]
        }
        self.next_question = next_question

    def select_next(self, *args, **kwargs):
        return self.next_question


async def _session_current_question_id(db: DB, session_id: int) -> str | None:
    async with aiosqlite.connect(db.path) as conn:
        row = await (
            await conn.execute(
                "SELECT current_question_id FROM sessions WHERE id = ?",
                (session_id,),
            )
        ).fetchone()
    return row[0] if row else None


async def test_next_question_is_used_as_subsequent_answer_context(tmp_path):
    db = DB(str(tmp_path / "virtualme.db"))
    await db.init()
    settings = Settings(anthropic_api_key=SecretStr("test"), use_ppa=False)
    q2 = Question(
        id="Q2",
        week=1,
        dimension=Dimension.SKILL,
        text="What skill matters most?",
    )
    selector = _FixedSelector(q2)
    claude = _Claude()

    await process_turn("u1", "First answer.", claude, db, selector, settings)
    assert await _session_current_question_id(db, 1) == "Q2"

    await process_turn("u1", "Second answer.", claude, db, selector, settings)

    assert claude.messages.depth_questions == [
        "How has work been?",
        "What skill matters most?",
    ]
    summary = await db.load_anchors_summary("u1")
    assert summary[Dimension.SKILL][0].source_question_ids == ["Q2"]


async def test_follow_up_branch_does_not_advance_current_question(tmp_path):
    db = DB(str(tmp_path / "virtualme.db"))
    await db.init()
    settings = Settings(anthropic_api_key=SecretStr("test"), use_ppa=False)
    q2 = Question(
        id="Q2",
        week=1,
        dimension=Dimension.SKILL,
        text="What skill matters most?",
    )
    selector = _FixedSelector(q2)
    claude = _Claude(depth="fact")
    session = await db.get_or_create_session("u1", week=1)
    await db.set_current_question_id(session.id, "Q2")

    await process_turn("u1", "A short fact.", claude, db, selector, settings)

    assert await _session_current_question_id(db, session.id) == "Q2"


async def test_selector_none_does_not_persist_default_question(tmp_path):
    db = DB(str(tmp_path / "virtualme.db"))
    await db.init()
    settings = Settings(anthropic_api_key=SecretStr("test"), use_ppa=False)
    selector = _FixedSelector(None)
    claude = _Claude()
    session = await db.get_or_create_session("u1", week=1)
    await db.set_current_question_id(session.id, "Q2")

    await process_turn("u1", "Answer while selector returns none.", claude, db, selector, settings)

    assert await _session_current_question_id(db, session.id) == "Q2"
