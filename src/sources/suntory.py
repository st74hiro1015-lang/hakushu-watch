from __future__ import annotations

from urllib.parse import urljoin, urlparse

from selectolax.parser import HTMLParser

from src.sources.base import Item, Source, stable_key, strip_boilerplate

KEYWORDS = ("白州", "山崎", "響", "抽選", "限定", "発売", "予約", "受付")


def _is_relevant(text: str) -> bool:
    return any(k in text for k in KEYWORDS)


class SuntoryProductSource(Source):
    """Suntory brand product page (whisky/hakushu, /yamazaki, /hibiki).

    These pages list "お知らせ"/"NEWS" style announcements. We expose each
    announcement (title + link to detail page) as an Item if it mentions
    白州/山崎/響/抽選/予約 keywords.
    """

    def fetch_items(self) -> list[Item]:
        html = self._fetch_html()
        parser = HTMLParser(html)
        strip_boilerplate(parser)
        items: list[Item] = []
        seen_keys: set[str] = set()
        for a in parser.css("a[href]"):
            href = a.attributes.get("href") or ""
            text = a.text(strip=True)
            if not href or not text or len(text) < 6:
                continue
            if not _is_relevant(text):
                continue
            full = urljoin(self.url, href)
            if not full.startswith("https://www.suntory.co.jp"):
                continue
            key = stable_key(self.source_key, full)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            items.append(Item(key=key, title=text[:120], url=full))
        return items


class SuntoryNewsSource(Source):
    """Suntory white州蒸溜所 News list page."""

    def fetch_items(self) -> list[Item]:
        html = self._fetch_html()
        parser = HTMLParser(html)
        strip_boilerplate(parser)
        items: list[Item] = []
        seen_keys: set[str] = set()
        # News pages typically have an article list with <a> + dated entries.
        for a in parser.css("a[href]"):
            href = a.attributes.get("href") or ""
            text = a.text(strip=True)
            if not text or len(text) < 8:
                continue
            full = urljoin(self.url, href)
            host = urlparse(full).netloc
            if "suntory.co.jp" not in host:
                continue
            # Detail pages are typically /factory/hakushu/news/detail/* or
            # similar dated paths. Filter out nav/menu links.
            if "/news/" not in full or full.rstrip("/").endswith("/news"):
                continue
            key = stable_key(self.source_key, full)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            items.append(Item(key=key, title=text[:120], url=full))
        return items


SOURCES = [
    SuntoryProductSource(
        source_key="suntory_hakushu_product",
        url="https://www.suntory.co.jp/whisky/hakushu/",
        label="サントリー白州",
    ),
    SuntoryProductSource(
        source_key="suntory_yamazaki_product",
        url="https://www.suntory.co.jp/whisky/yamazaki/",
        label="サントリー山崎",
    ),
    SuntoryProductSource(
        source_key="suntory_hibiki_product",
        url="https://www.suntory.co.jp/whisky/hibiki/",
        label="サントリー響",
    ),
    SuntoryNewsSource(
        source_key="suntory_hakushu_distillery_news",
        url="https://www.suntory.co.jp/factory/hakushu/news/",
        label="白州蒸溜所News",
    ),
]
