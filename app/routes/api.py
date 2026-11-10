from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import settings
from app.models.schemas import QueryRequest
from app.services.pipeline import AgentWorkbench

router = APIRouter()


def get_workbench() -> AgentWorkbench:
    from app.main import workbench

    return workbench


WorkbenchDependency = Annotated[AgentWorkbench, Depends(get_workbench)]


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/users")
def list_users(workbench: WorkbenchDependency) -> list[dict]:
    return [user.model_dump() for user in workbench.identity.list_users()]


@router.post("/query")
def query(payload: QueryRequest, workbench: WorkbenchDependency) -> dict:
    return workbench.handle_query(
        user_id=payload.user_id,
        query=payload.query,
        requested_tool=payload.requested_tool,
    ).model_dump()


@router.get("/traces")
def list_traces(workbench: WorkbenchDependency) -> list[dict]:
    return [trace.model_dump(mode="json") for trace in workbench.traces.list()]


@router.get("/traces/{request_id}")
def get_trace(request_id: str, workbench: WorkbenchDependency) -> dict:
    trace = workbench.traces.get(request_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace.model_dump(mode="json")


@router.get("/review-queue")
def review_queue(workbench: WorkbenchDependency) -> list[dict]:
    return [item.model_dump(mode="json") for item in workbench.review_queue.list()]


@router.get("/metrics")
def metrics(workbench: WorkbenchDependency) -> dict:
    return workbench.metrics.summarize(workbench.traces.list())


@router.post("/benchmarks/run")
def run_benchmarks(workbench: WorkbenchDependency) -> dict:
    return workbench.run_benchmarks().model_dump()


@router.get("/benchmarks/latest")
def latest_benchmark() -> dict:
    if not settings.benchmark_result_path.exists():
        raise HTTPException(status_code=404, detail="No benchmark run has been recorded yet")
    return json.loads(settings.benchmark_result_path.read_text(encoding="utf-8"))
