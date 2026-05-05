from __future__ import annotations

from dataclasses import dataclass

from selectolax.parser import HTMLParser

from src.core import http
from src.core.hash import hash_normalized, normalize

BOILERPLATE_TAGS = ("script", "style", "noscript", "nav", "footer", "header", "iframe")


def strip_boilerplate(parser: HTMLParser) -> None:
    for tag in BOILERPLATE_TAGS:
        for node in parser.css(tag):
            node.decompose()


@dataclass
class FetchResult:
    key: str
    url: str
    label: str
    content_hash: str
    excerpt: str  # truncated, for display only
    full_text: str  # full normalized text, for keyword filtering
    fallback_used: bool


@dataclass
class Source:
    key: str
    url: str
    label: str
    selector: str | None  # None = whole-page hash

    def fetch(self) -> FetchResult:
        html = http.fetch(self.url)
        text, fallback_used = self._extract(html)
        normalized = normalize(text)
        return FetchResult(
            key=self.key,
            url=self.url,
            label=self.label,
            content_hash=hash_normalized(text),
            excerpt=normalized[:600],
            full_text=normalized,
            fallback_used=fallback_used,
        )

    def _extract(self, html: str) -> tuple[str, bool]:
        parser = HTMLParser(html)
        strip_boilerplate(parser)
        if self.selector:
            nodes = parser.css(self.selector)
            if nodes:
                return " ".join(n.text(separator=" ", strip=True) for n in nodes), False
        body = parser.body
        text = body.text(separator=" ", strip=True) if body else parser.text(strip=True)
        return text, self.selector is not None
