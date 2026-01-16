from typing import Any

from .caller_registry import CALLER_REGISTRY
from PIL.Image import Image as PILImage
from ..io import extract_from_markdown
from .llm_caller import LLMCaller


class LLMClient:
    def __init__(self, provider: str):
        self._caller = self._get_caller(provider)

    def _get_caller(self, provider: str) -> LLMCaller:
        provider = provider.lower()
        if provider not in CALLER_REGISTRY:
            raise ValueError(
                f"Unsupported provider: {provider}. Supported providers: {list(CALLER_REGISTRY.keys())}"
            )
        return CALLER_REGISTRY[provider]()

    def call_text_generation(self, model: str, prompt: str, **kwargs: Any) -> str:
        text_response = self._caller.generate_text(model, prompt, **kwargs)
        style_normalized_text_response = extract_from_markdown(text_response)
        return style_normalized_text_response

    def call_image_understanding(
        self, model: str, prompt: str, image_path: str, **kwargs: Any
    ) -> str:
        text_response = self._caller.understand_image(
            model, prompt, image_path, **kwargs
        )
        style_normalized_text_response = extract_from_markdown(text_response)
        return style_normalized_text_response

    def call_image_generation(self, model: str, prompt: str, **kwargs: Any) -> PILImage:
        pil_image = self._caller.generate_image(model, prompt, **kwargs)
        return pil_image
