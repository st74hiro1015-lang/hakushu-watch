from __future__ import annotations

import re
import urllib.parse
from dataclasses import dataclass, field
from urllib.parse import urlparse

from selectolax.parser import HTMLParser

from src.sources.base import Item, Source, stable_key, strip_boilerplate

ITEM_SELECTOR = ".searchresultitem"


def _strip_tracking(href: str) -> str:
    parts = urlparse(href)
    # Rakuten's product URLs are clean like /<shop>/<id>/. Drop query string
    # (often tracking) so identical products dedupe across polls.
    return f"{parts.scheme}://{parts.netloc}{parts.path}"


@dataclass
class RakutenFurusatoSource(Source):
    """Order-insensitive per-product items from Rakuten Furusato search.

    Filters:
      - drops [PR] paid placement cards
      - drops cards whose title doesn't contain ALL `must_contain` tokens
        (e.g. ("山崎", "サントリー") avoids 山崎ワイナリー / 山崎金属工業 noise)
    """

    must_contain: tuple[str, ...] = field(default_factory=tuple)

    def fetch_items(self) -> list[Item]:
        html = self._fetch_html()
        parser = HTMLParser(html)
        strip_boilerplate(parser)
        cards = parser.css(ITEM_SELECTOR)
        items: list[Item] = []
        seen_keys: set[str] = set()
        for card in cards:
            title_node = card.css_first(".c-productitembox__detail__name") \
                or card.css_first("h2") or card.css_first(".title")
            title = title_node.text(separator=" ", strip=True) if title_node else ""
            if not title or title.startswith("[PR]"):
                continue
            if any(kw not in title for kw in self.must_contain):
                continue
            link = card.css_first("a[href]")
            href = (link.attributes.get("href") or "") if link else ""
            if not href.startswith("http"):
                continue
            href = _strip_tracking(href)
            key = stable_key(self.source_key, href)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            items.append(Item(key=key, title=title[:140], url=href))
        return items


def _url(query: str) -> str:
    return f"https://search.rakuten.co.jp/search/mall/{urllib.parse.quote(query)}/"


SOURCES = [
    RakutenFurusatoSource(
        source_key="rakuten_furusato_hakushu",
        url=_url("ふるさと納税 白州 サントリー"),
        label="楽天ふるさと納税 白州",
        must_contain=("白州", "サントリー"),
    ),
    RakutenFurusatoSource(
        source_key="rakuten_furusato_yamazaki",
        url=_url("ふるさと納税 山崎 サントリー ウイスキー"),
        label="楽天ふるさと納税 山崎",
        must_contain=("山崎", "サントリー"),
    ),
    RakutenFurusatoSource(
        source_key="rakuten_furusato_hibiki",
        url=_url("ふるさと納税 響 サントリー"),
        label="楽天ふるさと納税 響",
        must_contain=("響", "サントリー"),
    ),
]
