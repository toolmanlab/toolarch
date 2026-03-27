"""Graph adapter interface — unified API for graph backends."""

from __future__ import annotations

from abc import ABC, abstractmethod

from toolarch.models import Edge, Node, ParseResult, RunSummary


class GraphAdapter(ABC):
    """Abstract graph storage backend."""

    @abstractmethod
    def load(self, parse_result: ParseResult) -> None:
        """Load parsed nodes and edges into the graph."""
        ...

    @abstractmethod
    def get_nodes(self, kind: str | None = None) -> list[Node]:
        """Get all nodes, optionally filtered by kind."""
        ...

    @abstractmethod
    def get_edges(self, kind: str | None = None) -> list[Edge]:
        """Get all edges, optionally filtered by kind."""
        ...

    @abstractmethod
    def get_dependents(self, node_id: str) -> list[Edge]:
        """Get edges where node_id is the target (afferent coupling)."""
        ...

    @abstractmethod
    def get_dependencies(self, node_id: str) -> list[Edge]:
        """Get edges where node_id is the source (efferent coupling)."""
        ...

    @abstractmethod
    def save_run(self, summary: RunSummary) -> None:
        """Persist a run summary."""
        ...

    @abstractmethod
    def load_last_run(self) -> RunSummary | None:
        """Load the most recent run summary."""
        ...
