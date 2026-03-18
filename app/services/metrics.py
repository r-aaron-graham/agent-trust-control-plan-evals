from __future__ import annotations

from app.models.schemas import TraceRecord


class MetricsService:
    def summarize(self, traces: list[TraceRecord]) -> dict:
        if not traces:
            return {
                "total_requests": 0,
                "approved": 0,
                "denied": 0,
                "review_required": 0,
                "fallback": 0,
                "review_rate": 0.0,
                "fallback_rate": 0.0,
                "average_groundedness": 0.0,
                "average_citation_coverage": 0.0,
            }

        approved = sum(1 for t in traces if t.status == "approved")
        denied = sum(1 for t in traces if t.status == "denied")
        review_required = sum(1 for t in traces if t.status == "review_required")
        fallback = sum(1 for t in traces if t.status == "fallback")
        evals = [t.evaluation for t in traces if t.evaluation is not None]
        avg_groundedness = round(sum(e.groundedness_score for e in evals) / len(evals), 2) if evals else 0.0
        avg_citation = round(sum(e.citation_coverage for e in evals) / len(evals), 2) if evals else 0.0
        total = len(traces)
        return {
            "total_requests": total,
            "approved": approved,
            "denied": denied,
            "review_required": review_required,
            "fallback": fallback,
            "review_rate": round(review_required / total, 2),
            "fallback_rate": round(fallback / total, 2),
            "average_groundedness": avg_groundedness,
            "average_citation_coverage": avg_citation,
        }
