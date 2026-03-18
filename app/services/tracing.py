from __future__ import annotations

from pathlib import Path

from app.models.schemas import TraceRecord


class TraceStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._items: list[TraceRecord] = []
        if self.path.exists():
            self._load_existing()

    def _load_existing(self) -> None:
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                self._items.append(TraceRecord.model_validate_json(line))

    def write(self, trace: TraceRecord) -> None:
        self._items.append(trace)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(trace.model_dump_json())
            fh.write("\n")

    def list(self) -> list[TraceRecord]:
        return list(reversed(self._items))

    def get(self, request_id: str) -> TraceRecord | None:
        for item in self._items:
            if item.request_id == request_id:
                return item
        return None

    def clear(self) -> None:
        self._items = []
        self.path.write_text("", encoding="utf-8")
