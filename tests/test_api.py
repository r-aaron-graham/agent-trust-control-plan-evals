from fastapi.testclient import TestClient
from app.main import app, workbench

client = TestClient(app)


def setup_function() -> None:
    workbench.traces.clear()
    workbench.review_queue.clear()


def test_query_endpoint() -> None:
    response = client.post(
        "/api/query",
        json={"user_id": "architect_1", "query": "How are traces logged and replayed?"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "approved"


def test_metrics_endpoint() -> None:
    client.post("/api/query", json={"user_id": "viewer_1", "query": "What does this workbench do?"})
    response = client.get("/api/metrics")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_requests"] >= 1
