from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field


class SourceState(BaseModel):
    hash: str
    last_seen_iso: str
    fallback_used: bool = False
    excerpt: str = ""


class State(BaseModel):
    version: int = 1
    sources: dict[str, SourceState] = Field(default_factory=dict)


def load(path: Path) -> State:
    if not path.exists():
        return State()
    try:
        return State.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception:
        # Corrupted state -> reset rather than crash. First poll will look like
        # all sources are new (filtered by keyword, so noise is bounded).
        return State()


def save(path: Path, state: State) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(state.model_dump(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
