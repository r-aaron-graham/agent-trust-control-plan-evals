# Architecture

This repository extends the argument from **RAG Is Not Enough** by making runtime evaluation concrete.

## Request lifecycle

1. Resolve caller identity and role.
2. Evaluate policy for role, requested tool, and risk indicators.
3. Retrieve only from authorized classifications.
4. Generate a bounded answer from the retrieved evidence.
5. Score groundedness, citation coverage, and confidence.
6. Release, fallback, deny, or route to human review.
7. Persist the full trace for inspection and benchmark replay.

## Why this matters

The project is intentionally simple, but it demonstrates the minimum runtime discipline that many agent demos skip:

- authorization before retrieval
- evaluation before release
- explicit fallback and refusal paths
- replayable traces and benchmark cases
- human review rather than silent failure
