"""Tests for cycle detection."""

from toolarch.analyzers.cycles import CycleAnalyzer
from toolarch.graph.sqlite_graph import SQLiteGraph
from toolarch.models import Edge, EdgeKind, Node, NodeKind, ParseResult


def test_detects_cycle():
    nodes = [
        Node(id="m1", name="mod_a", kind=NodeKind.MODULE, file_path="a.py", line_start=1, line_end=5, module="mod_a"),
        Node(id="m2", name="mod_b", kind=NodeKind.MODULE, file_path="b.py", line_start=1, line_end=5, module="mod_b"),
    ]
    edges = [
        Edge(id="e1", source_id="m1", target_id="m2", kind=EdgeKind.IMPORT),
        Edge(id="e2", source_id="m2", target_id="m1", kind=EdgeKind.IMPORT),
    ]
    graph = SQLiteGraph()
    graph.load(ParseResult(nodes=nodes, edges=edges, root_path="/tmp", lang="python"))

    result = CycleAnalyzer().analyze(graph)
    assert len(result.issues) == 1
    assert "Circular dependency" in result.issues[0].message


def test_no_cycle():
    nodes = [
        Node(id="m1", name="mod_a", kind=NodeKind.MODULE, file_path="a.py", line_start=1, line_end=5, module="mod_a"),
        Node(id="m2", name="mod_b", kind=NodeKind.MODULE, file_path="b.py", line_start=1, line_end=5, module="mod_b"),
    ]
    edges = [
        Edge(id="e1", source_id="m1", target_id="m2", kind=EdgeKind.IMPORT),
    ]
    graph = SQLiteGraph()
    graph.load(ParseResult(nodes=nodes, edges=edges, root_path="/tmp", lang="python"))

    result = CycleAnalyzer().analyze(graph)
    assert len(result.issues) == 0
