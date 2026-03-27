"""Tests for the Python parser."""

from pathlib import Path

from toolarch.models import EdgeKind, NodeKind
from toolarch.parser.python_parser import PythonParser

FIXTURES = Path(__file__).parent / "fixtures" / "sample_python"


def test_parse_finds_modules():
    parser = PythonParser()
    result = parser.parse(FIXTURES)
    module_names = {n.name for n in result.nodes if n.kind == NodeKind.MODULE}
    assert "__init__" in module_names
    assert "module_a" in module_names
    assert "module_b" in module_names


def test_parse_finds_classes():
    parser = PythonParser()
    result = parser.parse(FIXTURES)
    class_names = {n.name for n in result.nodes if n.kind == NodeKind.CLASS}
    assert "ServiceA" in class_names
    assert "ServiceB" in class_names


def test_parse_finds_functions():
    parser = PythonParser()
    result = parser.parse(FIXTURES)
    func_names = {n.name for n in result.nodes if n.kind == NodeKind.FUNCTION}
    assert "greet" in func_names
    assert "helper" in func_names


def test_parse_finds_import_edges():
    parser = PythonParser()
    result = parser.parse(FIXTURES)
    import_edges = [e for e in result.edges if e.kind == EdgeKind.IMPORT]
    assert len(import_edges) >= 2
