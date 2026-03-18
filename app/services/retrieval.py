from __future__ import annotations

import json
import re
from pathlib import Path

from app.models.schemas import Document, RetrievedChunk, RetrievalResult

TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")
MINIMUM_INCLUDE_SCORE = 0.30


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text)}


class RetrievalService:
    def __init__(self, corpus_path: Path) -> None:
        with corpus_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        self.documents = [Document.model_validate(item) for item in data]

    def search(self, query: str, allowed_classifications: list[str], top_k: int = 5) -> RetrievalResult:
        query_terms = tokenize(query)
        scored: list[tuple[float, Document]] = []
        filtered_out: list[RetrievedChunk] = []
        matched_any = False

        for doc in self.documents:
            doc_terms = tokenize(doc.title + " " + doc.body + " " + " ".join(doc.tags))
            overlap = len(query_terms & doc_terms)
            if overlap == 0:
                continue
            matched_any = True
            score = min(1.0, overlap / max(3, len(query_terms)))
            if doc.stale:
                score *= 0.7
            excerpt = doc.body[:180].replace("\n", " ")
            if score < MINIMUM_INCLUDE_SCORE:
                continue
            chunk = RetrievedChunk(
                doc_id=doc.doc_id,
                title=doc.title,
                excerpt=excerpt,
                classification=doc.classification,
                score=round(score, 2),
                included=doc.classification in allowed_classifications,
                reason="matched" if doc.classification in allowed_classifications else "filtered_by_classification",
                stale=doc.stale,
            )
            if doc.classification in allowed_classifications:
                scored.append((score, doc))
            else:
                filtered_out.append(chunk)

        scored.sort(key=lambda pair: pair[0], reverse=True)
        retrieved = [
            RetrievedChunk(
                doc_id=doc.doc_id,
                title=doc.title,
                excerpt=doc.body[:180].replace("\n", " "),
                classification=doc.classification,
                score=round(score, 2),
                included=True,
                reason="matched",
                stale=doc.stale,
            )
            for score, doc in scored[:top_k]
        ]

        if not matched_any or not retrieved:
            quality = "none"
        else:
            avg = sum(item.score for item in retrieved) / len(retrieved)
            if avg >= 0.75:
                quality = "strong"
            elif avg >= 0.45:
                quality = "moderate"
            else:
                quality = "weak"

        return RetrievalResult(
            retrieved=retrieved,
            filtered_out=filtered_out,
            query_terms=sorted(query_terms),
            quality=quality,
        )
