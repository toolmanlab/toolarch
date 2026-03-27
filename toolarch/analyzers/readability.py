"""Readability analyzer: complexity, line count, doc coverage, optional LLM scoring."""

from __future__ import annotations


from toolarch.analyzers.base import BaseAnalyzer
from toolarch.graph.adapter import GraphAdapter
from toolarch.models import AnalysisResult, Issue, Metric, Severity


class ReadabilityAnalyzer(BaseAnalyzer):
    """Score function readability (0-100) based on heuristics and optional LLM."""

    MAX_FUNCTION_LINES = 50
    MAX_COMPLEXITY_SCORE = 20  # Cyclomatic complexity threshold

    @property
    def name(self) -> str:
        return "readability"

    def analyze(self, graph: GraphAdapter) -> AnalysisResult:
        functions = graph.get_nodes(kind="function")

        metrics: list[Metric] = []
        issues: list[Issue] = []

        for func in functions:
            lines = func.metadata.get("lines", 0)

            # Simple readability score (0-100)
            score = 100.0

            # Penalize long functions
            if lines > self.MAX_FUNCTION_LINES:
                penalty = min(40, (lines - self.MAX_FUNCTION_LINES) * 0.8)
                score -= penalty

            # Penalize very short names (likely unclear)
            if len(func.name) <= 2 and not func.name.startswith("_"):
                score -= 15

            # Penalize names without separators (camelCase/snake_case) when long
            if len(func.name) > 15 and "_" not in func.name and not any(
                c.isupper() for c in func.name[1:]
            ):
                score -= 10

            score = max(0, min(100, score))

            metrics.append(
                Metric(
                    node_id=func.id,
                    name="readability",
                    value=round(score, 1),
                    details={"lines": lines, "name_length": len(func.name)},
                )
            )

            if score < 50:
                issues.append(
                    Issue(
                        rule="low-readability",
                        message=f"Function '{func.name}' has low readability score ({score:.0f}/100)",
                        severity=Severity.MEDIUM if score >= 30 else Severity.HIGH,
                        location=f"{func.file_path}:{func.line_start}",
                    )
                )

        summary = f"Scored readability for {len(functions)} functions."
        return AnalysisResult(analyzer=self.name, issues=issues, metrics=metrics, summary=summary)
