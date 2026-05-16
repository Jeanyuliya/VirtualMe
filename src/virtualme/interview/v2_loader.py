from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml

from virtualme.interview.v2_schema import (
    DomainPack,
    DomainPackCollection,
    DomainPackQuestion,
    V2DimensionConfig,
    V2IntakeQuestion,
    V2Question,
    V2QuestionPool,
    VoiceRoleplay,
)
from virtualme.storage.db import Dimension

USER_TEXT_FIELDS = ("text", "user_explain", "purpose", "stop_condition")


def default_v2_question_pool_path() -> Path:
    return Path(str(files("virtualme").joinpath("data/question-pool-v2.yaml")))


def default_domain_packs_path() -> Path:
    return Path(str(files("virtualme").joinpath("data/domain-packs-v2.yaml")))


def load_v2_question_pool(path: str | Path | None = None) -> V2QuestionPool:
    source = default_v2_question_pool_path() if path is None else Path(path)
    raw = _load_yaml(source)
    meta = raw.get("meta", {})
    intake = raw.get("intake", {})
    pool = V2QuestionPool(
        version=raw["version"],
        status=raw.get("status", ""),
        production_enabled=bool(meta.get("production_enabled", False)),
        intake_questions=[V2IntakeQuestion(**item) for item in intake.get("questions", [])],
        dimensions={
            Dimension(key): V2DimensionConfig(**value)
            for key, value in raw.get("dimensions", {}).items()
        },
        progress_prompts=dict(raw.get("progress_prompts", {})),
        transitions=dict(raw.get("transitions", {})),
        questions=[V2Question(**item) for item in raw.get("questions", [])],
    )
    _assert_no_placeholders(_pool_texts(pool))
    return pool


def load_domain_packs(path: str | Path | None = None) -> DomainPackCollection:
    source = default_domain_packs_path() if path is None else Path(path)
    raw = _load_yaml(source)
    collection = DomainPackCollection(**raw)
    _assert_no_placeholders(_domain_pack_texts(collection))
    return collection


def load_merged_v2_question_pool(
    *,
    question_pool_path: str | Path | None = None,
    domain_packs_path: str | Path | None = None,
    domain_pack: str | None = None,
) -> V2QuestionPool:
    pool = load_v2_question_pool(question_pool_path)
    if domain_pack is None:
        return pool

    packs = load_domain_packs(domain_packs_path)
    try:
        pack = packs.packs[domain_pack]
    except KeyError as exc:
        raise ValueError(f"unknown domain pack: {domain_pack}") from exc

    merged_questions = [*pool.questions, *_domain_pack_questions(domain_pack, pack)]
    return pool.model_copy(update={"questions": merged_questions})


def _load_yaml(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return raw


def _domain_pack_questions(slug: str, pack: DomainPack) -> list[V2Question]:
    questions: list[V2Question] = []
    questions.extend(
        _domain_question_to_v2(slug, Dimension.SKILL, question)
        for question in pack.skill_questions
    )
    questions.extend(
        _domain_question_to_v2(slug, Dimension.PEOPLE, question)
        for question in pack.people_questions
    )
    questions.extend(
        _voice_roleplay_to_v2(slug, roleplay) for roleplay in pack.voice_roleplays
    )
    questions.extend(
        _domain_question_to_v2(slug, Dimension.BOUNDARIES, question)
        for question in pack.boundaries_questions
    )
    return questions


def _domain_question_to_v2(
    slug: str, dimension: Dimension, question: DomainPackQuestion
) -> V2Question:
    purpose = question.purpose or question.signal or f"補充 {dimension.value} 領域化人格訊號。"
    return V2Question(
        id=question.id,
        dimension=dimension,
        text=question.text,
        purpose=purpose,
        expected_anchor="domain_signal",
        follow_up_max=question.follow_up_max,
        stop_condition=question.stop_condition or "取得領域化人格訊號後停止。",
        risk_level=question.risk_level,
        source=f"domain:{slug}",
    )


def _voice_roleplay_to_v2(slug: str, roleplay: VoiceRoleplay) -> V2Question:
    return V2Question(
        id=roleplay.id,
        dimension=Dimension.VOICE,
        stage="voice_roleplay",
        text=roleplay.text,
        purpose=roleplay.extraction_target or "萃取領域化語氣樣本。",
        expected_anchor="domain_signal",
        follow_up_max=1,
        stop_condition="取得一段真實訊息範本後停止。",
        risk_level="medium",
        source=f"domain:{slug}",
    )


def _pool_texts(pool: V2QuestionPool) -> list[str]:
    texts: list[str] = []
    for question in pool.intake_questions:
        texts.extend([question.text, question.user_explain, question.stop_condition])
    for dimension in pool.dimensions.values():
        texts.extend([dimension.name, dimension.purpose, dimension.avoid])
    texts.extend(pool.progress_prompts.values())
    texts.extend(pool.transitions.values())
    for question in pool.questions:
        for field in USER_TEXT_FIELDS:
            texts.append(str(getattr(question, field)))
        texts.extend(question.follow_ups)
    return texts


def _domain_pack_texts(collection: DomainPackCollection) -> list[str]:
    texts: list[str] = []
    for pack in collection.packs.values():
        texts.append(pack.name)
        texts.extend(pack.domain_role)
        texts.extend(pack.core_task)
        texts.extend(pack.primary_counterparty)
        texts.extend(pack.decision_partner)
        for question in [
            *pack.skill_questions,
            *pack.people_questions,
            *pack.boundaries_questions,
        ]:
            texts.extend(
                [
                    question.title,
                    question.text,
                    question.purpose,
                    question.expected_anchor,
                    question.stop_condition,
                    question.signal,
                ]
            )
        for roleplay in pack.voice_roleplays:
            texts.extend([roleplay.title, roleplay.text, roleplay.extraction_target])
        for bad_question in pack.bad_questions:
            texts.extend([bad_question.bad, bad_question.why, bad_question.better])
        texts.extend(pack.persona_anchor_examples)
    return texts


def _assert_no_placeholders(texts: list[str]) -> None:
    leaked = [text for text in texts if "{" in text or "}" in text]
    if leaked:
        raise ValueError(f"unresolved placeholders in v2 interview data: {leaked[:3]}")

