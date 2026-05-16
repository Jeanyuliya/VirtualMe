from virtualme.storage.db import DB, Anchor, Dimension, Layer, SubjectDomain
from virtualme.subject import score_completeness
from virtualme.subject_status import main


def _anchor(dimension: Dimension, triangulated: bool = False) -> Anchor:
    return Anchor(
        interviewee_id="u1",
        dimension=dimension,
        layer=Layer.PRINCIPLE,
        content=f"{dimension.value} anchor",
        triangulated=triangulated,
    )


def test_score_completeness_empty_anchors_has_zero_total_and_weakest():
    report = score_completeness({})

    assert report.total_score == 0.0
    assert report.weakest is not None


def test_score_completeness_caps_full_voice_with_triangulated_bonus():
    report = score_completeness(
        {Dimension.VOICE: [_anchor(Dimension.VOICE), _anchor(Dimension.VOICE), _anchor(Dimension.VOICE, True)]}
    )

    voice_score = next(
        score for score in report.per_dimension if score.dimension == Dimension.VOICE
    )
    assert voice_score.anchor_count == 3
    assert voice_score.triangulated_count == 1
    assert voice_score.coverage == 1.0


def test_score_completeness_weighted_total_for_priority_dimensions():
    report = score_completeness(
        {
            Dimension.VOICE: [
                _anchor(Dimension.VOICE),
                _anchor(Dimension.VOICE),
                _anchor(Dimension.VOICE),
            ],
            Dimension.BOUNDARIES: [
                _anchor(Dimension.BOUNDARIES),
                _anchor(Dimension.BOUNDARIES),
                _anchor(Dimension.BOUNDARIES),
            ],
        }
    )

    assert 0.0 < report.total_score < 100.0


async def test_subject_status_cli_smoke(tmp_path, monkeypatch, capsys):
    db_path = tmp_path / "virtualme.db"
    db = DB(str(db_path))
    await db.init()
    await db.get_or_create_subject(
        "friend0",
        domain=SubjectDomain.HR_HRBP,
        display_name="Friend Zero",
        goal="HR LINE clone",
    )
    await db.save_anchor("friend0", Dimension.VOICE, Layer.FACT, "plain spoken", [1], ["Q1"])
    await db.save_anchor(
        "friend0",
        Dimension.BOUNDARIES,
        Layer.PRINCIPLE,
        "protects private details",
        [1, 2, 3],
        ["Q1", "Q2", "Q3"],
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "virtualme.subject_status",
            "--db",
            f"sqlite:///{db_path}",
            "--interviewee",
            "friend0",
        ],
    )

    await main()

    output = capsys.readouterr().out
    assert "Subject: Friend Zero" in output
    assert "總完成度" in output
    assert "%" in output
