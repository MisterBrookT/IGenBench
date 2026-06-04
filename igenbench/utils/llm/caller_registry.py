from typing import Callable, Dict, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from .llm_caller import LLMCaller

CALLER_REGISTRY: Dict[str, Type["LLMCaller"]] = {}


def register_caller(name: str) -> Callable[[Type["LLMCaller"]], Type["LLMCaller"]]:
    """Class decorator that registers an LLMCaller implementation under *name*.

    Usage::

        @register_caller("google")
        class GoogleCaller(LLMCaller): ...

    Raises:
        ValueError: If *name* is already registered.
    """

    def wrapper(cls: Type["LLMCaller"]) -> Type["LLMCaller"]:
        if name in CALLER_REGISTRY:
            raise ValueError(f"Caller {name} already registered")
        CALLER_REGISTRY[name] = cls
        return cls

    return wrapper
