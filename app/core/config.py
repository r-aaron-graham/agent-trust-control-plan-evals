from pathlib import Path
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Agent Trust Control Plane Evals"
    version: str = "0.1.0"
    trace_store_path: Path = Path("app/data/runtime/traces.jsonl")
    review_queue_path: Path = Path("app/data/runtime/review_queue.jsonl")
    benchmark_result_path: Path = Path("app/data/runtime/latest_benchmark.json")
    corpus_path: Path = Path("app/data/corpus.json")
    golden_eval_path: Path = Path("app/data/golden_eval_set.jsonl")


settings = Settings()
