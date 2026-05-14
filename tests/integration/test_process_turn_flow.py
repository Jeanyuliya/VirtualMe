import aiosqlite
from pydantic import SecretStr

from virtualme.config import Settings
from virtualme.interview.bot import process_turn
from virtualme.interview.question_selector import QuestionSelector
from virtualme.storage.db import DB, Dimension, Question


class _Content:
    def __init__(self, text: str):
        self.text = text


class _Messages:
    def __init__(self):
        self.ppa_calls = 0

    async def create(self, **kwargs):
        max_tokens = kwargs["max_tokens"]
        if max_tokens == 10:
            text = "principle"
        elif max_tokens == 500:
            text = "[]"
        elif max_tokens == 150:
            self.ppa_calls += 1
            text = (
                '{"assistant": "好的,下次再聊"}'
                if self.ppa_calls == 5
                else f'{{"assistant": "reply {self.ppa_calls}"}}'
            )
        elif max_tokens == 900:
            text = """
            [
              {
                "subject": "interviewee",
                "relation": "preference",
                "object": "direct interview flow",
                "source_turn_ids": [1],
                "confidence": 0.9
              }
            ]
            """
        else:
            text = "OK"
        return type("Response", (), {"content": [_Content(text)]})


class _Claude:
    def __init__(self):
        self.messages = _Messages()


async def test_process_turn_scrubs_redactions_and_finalizes_session(tmp_path):
    db = DB(str(tmp_path / "virtualme.db"))
    await db.init()
    selector = QuestionSelector(
        {
            1: [
                Question(
                    id="Q1",
                    week=1,
                    dimension=Dimension.STATE,
                    text="How has work been?",
                )
            ]
        }
    )
    settings = Settings(anthropic_api_key=SecretStr("test"), use_ppa=True)
    claude = _Claude()
    messages = [
        "When the migration started, I preferred short questions.",
        "When I worked with John Smith on a long client migration, salary was 185k and email maki@example.com.",
        "When the team got stuck, I asked for direct evidence.",
        "When planning, I choose the smallest reversible check.",
        "好累了,今天先這樣",
    ]

    for message in messages:
        await process_turn("u1", message, claude, db, selector, settings)

    turns = await db.load_session_turns(1)
    user_texts = [turn.content for turn in turns if turn.role == "user"]
    assert any("[Person A]" in text and "[EMAIL]" in text for text in user_texts)
    assert not any("maki@example.com" in text or "John Smith" in text for text in user_texts)

    async with aiosqlite.connect(db.path) as conn:
        redaction_count = (await (await conn.execute("SELECT COUNT(*) FROM redactions")).fetchone())[0]
        session = await (
            await conn.execute("SELECT status, ended_at FROM sessions WHERE id = 1")
        ).fetchone()
    assert redaction_count >= 3
    assert session[0] == "completed"
    assert session[1] is not None

    triples = await db.load_triples("u1")
    assert len(triples) == 1
    assert triples[0].object == "direct interview flow"
