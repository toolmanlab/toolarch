"""Cycle detection using Tarjan's SCC algorithm."""

from __future__ import annotations

from toolarch.analyzers.base import BaseAnalyzer
from toolarch.graph.adapter import GraphAdapter
from toolarch.models import AnalysisResult, Issue, Severity


class CycleAnalyzer(BaseAnalyzer):
    """Detect circular dependencies at the module level."""

    @property
    def name(self) -> str:
        return "cycles"

    def analyze(self, graph: GraphAdapter) -> AnalysisResult:
        modules = graph.get_nodes(kind="module")
        import_edges = graph.get_edges(kind="import")

        # Build adjacency list (module_id -> set of target module_ids)
        adj: dict[str, set[str]] = {m.id: set() for m in modules}
        module_ids = set(adj.keys())
        for edge in import_edges:
            if edge.source_id in module_ids and edge.target_id in module_ids:
                adj[edge.source_id].add(edge.target_id)

        sccs = self._tarjan_scc(adj)

        # Only SCCs with > 1 node are cycles
        cycles = [scc for scc in sccs if len(scc) > 1]

        id_to_name = {m.id: m.name for m in modules}
        issues: list[Issue] = []
        for cycle in cycles:
            names = [id_to_name.get(nid, nid) for nid in cycle]
            severity = Severity.HIGH if len(cycle) > 2 else Severity.MEDIUM
            issues.append(
                Issue(
                    rule="circular-dependency",
                    message=f"Circular dependency: {' -> '.join(names)} -> {names[0]}",
                    severity=severity,
                    details={"cycle": names},
                )
            )

        summary = f"Found {len(cycles)} cycle(s) across {len(modules)} modules."
        return AnalysisResult(analyzer=self.name, issues=issues, summary=summary)

    @staticmethod
    def _tarjan_scc(adj: dict[str, set[str]]) -> list[list[str]]:
        """Tarjan's strongly connected components algorithm."""
        index_counter = [0]
        stack: list[str] = []
        on_stack: set[str] = set()
        index: dict[str, int] = {}
        lowlink: dict[str, int] = {}
        result: list[list[str]] = []

        def strongconnect(v: str) -> None:
            index[v] = index_counter[0]
            lowlink[v] = index_counter[0]
            index_counter[0] += 1
            stack.append(v)
            on_stack.add(v)

            for w in adj.get(v, set()):
                if w not in index:
                    strongconnect(w)
                    lowlink[v] = min(lowlink[v], lowlink[w])
                elif w in on_stack:
                    lowlink[v] = min(lowlink[v], index[w])

            if lowlink[v] == index[v]:
                scc: list[str] = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    scc.append(w)
                    if w == v:
                        break
                result.append(scc)

        for v in adj:
            if v not in index:
                strongconnect(v)

        return result
