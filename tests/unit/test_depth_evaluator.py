from virtualme.interview.depth_evaluator import evaluate_depth
from virtualme.storage.db import Layer


class _Content:
    def __init__(self, text: str):
        self.text = text


class _Messages:
    def __init__(self, text: str):
        self.text = text

    async def create(self, **kwargs):
        return type("Response", (), {"content": [_Content(self.text)]})


class _Claude:
    def __init__(self, text: str):
        self.messages = _Messages(text)


async def test_depth_fact():
    depth = await evaluate_depth("I yelled at my manager once", "What happened?", _Claude("fact"))
    assert depth == Layer.FACT


async def test_depth_pattern():
    answer = "I always speak my mind regardless of authority"
    depth = await evaluate_depth(answer, "How do you handle authority?", _Claude("pattern"))
    assert depth == Layer.PATTERN


async def test_depth_principle():
    answer = "I value directness because trust requires people to know where they stand"
    depth = await evaluate_depth(answer, "What do you value?", _Claude("principle"))
    assert depth == Layer.PRINCIPLE
