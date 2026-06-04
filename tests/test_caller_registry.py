"""Unit tests for the @register_caller decorator and CALLER_REGISTRY."""

import pytest

from igenbench.utils.llm.caller_registry import CALLER_REGISTRY, register_caller
from igenbench.utils.llm.llm_caller import LLMCaller


def test_register_caller_adds_to_registry():
    name = "_test_provider_add"
    try:

        @register_caller(name)
        class _DummyCaller(LLMCaller):
            pass

        assert name in CALLER_REGISTRY
        assert CALLER_REGISTRY[name] is _DummyCaller
    finally:
        CALLER_REGISTRY.pop(name, None)


def test_register_caller_duplicate_raises():
    name = "_test_provider_dup"
    try:

        @register_caller(name)
        class _First(LLMCaller):
            pass

        with pytest.raises(ValueError, match="already registered"):

            @register_caller(name)
            class _Second(LLMCaller):
                pass

    finally:
        CALLER_REGISTRY.pop(name, None)


def test_register_caller_returns_class_unchanged():
    name = "_test_provider_ret"
    try:

        @register_caller(name)
        class _MyProvider(LLMCaller):
            pass

        assert _MyProvider.__name__ == "_MyProvider"
    finally:
        CALLER_REGISTRY.pop(name, None)


def test_built_in_providers_registered():
    for provider in ("google", "openrouter", "replicate"):
        assert provider in CALLER_REGISTRY, f"{provider} not found in registry"
