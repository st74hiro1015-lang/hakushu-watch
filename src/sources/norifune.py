from __future__ import annotations

from urllib.parse import urlparse

from selectolax.parser import HTMLParser

from src.sources.base import Item, Source, stable_key, strip_boilerplate
from src.sources.nyuka_now import (
    STORE_HEADING_KEYWORDS,
    _is_store_heading,
    _pick_link,
    _walk_until_next_heading,
)


class NorifuneSource(Source):
    """Extract per-store entries from a norifune.com article page.

    Layout differs from nyuka-now (Cocoon vs JIN theme) but the overall pattern
    of "heading per store, then table/links with the store's apply URL" is the
    same, so we share helpers from nyuka_now.
    """

    def fetch_items(self) -> list[Item]:
        html = self._fetch_html()
        parser = HTMLParser(html)
        strip_boilerplate(parser)
        # JIN theme wraps article body in `.cps-post-main` (also has
        # `.entry-content` token via multi-class). Try both.
        content = parser.css_first(".cps-post-main") or parser.css_first(".entry-content")
        if content is None:
            return []
        aggregator_host = urlparse(self.url).netloc.lower()
        items: list[Item] = []
        seen_keys: set[str] = set()
        for tag in ("h2", "h3", "h4"):
            for h in content.css(tag):
                store_name = h.text(strip=True)
                if not store_name or not _is_store_heading(store_name):
                    continue
                section = _walk_until_next_heading(h)
                link = _pick_link(section, aggregator_host)
                if link is None:
                    continue
                key = stable_key(self.source_key, store_name, link)
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                items.append(Item(key=key, title=store_name, url=link))
        return items


SOURCES = [
    NorifuneSource(
        source_key="norifune_hakushu",
        url="https://norifune.com/liqueur/whisky/japanese/hakusyu-buy",
        label="ノリフネ 白州",
    ),
    NorifuneSource(
        source_key="norifune_tokyucard",
        url="https://norifune.com/liqueur/whisky/japanese/tokyucard-whisky",
        label="ノリフネ 東急カード",
    ),
    NorifuneSource(
        source_key="norifune_lottery_whisky",
        url="https://norifune.com/liqueur/whisky/lottery-whisky",
        label="ノリフネ 希少抽選",
    ),
]
