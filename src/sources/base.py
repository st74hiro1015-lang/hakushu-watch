from __future__ import annotations

import hashlib
from dataclasses import dataclass

from selectolax.parser import HTMLParser

from src.core import http

BOILERPLATE_TAGS = ("script", "style", "noscript", "nav", "footer", "header", "iframe")


def strip_boilerplate(parser: HTMLParser) -> None:
    for tag in BOILERPLATE_TAGS:
        for node in parser.css(tag):
            node.decompose()


@dataclass(frozen=True)
class Item:
    """A single notifiable entity (e.g. one store's lottery, one product listing).

    Notifications are sent at item granularity: title + url, nothing else.
    `key` is the stable identifier we de-dupe on across polls.
    """

    key: str
    title: str  # what the user sees (store name or product name)
    url: str  # link the user clicks


def stable_key(*parts: str) -> str:
    return hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:16]


@dataclass
class Source:
    """A pollable source. Subclasses implement fetch_items()."""

    source_key: str  # stable id for state file
    url: str
    label: str  # human-readable source name (used as fallback prefix in titles)

    def fetch_items(self) -> list[Item]:
        raise NotImplementedError

    def _fetch_html(self) -> str:
        return http.fetch(self.url)
