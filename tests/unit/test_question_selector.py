from virtualme.interview.question_selector import QuestionSelector
from virtualme.storage.db import Anchor, Dimension, Layer, Question, Session


def _question(id_: str, dimension: Dimension, energy_tax: str = "mid") -> Question:
    return Question(id=id_, week=1, dimension=dimension, text=id_, energy_tax=energy_tax)


def _session() -> Session:
    return Session(id=1, interviewee_id="u1", week=1)


def test_returns_none_when_unexplored_layer_exists():
    selector = QuestionSelector({1: [_question("H1", Dimension.HISTORY)]})
    anchors = {
        Dimension.HISTORY: [
            Anchor(
                interviewee_id="u1",
                dimension=Dimension.HISTORY,
                layer=Layer.FACT,
                content="joined once",
            )
        ]
    }
    assert selector.select_next(_session(), None, anchors, energy=5) is None


def test_picks_biggest_gap_dimension():
    selector = QuestionSelector(
        {1: [_question("H1", Dimension.HISTORY), _question("S1", Dimension.SKILL)]}
    )
    anchors = {
        Dimension.HISTORY: [
            Anchor(
                interviewee_id="u1",
                dimension=Dimension.HISTORY,
                layer=Layer.PRINCIPLE,
                content="history principle",
            )
        ]
    }
    assert selector.select_next(_session(), None, anchors, energy=5).dimension == Dimension.SKILL


def test_low_energy_switches_to_light_topic():
    selector = QuestionSelector(
        {
            1: [
                _question("H1", Dimension.HISTORY, "high"),
                _question("STATE1", Dimension.STATE, "low"),
            ]
        }
    )
    assert selector.select_next(_session(), None, {}, energy=2).dimension == Dimension.STATE
