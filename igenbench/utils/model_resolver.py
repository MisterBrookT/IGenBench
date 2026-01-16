"""Unified model name processing and normalization."""


class ModelNameResolver:
    """Utilities for consistent model name processing across all components."""

    @staticmethod
    def normalize_for_filename(model_name: str) -> str:
        """Convert model name to filesystem-safe format.

        Args:
            model_name: Original model name (e.g., "gemini-2.5-pro", "openai/gpt-4")

        Returns:
            Normalized name safe for filenames (e.g., "gemini_2_5_pro", "gpt_4")
        """
        # Replace problematic characters
        normalized = model_name.replace("-", "_").replace(".", "_")

        # Handle provider/model format (e.g., "openai/gpt-4" -> "gpt_4")
        if "/" in normalized:
            normalized = normalized.split("/")[1]

        return normalized

    @staticmethod
    def build_image_filename(
        item_id: str, model_name: str, extension: str = ".png"
    ) -> str:
        """Build consistent image filename for generated images.

        Args:
            item_id: Item identifier
            model_name: Model name to normalize
            extension: File extension (default: .png)

        Returns:
            Consistent filename format
        """
        normalized_model = ModelNameResolver.normalize_for_filename(model_name)
        return f"{item_id}_{normalized_model}{extension}"
