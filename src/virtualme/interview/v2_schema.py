from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from virtualme.storage.db import Dimension

RiskLevel = Literal["low", "medium", "high"]
ExpectedAnchor = Literal["fact", "pattern", "principle", "mixed", "domain_signal"]


class V2IntakeQuestion(BaseModel):
    id: str
    text: str
    captures: list[str] = Field(default_factory=list)
    user_explain: str
    follow_up_max: int = 1
    stop_condition: str
    risk_level: RiskLevel = "low"


class V2DimensionConfig(BaseModel):
    name: str
    purpose: str
    avoid: str
    completion_threshold: int


class V2Question(BaseModel):
    id: str
    dimension: Dimension
    stage: str = "domain_overlay"
    text: str
    purpose: str
    user_explain: str = ""
    expected_anchor: ExpectedAnchor = "domain_signal"
    acceptable_answers: list[str] = Field(default_factory=list)
    follow_ups: list[str] = Field(default_factory=list)
    follow_up_max: int = 1
    stop_condition: str
    risk_level: RiskLevel = "low"
    optional: bool = False
    source: str = "generic"

    @field_validator("text", "purpose", "stop_condition")
    @classmethod
    def _required_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("field must not be empty")
        return value


class V2QuestionPool(BaseModel):
    version: int
    status: str
    production_enabled: bool
    intake_questions: list[V2IntakeQuestion]
    dimensions: dict[Dimension, V2DimensionConfig]
    progress_prompts: dict[str, str]
    transitions: dict[str, str]
    questions: list[V2Question]


class BadQuestionAlternative(BaseModel):
    bad: str
    why: str
    better: str


class DomainPackQuestion(BaseModel):
    id: str
    title: str = ""
    text: str
    purpose: str = ""
    expected_anchor: str = ""
    follow_up_max: int = 1
    stop_condition: str = ""
    risk_level: RiskLevel = "low"
    signal: str = ""


class VoiceRoleplay(BaseModel):
    id: str
    title: str = ""
    text: str
    extraction_target: str = ""


class DomainPack(BaseModel):
    name: str
    source: str = ""
    domain_role: list[str]
    core_task: list[str]
    primary_counterparty: list[str]
    decision_partner: list[str]
    skill_questions: list[DomainPackQuestion]
    people_questions: list[DomainPackQuestion]
    voice_roleplays: list[VoiceRoleplay]
    boundaries_questions: list[DomainPackQuestion]
    bad_questions: list[BadQuestionAlternative]
    persona_anchor_examples: list[str]


class DomainPackCollection(BaseModel):
    version: int
    status: str
    production_enabled: bool
    source: str = ""
    packs: dict[str, DomainPack]

