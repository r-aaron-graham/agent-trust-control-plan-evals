from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field

Role = Literal["viewer", "analyst", "architect", "admin"]
Classification = Literal["public", "internal", "restricted", "confidential"]
Status = Literal["approved", "denied", "review_required", "fallback"]


class Document(BaseModel):
    doc_id: str
    title: str
    body: str
    classification: Classification
    tags: list[str] = Field(default_factory=list)
    stale: bool = False
    owner_roles: list[Role] = Field(default_factory=list)


class UserContext(BaseModel):
    user_id: str
    role: Role
    display_name: str
    team: str


class PolicyDecision(BaseModel):
    allowed: bool
    reason: str
    allowed_tools: list[str] = Field(default_factory=list)
    allowed_classifications: list[Classification] = Field(default_factory=list)
    risk_level: Literal["low", "medium", "high"] = "low"


class RetrievedChunk(BaseModel):
    doc_id: str
    title: str
    excerpt: str
    classification: Classification
    score: float
    included: bool = True
    reason: str = "matched"
    stale: bool = False


class RetrievalResult(BaseModel):
    retrieved: list[RetrievedChunk] = Field(default_factory=list)
    filtered_out: list[RetrievedChunk] = Field(default_factory=list)
    query_terms: list[str] = Field(default_factory=list)
    quality: Literal["strong", "moderate", "weak", "none"] = "none"


class GeneratedAnswer(BaseModel):
    answer: str
    citations: list[str] = Field(default_factory=list)
    model_name: str = "rule-based-reference-generator"
    notes: list[str] = Field(default_factory=list)


class EvaluationResult(BaseModel):
    groundedness_score: float
    citation_coverage: float
    confidence: float
    risk_level: Literal["low", "medium", "high"]
    requires_review: bool
    status: Status
    reasons: list[str] = Field(default_factory=list)


class ReviewItem(BaseModel):
    request_id: str
    user_id: str
    role: Role
    query: str
    reason_codes: list[str] = Field(default_factory=list)
    created_at: datetime


class TraceRecord(BaseModel):
    request_id: str
    created_at: datetime
    user_id: str
    role: Role
    query: str
    requested_tool: str | None = None
    status: Status
    policy: PolicyDecision
    retrieval: RetrievalResult
    answer: GeneratedAnswer | None = None
    evaluation: EvaluationResult | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class QueryRequest(BaseModel):
    user_id: str
    query: str
    requested_tool: str | None = None


class QueryResponse(BaseModel):
    request_id: str
    status: Status
    role: Role
    answer: str
    citations: list[str] = Field(default_factory=list)
    policy_reason: str
    evaluation: EvaluationResult | None = None
    retrieval_quality: str


class BenchmarkCase(BaseModel):
    case_id: str
    user_id: str
    query: str
    expected_status: Status
    expected_policy_allowed: bool
    minimum_groundedness: float = 0.0
    notes: str = ""


class BenchmarkCaseResult(BaseModel):
    case_id: str
    expected_status: Status
    actual_status: Status
    passed: bool
    groundedness_score: float | None = None
    citation_coverage: float | None = None
    notes: str = ""


class BenchmarkRunSummary(BaseModel):
    total_cases: int
    passed_cases: int
    failed_cases: int
    accuracy: float
    results: list[BenchmarkCaseResult]
