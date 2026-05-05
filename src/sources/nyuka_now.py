from __future__ import annotations

from src.sources.base import Source

# nyuka-now.com (Cocoon-derived WP theme) wraps article body in `.postContents`.
SELECTOR = ".postContents"

SOURCES = [
    Source(
        key="nyuka_now_hakushu_lottery",
        url="https://nyuka-now.com/archives/839",
        label="nyuka-now 白州抽選まとめ",
        selector=SELECTOR,
    ),
    Source(
        key="nyuka_now_yamazaki_lottery",
        url="https://nyuka-now.com/archives/834",
        label="nyuka-now 山崎・響・白州まとめ",
        selector=SELECTOR,
    ),
    Source(
        key="nyuka_now_restock",
        url="https://nyuka-now.com/archives/1022",
        label="nyuka-now 在庫・再販",
        selector=SELECTOR,
    ),
]
