"""Base class for all scanner modules."""

from __future__ import annotations

import abc
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argus.models import Finding, ScanContext

logger = logging.getLogger("argus")


class BaseModule(abc.ABC):
    """Every scanner module inherits from this."""

    name: str = ""  # e.g. "dns_intel"
    description: str = ""  # Human-readable description
    phase: int = 1  # Execution phase (1-5)
    step: int = 1  # Build step (1-10)

    @abc.abstractmethod
    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        """Run the module and return findings. Also mutate context with raw data."""
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} phase={self.phase} step={self.step}>"
