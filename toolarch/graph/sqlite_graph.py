"""SQLite-backed graph storage."""

from __future__ import annotations

import json
import sqlite3
from importlib.resources import files
from pathlib import Path

from toolarch.graph.adapter import GraphAdapter
from toolarch.models import Edge, EdgeKind, Node, NodeKind, ParseResult, RunSummary


class SQLiteGraph(GraphAdapter):
    """In-memory SQLite graph (optionally persisted to disk)."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        if db_path:
            self._conn = sqlite3.connect(str(db_path))
        else:
            self._conn = sqlite3.connect(":memory:")
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        schema_path = files("toolarch.graph").joinpath("schema.sql")
        schema = schema_path.read_text()
        self._conn.executescript(schema)

    def load(self, parse_result: ParseResult) -> None:
        """Load parsed nodes and edges into SQLite."""
        cur = self._conn.cursor()
        for node in parse_result.nodes:
            cur.execute(
                "INSERT OR REPLACE INTO nodes (id, name, kind, file_path, line_start, line_end, module, metadata) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    node.id,
                    node.name,
                    node.kind.value,
                    node.file_path,
                    node.line_start,
                    node.line_end,
                    node.module,
                    json.dumps(node.metadata),
                ),
            )
        for edge in parse_result.edges:
            cur.execute(
                "INSERT OR REPLACE INTO edges (id, source_id, target_id, kind, weight) "
                "VALUES (?, ?, ?, ?, ?)",
                (edge.id, edge.source_id, edge.target_id, edge.kind.value, edge.weight),
            )
        self._conn.commit()

    def get_nodes(self, kind: str | None = None) -> list[Node]:
        cur = self._conn.cursor()
        if kind:
            cur.execute("SELECT * FROM nodes WHERE kind = ?", (kind,))
        else:
            cur.execute("SELECT * FROM nodes")
        return [self._row_to_node(row) for row in cur.fetchall()]

    def get_edges(self, kind: str | None = None) -> list[Edge]:
        cur = self._conn.cursor()
        if kind:
            cur.execute("SELECT * FROM edges WHERE kind = ?", (kind,))
        else:
            cur.execute("SELECT * FROM edges")
        return [self._row_to_edge(row) for row in cur.fetchall()]

    def get_dependents(self, node_id: str) -> list[Edge]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM edges WHERE target_id = ?", (node_id,))
        return [self._row_to_edge(row) for row in cur.fetchall()]

    def get_dependencies(self, node_id: str) -> list[Edge]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM edges WHERE source_id = ?", (node_id,))
        return [self._row_to_edge(row) for row in cur.fetchall()]

    def save_run(self, summary: RunSummary) -> None:
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO runs (root_path, lang, summary_json) VALUES (?, ?, ?)",
            (summary.root_path, summary.lang, summary.model_dump_json()),
        )
        run_id = cur.lastrowid
        for result in summary.results:
            for metric in result.metrics:
                cur.execute(
                    "INSERT INTO metrics (node_id, metric_name, metric_value, run_id) VALUES (?, ?, ?, ?)",
                    (metric.node_id, metric.name, metric.value, run_id),
                )
        self._conn.commit()

    def load_last_run(self) -> RunSummary | None:
        cur = self._conn.cursor()
        cur.execute("SELECT summary_json FROM runs ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        if row is None:
            return None
        return RunSummary.model_validate_json(row[0])

    @staticmethod
    def _row_to_node(row: sqlite3.Row) -> Node:
        return Node(
            id=row["id"],
            name=row["name"],
            kind=NodeKind(row["kind"]),
            file_path=row["file_path"],
            line_start=row["line_start"],
            line_end=row["line_end"],
            module=row["module"],
            metadata=json.loads(row["metadata"]),
        )

    @staticmethod
    def _row_to_edge(row: sqlite3.Row) -> Edge:
        return Edge(
            id=row["id"],
            source_id=row["source_id"],
            target_id=row["target_id"],
            kind=EdgeKind(row["kind"]),
            weight=row["weight"],
        )
