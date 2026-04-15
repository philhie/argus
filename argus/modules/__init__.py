"""Module registry — auto-discovers and registers all scanner modules."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argus.modules.base import BaseModule

_REGISTRY: dict[str, type[BaseModule]] = {}


def register(cls: type[BaseModule]) -> type[BaseModule]:
    """Decorator to register a module class."""
    _REGISTRY[cls.name] = cls
    return cls


def get_modules_for_step(step: int) -> list[type[BaseModule]]:
    """Return module classes for a given build step, ordered by phase."""
    return sorted(
        [m for m in _REGISTRY.values() if m.step == step],
        key=lambda m: m.phase,
    )


def get_all_modules() -> list[type[BaseModule]]:
    """Return all registered modules ordered by phase then step."""
    return sorted(_REGISTRY.values(), key=lambda m: (m.phase, m.step))


def get_modules_up_to_step(step: int) -> list[type[BaseModule]]:
    """Return all modules from step 1 through the given step."""
    return sorted(
        [m for m in _REGISTRY.values() if m.step <= step],
        key=lambda m: (m.phase, m.step),
    )
