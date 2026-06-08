"""Regression tests for documented CLI defaults."""

from typer.testing import CliRunner

from igenbench.cli.main import app
from igenbench.defaults import DEFAULT_EVALUATION_MODEL

runner = CliRunner()


def test_eval_help_shows_default_evaluation_model():
    result = runner.invoke(app, ["eval", "--help"])

    assert result.exit_code == 0
    assert DEFAULT_EVALUATION_MODEL in result.output


def test_batch_eval_help_shows_default_evaluation_model():
    result = runner.invoke(app, ["batch-eval", "--help"])

    assert result.exit_code == 0
    assert DEFAULT_EVALUATION_MODEL in result.output
