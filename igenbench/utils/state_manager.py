"""Unified state management for VISItem loading, saving, and resume logic."""

import json
from pathlib import Path
from typing import Optional

from igenbench.utils.logger import logger
from igenbench.vis_item import VISItem


class ItemStateManager:
    """Centralized state management for VISItem operations."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)

    def load_item(self, source_path: str, resume: bool = False) -> VISItem:
        """Unified item loading logic.

        Args:
            source_path: Original input path (e.g., "datasets/0.json")
            resume: If True, load from output dir; if False, load from source

        Returns:
            VISItem loaded from the appropriate location
        """
        if not resume:
            return VISItem.from_dict(source_path)

        # Resume mode: load from output directory if exists
        item_temp = VISItem.from_dict(source_path)
        output_path = self.output_dir / item_temp.id / f"{item_temp.id}.json"

        if output_path.exists():
            logger.debug(f"📂 Resume: loading from {output_path}")
            return VISItem.from_dict(str(output_path))
        else:
            logger.debug(f"📂 Resume: output not found, loading from {source_path}")
            return item_temp

    def save_item(self, item: VISItem) -> None:
        """Atomic item saving with proper error handling.

        Args:
            item: VISItem to save
        """
        save_path = self.output_dir / item.id / f"{item.id}.json"
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Use VISItem's own save method which handles the new format correctly
        item.save_item(str(save_path))
        logger.debug(f"💾 Saved item {item.id} to {save_path}")

    def is_stage_completed(
        self,
        item_id: str,
        stage: str,
        method: Optional[str] = None,
        configured_dimensions: Optional[list] = None,
    ) -> bool:
        """Consistent completion checking across all stages.

        Args:
            item_id: ID of the item to check
            stage: Stage name ("draft", "generate", "generate_questions", "evaluate")
            method: Method name for generate/evaluate stages
            configured_dimensions: List of dimensions for question/evaluate stages

        Returns:
            True if stage is completed, False otherwise
        """
        item_dir = self.output_dir / str(item_id)
        item_json = item_dir / f"{item_id}.json"

        if not item_json.exists():
            return False

        try:
            with open(item_json, "r") as f:
                data = json.load(f)

            if stage == "draft":
                # Draft is completed if t2i_prompt exists in design_space
                design_space = data.get("design_space", {})
                t2i_prompt = design_space.get("t2i_prompt", "")
                return bool(t2i_prompt and t2i_prompt.strip())

            elif stage == "generate":
                if not method:
                    return False
                # Generate is completed if method exists in generation record AND file exists
                generation = data.get("generation", {})
                if method in generation and generation[method]:
                    file_path = Path(generation[method])
                    return file_path.exists()
                return False

            elif stage == "generate_questions":
                if not configured_dimensions:
                    return False
                return self._validate_questions_completion(data, configured_dimensions)

            elif stage == "evaluate":
                if not method or not configured_dimensions:
                    return False
                return self._validate_evaluation_completion(
                    data, method, configured_dimensions
                )

            return False

        except Exception as e:
            logger.warning(f"Error checking completion for {item_id}/{stage}: {e}")
            return False

    def _validate_questions_completion(
        self, data: dict, configured_dimensions: list
    ) -> bool:
        """Validate that questions are properly generated for all dimensions."""
        evaluation = data.get("evaluation", {})

        for dimension in configured_dimensions:
            entries = evaluation.get(dimension, [])
            if not entries:
                return False

            # Check each entry for valid questions
            for entry in entries:
                question = entry.get("question", "")
                if not question or not question.strip():
                    return False

        return True

    def _validate_evaluation_completion(
        self, data: dict, method: str, configured_dimensions: list
    ) -> bool:
        """Validate that evaluation is complete for all dimensions."""
        # Parse method format: eval_model_gen_model
        if "_" not in method:
            return False

        parts = method.split("_", 1)
        if len(parts) != 2:
            return False

        eval_model, gen_model = parts
        evaluation = data.get("evaluation", {})

        if not evaluation:
            return False

        # Check each configured dimension
        for dimension in configured_dimensions:
            entries = evaluation.get(dimension, [])
            if not entries:
                return False

            # Check if all entries have judgments for the eval_model and gen_model
            for entry in entries:
                judgments = entry.get("judgments", [])
                has_judgment = any(
                    j.get("eval_model") == eval_model
                    and j.get("gen_model") == gen_model
                    for j in judgments
                )
                if not has_judgment:
                    return False

        return True
