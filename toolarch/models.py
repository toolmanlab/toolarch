"""Core data models for ToolArch."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class NodeKind(str, Enum):
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"


class EdgeKind(str, Enum):
    IMPORT = "import"
    CALL = "call"
    INHERIT = "inherit"


class Severity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Node(BaseModel):
    """A code entity: module, class, or function."""

    id: str
    name: str
    kind: NodeKind
    file_path: str
    line_start: int
    line_end: int
    module: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class Edge(BaseModel):
    """A relationship between two nodes."""

    id: str
    source_id: str
    target_id: str
    kind: EdgeKind
    weight: float = 1.0


class ParseResult(BaseModel):
    """Output of a parser run."""

    nodes: list[Node]
    edges: list[Edge]
    root_path: str
    lang: str


class Issue(BaseModel):
    """A single architecture issue found by an analyzer."""

    rule: str
    message: str
    severity: Severity
    location: str = ""
    details: dict[str, Any] = Field(default_factory=dict)


class Metric(BaseModel):
    """A computed metric for a node or module."""

    node_id: str
    name: str
    value: float
    details: dict[str, Any] = Field(default_factory=dict)


class AnalysisResult(BaseModel):
    """Output of an analyzer run."""

    analyzer: str
    issues: list[Issue] = Field(default_factory=list)
    metrics: list[Metric] = Field(default_factory=list)
    summary: str = ""


class RunSummary(BaseModel):
    """Summary of a full analysis run."""

    root_path: str
    lang: str
    total_nodes: int = 0
    total_edges: int = 0
    results: list[AnalysisResult] = Field(default_factory=list)

    @property
    def total_issues(self) -> int:
        return sum(len(r.issues) for r in self.results)

    @property
    def high_severity_count(self) -> int:
        return sum(
            1 for r in self.results for i in r.issues if i.severity == Severity.HIGH
        )
