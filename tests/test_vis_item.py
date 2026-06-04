"""Unit tests for VISItem and related data classes. No API keys required."""

from pathlib import Path

from igenbench.vis_item import EvalEntry, Judgment, VISItem

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_ITEM_PATH = FIXTURES_DIR / "sample_item.json"


# ─── Loading ──────────────────────────────────────────────────────────────────


def test_from_dict_loads_id():
    item = VISItem.from_dict(str(SAMPLE_ITEM_PATH))
    assert item.id == "test-001"


def test_from_dict_loads_prompt():
    item = VISItem.from_dict(str(SAMPLE_ITEM_PATH))
    assert "bar chart" in item.t2i_prompt


def test_from_dict_loads_evaluation_entries():
    item = VISItem.from_dict(str(SAMPLE_ITEM_PATH))
    assert len(item.evaluation) == 2


def test_from_dict_eval_entry_fields():
    item = VISItem.from_dict(str(SAMPLE_ITEM_PATH))
    entry = item.evaluation[0]
    assert entry.source == "prompt"
    assert entry.question_type == "count"
    assert entry.ground == "4"


def test_from_dict_loads_judgment():
    item = VISItem.from_dict(str(SAMPLE_ITEM_PATH))
    entry = item.evaluation[1]  # has one judgment
    assert len(entry.judgments) == 1
    j = entry.judgments[0]
    assert isinstance(j, Judgment)
    assert j.answer == "1"
    assert j.gen_model == "gemini-2.5-flash-image"


# ─── has_judgment / add_judgment ──────────────────────────────────────────────


def test_has_judgment_true():
    item = VISItem.from_dict(str(SAMPLE_ITEM_PATH))
    entry = item.evaluation[1]
    assert entry.has_judgment("gemini-2.5-flash-image", "gemini-2.5-flash")


def test_has_judgment_false_wrong_gen_model():
    item = VISItem.from_dict(str(SAMPLE_ITEM_PATH))
    entry = item.evaluation[1]
    assert not entry.has_judgment("unknown-model", "gemini-2.5-flash")


def test_add_judgment_appends():
    entry = EvalEntry(
        source="prompt",
        ground="2",
        question="How many axes?",
        question_type="count",
    )
    entry.add_judgment("gen-model", "eval-model", "reasoning", "1")
    assert len(entry.judgments) == 1
    assert entry.judgments[0].answer == "1"


# ─── check_evaluation_complete ────────────────────────────────────────────────


def test_check_evaluation_complete_false_when_missing_judgment():
    item = VISItem.from_dict(str(SAMPLE_ITEM_PATH))
    # evaluation[0] has no judgments
    assert not item.check_evaluation_complete(
        "gemini-2.5-flash-image", "gemini-2.5-flash"
    )


def test_check_evaluation_complete_true_when_all_judged():
    item = VISItem(
        id="x",
        evaluation=[
            EvalEntry(
                judgments=[
                    Judgment(gen_model="gm", eval_model="em", analysis="ok", answer="1")
                ]
            )
        ],
    )
    assert item.check_evaluation_complete("gm", "em")


def test_check_evaluation_complete_false_empty():
    item = VISItem(id="x", evaluation=[])
    assert not item.check_evaluation_complete("gm", "em")


# ─── check_generation_exists ─────────────────────────────────────────────────


def test_check_generation_exists_false_when_empty():
    item = VISItem.from_dict(str(SAMPLE_ITEM_PATH))
    assert not item.check_generation_exists("any-model")


def test_check_generation_exists_true_after_update():
    item = VISItem(id="x", generation={})
    item.update_generation("my-model", "/path/to/img.png")
    assert item.check_generation_exists("my-model")


# ─── save / round-trip ────────────────────────────────────────────────────────


def test_save_item_creates_file(tmp_path):
    item = VISItem.from_dict(str(SAMPLE_ITEM_PATH))
    item.save_item(str(tmp_path))
    expected = tmp_path / "test-001" / "test-001.json"
    assert expected.exists()


def test_save_item_direct_path(tmp_path):
    item = VISItem.from_dict(str(SAMPLE_ITEM_PATH))
    out = tmp_path / "out.json"
    item.save_item(str(out))
    assert out.exists()


def test_round_trip_preserves_data(tmp_path):
    item = VISItem.from_dict(str(SAMPLE_ITEM_PATH))
    item.save_item(str(tmp_path))
    saved_path = tmp_path / "test-001" / "test-001.json"
    reloaded = VISItem.from_dict(str(saved_path))
    assert reloaded.id == item.id
    assert len(reloaded.evaluation) == len(item.evaluation)
    assert reloaded.evaluation[1].judgments[0].answer == "1"


# ─── get_evaluation_by_source ────────────────────────────────────────────────


def test_get_evaluation_by_source():
    item = VISItem.from_dict(str(SAMPLE_ITEM_PATH))
    prompt_entries = item.get_evaluation_by_source("prompt")
    seed_entries = item.get_evaluation_by_source("seed")
    assert len(prompt_entries) == 1
    assert len(seed_entries) == 1
    assert prompt_entries[0].source == "prompt"
