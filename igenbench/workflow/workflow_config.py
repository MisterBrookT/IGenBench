"""Workflow configuration classes for consistent parameter management."""

from dataclasses import dataclass, field
from typing import Optional

from igenbench.utils.llm.client import LLMClient


@dataclass
class WorkflowConfig:
    """Base configuration for workflow operations.

    Provides consistent configuration management across all workflows.
    """

    provider: str
    model: str
    output_dir: str
    resume: bool = True

    # LLM client is created automatically based on provider
    _llm_client: Optional[LLMClient] = field(default=None, init=False, repr=False)

    @property
    def llm_client(self) -> LLMClient:
        """Get or create LLM client instance."""
        if self._llm_client is None:
            self._llm_client = LLMClient(self.provider)
        return self._llm_client

    def validate(self) -> None:
        """Validate configuration parameters.

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.provider:
            raise ValueError("Provider cannot be empty")

        if not self.model:
            raise ValueError("Model cannot be empty")

        if not self.output_dir:
            raise ValueError("Output directory cannot be empty")

        # Validate provider by attempting to create client
        try:
            _ = self.llm_client
        except ValueError as e:
            raise ValueError(f"Invalid provider '{self.provider}': {e}")


@dataclass
class GenWorkflowConfig(WorkflowConfig):
    """Configuration specific to generation workflows."""

    def validate(self) -> None:
        """Validate generation-specific configuration."""
        super().validate()
        # Add any generation-specific validation here if needed


@dataclass
class EvalWorkflowConfig(WorkflowConfig):
    """Configuration specific to evaluation workflows."""

    def validate(self) -> None:
        """Validate evaluation-specific configuration."""
        super().validate()
        # Add any evaluation-specific validation here if needed
