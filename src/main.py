from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

from src.core import state as state_mod
from src.core.http import FetchError
from src.notifier import line
from src.sources import norifune, nyuka_now, rakuten_furusato, suntory
from src.sources.base import FetchResult, Source

KEYWORDS = ("白州", "山崎", "響", "抽選", "販売", "予約", "受付", "入荷", "再販")
DEFAULT_STATE_PATH = Path("state/state.json")
SOURCE_INTERVAL_SEC = 2.0

ALL_SOURCES: list[Source] = [
    *nyuka_now.SOURCES,
    *norifune.SOURCES,
    *suntory.SOURCES,
    *rakuten_furusato.SOURCES,
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("hakushu-watch")


def has_keyword(text: str) -> bool:
    return any(kw in text for kw in KEYWORDS)


def format_message(result: FetchResult, prev_excerpt: str) -> str:
    header = f"[更新検知] {result.label}"
    if result.fallback_used:
        header += "\n[警告] セレクタ要更新（fallback使用中）"
    return (
        f"{header}\n"
        f"{result.url}\n"
        f"---\n"
        f"[新しい本文抜粋]\n{result.excerpt}\n"
        f"---\n"
        f"[前回抜粋]\n{prev_excerpt[:300] or '(初回)'}"
    )


def run(state_path: Path, dry_run: bool) -> int:
    state = state_mod.load(state_path)
    notifications_sent = 0
    failures = 0

    for i, source in enumerate(ALL_SOURCES):
        if i > 0:
            time.sleep(SOURCE_INTERVAL_SEC)
        log.info("fetch %s (%s)", source.key, source.url)
        try:
            result = source.fetch()
        except FetchError as e:
            log.warning("fetch failed: %s -> %s", source.key, e)
            failures += 1
            continue
        except Exception as e:  # noqa: BLE001 - one source failure must not stop the run
            log.exception("unexpected error on %s: %s", source.key, e)
            failures += 1
            continue

        prev = state.sources.get(source.key)
        is_new = prev is None
        changed = (not is_new) and prev.hash != result.content_hash
        keyword_hit = has_keyword(result.full_text)

        if (is_new or changed) and keyword_hit:
            msg = format_message(result, prev.excerpt if prev else "")
            log.info("notify %s (new=%s changed=%s)", source.key, is_new, changed)
            if dry_run:
                print("[DRY-RUN MESSAGE]")
                print(msg)
                print()
            else:
                try:
                    line.push(msg)
                    notifications_sent += 1
                except Exception as e:  # noqa: BLE001
                    log.exception("LINE push failed for %s: %s", source.key, e)
                    # Keep state unchanged so we retry next run.
                    continue
        elif (is_new or changed) and not keyword_hit:
            log.info("change without keyword match, suppressing: %s", source.key)

        state.sources[source.key] = state_mod.SourceState(
            hash=result.content_hash,
            last_seen_iso=state_mod.now_iso(),
            fallback_used=result.fallback_used,
            excerpt=result.excerpt,
        )

    state_mod.save(state_path, state)
    log.info(
        "done: sources=%d notifications=%d failures=%d",
        len(ALL_SOURCES),
        notifications_sent,
        failures,
    )
    return 0 if failures < len(ALL_SOURCES) else 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="hakushu-watch")
    p.add_argument("--dry-run", action="store_true", help="Skip LINE push, print to stdout")
    p.add_argument(
        "--state",
        type=Path,
        default=DEFAULT_STATE_PATH,
        help="Path to state.json",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    return run(state_path=args.state, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
