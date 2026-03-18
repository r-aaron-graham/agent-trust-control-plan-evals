.PHONY: install run test benchmark lint

install:
	pip install -e .[dev]

run:
	uvicorn app.main:app --reload

test:
	pytest -q

benchmark:
	python scripts/run_benchmarks.py

lint:
	ruff check .
