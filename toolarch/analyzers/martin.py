"""Robert C. Martin's package metrics: Abstractness, Instability, Distance."""

from __future__ import annotations

from toolarch.analyzers.base import BaseAnalyzer
from toolarch.graph.adapter import GraphAdapter
from toolarch.models import AnalysisResult, Issue, Metric, NodeKind, Severity


class MartinAnalyzer(BaseAnalyzer):
    """Compute Martin metrics per module."""

    DISTANCE_THRESHOLD = 0.7  # Flag modules far from the main sequence

    @property
    def name(self) -> str:
        return "martin"

    def analyze(self, graph: GraphAdapter) -> AnalysisResult:
        modules = graph.get_nodes(kind="module")
        all_nodes = graph.get_nodes()
        import_edges = graph.get_edges(kind="import")

        module_ids = {m.id for m in modules}

        # Count classes per module (total and abstract)
        classes_by_module: dict[str, list[str]] = {m.id: [] for m in modules}
        abstract_by_module: dict[str, int] = {m.id: 0 for m in modules}
        for node in all_nodes:
            if node.kind == NodeKind.CLASS:
                mod_id = self._find_module(node.module, modules)
                if mod_id:
                    classes_by_module[mod_id].append(node.id)
                    # Heuristic: class with "Abstract" or "Base" prefix, or ABC in name
                    if any(
                        kw in node.name for kw in ("Abstract", "Base", "ABC", "Interface")
                    ):
                        abstract_by_module[mod_id] = abstract_by_module.get(mod_id, 0) + 1

        # Afferent (Ca) and efferent (Ce) couplings per module
        ca: dict[str, int] = {m.id: 0 for m in modules}
        ce: dict[str, int] = {m.id: 0 for m in modules}
        for edge in import_edges:
            if edge.source_id in module_ids:
                ce[edge.source_id] = ce.get(edge.source_id, 0) + 1
            if edge.target_id in module_ids:
                ca[edge.target_id] = ca.get(edge.target_id, 0) + 1

        metrics: list[Metric] = []
        issues: list[Issue] = []

        for mod in modules:
            total_classes = len(classes_by_module[mod.id])
            abstract_classes = abstract_by_module.get(mod.id, 0)

            # Abstractness: A = abstract / total (0 if no classes)
            a = abstract_classes / total_classes if total_classes > 0 else 0.0

            # Instability: I = Ce / (Ca + Ce) (0 if no couplings)
            ca_val = ca.get(mod.id, 0)
            ce_val = ce.get(mod.id, 0)
            total_coupling = ca_val + ce_val
            instability = ce_val / total_coupling if total_coupling > 0 else 0.0

            # Distance from main sequence: D = |A + I - 1|
            distance = abs(a + instability - 1)

            metrics.extend(
                [
                    Metric(node_id=mod.id, name="abstractness", value=round(a, 3)),
                    Metric(node_id=mod.id, name="instability", value=round(instability, 3)),
                    Metric(
                        node_id=mod.id,
                        name="distance",
                        value=round(distance, 3),
                        details={
                            "ca": ca_val,
                            "ce": ce_val,
                            "abstract_classes": abstract_classes,
                            "total_classes": total_classes,
                        },
                    ),
                ]
            )

            if distance > self.DISTANCE_THRESHOLD:
                issues.append(
                    Issue(
                        rule="martin-distance",
                        message=(
                            f"Module '{mod.name}' is far from the main sequence "
                            f"(D={distance:.2f}, A={a:.2f}, I={instability:.2f})"
                        ),
                        severity=Severity.MEDIUM,
                        location=mod.file_path,
                        details={"distance": distance, "abstractness": a, "instability": instability},
                    )
                )

        summary = f"Computed Martin metrics for {len(modules)} modules."
        return AnalysisResult(analyzer=self.name, issues=issues, metrics=metrics, summary=summary)

    @staticmethod
    def _find_module(module_name: str, modules: list) -> str | None:
        for m in modules:
            if m.name == module_name:
                return m.id
        return None
