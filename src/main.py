from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

from src.core import state as state_mod
from src.core.http import FetchError
from src.notifier import line
from src.sources import (
    norifune,
    nyuka_now,
    rakuten_furusato,
    suntory,
    takashimaya,
)
from src.sources.base import Item, Source

DEFAULT_STATE_PATH = Path("state/state.json")
SOURCE_INTERVAL_SEC = 2.0
MAX_NEW_ITEMS_PER_SOURCE = 30  # safety cap; if more, treat as broken & skip

ALL_SOURCES: list[Source] = [
    *nyuka_now.SOURCES,
    *norifune.SOURCES,
    *suntory.SOURCES,
    *rakuten_furusato.SOURCES,
    *takashimaya.SOURCES,
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("hakushu-watch")


def format_message(item: Item, source_label: str) -> str:
    # Strict format the user asked for: store/title + URL only.
    # Source label appears as a tiny suffix so user knows which feed surfaced it.
    return f"{item.title}\n{item.url}\n— {source_label}"


def run(state_path: Path, dry_run: bool) -> int:
    state = state_mod.load(state_path)
    notifications_sent = 0
    failures = 0

    for i, source in enumerate(ALL_SOURCES):
        if i > 0:
            time.sleep(SOURCE_INTERVAL_SEC)
        log.info("fetch %s", source.source_key)
        try:
            items = source.fetch_items()
        except FetchError as e:
            log.warning("fetch failed: %s -> %s", source.source_key, e)
            failures += 1
            continue
        except Exception as e:  # noqa: BLE001 - one source failure must not stop the run
            log.exception("unexpected error on %s: %s", source.source_key, e)
            failures += 1
            continue

        prev = state.sources.get(source.source_key)
        is_first_run = prev is None or not prev.seen_keys
        seen = set(prev.seen_keys) if prev else set()
        new_items = [it for it in items if it.key not in seen]

        if is_first_run:
            log.info(
                "first run for %s: initializing %d items (no notifications)",
                source.source_key,
                len(items),
            )
        elif len(new_items) > MAX_NEW_ITEMS_PER_SOURCE:
            log.warning(
                "%s reports %d new items (>%d) -- likely a parser/site change. "
                "Skipping notifications, refreshing state.",
                source.source_key,
                len(new_items),
                MAX_NEW_ITEMS_PER_SOURCE,
            )
        else:
            for item in new_items:
                msg = format_message(item, source.label)
                log.info("notify %s: %s", source.source_key, item.title[:60])
                if dry_run:
                    print("[DRY-RUN]")
                    print(msg)
                    print()
                else:
                    try:
                        line.push(msg)
                        notifications_sent += 1
                    except Exception as e:  # noqa: BLE001
                        log.exception("LINE push failed for %s: %s", source.source_key, e)
                        # Don't update state for this source so we retry next run.
                        break
            else:
                pass  # else clause runs if for didn't break -- nothing extra to do

        # Update state with current item set
        state.sources[source.source_key] = state_mod.SourceState(
            seen_keys=sorted({it.key for it in items}),
            last_seen_iso=state_mod.now_iso(),
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
    p.add_argument("--state", type=Path, default=DEFAULT_STATE_PATH)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    return run(state_path=args.state, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
