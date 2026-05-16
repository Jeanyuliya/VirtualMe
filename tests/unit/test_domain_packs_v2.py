from pathlib import Path

import yaml

DOMAIN_PACK_PATH = Path("src/virtualme/data/domain-packs-v2.yaml")


def _load_domain_packs() -> dict:
    return yaml.safe_load(DOMAIN_PACK_PATH.read_text(encoding="utf-8"))


def test_domain_packs_v2_parse_and_include_all_domains():
    data = _load_domain_packs()

    assert data["version"] == 2
    assert data["production_enabled"] is False
    assert set(data["packs"]) == {
        "engineer_ai_builder",
        "sales_bd",
        "pm_tpm",
        "consultant",
        "manager_people_lead",
        "creator_writer",
        "teacher_coach",
        "founder_operator",
    }


def test_domain_packs_v2_have_required_sections_and_counts():
    data = _load_domain_packs()

    for pack in data["packs"].values():
        assert len(pack["domain_role"]) >= 1
        assert len(pack["core_task"]) >= 1
        assert len(pack["primary_counterparty"]) >= 1
        assert len(pack["decision_partner"]) >= 1
        assert len(pack["skill_questions"]) == 8
        assert len(pack["people_questions"]) == 5
        assert len(pack["voice_roleplays"]) == 5
        assert len(pack["boundaries_questions"]) == 5
        assert len(pack["bad_questions"]) == 5
        assert len(pack["persona_anchor_examples"]) == 12


def test_domain_packs_v2_skill_questions_keep_anchor_metadata():
    data = _load_domain_packs()

    for slug, pack in data["packs"].items():
        for question in pack["skill_questions"]:
            assert question["id"].startswith(f"{slug}_skill_")
            assert question["text"]
            assert question["purpose"]
            assert question["expected_anchor"]
            assert question["follow_up_max"] in {1, 2}
            assert question["stop_condition"]
            assert question["risk_level"] in {"low", "medium", "high"}


def test_domain_packs_v2_no_template_placeholders_or_appendix_leakage():
    data = _load_domain_packs()
    serialized = yaml.safe_dump(data, allow_unicode=True)

    assert "{decision_partner}" not in serialized
    assert "泛用 SOUL / HISTORY / JOURNAL / STATE 骨架" not in serialized
    assert "反感問法總原則" not in serialized
