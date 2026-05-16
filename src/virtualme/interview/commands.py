"""Lightweight interview command detection — BW7.

Two interactions that are *not* interview answers and must not be extracted:

- status query  -- "which personality block are we collecting right now?"
- re-talk request -- "let's redo the VOICE block"

Detection is keyword-based (CJK + English) and length-capped: a PoC-scale
heuristic, not an LLM intent classifier. A long storytelling answer that
happens to contain a keyword is left alone (see COMMAND_MAX_LEN). Known
limitation: a short genuine answer containing e.g. "重談" can false-trigger.
"""

from __future__ import annotations

from dataclasses import dataclass

from virtualme.storage.db import Dimension

# Commands are short. Anything longer is treated as a real interview answer.
COMMAND_MAX_LEN = 40

# Human-facing Chinese labels for each extraction dimension.
DIMENSION_LABELS: dict[Dimension, str] = {
    Dimension.SOUL: "靈魂・核心價值",
    Dimension.VOICE: "語氣・表達",
    Dimension.SKILL: "專業技能",
    Dimension.PEOPLE: "人際關係",
    Dimension.HISTORY: "人生歷程",
    Dimension.JOURNAL: "反思札記",
    Dimension.BOUNDARIES: "界線・原則",
    Dimension.STATE: "近況",
}

# Keywords that point at a specific dimension. First dimension to match wins.
DIMENSION_KEYWORDS: dict[Dimension, list[str]] = {
    Dimension.SOUL: ["soul", "靈魂", "核心價值", "價值觀", "信念"],
    Dimension.VOICE: ["voice", "語氣", "口吻", "表達", "說話方式"],
    Dimension.SKILL: ["skill", "技能", "專業", "能力"],
    Dimension.PEOPLE: ["people", "人際", "人脈", "同事", "夥伴", "關係"],
    Dimension.HISTORY: ["history", "歷程", "經歷", "過去"],
    Dimension.JOURNAL: ["journal", "札記", "反思", "日誌"],
    Dimension.BOUNDARIES: ["boundaries", "界線", "界限", "原則", "底線", "紅線"],
    Dimension.STATE: ["state", "近況", "現況"],
}

STATUS_KEYWORDS = [
    "現在在問",
    "在問什麼",
    "在收集",
    "收集哪",
    "收集到哪",
    "哪一塊",
    "哪一個維度",
    "目前進度",
    "訪談進度",
    "到哪了",
    "which block",
    "which dimension",
    "what are we",
    "progress",
]

RETALK_KEYWORDS = [
    "重談",
    "重新談",
    "再談一次",
    "重新講",
    "重新訪談",
    "重來",
    "redo",
    "re-talk",
    "retalk",
]


@dataclass
class StatusQuery:
    """User asked which dimension is being collected."""


@dataclass
class RetalkRequest:
    """User asked to re-interview a dimension. ``dimension`` is None when the
    request did not name a recognisable block."""

    dimension: Dimension | None


InterviewCommand = StatusQuery | RetalkRequest


def _match_dimension(text: str) -> Dimension | None:
    for dimension, keywords in DIMENSION_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return dimension
    return None


def detect_command(message: str) -> InterviewCommand | None:
    """Return an InterviewCommand if the message is a meta-command, else None."""
    stripped = message.strip()
    if not stripped or len(stripped) > COMMAND_MAX_LEN:
        return None
    text = stripped.lower()
    if any(keyword in text for keyword in RETALK_KEYWORDS):
        return RetalkRequest(dimension=_match_dimension(text))
    if any(keyword in text for keyword in STATUS_KEYWORDS):
        return StatusQuery()
    return None


def format_status_reply(
    current_dimension: Dimension,
    covered_dimensions: list[Dimension],
) -> str:
    current = DIMENSION_LABELS[current_dimension]
    if covered_dimensions:
        covered = "、".join(DIMENSION_LABELS[dim] for dim in covered_dimensions)
        covered_line = f"目前已經收集到的維度：{covered}。"  # noqa: RUF001
    else:
        covered_line = "目前還沒有任何維度收集到內容。"
    return (
        f"我們現在正在收集的人格維度是【{current}】。\n"
        f"{covered_line}\n"
        "如果想重談某一塊，可以跟我說「重談 + 維度名稱」（例如「重談 人際關係」）。"  # noqa: RUF001
    )


def format_retalk_reply(dimension: Dimension, question_text: str) -> str:
    label = DIMENSION_LABELS[dimension]
    return f"好，我們重新談【{label}】這一塊。\n{question_text}"  # noqa: RUF001


def format_retalk_needs_dimension() -> str:
    blocks = "、".join(DIMENSION_LABELS.values())
    return (
        "你想重談哪一塊呢？可選的人格維度有：\n"  # noqa: RUF001
        f"{blocks}。\n"
        "跟我說「重談 + 維度名稱」就可以了。"
    )
