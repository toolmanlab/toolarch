"""Tests for SQLite graph storage."""

from toolarch.graph.sqlite_graph import SQLiteGraph
from toolarch.models import Edge, EdgeKind, Node, NodeKind, ParseResult, RunSummary


def _make_parse_result() -> ParseResult:
    nodes = [
        Node(id="m1", name="mod_a", kind=NodeKind.MODULE, file_path="mod_a.py", line_start=1, line_end=10, module="mod_a"),
        Node(id="m2", name="mod_b", kind=NodeKind.MODULE, file_path="mod_b.py", line_start=1, line_end=8, module="mod_b"),
    ]
    edges = [
        Edge(id="e1", source_id="m1", target_id="m2", kind=EdgeKind.IMPORT),
    ]
    return ParseResult(nodes=nodes, edges=edges, root_path="/tmp/test", lang="python")


def test_load_and_query():
    graph = SQLiteGraph()
    graph.load(_make_parse_result())
    assert len(graph.get_nodes()) == 2
    assert len(graph.get_edges()) == 1


def test_get_nodes_by_kind():
    graph = SQLiteGraph()
    graph.load(_make_parse_result())
    modules = graph.get_nodes(kind="module")
    assert len(modules) == 2


def test_dependencies():
    graph = SQLiteGraph()
    graph.load(_make_parse_result())
    deps = graph.get_dependencies("m1")
    assert len(deps) == 1
    assert deps[0].target_id == "m2"


def test_dependents():
    graph = SQLiteGraph()
    graph.load(_make_parse_result())
    dependents = graph.get_dependents("m2")
    assert len(dependents) == 1
    assert dependents[0].source_id == "m1"


def test_save_and_load_run():
    graph = SQLiteGraph()
    graph.load(_make_parse_result())
    summary = RunSummary(root_path="/tmp/test", lang="python", total_nodes=2, total_edges=1)
    graph.save_run(summary)
    loaded = graph.load_last_run()
    assert loaded is not None
    assert loaded.root_path == "/tmp/test"
    assert loaded.total_nodes == 2
