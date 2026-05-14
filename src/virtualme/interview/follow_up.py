from enum import StrEnum

from anthropic import AsyncAnthropic

from virtualme.storage.db import Anchor, Layer


class FollowUpRule(StrEnum):
    R1_FACT_TO_PATTERN = "R1"
    R2_PATTERN_TO_PRINCIPLE = "R2"
    R3_PRINCIPLE_TO_COUNTEREXAMPLE = "R3"
    R4_ABSTRACT_TO_CONCRETE = "R4"
    R5_REPEAT_TO_TRIANGULATE = "R5"


ABSTRACT_MARKERS = {"honesty", "trust", "directness", "quality", "freedom", "respect"}


def select_rule(
    answer: str, depth: Layer, accumulated_anchors: list[Anchor]
) -> FollowUpRule | None:
    normalized = answer.lower()
    if any(marker in normalized for marker in ABSTRACT_MARKERS) and len(answer.split()) <= 14:
        return FollowUpRule.R4_ABSTRACT_TO_CONCRETE
    if depth == Layer.FACT:
        return FollowUpRule.R1_FACT_TO_PATTERN
    if depth == Layer.PATTERN:
        return FollowUpRule.R2_PATTERN_TO_PRINCIPLE
    if depth != Layer.PRINCIPLE:
        return None
    if _has_triangulated_repeat(answer, accumulated_anchors):
        return FollowUpRule.R5_REPEAT_TO_TRIANGULATE
    return None if _has_concrete_example(answer) else FollowUpRule.R3_PRINCIPLE_TO_COUNTEREXAMPLE


async def generate_follow_up(
    rule: FollowUpRule, answer: str, original_question: str, claude: AsyncAnthropic
) -> str:
    if rule == FollowUpRule.R5_REPEAT_TO_TRIANGULATE:
        return "I think we have this principle clearly enough. Let me ask from another angle."
    prompt = f"""
Generate one short therapist-style follow-up question for rule {rule.value}.
Original question: {original_question}
Answer: {answer}
Keep their wording. Do not advise, praise, or explain.
"""
    response = await claude.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=80,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def _has_triangulated_repeat(answer: str, anchors: list[Anchor]) -> bool:
    words = set(answer.lower().split())
    for anchor in anchors:
        overlap = words & set(anchor.content.lower().split())
        if anchor.layer == Layer.PRINCIPLE and len(overlap) >= 4 and len(set(anchor.source_turn_ids)) >= 3:
            return True
    return False


def _has_concrete_example(answer: str) -> bool:
    lowered = answer.lower()
    markers = ("once", "yesterday", "last ", "when ", "client", "manager", "case")
    return any(marker in lowered for marker in markers)
