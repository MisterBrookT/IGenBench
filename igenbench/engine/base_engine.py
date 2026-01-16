"""Base engine interface for consistent engine implementations."""

from igenbench.utils.llm.client import LLMClient


class BaseEngine:
    """Base class for all engine implementations.

    Engines contain pure algorithm implementations without:
    - File I/O operations
    - State management
    - Direct path resolution

    All engines should be testable without external dependencies.
    """

    def __init__(self, llm_client: LLMClient, model: str):
        """Initialize engine with LLM client and model.

        Args:
            llm_client: LLM client for making API calls
            model: Model name to use for processing
        """
        self.llm_client = llm_client
        self.model = model

    def __str__(self) -> str:
        """String representation of the engine."""
        return f"{self.__class__.__name__}(model={self.model})"
