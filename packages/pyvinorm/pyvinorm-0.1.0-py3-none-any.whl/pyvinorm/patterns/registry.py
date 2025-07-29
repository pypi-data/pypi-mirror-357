import logging

from typing import Dict, Type
from .base import BasePattern

logger = logging.getLogger(__name__)

__PATTERN_REGISTRY: Dict[str, Type[BasePattern]] = {}


def register_pattern(cls):
    """
    Decorator to register a pattern class in the registry.
    """
    if not issubclass(cls, BasePattern):
        raise TypeError(f"{cls.__name__} must be a subclass of BasePattern.")

    pattern_id = cls.__name__
    if pattern_id in __PATTERN_REGISTRY:
        raise ValueError(f"Pattern ID {pattern_id} is already registered.")

    __PATTERN_REGISTRY[pattern_id] = cls
    logger.info(f"Registered pattern: {pattern_id}")

    return cls


def get_patterns() -> Dict[str, BasePattern]:
    """
    Get the registered patterns.

    :return: A dictionary of registered patterns.
    """
    return {pattern_id: cls() for pattern_id, cls in __PATTERN_REGISTRY.items()}


def get_pattern(pattern_id: str) -> BasePattern:
    """
    Get a specific pattern by its ID.

    :param pattern_id: The ID of the pattern to retrieve.
    :return: The pattern class associated with the given ID.
    :raises KeyError: If the pattern ID is not found in the registry.
    """
    if pattern_id not in __PATTERN_REGISTRY:
        raise KeyError(f"Pattern ID {pattern_id} not found in registry.")

    cls = __PATTERN_REGISTRY[pattern_id]
    return cls()
