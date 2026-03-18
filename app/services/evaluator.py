from __future__ import annotations

from app.models.schemas import EvaluationResult, GeneratedAnswer, PolicyDecision, RetrievalResult


class Evaluator:
    def score(self, *, answer: GeneratedAnswer, retrieval: RetrievalResult, policy: PolicyDecision) -> EvaluationResult:
        num_retrieved = len(retrieval.retrieved)
        cited = len(answer.citations)
        max_score = max((item.score for item in retrieval.retrieved), default=0.0)
        citation_coverage = min(1.0, cited / max(1, num_retrieved))
        stale_penalty = 0.15 if any(item.stale for item in retrieval.retrieved) else 0.0
        groundedness = max(0.0, min(1.0, (0.65 * max_score) + (0.35 * citation_coverage) - stale_penalty))
        confidence = max(0.0, min(1.0, (0.55 * groundedness) + (0.45 * citation_coverage)))

        reasons: list[str] = []
        requires_review = False
        status = "approved"

        if num_retrieved == 0:
            reasons.append("no_authorized_evidence")
            status = "fallback"
        elif groundedness < 0.2:
            reasons.append("insufficient_grounding")
            status = "fallback"
        else:
            if policy.risk_level == "high":
                reasons.append("high_risk_request")
                requires_review = True
            if citation_coverage < 0.6:
                reasons.append("low_citation_coverage")
                requires_review = True
            if groundedness < 0.5:
                reasons.append("low_groundedness")
                requires_review = True
            if retrieval.quality == "weak" and groundedness < 0.6:
                reasons.append("weak_retrieval")
                requires_review = True
            if any(item.stale for item in retrieval.retrieved):
                reasons.append("stale_source_detected")
                requires_review = True

        if status not in {"fallback"} and requires_review:
            status = "review_required"

        return EvaluationResult(
            groundedness_score=round(groundedness, 2),
            citation_coverage=round(citation_coverage, 2),
            confidence=round(confidence, 2),
            risk_level=policy.risk_level,
            requires_review=requires_review,
            status=status,
            reasons=reasons,
        )
