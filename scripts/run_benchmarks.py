from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.services.pipeline import AgentWorkbench

if __name__ == "__main__":
    workbench = AgentWorkbench()
    summary = workbench.run_benchmarks()
    print(f"Benchmark accuracy: {summary.accuracy} ({summary.passed_cases}/{summary.total_cases})")
    for result in summary.results[:5]:
        print(f"- {result.case_id}: {result.actual_status} | passed={result.passed}")
