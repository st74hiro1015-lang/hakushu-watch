from __future__ import annotations

from dataclasses import dataclass

from selectolax.parser import HTMLParser

from src.core import http
from src.core.hash import hash_normalized, normalize


@dataclass
class FetchResult:
    key: str
    url: str
    label: str
    content_hash: str
    excerpt: str
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
        return FetchResult(
            key=self.key,
            url=self.url,
            label=self.label,
            content_hash=hash_normalized(text),
            excerpt=normalize(text)[:600],
            fallback_used=fallback_used,
        )

    def _extract(self, html: str) -> tuple[str, bool]:
        parser = HTMLParser(html)
        # Drop script/style/nav/footer/header to remove most boilerplate.
        for tag in ("script", "style", "noscript", "nav", "footer", "header", "iframe"):
            for node in parser.css(tag):
                node.decompose()
        if self.selector:
            nodes = parser.css(self.selector)
            if nodes:
                return " ".join(n.text(separator=" ", strip=True) for n in nodes), False
        body = parser.body
        text = body.text(separator=" ", strip=True) if body else parser.text(strip=True)
        return text, self.selector is not None
