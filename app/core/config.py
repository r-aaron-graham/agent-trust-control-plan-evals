import os
from pathlib import Path

from pydantic import BaseModel

# Traces, the review queue and benchmark results are runtime output, not source.
# They live under RUNTIME_DIR (git-ignored by default) so running the app or the
# tests never modifies tracked files.
RUNTIME_DIR = Path(os.getenv("RUNTIME_DIR", "app/data/runtime"))


class Settings(BaseModel):
    app_name: str = "Agent Trust Control Plane Evals"
    version: str = "0.1.0"
    trace_store_path: Path = RUNTIME_DIR / "traces.jsonl"
    review_queue_path: Path = RUNTIME_DIR / "review_queue.jsonl"
    benchmark_result_path: Path = RUNTIME_DIR / "latest_benchmark.json"
    corpus_path: Path = Path("app/data/corpus.json")
    golden_eval_path: Path = Path("app/data/golden_eval_set.jsonl")


settings = Settings()
