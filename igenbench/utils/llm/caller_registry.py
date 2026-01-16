from typing import Dict, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from .llm_caller import LLMCaller

CALLER_REGISTRY: Dict[str, Type["LLMCaller"]] = {}


def register_caller(name: str):
    def wrapper(cls: "LLMCaller") -> "LLMCaller":
        if name in CALLER_REGISTRY:
            raise ValueError(f"Caller {name} already registered")
        CALLER_REGISTRY[name] = cls
        return cls

    return wrapper
