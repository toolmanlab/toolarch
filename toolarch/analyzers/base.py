"""Base analyzer interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from toolarch.graph.adapter import GraphAdapter
from toolarch.models import AnalysisResult


class BaseAnalyzer(ABC):
    """Abstract base for architecture analyzers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable analyzer name."""
        ...

    @abstractmethod
    def analyze(self, graph: GraphAdapter) -> AnalysisResult:
        """Run analysis on the graph and return results."""
        ...
