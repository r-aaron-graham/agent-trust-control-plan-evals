# Benchmark card: golden evaluation set

## Purpose

A compact benchmark set for testing release gates, refusal behavior, and human review routing.

## Composition

- low-risk approved requests
- unauthorized access attempts
- high-risk sensitive requests
- weak retrieval cases
- stale-source cases
- review-queue visibility checks

## Primary metrics

- status accuracy (approved, denied, review_required, fallback)
- groundedness score
- citation coverage
- review queue rate

## Limitation

This benchmark is deterministic and rule-based. It is designed for runtime governance demonstrations, not language-model quality leaderboards.
