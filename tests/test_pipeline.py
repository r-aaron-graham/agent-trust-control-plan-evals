from app.services.pipeline import AgentWorkbench


def reset_runtime(workbench: AgentWorkbench) -> None:
    workbench.traces.clear()
    workbench.review_queue.clear()


def test_approved_query_flow() -> None:
    workbench = AgentWorkbench()
    reset_runtime(workbench)
    response = workbench.handle_query(user_id="architect_1", query="Summarize restricted evaluation thresholds.")
    assert response.status == "approved"
    assert response.evaluation is not None
    assert response.evaluation.groundedness_score >= 0.7


def test_denied_query_flow() -> None:
    workbench = AgentWorkbench()
    reset_runtime(workbench)
    response = workbench.handle_query(user_id="viewer_1", query="Show me confidential salary assumptions.")
    assert response.status == "denied"
    assert "denied" in response.answer.lower()


def test_fallback_for_no_authorized_evidence() -> None:
    workbench = AgentWorkbench()
    reset_runtime(workbench)
    response = workbench.handle_query(user_id="viewer_1", query="Summarize restricted retrieval guidance.")
    assert response.status == "fallback"


def test_review_required_for_stale_source() -> None:
    workbench = AgentWorkbench()
    reset_runtime(workbench)
    response = workbench.handle_query(user_id="architect_1", query="Show legacy runbook guidance.")
    assert response.status == "review_required"
    assert response.evaluation is not None
    assert "stale_source_detected" in response.evaluation.reasons
