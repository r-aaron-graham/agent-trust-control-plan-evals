# Agent Trust Control Plane Evals

[![CI](https://github.com/r-aaron-graham/agent-trust-control-plan-evals/actions/workflows/ci.yml/badge.svg)](https://github.com/r-aaron-graham/agent-trust-control-plan-evals/actions/workflows/ci.yml)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg?logo=docker&logoColor=white)
![Golden set](https://img.shields.io/badge/golden%20set-30%2F30%20passing-brightgreen.svg)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A fully built reference repository for the follow-on article:

**How I Evaluate AI Agents in Production: Traces, Policy Tests, Retrieval Benchmarks, and Human Review**

This repository is the practical sequel to **RAG Is Not Enough: Building the Control Plane Around an AI Agent**. The first project established the argument that retrieval alone is not a control plane. This project answers the next question:

**How do you know the control plane is actually working?**

It demonstrates a runtime workbench for:

- policy-aware request handling
- authorized retrieval with diagnostics
- bounded answer generation
- groundedness and citation-coverage scoring
- release gates: approve, deny, fallback, or human review
- trace logging for replay and inspection
- golden evaluation sets and benchmark runs
- a minimal UI so a hiring manager can understand the system in under 30 seconds

---

## Core idea

This project shows how an AI agent is **tested, observed, and release-gated in runtime**, not just prompted.

---

## Repository structure

```text
agent-trust-control-plane-evals/
├── app/
│   ├── core/
│   ├── data/
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── main.py
├── docs/
│   ├── assets/
│   └── benchmark_cards/
├── frontend/
├── scripts/
├── tests/
├── .github/workflows/
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
└── README.md
```

---

## What this repository proves

### 1. Policy tests
The system resolves identity, enforces tool scope, blocks destructive requests, and refuses sensitive access outside role boundaries.

### 2. Retrieval diagnostics
Retrieval is filtered by classification before release. The trace shows what was retrieved, what was filtered, and why.

### 3. Runtime evaluation
Every answer is scored for groundedness, citation coverage, and confidence before release.

### 4. Human review
Weak retrieval, stale evidence, or high-risk requests are routed to review instead of being released blindly.

### 5. Benchmark repeatability
A golden evaluation set lets you test changes in runtime behavior and catch regressions in CI.

---

## Quickstart

### Local run

```bash
pip install -e .[dev]
uvicorn app.main:app --reload
```

Open:

- API root: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`
- Frontend: `http://127.0.0.1:8000/frontend/index.html`

### Docker

```bash
docker compose up --build
```

Runs as a non-root user with a healthcheck on `/api/health`. Traces, the review queue and benchmark results go to a named volume.

### Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `RUNTIME_DIR` | `app/data/runtime` | Where traces, the review queue and benchmark results are written. Git-ignored. |

### Run tests

```bash
pip install -e .[dev]
make lint
make test
```

Tests run against a temporary runtime directory, so they never modify files in the repo. Besides the pipeline, policy and benchmark tests, they cover input limits (empty, blank and oversized queries are rejected before anything is written to the trace log), unknown callers, role scoping for confidential topics, disallowed tools, and trace persistence across restarts.

### Run benchmarks

```bash
python scripts/run_benchmarks.py
```

---

## Example request lifecycle

```python
response = workbench.handle_query(
    user_id="architect_1",
    query="Summarize the release gate and trace logging behavior."
)
```

Example outcomes:

- `approved` for supported low-risk requests
- `denied` for destructive or unauthorized requests
- `review_required` for weak retrieval, stale evidence, or sensitive-but-allowed flows
- `fallback` when no authorized evidence exists

---

## Demo personas

- `viewer_1` → public-only access
- `analyst_1` → public + internal access
- `architect_1` → public + internal + restricted access
- `admin_1` → full scope + benchmark and review controls

---

## Benchmarks included

The golden evaluation set contains 30 cases across:

- approved low-risk queries
- unauthorized confidential requests
- destructive action attempts
- review-queue visibility checks
- stale-source retrieval
- weak retrieval / no evidence fallback

---

## Screens/assets

- `docs/assets/lifecycle.svg` — architecture visual
- live UI in `frontend/`
- trace output available through `/api/traces`
- metrics available through `/api/metrics`

---

## What this demonstrates

The point of the repository is to show runtime behavior that is measured and governed, not just described:

- a platform view of AI systems, not a single model call
- LLMOps practice: traces, golden-set benchmarks, release gating in CI
- API and systems design
- runtime governance: policy, scoped retrieval, human review
- evaluation discipline with reproducible results

---

## Next expansion ideas

- plug in a real LLM provider behind the generator interface
- add reranking and retrieval quality dashboards
- stream traces to OpenTelemetry or a warehouse
- add policy packs for multiple business domains
- publish benchmark cards to Hugging Face Datasets
