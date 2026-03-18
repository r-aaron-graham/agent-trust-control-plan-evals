from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.models.schemas import ReviewItem


class ReviewQueue:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._items: list[ReviewItem] = []
        if self.path.exists():
            self._load_existing()

    def _load_existing(self) -> None:
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                self._items.append(ReviewItem.model_validate_json(line))

    def submit(self, request_id: str, user_id: str, role: str, query: str, reason_codes: list[str]) -> ReviewItem:
        item = ReviewItem(
            request_id=request_id,
            user_id=user_id,
            role=role,
            query=query,
            reason_codes=reason_codes,
            created_at=datetime.now(timezone.utc),
        )
        self._items.append(item)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(item.model_dump_json())
            fh.write("\n")
        return item

    def list(self) -> list[ReviewItem]:
        return list(reversed(self._items))

    def clear(self) -> None:
        self._items = []
        self.path.write_text("", encoding="utf-8")
