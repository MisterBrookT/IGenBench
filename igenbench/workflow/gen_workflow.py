from pathlib import Path

from igenbench.workflow.workflow_config import GenWorkflowConfig
from igenbench.engine.gen_engine import GenEngine
from igenbench.utils.logger import logger
from igenbench.utils.path_resolver import PathResolver
from igenbench.utils.state_manager import ItemStateManager
from igenbench.vis_item import VISItem


class GenWorkflow:
    """Workflow wrapper for text-to-image generation."""

    def __init__(
        self, provider: str, model: str, output_dir: str, resume: bool = False
    ):
        """Initialize GenWorkflow.

        Args:
            provider: LLM provider name
            model: Generation model name
            output_dir: Output directory path
            resume: Whether to resume from existing state
        """
        # Create configuration
        self.config = GenWorkflowConfig(
            provider=provider, model=model, output_dir=output_dir, resume=resume
        )
        self.config.validate()

        # Create state manager and engine
        self.state_manager = ItemStateManager(output_dir)
        self.engine = GenEngine(self.config.llm_client, model)

        # Store for compatibility
        self.model = model
        self.output_dir = output_dir
        self.resume = resume

    def run(self, item: VISItem) -> VISItem:
        """Run text-to-image generation workflow.

        Args:
            item: VISItem to process

        Returns:
            Updated VISItem with generation results
        """
        # Check if already generated
        if self.resume and item.check_generation_exists(self.model):
            existing_path = Path(item.generation[self.model])
            if existing_path.exists():
                logger.info(
                    f"✅ Image already exists for {item.id}/{self.model}: {existing_path}"
                )
                return item

        logger.info(f"🎨 Generating image for item {item.id} with {self.model}")

        # Generate image
        image = self.engine.text2image(item)
        image_path = PathResolver.resolve_image_path(
            item.id, self.model, self.output_dir
        )
        image_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(image_path)

        # Update generation record
        item.update_generation(self.model, str(image_path))
        self.state_manager.save_item(item)

        logger.info(f"✅ Image generated: {image_path}")
        return item
