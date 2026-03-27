"""Tree-sitter based Python parser."""

from __future__ import annotations

import hashlib
from pathlib import Path

import tree_sitter_python as tspython
from tree_sitter import Language, Parser

from toolarch.models import Edge, EdgeKind, Node, NodeKind, ParseResult
from toolarch.parser.base import BaseParser

PY_LANGUAGE = Language(tspython.language())


def _node_id(file_path: str, name: str, kind: str) -> str:
    raw = f"{file_path}::{kind}::{name}"
    return hashlib.sha1(raw.encode()).hexdigest()[:12]


def _edge_id(source_id: str, target_id: str, kind: str) -> str:
    raw = f"{source_id}->{target_id}::{kind}"
    return hashlib.sha1(raw.encode()).hexdigest()[:12]


class PythonParser(BaseParser):
    """Parse Python source files using tree-sitter."""

    def __init__(self) -> None:
        self._parser = Parser(PY_LANGUAGE)

    def parse(self, path: Path) -> ParseResult:
        """Parse all .py files under path."""
        nodes: list[Node] = []
        edges: list[Edge] = []

        py_files = sorted(path.rglob("*.py"))
        for file_path in py_files:
            file_nodes, file_edges = self._parse_file(file_path, path)
            nodes.extend(file_nodes)
            edges.extend(file_edges)

        # Resolve import edges: match import names to module nodes
        module_map = {n.name: n.id for n in nodes if n.kind == NodeKind.MODULE}
        resolved_edges: list[Edge] = []
        for edge in edges:
            if edge.kind == EdgeKind.IMPORT and edge.target_id.startswith("unresolved:"):
                target_name = edge.target_id.removeprefix("unresolved:")
                # Try direct match, then dotted prefix match
                target_id = module_map.get(target_name)
                if target_id is None:
                    # Try matching first component
                    parts = target_name.split(".")
                    for i in range(len(parts), 0, -1):
                        candidate = ".".join(parts[:i])
                        if candidate in module_map:
                            target_id = module_map[candidate]
                            break
                if target_id:
                    resolved_edges.append(
                        Edge(
                            id=edge.id,
                            source_id=edge.source_id,
                            target_id=target_id,
                            kind=edge.kind,
                        )
                    )
            else:
                resolved_edges.append(edge)

        return ParseResult(
            nodes=nodes, edges=resolved_edges, root_path=str(path), lang="python"
        )

    def _parse_file(
        self, file_path: Path, root: Path
    ) -> tuple[list[Node], list[Edge]]:
        source = file_path.read_bytes()
        tree = self._parser.parse(source)

        rel = file_path.relative_to(root)
        module_name = str(rel.with_suffix("")).replace("/", ".")
        file_str = str(rel)

        nodes: list[Node] = []
        edges: list[Edge] = []

        # Module node
        mod_id = _node_id(file_str, module_name, "module")
        nodes.append(
            Node(
                id=mod_id,
                name=module_name,
                kind=NodeKind.MODULE,
                file_path=file_str,
                line_start=1,
                line_end=source.count(b"\n") + 1,
                module=module_name,
            )
        )

        self._walk(tree.root_node, source, file_str, module_name, mod_id, nodes, edges)
        return nodes, edges

    def _walk(
        self,
        node: object,
        source: bytes,
        file_str: str,
        module_name: str,
        mod_id: str,
        nodes: list[Node],
        edges: list[Edge],
    ) -> None:
        for child in node.children:  # type: ignore[attr-defined]
            if child.type == "class_definition":
                self._extract_class(child, source, file_str, module_name, mod_id, nodes, edges)
            elif child.type == "function_definition":
                self._extract_function(child, source, file_str, module_name, mod_id, nodes, edges)
            elif child.type in ("import_statement", "import_from_statement"):
                self._extract_import(child, source, mod_id, edges)

    def _extract_class(
        self,
        node: object,
        source: bytes,
        file_str: str,
        module_name: str,
        mod_id: str,
        nodes: list[Node],
        edges: list[Edge],
    ) -> None:
        name_node = node.child_by_field_name("name")  # type: ignore[attr-defined]
        if not name_node:
            return
        name = source[name_node.start_byte : name_node.end_byte].decode()
        cls_id = _node_id(file_str, name, "class")
        nodes.append(
            Node(
                id=cls_id,
                name=name,
                kind=NodeKind.CLASS,
                file_path=file_str,
                line_start=node.start_point[0] + 1,  # type: ignore[attr-defined]
                line_end=node.end_point[0] + 1,  # type: ignore[attr-defined]
                module=module_name,
            )
        )

        # Extract methods inside class
        body = node.child_by_field_name("body")  # type: ignore[attr-defined]
        if body:
            for child in body.children:  # type: ignore[attr-defined]
                if child.type == "function_definition":
                    self._extract_function(
                        child, source, file_str, module_name, mod_id, nodes, edges
                    )

        # Superclass edges
        superclasses = node.child_by_field_name("superclasses")  # type: ignore[attr-defined]
        if superclasses:
            for arg in superclasses.children:  # type: ignore[attr-defined]
                if arg.type == "identifier":
                    base_name = source[arg.start_byte : arg.end_byte].decode()
                    edges.append(
                        Edge(
                            id=_edge_id(cls_id, base_name, "inherit"),
                            source_id=cls_id,
                            target_id=f"unresolved:{base_name}",
                            kind=EdgeKind.INHERIT,
                        )
                    )

    def _extract_function(
        self,
        node: object,
        source: bytes,
        file_str: str,
        module_name: str,
        mod_id: str,
        nodes: list[Node],
        edges: list[Edge],
    ) -> None:
        name_node = node.child_by_field_name("name")  # type: ignore[attr-defined]
        if not name_node:
            return
        name = source[name_node.start_byte : name_node.end_byte].decode()
        func_id = _node_id(file_str, name, "function")
        nodes.append(
            Node(
                id=func_id,
                name=name,
                kind=NodeKind.FUNCTION,
                file_path=file_str,
                line_start=node.start_point[0] + 1,  # type: ignore[attr-defined]
                line_end=node.end_point[0] + 1,  # type: ignore[attr-defined]
                module=module_name,
                metadata={"lines": node.end_point[0] - node.start_point[0] + 1},  # type: ignore[attr-defined]
            )
        )

    def _extract_import(
        self,
        node: object,
        source: bytes,
        mod_id: str,
        edges: list[Edge],
    ) -> None:
        text = source[node.start_byte : node.end_byte].decode()  # type: ignore[attr-defined]
        # Simple extraction: get the module name from import
        if node.type == "import_from_statement":  # type: ignore[attr-defined]
            module_node = node.child_by_field_name("module_name")  # type: ignore[attr-defined]
            if module_node:
                mod_name = source[module_node.start_byte : module_node.end_byte].decode()
                edges.append(
                    Edge(
                        id=_edge_id(mod_id, mod_name, "import"),
                        source_id=mod_id,
                        target_id=f"unresolved:{mod_name}",
                        kind=EdgeKind.IMPORT,
                    )
                )
        elif node.type == "import_statement":  # type: ignore[attr-defined]
            for child in node.children:  # type: ignore[attr-defined]
                if child.type == "dotted_name":
                    mod_name = source[child.start_byte : child.end_byte].decode()
                    edges.append(
                        Edge(
                            id=_edge_id(mod_id, mod_name, "import"),
                            source_id=mod_id,
                            target_id=f"unresolved:{mod_name}",
                            kind=EdgeKind.IMPORT,
                        )
                    )
