"""Tree-sitter based Java parser — stub for future implementation."""

from __future__ import annotations

from pathlib import Path

from toolarch.models import ParseResult
from toolarch.parser.base import BaseParser


class JavaParser(BaseParser):
    """Placeholder for Java parsing support."""

    def parse(self, path: Path) -> ParseResult:
        raise NotImplementedError("Java parser not yet implemented.")
