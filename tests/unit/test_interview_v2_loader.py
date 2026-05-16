from pathlib import Path

import pytest

from virtualme.interview.v2_loader import (
    default_domain_packs_path,
    default_v2_question_pool_path,
    load_domain_packs,
    load_merged_v2_question_pool,
    load_v2_question_pool,
)
from virtualme.storage.db import Dimension


def test_load_v2_question_pool_reads_generic_draft():
    pool = load_v2_question_pool()

    assert default_v2_question_pool_path().name == "question-pool-v2.yaml"
    assert pool.version == 2
    assert pool.production_enabled is False
    assert len(pool.intake_questions) == 5
    assert len(pool.dimensions) == 8
    assert len(pool.questions) == 64
    first = pool.questions[0]
    assert first.dimension == Dimension.STATE
    assert first.purpose
    assert first.user_explain
    assert first.expected_anchor == "fact"
    assert first.follow_up_max == 2
    assert first.stop_condition
    assert first.risk_level == "low"


def test_load_domain_packs_reads_all_structured_packs():
    packs = load_domain_packs()

    assert default_domain_packs_path().name == "domain-packs-v2.yaml"
    assert packs.version == 2
    assert set(packs.packs) == {
        "engineer_ai_builder",
        "sales_bd",
        "pm_tpm",
        "consultant",
        "manager_people_lead",
        "creator_writer",
        "teacher_coach",
        "founder_operator",
    }
    engineer = packs.packs["engineer_ai_builder"]
    assert len(engineer.skill_questions) == 8
    assert len(engineer.people_questions) == 5
    assert len(engineer.voice_roleplays) == 5
    assert len(engineer.boundaries_questions) == 5
    assert len(engineer.bad_questions) == 5
    assert len(engineer.persona_anchor_examples) == 12


def test_load_merged_v2_question_pool_appends_domain_overlay():
    generic = load_v2_question_pool()
    merged = load_merged_v2_question_pool(domain_pack="engineer_ai_builder")

    assert len(merged.questions) == len(generic.questions) + 23
    assert any(question.id == "state_01" for question in merged.questions)
    domain_questions = [
        question for question in merged.questions if question.source == "domain:engineer_ai_builder"
    ]
    assert {question.dimension for question in domain_questions} == {
        Dimension.SKILL,
        Dimension.PEOPLE,
        Dimension.VOICE,
        Dimension.BOUNDARIES,
    }
    assert any(question.id == "engineer_ai_builder_skill_01" for question in domain_questions)
    voice = next(question for question in domain_questions if question.dimension == Dimension.VOICE)
    assert voice.stage == "voice_roleplay"
    assert voice.stop_condition == "取得一段真實訊息範本後停止。"


def test_load_merged_v2_question_pool_rejects_unknown_domain_pack():
    with pytest.raises(ValueError, match="unknown domain pack"):
        load_merged_v2_question_pool(domain_pack="missing_domain")


def test_v2_loader_rejects_unresolved_placeholders(tmp_path):
    source = Path("src/virtualme/data/question-pool-v2.yaml")
    target = tmp_path / "question-pool-v2.yaml"
    target.write_text(
        source.read_text(encoding="utf-8").replace("最近這陣子", "{domain_role} 最近這陣子", 1),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unresolved placeholders"):
        load_v2_question_pool(target)
