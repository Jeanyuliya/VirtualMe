from virtualme.storage.db import DB, Subject, SubjectDomain, SubjectStatus
from virtualme.subject import render_subject_md


async def test_get_or_create_subject_creates_once_and_does_not_overwrite(tmp_path):
    db = DB(str(tmp_path / "virtualme.db"))
    await db.init()

    first = await db.get_or_create_subject(
        "friend0",
        domain=SubjectDomain.HR_HRBP,
        display_name="Friend Zero",
        goal="HR LINE clone",
    )
    second = await db.get_or_create_subject(
        "friend0",
        domain=SubjectDomain.ENGINEER,
        display_name="Changed",
        goal="Changed goal",
    )

    assert first.interviewee_id == "friend0"
    assert first.domain == SubjectDomain.HR_HRBP
    assert first.display_name == "Friend Zero"
    assert first.goal == "HR LINE clone"
    assert second == first


async def test_get_subject_returns_none_for_missing_subject(tmp_path):
    db = DB(str(tmp_path / "virtualme.db"))
    await db.init()

    assert await db.get_subject("missing") is None


async def test_update_subject_only_updates_provided_fields_and_round_trips_enums(tmp_path):
    db = DB(str(tmp_path / "virtualme.db"))
    await db.init()
    created = await db.get_or_create_subject(
        "friend0",
        domain=SubjectDomain.SALES,
        display_name="Friend Zero",
        goal="Initial goal",
    )

    updated = await db.update_subject(
        "friend0",
        domain=SubjectDomain.HR_HRBP,
        status=SubjectStatus.EXTRACTED,
    )

    assert updated.domain == SubjectDomain.HR_HRBP
    assert updated.status == SubjectStatus.EXTRACTED
    assert updated.display_name == "Friend Zero"
    assert updated.goal == "Initial goal"
    assert updated.created_at == created.created_at
    assert updated.updated_at is not None

    fetched = await db.get_subject("friend0")
    assert fetched is not None
    assert fetched.domain == SubjectDomain.HR_HRBP
    assert fetched.status == SubjectStatus.EXTRACTED


def test_render_subject_md_includes_profile_fields():
    text = render_subject_md(
        Subject(
            interviewee_id="friend0",
            display_name="Friend Zero",
            domain=SubjectDomain.HR_HRBP,
            goal="HR LINE clone",
            status=SubjectStatus.EXTRACTED,
            created_at="2026-05-16 10:00:00",
            updated_at="2026-05-16 10:10:00",
        )
    )

    assert "# Subject: Friend Zero" in text
    assert "- Domain: hr-hrbp" in text
    assert "- Goal: HR LINE clone" in text
    assert "- Status: extracted" in text
