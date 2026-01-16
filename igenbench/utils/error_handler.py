"""Enhanced error classification and handling utilities."""

from enum import Enum
from typing import Dict, List


class ErrorCategory(Enum):
    """Categories of errors that can occur during pipeline processing."""

    RECOVERABLE = "recoverable"  # Network timeouts, rate limits, temporary file locks
    PERMANENT = "permanent"  # Invalid config, missing files, malformed data
    SYSTEM = "system"  # Out of memory, disk full


class ErrorHandler:
    """Enhanced error classification and handling utilities."""

    # Error classification patterns
    SYSTEM_KEYWORDS = [
        "out of memory",
        "disk full",
        "no space left",
        "memory error",
        "permission denied",
        "access denied",
    ]

    RECOVERABLE_KEYWORDS = [
        "rate limit",
        "timeout",
        "connection",
        "network",
        "temporary",
        "503",
        "502",
        "429",
        "quota exceeded",
        "service unavailable",
        "generated questions are invalid or empty",  # Special case for question generation
    ]

    PERMANENT_KEYWORDS = [
        "not found",
        "invalid",
        "malformed",
        "bad request",
        "404",
        "401",
        "403",
        "400",
    ]

    @staticmethod
    def classify_error(error: Exception) -> ErrorCategory:
        """Classify an error into appropriate category.

        Args:
            error: Exception to classify

        Returns:
            ErrorCategory indicating how the error should be handled
        """
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()

        # Check system errors first (most critical)
        if any(keyword in error_str for keyword in ErrorHandler.SYSTEM_KEYWORDS):
            return ErrorCategory.SYSTEM

        # Check for specific exception types
        if error_type in ["memoryerror", "oserror", "permissionerror"]:
            return ErrorCategory.SYSTEM

        # Check recoverable errors
        if any(keyword in error_str for keyword in ErrorHandler.RECOVERABLE_KEYWORDS):
            return ErrorCategory.RECOVERABLE

        # Check for network-related exception types
        if error_type in ["connectionerror", "timeout", "httperror"]:
            return ErrorCategory.RECOVERABLE

        # Check permanent errors
        if any(keyword in error_str for keyword in ErrorHandler.PERMANENT_KEYWORDS):
            return ErrorCategory.PERMANENT

        # Check for validation-related exception types
        if error_type in ["valueerror", "typeerror", "keyerror", "filenotfounderror"]:
            return ErrorCategory.PERMANENT

        # Default to recoverable for unknown errors (safer approach)
        return ErrorCategory.RECOVERABLE

    @staticmethod
    def get_error_message_with_context(
        error: Exception, stage: str, item_id: str = None, method: str = None
    ) -> str:
        """Generate detailed error message with context.

        Args:
            error: Exception that occurred
            stage: Pipeline stage where error occurred
            item_id: Item ID if applicable
            method: Method name if applicable

        Returns:
            Detailed error message with context
        """
        base_msg = str(error)
        context_parts = []

        if item_id:
            context_parts.append(f"item {item_id}")
        if method:
            context_parts.append(f"method {method}")

        context = f" ({', '.join(context_parts)})" if context_parts else ""

        return f"Error in {stage} stage{context}: {base_msg}"

    @staticmethod
    def get_retry_guidance(error: Exception, attempt: int, max_attempts: int) -> str:
        """Get guidance message for retry scenarios.

        Args:
            error: Exception that occurred
            attempt: Current attempt number (1-based)
            max_attempts: Maximum number of attempts

        Returns:
            Guidance message for the user
        """
        category = ErrorHandler.classify_error(error)

        if category == ErrorCategory.SYSTEM:
            return f"System error detected (attempt {attempt}/{max_attempts}): {error}. Consider checking system resources."

        elif category == ErrorCategory.PERMANENT:
            return f"Permanent error detected (attempt {attempt}/{max_attempts}): {error}. This error is unlikely to resolve with retries."

        else:  # RECOVERABLE
            if attempt < max_attempts:
                return f"Recoverable error (attempt {attempt}/{max_attempts}): {error}. Will retry with backoff."
            else:
                return f"All retry attempts exhausted ({max_attempts} attempts): {error}. Consider checking network connectivity or service status."

    @staticmethod
    def should_retry(error: Exception) -> bool:
        """Determine if an error should be retried.

        Args:
            error: Exception to check

        Returns:
            True if error should be retried, False otherwise
        """
        category = ErrorHandler.classify_error(error)
        return category == ErrorCategory.RECOVERABLE

    @staticmethod
    def get_error_summary(errors: List[Exception]) -> Dict[str, int]:
        """Generate summary of errors by category.

        Args:
            errors: List of exceptions to summarize

        Returns:
            Dictionary mapping category names to counts
        """
        summary = {}

        for error in errors:
            category = ErrorHandler.classify_error(error)
            category_name = category.value
            summary[category_name] = summary.get(category_name, 0) + 1

        return summary
