"""Base parser interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from toolarch.models import ParseResult


class BaseParser(ABC):
    """Abstract base for language-specific code parsers."""

    @abstractmethod
    def parse(self, path: Path) -> ParseResult:
        """Parse all source files under `path` and return nodes + edges."""
        ...
