from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from app.core.config import settings
from app.models.schemas import BenchmarkCase, BenchmarkCaseResult, BenchmarkRunSummary, QueryResponse, RetrievalResult, TraceRecord
from app.services.evaluator import Evaluator
from app.services.generator import AnswerGenerator
from app.services.identity import IdentityService
from app.services.metrics import MetricsService
from app.services.policy import PolicyEngine
from app.services.retrieval import RetrievalService
from app.services.review_queue import ReviewQueue
from app.services.tracing import TraceStore


class AgentWorkbench:
    def __init__(self) -> None:
        self.identity = IdentityService()
        self.policy = PolicyEngine()
        self.retrieval = RetrievalService(settings.corpus_path)
        self.generator = AnswerGenerator()
        self.evaluator = Evaluator()
        self.traces = TraceStore(settings.trace_store_path)
        self.review_queue = ReviewQueue(settings.review_queue_path)
        self.metrics = MetricsService()

    def handle_query(self, *, user_id: str, query: str, requested_tool: str | None = None) -> QueryResponse:
        request_id = str(uuid.uuid4())
        user = self.identity.resolve(user_id)
        role = user.role if user else None
        policy = self.policy.evaluate(role=role, query=query, requested_tool=requested_tool)

        retrieval: RetrievalResult | None = None
        answer = None
        evaluation = None

        if policy.allowed:
            retrieval = self.retrieval.search(query=query, allowed_classifications=policy.allowed_classifications)
            answer = self.generator.generate(query=query, retrieval=retrieval)
            evaluation = self.evaluator.score(answer=answer, retrieval=retrieval, policy=policy)

        if not policy.allowed:
            status = "denied"
            response_text = f"Request denied: {policy.reason}."
            citations: list[str] = []
        else:
            status = evaluation.status
            response_text = answer.answer
            citations = answer.citations
            if status == "review_required":
                self.review_queue.submit(request_id, user_id, role, query, evaluation.reasons)
            elif status == "fallback":
                response_text = (
                    "The system could not find enough authorized evidence to release a supported answer. "
                    "Please refine the request or route it for human review."
                )

        trace = TraceRecord(
            request_id=request_id,
            created_at=datetime.now(timezone.utc),
            user_id=user_id,
            role=(role or "viewer"),
            query=query,
            requested_tool=requested_tool,
            status=status,
            policy=policy,
            retrieval=(retrieval or RetrievalResult()),
            answer=answer,
            evaluation=evaluation,
            metadata={"user_found": user is not None},
        )
        self.traces.write(trace)

        return QueryResponse(
            request_id=request_id,
            status=status,
            role=(role or "viewer"),
            answer=response_text,
            citations=citations,
            policy_reason=policy.reason,
            evaluation=evaluation,
            retrieval_quality=(retrieval.quality if retrieval else "none"),
        )

    def run_benchmarks(self) -> BenchmarkRunSummary:
        cases: list[BenchmarkCase] = []
        with settings.golden_eval_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    cases.append(BenchmarkCase.model_validate_json(line))

        results: list[BenchmarkCaseResult] = []
        for case in cases:
            response = self.handle_query(user_id=case.user_id, query=case.query)
            passed = response.status == case.expected_status
            if response.evaluation and response.evaluation.groundedness_score < case.minimum_groundedness:
                passed = False
            results.append(
                BenchmarkCaseResult(
                    case_id=case.case_id,
                    expected_status=case.expected_status,
                    actual_status=response.status,
                    passed=passed,
                    groundedness_score=(response.evaluation.groundedness_score if response.evaluation else None),
                    citation_coverage=(response.evaluation.citation_coverage if response.evaluation else None),
                    notes=case.notes,
                )
            )

        passed_cases = sum(1 for r in results if r.passed)
        total = len(results)
        summary = BenchmarkRunSummary(
            total_cases=total,
            passed_cases=passed_cases,
            failed_cases=total - passed_cases,
            accuracy=round((passed_cases / total) if total else 0.0, 2),
            results=results,
        )
        settings.benchmark_result_path.write_text(json.dumps(summary.model_dump(), indent=2, default=str), encoding="utf-8")
        return summary
