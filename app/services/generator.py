from __future__ import annotations

from app.models.schemas import GeneratedAnswer, RetrievalResult


class AnswerGenerator:
    def generate(self, *, query: str, retrieval: RetrievalResult) -> GeneratedAnswer:
        if not retrieval.retrieved:
            return GeneratedAnswer(
                answer=(
                    "I do not have enough authorized evidence to answer this reliably. "
                    "A human review or broader approved retrieval scope is required."
                ),
                citations=[],
                notes=["no_authorized_context"],
            )

        top = retrieval.retrieved[:3]
        bullets: list[str] = []
        citations: list[str] = []
        for chunk in top:
            bullets.append(f"- {chunk.title}: {chunk.excerpt[:110]}...")
            citations.append(chunk.doc_id)

        answer = (
            f"Request summary: {query}\n\n"
            "Supported evidence:\n"
            + "\n".join(bullets)
            + "\n\n"
            + "Proposed response: Based on the authorized retrieved context above, this answer is limited to the cited evidence. "
            + "Any action outside those sources should be reviewed before release."
        )
        return GeneratedAnswer(answer=answer, citations=citations, notes=[f"retrieval_quality:{retrieval.quality}"])
