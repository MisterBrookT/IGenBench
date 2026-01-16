"""Evaluation commands for generated images."""

import typer

from igenbench.cli.main import app
from igenbench.utils.logger import logger
from igenbench.workflow.eval_workflow import EvalWorkflow
from igenbench.vis_item import VISItem


@app.command("eval")
def cmd_run_evaluation(
    info_path: str = typer.Option(
        ..., "--info-path", help="Path to the VISItem JSON file"
    ),
    gen_model: str = typer.Option(
        ..., "--gen-model", help="Name of the generation model that created the image"
    ),
    provider: str = typer.Option("google", "--provider", help="LLM provider to use"),
    model: str = typer.Option(
        "gemini-2.5-flash", "--model", help="Model name to use for evaluation"
    ),
    output_dir: str = typer.Option(
        "outputs/", "--output-dir", help="Output directory path"
    ),
    image_path: str = typer.Option(
        None,
        "--image-path",
        help="Path to the generated image to evaluate (optional, will be auto-resolved if not provided)",
    ),
    resume: bool = typer.Option(
        False,
        "--resume",
        help="Resume from output directory to skip already processed items",
    ),
):
    """Run evaluation on a generated image using pre-generated questions.

    Evaluates the generated image on all questions in the VISItem.
    """
    try:
        workflow = EvalWorkflow(provider, model, output_dir, resume=resume)
        
        # Load item - use state_manager for resume functionality
        if resume:
            item = workflow.state_manager.load_item(info_path, resume=True)
        else:
            item = VISItem.from_dict(info_path)

        # Run evaluation on all questions
        item = workflow.run(item, gen_model, image_path)

        # Save result
        item.save_item(output_path=output_dir)
        save_path = item.build_save_path(output_dir)
        logger.info(f"✅ Evaluation completed successfully for {item.id}.json, saved to {save_path}")

    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        raise typer.Exit(code=2)
    except ValueError as e:
        logger.error(f"❌ Invalid input: {e}")
        raise typer.Exit(code=3)
    except Exception as e:
        logger.exception(f"❌ Evaluation failed for {info_path}: {e}")
        raise typer.Exit(code=1)
