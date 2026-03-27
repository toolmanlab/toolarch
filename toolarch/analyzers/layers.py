"""Layer compliance checker."""

from __future__ import annotations

from toolarch.analyzers.base import BaseAnalyzer
from toolarch.graph.adapter import GraphAdapter
from toolarch.models import AnalysisResult, Issue, Severity

# Default layering: higher layers can depend on lower, not vice versa.
# Index 0 = highest layer (api), index N = lowest (model).
DEFAULT_LAYERS: list[list[str]] = [
    ["api", "controller", "handler", "view", "route"],
    ["service", "usecase", "interactor"],
    ["repository", "repo", "dao", "store", "gateway"],
    ["model", "entity", "domain", "schema"],
]


class LayerAnalyzer(BaseAnalyzer):
    """Check that module dependencies respect the defined layer ordering."""

    def __init__(self, layers: list[list[str]] | None = None) -> None:
        self._layers = layers or DEFAULT_LAYERS

    @property
    def name(self) -> str:
        return "layers"

    def analyze(self, graph: GraphAdapter) -> AnalysisResult:
        modules = graph.get_nodes(kind="module")
        import_edges = graph.get_edges(kind="import")

        # Map module_id -> layer index (lower = higher in stack)
        id_to_name = {m.id: m.name for m in modules}
        id_to_layer: dict[str, int] = {}
        for m in modules:
            layer_idx = self._classify(m.name)
            if layer_idx is not None:
                id_to_layer[m.id] = layer_idx

        module_ids = {m.id for m in modules}
        issues: list[Issue] = []

        for edge in import_edges:
            if edge.source_id not in id_to_layer or edge.target_id not in id_to_layer:
                continue
            src_layer = id_to_layer[edge.source_id]
            tgt_layer = id_to_layer[edge.target_id]
            # Violation: lower layer depends on higher layer
            if src_layer > tgt_layer:
                src_name = id_to_name.get(edge.source_id, edge.source_id)
                tgt_name = id_to_name.get(edge.target_id, edge.target_id)
                issues.append(
                    Issue(
                        rule="layer-violation",
                        message=(
                            f"Layer violation: '{src_name}' (layer {src_layer}) "
                            f"depends on '{tgt_name}' (layer {tgt_layer})"
                        ),
                        severity=Severity.HIGH,
                        details={
                            "source": src_name,
                            "target": tgt_name,
                            "source_layer": src_layer,
                            "target_layer": tgt_layer,
                        },
                    )
                )

        summary = f"Checked {len(import_edges)} imports, found {len(issues)} layer violation(s)."
        return AnalysisResult(analyzer=self.name, issues=issues, summary=summary)

    def _classify(self, module_name: str) -> int | None:
        """Return the layer index for a module name, or None if unclassified."""
        parts = module_name.lower().split(".")
        for idx, keywords in enumerate(self._layers):
            for part in parts:
                if part in keywords:
                    return idx
        return None
