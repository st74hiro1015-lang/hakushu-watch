from __future__ import annotations

from src.sources.base import Source

SOURCES = [
    Source(
        key="norifune_hakushu",
        url="https://norifune.com/liqueur/whisky/japanese/hakusyu-buy",
        label="ノリフネ 白州",
        selector=".cps-post-main, .entry-content, article",
    ),
]
