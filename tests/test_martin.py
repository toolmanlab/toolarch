"""Tests for Martin metrics."""

from toolarch.analyzers.martin import MartinAnalyzer
from toolarch.graph.sqlite_graph import SQLiteGraph
from toolarch.models import Edge, EdgeKind, Node, NodeKind, ParseResult


def _build_graph() -> SQLiteGraph:
    nodes = [
        Node(id="m1", name="mod_a", kind=NodeKind.MODULE, file_path="a.py", line_start=1, line_end=20, module="mod_a"),
        Node(id="m2", name="mod_b", kind=NodeKind.MODULE, file_path="b.py", line_start=1, line_end=15, module="mod_b"),
        Node(id="c1", name="AbstractService", kind=NodeKind.CLASS, file_path="a.py", line_start=3, line_end=10, module="mod_a"),
        Node(id="c2", name="ConcreteService", kind=NodeKind.CLASS, file_path="a.py", line_start=12, line_end=20, module="mod_a"),
        Node(id="c3", name="Repository", kind=NodeKind.CLASS, file_path="b.py", line_start=3, line_end=15, module="mod_b"),
    ]
    edges = [
        Edge(id="e1", source_id="m1", target_id="m2", kind=EdgeKind.IMPORT),
    ]
    graph = SQLiteGraph()
    graph.load(ParseResult(nodes=nodes, edges=edges, root_path="/tmp", lang="python"))
    return graph


def test_martin_metrics_computed():
    graph = _build_graph()
    result = MartinAnalyzer().analyze(graph)
    assert len(result.metrics) > 0

    # Check that abstractness is computed for mod_a (has 1 abstract out of 2 classes)
    mod_a_abstractness = [
        m for m in result.metrics if m.name == "abstractness" and m.node_id == "m1"
    ]
    assert len(mod_a_abstractness) == 1
    assert mod_a_abstractness[0].value == 0.5  # 1 abstract / 2 total


def test_martin_instability():
    graph = _build_graph()
    result = MartinAnalyzer().analyze(graph)

    # mod_a has Ce=1 (imports mod_b), Ca=0 → I = 1.0
    mod_a_instability = [
        m for m in result.metrics if m.name == "instability" and m.node_id == "m1"
    ]
    assert len(mod_a_instability) == 1
    assert mod_a_instability[0].value == 1.0


def test_martin_distance():
    graph = _build_graph()
    result = MartinAnalyzer().analyze(graph)

    # mod_a: A=0.5, I=1.0, D=|0.5+1.0-1|=0.5
    mod_a_distance = [
        m for m in result.metrics if m.name == "distance" and m.node_id == "m1"
    ]
    assert len(mod_a_distance) == 1
    assert mod_a_distance[0].value == 0.5
