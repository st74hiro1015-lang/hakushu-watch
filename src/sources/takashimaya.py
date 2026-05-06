from __future__ import annotations

from urllib.parse import urljoin, urlparse

from selectolax.parser import HTMLParser

from src.sources.base import Item, Source, stable_key, strip_boilerplate

KEYWORDS = ("白州", "山崎", "響", "サントリー", "ウイスキー")


def _is_relevant(text: str) -> bool:
    return any(k in text for k in KEYWORDS)


class TakashimayaTakasakiSource(Source):
    """高崎高島屋 home page: extract event/news links containing whisky keywords."""

    def fetch_items(self) -> list[Item]:
        html = self._fetch_html()
        parser = HTMLParser(html)
        strip_boilerplate(parser)
        items: list[Item] = []
        seen_keys: set[str] = set()
        for a in parser.css("a[href]"):
            href = a.attributes.get("href") or ""
            text = a.text(strip=True)
            if not text or len(text) < 6 or not _is_relevant(text):
                continue
            full = urljoin(self.url, href)
            if "takashimaya.co.jp" not in urlparse(full).netloc:
                continue
            key = stable_key(self.source_key, full, text[:80])
            if key in seen_keys:
                continue
            seen_keys.add(key)
            items.append(Item(key=key, title=text[:120], url=full))
        return items


class TakashimayaWhiskyLoungeSource(Source):
    """高島屋オンライン ウイスキーラウンジ: each product card is an item."""

    def fetch_items(self) -> list[Item]:
        html = self._fetch_html()
        parser = HTMLParser(html)
        strip_boilerplate(parser)
        items: list[Item] = []
        seen_keys: set[str] = set()
        for card in parser.css(".c-productitembox"):
            link = card.css_first("a[href]")
            title_node = card.css_first(".c-productitembox__detail__name")
            href = (link.attributes.get("href") or "") if link else ""
            title = title_node.text(separator=" ", strip=True) if title_node else ""
            if not href or not title:
                continue
            full = urljoin(self.url, href)
            # Only keep whisky-related cards (drops the recommendation widget noise)
            if not _is_relevant(title):
                continue
            key = stable_key(self.source_key, full)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            items.append(Item(key=key, title=title[:140], url=full))
        return items


SOURCES = [
    TakashimayaTakasakiSource(
        source_key="takashimaya_takasaki_home",
        url="https://www.takashimaya.co.jp/takasaki/",
        label="高崎高島屋",
    ),
    TakashimayaWhiskyLoungeSource(
        source_key="takashimaya_whisky_lounge",
        url="https://www.takashimaya.co.jp/shopping/special/0900008539/",
        label="高島屋ウイスキーラウンジ",
    ),
]
