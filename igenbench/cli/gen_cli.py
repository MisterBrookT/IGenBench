"""Generation commands for text-to-image models."""

import typer

from igenbench.cli.main import app
from igenbench.utils.logger import logger
from igenbench.workflow.gen_workflow import GenWorkflow
from igenbench.vis_item import VISItem


@app.command("gen")
def cmd_gen(
    info_path: str = typer.Option(
        ..., "--info-path", help="Path to the VISItem JSON file"
    ),
    provider: str = typer.Option("google", "--provider", help="LLM provider to use"),
    model: str = typer.Option(
        "gemini-2.0-flash-exp", "--model", help="Model to use for image generation"
    ),
    output_dir: str = typer.Option(
        "outputs/", "--output-dir", help="Output directory path"
    ),
    resume: bool = typer.Option(
        False,
        "--resume",
        help="Resume from output directory to skip already generated images",
    ),
):
    """Generate image from text prompt using text-to-image model.

    Reads the VISItem and generates an image based on the t2i_prompt field.
    """
    try:
        workflow = GenWorkflow(provider, model, output_dir, resume=resume)
        
        # Load item - use state_manager for resume functionality
        if resume:
            item = workflow.state_manager.load_item(info_path, resume=True)
        else:
            item = VISItem.from_dict(info_path)

        # Run generation
        item = workflow.run(item)

        # Save result
        item.save_item(output_path=output_dir)
        save_path = item.build_save_path(output_dir)
        logger.info(f"✅ Generation completed for {item.id}.json, saved to {save_path}")

    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        raise typer.Exit(code=2)
    except ValueError as e:
        logger.error(f"❌ Invalid input: {e}")
        raise typer.Exit(code=3)
    except Exception as e:
        logger.exception(f"❌ Generation failed for {info_path}: {e}")
        raise typer.Exit(code=1)
