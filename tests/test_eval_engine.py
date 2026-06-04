"""Unit tests for EvalEngine — no API keys required (LLMClient is mocked)."""

from unittest.mock import MagicMock

import pytest

from igenbench.engine.eval_engine import EvalEngine
from igenbench.vis_item import EvalEntry, Judgment


def _make_engine(response):
    """Return an EvalEngine whose LLMClient returns *response* from call_image_understanding."""
    client = MagicMock()
    client.call_image_understanding.return_value = response
    return EvalEngine(llm_client=client, model="eval-model")


# ─── judge_entry: happy path ──────────────────────────────────────────────────


def test_judge_entry_returns_judgment_with_dict_response():
    engine = _make_engine({"analysis": "looks correct", "answer": "1"})
    entry = EvalEntry(question="How many bars?", source="prompt", ground="4")
    j = engine.judge_entry(entry, "gen-model", "eval-model", "/fake/image.png")
    assert isinstance(j, Judgment)
    assert j.analysis == "looks correct"
    assert j.answer == "1"
    assert j.gen_model == "gen-model"
    assert j.eval_model == "eval-model"


def test_judge_entry_handles_plain_string_response():
    """When LLM returns a non-JSON string, analysis gets the text and answer is empty."""
    engine = _make_engine("The chart shows 4 bars.")
    entry = EvalEntry(question="How many bars?", source="prompt", ground="4")
    j = engine.judge_entry(entry, "gen-model", "eval-model", "/fake/image.png")
    assert j.analysis == "The chart shows 4 bars."
    assert j.answer == ""


def test_judge_entry_raises_on_empty_question():
    engine = _make_engine({"analysis": "", "answer": "1"})
    entry = EvalEntry(question="", source="prompt", ground="4")
    with pytest.raises(ValueError, match="Question is required"):
        engine.judge_entry(entry, "gen-model", "eval-model", "/fake/image.png")


# ─── check helpers ───────────────────────────────────────────────────────────


def test_check_eval_entry_being_judged_true():
    engine = _make_engine({})
    entry = EvalEntry(
        question="Q?",
        judgments=[Judgment(gen_model="gm", eval_model="em", analysis="", answer="1")],
    )
    assert engine.check_eval_entry_being_judged(entry, "gm", "em") is True


def test_check_eval_entry_being_judged_false():
    engine = _make_engine({})
    entry = EvalEntry(question="Q?")
    assert engine.check_eval_entry_being_judged(entry, "gm", "em") is False


def test_check_fully_evaluated_delegates_to_vis_item():
    from igenbench.vis_item import VISItem

    engine = _make_engine({})
    item = VISItem(
        id="x",
        evaluation=[
            EvalEntry(
                question="Q?",
                judgments=[
                    Judgment(gen_model="gm", eval_model="em", analysis="", answer="1")
                ],
            )
        ],
    )
    assert engine.check_fully_evaluated(item, "gm", "em") is True
