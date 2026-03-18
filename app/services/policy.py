from __future__ import annotations

from app.models.schemas import PolicyDecision, Role

ROLE_CLASSIFICATIONS = {
    "viewer": ["public"],
    "analyst": ["public", "internal"],
    "architect": ["public", "internal", "restricted"],
    "admin": ["public", "internal", "restricted", "confidential"],
}

ROLE_TOOLS = {
    "viewer": ["search_docs"],
    "analyst": ["search_docs", "get_metadata"],
    "architect": ["search_docs", "get_metadata", "view_traces"],
    "admin": ["search_docs", "get_metadata", "view_traces", "run_benchmarks", "manage_review_queue"],
}

DESTRUCTIVE_PATTERNS = ["delete", "drop table", "wipe", "remove user", "shutdown cluster"]
HIGH_RISK_PATTERNS = ["salary", "pii", "social security", "credential", "override policy", "confidential"]
REVIEW_QUEUE_RESTRICTED_PATTERNS = ["view the review queue", "show the review queue", "manage review queue"]


class PolicyEngine:
    def evaluate(self, *, role: Role | None, query: str, requested_tool: str | None = None) -> PolicyDecision:
        lowered = query.lower()
        if role is None:
            return PolicyDecision(
                allowed=False,
                reason="Unknown caller",
                allowed_tools=[],
                allowed_classifications=[],
                risk_level="high",
            )

        if any(pattern in lowered for pattern in DESTRUCTIVE_PATTERNS):
            return PolicyDecision(
                allowed=False,
                reason="Destructive action blocked by policy",
                allowed_tools=[],
                allowed_classifications=ROLE_CLASSIFICATIONS[role],
                risk_level="high",
            )

        allowed_tools = ROLE_TOOLS[role]
        if requested_tool and requested_tool not in allowed_tools:
            return PolicyDecision(
                allowed=False,
                reason=f"Tool '{requested_tool}' is not permitted for role '{role}'",
                allowed_tools=allowed_tools,
                allowed_classifications=ROLE_CLASSIFICATIONS[role],
                risk_level="medium",
            )

        risk_level = "high" if any(pattern in lowered for pattern in HIGH_RISK_PATTERNS) else "low"
        if role in {"viewer", "analyst", "architect"} and risk_level == "high":
            return PolicyDecision(
                allowed=False,
                reason="Sensitive or confidential request exceeds caller scope",
                allowed_tools=allowed_tools,
                allowed_classifications=ROLE_CLASSIFICATIONS[role],
                risk_level="high",
            )

        if any(pattern in lowered for pattern in REVIEW_QUEUE_RESTRICTED_PATTERNS) and role != "admin":
            return PolicyDecision(
                allowed=False,
                reason="Review queue visibility is restricted to admins",
                allowed_tools=allowed_tools,
                allowed_classifications=ROLE_CLASSIFICATIONS[role],
                risk_level="medium",
            )

        if "benchmark" in lowered and role != "admin":
            return PolicyDecision(
                allowed=False,
                reason="Benchmark operations are restricted to admins",
                allowed_tools=allowed_tools,
                allowed_classifications=ROLE_CLASSIFICATIONS[role],
                risk_level="medium",
            )

        return PolicyDecision(
            allowed=True,
            reason="Approved",
            allowed_tools=allowed_tools,
            allowed_classifications=ROLE_CLASSIFICATIONS[role],
            risk_level=risk_level,
        )
