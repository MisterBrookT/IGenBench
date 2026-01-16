"""Dedicated workflow for running evaluations on generated questions."""

from typing import List
from pathlib import Path

from igenbench.workflow.workflow_config import EvalWorkflowConfig
from igenbench.engine.eval_engine import EvalEngine
from igenbench.utils.logger import logger
from igenbench.utils.path_resolver import PathResolver
from igenbench.utils.state_manager import ItemStateManager
from igenbench.vis_item import VISItem


class EvalWorkflow:
    """Workflow dedicated to running evaluations on generated questions."""

    def __init__(
        self, provider: str, eval_model: str, output_dir: str, resume: bool = False
    ):
        """Initialize EvalWorkflow.

        Args:
            provider: LLM provider name
            eval_model: Evaluation model name
            output_dir: Output directory path
            resume: Whether to resume from existing state
        """
        # Create configuration
        self.config = EvalWorkflowConfig(
            provider=provider, model=eval_model, output_dir=output_dir, resume=resume
        )
        self.config.validate()

        # Create state manager and engine
        self.state_manager = ItemStateManager(output_dir)
        self.engine = EvalEngine(self.config.llm_client, eval_model)

        # Store for compatibility
        self.eval_model = eval_model
        self.output_dir = output_dir
        self.resume = resume

    def run(
        self,
        item: VISItem,
        gen_model_name: str,
        image_path: str = None,
    ) -> VISItem:
        """Run evaluation on all questions in the item.

        Args:
            item: VISItem to process
            gen_model_name: Name of the generation model that created the image
            image_path: Optional path to image file

        Returns:
            Updated VISItem with evaluation results
        """
        # Resolve image path if not provided
        if image_path is None:
            image_path = self._resolve_image_path(item, gen_model_name)

        # Check if already fully evaluated
        if self.resume and self.engine.check_fully_evaluated(
            item=item,
            gen_model=gen_model_name,
            eval_model=self.eval_model,
        ):
            logger.info(
                f"✅ All questions already evaluated for item {item.id} "
                f"with {self.eval_model} on {gen_model_name}"
            )
            return item

        logger.info(
            f"🔍 Evaluating item {item.id} with {self.eval_model} on {gen_model_name}"
        )
        
        item = self._evaluate_all(
            item=item,
            image_path=image_path,
            gen_model_name=gen_model_name,
        )

        return item

    def _resolve_image_path(self, item: VISItem, gen_model_name: str) -> Path:
        """Resolve image path from gen_model_name using PathResolver."""
        return PathResolver.resolve_image_path(item.id, gen_model_name, self.output_dir)

    def _evaluate_all(
        self, item: VISItem, image_path: Path, gen_model_name: str
    ) -> VISItem:
        """Evaluate all questions in the item."""
        if not item.evaluation:
            raise ValueError(
                f"No questions found for item {item.id}. "
                f"Questions should be generated before evaluation."
            )

        eval_model = self.eval_model
        total_questions = len(item.evaluation)

        for i, eval_entry in enumerate(item.evaluation):
            # Skip if already judged (for resume functionality)
            if self.resume and self.engine.check_eval_entry_being_judged(
                eval_entry=eval_entry, gen_model=gen_model_name, eval_model=eval_model
            ):
                logger.info(
                    f"⏭️  Skipping question {i + 1} / {total_questions} "
                    f"(already evaluated by {eval_model} on {gen_model_name})"
                )
                continue

            logger.info(
                f"🔍 Evaluating item {item.id} with {eval_model} on {gen_model_name} "
                f"-> {i + 1} / {total_questions}"
            )

            # Generate judgment using engine
            judgment = self.engine.judge_entry(
                eval_entry, gen_model_name, eval_model, str(image_path)
            )
            eval_entry.judgments.append(judgment)

            # Save after each question is evaluated (for incremental progress)
            self.state_manager.save_item(item)

        return item
