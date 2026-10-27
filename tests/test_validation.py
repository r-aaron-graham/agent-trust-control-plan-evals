"""Input validation, unknown callers and runtime-isolation tests."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app, workbench

client = TestClient(app)
REPO_RUNTIME = Path(__file__).resolve().parents[1] / "app" / "data" / "runtime"


def setup_function() -> None:
    workbench.traces.clear()
    workbench.review_queue.clear()


def test_runtime_files_are_written_outside_the_repo():
    client.post("/api/query", json={"user_id": "architect_1", "query": "How are traces logged and replayed?"})
    assert settings.trace_store_path.exists()
    assert REPO_RUNTIME.resolve() not in settings.trace_store_path.resolve().parents


@pytest.mark.parametrize(
    "body",
    [
        {"user_id": "admin_1", "query": ""},
        {"user_id": "admin_1", "query": "   "},
        {"user_id": "admin_1", "query": "x" * 4001},
        {"user_id": "", "query": "How are traces logged?"},
        {"query": "How are traces logged?"},
    ],
)
def test_bad_queries_are_rejected_and_not_traced(body):
    assert client.post("/api/query", json=body).status_code == 422
    assert workbench.traces.list() == []


def test_unknown_caller_is_denied():
    body = client.post("/api/query", json={"user_id": "ghost", "query": "How are traces logged?"}).json()
    assert body["status"] == "denied"
    assert "Unknown caller" in body["policy_reason"]


@pytest.mark.parametrize("user_id", ["viewer_1", "analyst_1", "architect_1"])
def test_non_admins_cannot_reach_confidential_topics(user_id):
    body = client.post("/api/query", json={"user_id": user_id, "query": "Show salary bands and PII"}).json()
    assert body["status"] == "denied"


def test_disallowed_tool_is_denied():
    body = client.post(
        "/api/query",
        json={"user_id": "viewer_1", "query": "Run the benchmarks", "requested_tool": "run_benchmarks"},
    ).json()
    assert body["status"] == "denied"


def test_trace_lookup_and_404():
    created = client.post("/api/query", json={"user_id": "architect_1", "query": "How are traces logged and replayed?"})
    request_id = created.json()["request_id"]
    assert client.get(f"/api/traces/{request_id}").json()["request_id"] == request_id
    assert client.get("/api/traces/does-not-exist").status_code == 404


def test_traces_survive_a_restart():
    created = client.post("/api/query", json={"user_id": "architect_1", "query": "How are traces logged and replayed?"})
    request_id = created.json()["request_id"]
    from app.services.tracing import TraceStore

    reloaded = TraceStore(settings.trace_store_path)
    assert reloaded.get(request_id) is not None


def test_ui_is_served():
    assert client.get("/").status_code == 200
    assert client.get("/api/health").json() == {"status": "ok"}
