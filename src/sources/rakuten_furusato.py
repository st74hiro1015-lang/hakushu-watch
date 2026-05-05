from __future__ import annotations

import re
import urllib.parse
from dataclasses import dataclass

from selectolax.parser import HTMLParser

from src.sources.base import Source, strip_boilerplate

# Each product card carries the `searchresultitem` token in its class list. That's
# the structural anchor; sibling tokens have hashed suffixes that change between
# Rakuten deployments.
ITEM_SELECTOR = ".searchresultitem"

# Strip Rakuten's per-card volatile chrome: viewer counters, review counts, points
# rotation. Without this every poll sees order shuffling and counter drift even
# when the underlying listings are identical.
RAKUTEN_NOISE = [
    re.compile(r"\d+人がチェック"),
    re.compile(r"\(\d+件\)"),  # review count
    re.compile(r"\d+ポイント"),
    re.compile(r"残り\s*\d+\s*[個本件]"),
]


def _normalize_card(text: str) -> str:
    for pat in RAKUTEN_NOISE:
        text = pat.sub("", text)
    return re.sub(r"\s+", " ", text).strip()


@dataclass
class RakutenSearchSource(Source):
    """Order-insensitive hash over Rakuten search result cards, brand-filtered.

    The default Source extracts joined text in DOM order, which makes the hash
    flap on every poll because Rakuten lightly reshuffles result order and
    rotates [PR] (paid) cards that aren't the brand we care about. We instead
    pull a stable per-card key (item URL + stock state + title), drop cards
    whose title doesn't contain `brand`, and sort -- so the hash only changes
    when the *set* of brand listings changes.
    """

    must_contain: tuple[str, ...] = ()  # all of these must appear in card title

    def _extract(self, html: str) -> tuple[str, bool]:
        parser = HTMLParser(html)
        strip_boilerplate(parser)
        items = parser.css(ITEM_SELECTOR)
        if not items:
            body = parser.body
            text = body.text(separator=" ", strip=True) if body else parser.text(strip=True)
            return text, True
        records: list[str] = []
        for item in items:
            title_node = item.css_first("h2") or item.css_first(".title")
            title = title_node.text(separator=" ", strip=True) if title_node else ""
            # PR (Rakuten paid-promotion) cards rotate every poll and are not the
            # actual organic search result we care about. Drop them.
            if title.startswith("[PR]"):
                continue
            if any(kw not in title for kw in self.must_contain):
                continue
            link = item.css_first("a[href]")
            href = link.attributes.get("href", "") or "" if link else ""
            href = re.sub(r"\?.*$", "", href)
            sold_out = bool(item.css_first(".dui-card.is-soldout, .sold-out, .item-soldout"))
            stock = "OOS" if sold_out else "OK"
            records.append(f"{href}|{stock}|{_normalize_card(title)[:200]}")
        records.sort()
        return "\n".join(records), False


def _url(query: str) -> str:
    return f"https://search.rakuten.co.jp/search/mall/{urllib.parse.quote(query)}/"


SOURCES = [
    RakutenSearchSource(
        key="rakuten_furusato_hakushu",
        url=_url("ふるさと納税 白州 サントリー"),
        label="楽天ふるさと納税 白州",
        selector=ITEM_SELECTOR,
        must_contain=("白州", "サントリー"),
    ),
    RakutenSearchSource(
        key="rakuten_furusato_yamazaki",
        url=_url("ふるさと納税 山崎 サントリー ウイスキー"),
        label="楽天ふるさと納税 山崎",
        selector=ITEM_SELECTOR,
        must_contain=("山崎", "サントリー"),
    ),
    RakutenSearchSource(
        key="rakuten_furusato_hibiki",
        url=_url("ふるさと納税 響 サントリー"),
        label="楽天ふるさと納税 響",
        selector=ITEM_SELECTOR,
        must_contain=("響", "サントリー"),
    ),
]
