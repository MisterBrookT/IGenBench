"""Batch generation and evaluation commands."""

from pathlib import Path

import typer

from igenbench.cli.main import app
from igenbench.utils.logger import logger
from igenbench.workflow.eval_workflow import EvalWorkflow
from igenbench.workflow.gen_workflow import GenWorkflow


@app.command("batch-gen")
def cmd_batch_gen(
    data_dir: str = typer.Option(
        ..., "--data-dir", help="Directory containing VISItem JSON files"
    ),
    provider: str = typer.Option("google", "--provider", help="LLM provider to use"),
    model: str = typer.Option(
        "gemini-2.0-flash-exp", "--model", help="Model to use for image generation"
    ),
    output_dir: str = typer.Option(
        "outputs/", "--output-dir", help="Output directory path"
    ),
    resume: bool = typer.Option(
        True,
        "--resume/--no-resume",
        help="Resume from existing state, skipping already generated images",
    ),
):
    """Batch generate infographic images for all VISItem JSON files in a directory."""
    json_files = sorted(Path(data_dir).glob("*.json"))

    if not json_files:
        logger.error(f"No JSON files found in {data_dir}")
        raise typer.Exit(code=2)

    logger.info(f"Starting batch generation: {len(json_files)} items with {model}")

    workflow = GenWorkflow(provider, model, output_dir, resume=resume)
    success_count = 0
    fail_count = 0

    for i, json_file in enumerate(json_files):
        try:
            item = workflow.state_manager.load_item(str(json_file), resume=resume)
            item = workflow.run(item)
            item.save_item(output_path=output_dir)
            success_count += 1
            logger.info(f"[{i + 1}/{len(json_files)}] ✅ {json_file.name}")
        except Exception as e:
            fail_count += 1
            logger.error(f"[{i + 1}/{len(json_files)}] ❌ {json_file.name}: {e}")

    logger.info(
        f"Batch generation done: {success_count} succeeded, {fail_count} failed"
    )
    if fail_count > 0:
        raise typer.Exit(code=1)


@app.command("batch-eval")
def cmd_batch_eval(
    data_dir: str = typer.Option(
        ..., "--data-dir", help="Directory containing VISItem JSON files"
    ),
    gen_model: str = typer.Option(
        ..., "--gen-model", help="Name of the model that generated the images"
    ),
    provider: str = typer.Option("google", "--provider", help="LLM provider to use"),
    model: str = typer.Option(
        "gemini-2.5-flash", "--model", help="Model name for evaluation"
    ),
    output_dir: str = typer.Option(
        "outputs/", "--output-dir", help="Output directory path"
    ),
    resume: bool = typer.Option(
        True,
        "--resume/--no-resume",
        help="Resume from existing state, skipping already evaluated questions",
    ),
):
    """Batch evaluate generated images for all VISItem JSON files in a directory."""
    json_files = sorted(Path(data_dir).glob("*.json"))

    if not json_files:
        logger.error(f"No JSON files found in {data_dir}")
        raise typer.Exit(code=2)

    logger.info(f"Starting batch evaluation: {len(json_files)} items with {model}")

    workflow = EvalWorkflow(provider, model, output_dir, resume=resume)
    success_count = 0
    fail_count = 0

    for i, json_file in enumerate(json_files):
        try:
            item = workflow.state_manager.load_item(str(json_file), resume=resume)
            item = workflow.run(item, gen_model)
            item.save_item(output_path=output_dir)
            success_count += 1
            logger.info(f"[{i + 1}/{len(json_files)}] ✅ {json_file.name}")
        except Exception as e:
            fail_count += 1
            logger.error(f"[{i + 1}/{len(json_files)}] ❌ {json_file.name}: {e}")

    logger.info(
        f"Batch evaluation done: {success_count} succeeded, {fail_count} failed"
    )
    if fail_count > 0:
        raise typer.Exit(code=1)
