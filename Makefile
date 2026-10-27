.PHONY: install run test benchmark lint docker docker-run

install:
	pip install -e .[dev]

run:
	uvicorn app.main:app --reload

test:
	pytest -q --cov=app --cov-report=term-missing

benchmark:
	python scripts/run_benchmarks.py

lint:
	ruff check .

docker:
	docker build -t agent-trust-control-plane-evals:local .

docker-run: docker
	docker run --rm -p 8000:8000 agent-trust-control-plane-evals:local
