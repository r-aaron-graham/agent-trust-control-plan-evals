from app.services.pipeline import AgentWorkbench


def test_benchmark_run_has_good_accuracy() -> None:
    workbench = AgentWorkbench()
    workbench.traces.clear()
    workbench.review_queue.clear()
    summary = workbench.run_benchmarks()
    assert summary.total_cases == 30
    assert summary.accuracy >= 0.75
