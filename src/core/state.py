from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field


class SourceState(BaseModel):
    seen_keys: list[str] = Field(default_factory=list)
    last_seen_iso: str = ""


class State(BaseModel):
    version: int = 2
    sources: dict[str, SourceState] = Field(default_factory=dict)


def load(path: Path) -> State:
    if not path.exists():
        return State()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        # Drop pre-v2 state (different schema): start clean. The first poll is
        # silent (no spurious "all items new" notifications).
        if data.get("version") != 2:
            return State()
        return State.model_validate(data)
    except Exception:
        return State()


def save(path: Path, state: State) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(state.model_dump(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
