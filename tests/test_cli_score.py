"""Unit tests for the `igenbench score` CLI command — no API keys required."""

import json
from pathlib import Path

from typer.testing import CliRunner

from igenbench.cli.main import app

runner = CliRunner()


def _make_result_file(tmp_path: Path, item_id: str, judgments: list) -> None:
    """Write a minimal VISItem JSON with the given judgments."""
    item_dir = tmp_path / item_id
    item_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "id": item_id,
        "t2i_prompt": "A chart.",
        "chart_type": "bar",
        "reference_image_url": None,
        "generation": {"my-gen-model": str(item_dir / "img.png")},
        "evaluation": [
            {
                "source": "prompt",
                "ground": "4",
                "question": "How many bars?",
                "question_type": "count",
                "judgments": judgments,
            }
        ],
    }
    (item_dir / f"{item_id}.json").write_text(json.dumps(data))


# ─── basic scoring ─────────────────────────────────────────────────────────────


def test_score_shows_accuracy(tmp_path):
    _make_result_file(
        tmp_path,
        "item-001",
        [
            {
                "gen_model": "my-gen-model",
                "eval_model": "my-eval-model",
                "analysis": "",
                "answer": "1",
            }
        ],
    )
    result = runner.invoke(app, ["score", "--output-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "100.0%" in result.output or "1/1" in result.output


def test_score_no_results_exits_nonzero(tmp_path):
    result = runner.invoke(app, ["score", "--output-dir", str(tmp_path)])
    assert result.exit_code != 0


def test_score_missing_dir_exits_nonzero(tmp_path):
    result = runner.invoke(
        app, ["score", "--output-dir", str(tmp_path / "nonexistent")]
    )
    assert result.exit_code != 0


def test_score_filter_by_gen_model(tmp_path):
    _make_result_file(
        tmp_path,
        "item-002",
        [
            {
                "gen_model": "model-A",
                "eval_model": "eval-M",
                "analysis": "",
                "answer": "1",
            }
        ],
    )
    # Correct filter — should find result
    result = runner.invoke(
        app, ["score", "--output-dir", str(tmp_path), "--gen-model", "model-A"]
    )
    assert result.exit_code == 0

    # Wrong filter — should print "No evaluation results"
    result2 = runner.invoke(
        app, ["score", "--output-dir", str(tmp_path), "--gen-model", "model-B"]
    )
    assert result2.exit_code == 0
    assert "No evaluation results" in result2.output


def test_score_by_source_breakdown(tmp_path):
    _make_result_file(
        tmp_path,
        "item-003",
        [{"gen_model": "gm", "eval_model": "em", "analysis": "", "answer": "0"}],
    )
    result = runner.invoke(app, ["score", "--output-dir", str(tmp_path), "--by-source"])
    assert result.exit_code == 0
    assert "prompt" in result.output
