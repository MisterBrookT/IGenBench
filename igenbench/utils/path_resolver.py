"""Unified path resolution and file handling utilities."""

from pathlib import Path
from typing import List, Optional

from igenbench.utils.model_resolver import ModelNameResolver


class PathResolver:
    """Utilities for consistent path resolution across all components."""

    @staticmethod
    def resolve_image_path(item_id: str, model_name: str, output_dir: str) -> Path:
        """Resolve image path using consistent logic.

        Args:
            item_id: Item identifier
            model_name: Model name (will be normalized)
            output_dir: Output directory base path

        Returns:
            Path to the image file
        """
        filename = ModelNameResolver.build_image_filename(item_id, model_name)
        return Path(output_dir) / item_id / filename

    @staticmethod
    def resolve_code_path(item_id: str, model_name: str, output_dir: str) -> Path:
        """Resolve code file path using consistent logic.

        Args:
            item_id: Item identifier
            model_name: Model name (will be normalized)
            output_dir: Output directory base path

        Returns:
            Path to the code file
        """
        filename = ModelNameResolver.build_code_filename(item_id, model_name)
        return Path(output_dir) / item_id / filename

    @staticmethod
    def resolve_item_json_path(item_id: str, output_dir: str) -> Path:
        """Resolve item JSON file path.

        Args:
            item_id: Item identifier
            output_dir: Output directory base path

        Returns:
            Path to the item JSON file
        """
        return Path(output_dir) / item_id / f"{item_id}.json"

    @staticmethod
    def find_image_with_extensions(
        base_path: Path, extensions: List[str]
    ) -> Optional[Path]:
        """Find image file with supported extensions.

        Args:
            base_path: Base path without extension
            extensions: List of extensions to try (e.g., [".png", ".jpg", ".jpeg"])

        Returns:
            Path to found image file, or None if not found
        """
        for ext in extensions:
            candidate = base_path.with_suffix(ext)
            if candidate.exists():
                return candidate
        return None

    @staticmethod
    def find_source_image(item_id: str, datasets_dir: str) -> Optional[Path]:
        """Find source image in datasets directory.

        Args:
            item_id: Item identifier
            datasets_dir: Datasets directory path

        Returns:
            Path to source image, or None if not found
        """
        base_path = Path(datasets_dir) / item_id
        extensions = [".png", ".jpg", ".jpeg", ".webp"]
        return PathResolver.find_image_with_extensions(base_path, extensions)

    @staticmethod
    def find_output_image(item_id: str, output_dir: str) -> Optional[Path]:
        """Find any image in output directory for an item.

        Args:
            item_id: Item identifier
            output_dir: Output directory path

        Returns:
            Path to found image, or None if not found
        """
        item_dir = Path(output_dir) / item_id
        if not item_dir.exists():
            return None

        # Look for any image files in the item directory
        extensions = [".png", ".jpg", ".jpeg", ".webp", ".svg"]
        for ext in extensions:
            for image_file in item_dir.glob(f"*{ext}"):
                return image_file

        return None

    @staticmethod
    def resolve_human_image_path(item_id: str, output_dir: str) -> Path:
        """Resolve path for human reference image.

        Args:
            item_id: Item identifier
            output_dir: Output directory base path

        Returns:
            Path where human reference image should be stored
        """
        return Path(output_dir) / item_id / f"{item_id}_human.png"
