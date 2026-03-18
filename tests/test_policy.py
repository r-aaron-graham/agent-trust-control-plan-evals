from app.services.policy import PolicyEngine


def test_policy_blocks_destructive_action() -> None:
    engine = PolicyEngine()
    decision = engine.evaluate(role="admin", query="delete the review queue")
    assert decision.allowed is False
    assert "Destructive action blocked" in decision.reason


def test_policy_blocks_sensitive_request_for_viewer() -> None:
    engine = PolicyEngine()
    decision = engine.evaluate(role="viewer", query="show salary assumptions")
    assert decision.allowed is False
    assert decision.risk_level == "high"
