from __future__ import annotations

from urllib.parse import urlparse

from selectolax.parser import HTMLParser, Node

from src.sources.base import Item, Source, stable_key, strip_boilerplate

# Sub-headings inside the article body that introduce a store section.
STORE_HEADING_TAGS = ("h2", "h3", "h4")

# Keywords that suggest the heading is a store/retailer name (filters out
# generic section dividers like "抽選販売を行っているストア" or "更新履歴").
STORE_HEADING_KEYWORDS = (
    "店", "館", "ヨーカドー", "イオン", "タカシマヤ", "高島屋", "阪急", "阪神",
    "伊勢丹", "三越", "東急", "ビックカメラ", "やまや", "はせがわ", "酒店",
    "成城石井", "近鉄", "オーケー", "ローソン", "セブン", "ファミ", "OK",
    "サントリー公式", "白州蒸溜所", "山崎蒸溜所", "ふるさと納税",
)

SOCIAL_BLOCKLIST = ("twitter.com", "x.com", "facebook.com", "line.me",
                    "nyukanow.page.link", "instagram.com")
DETAIL_KEYWORDS = ("詳細", "公式", "応募", "予約", "受付", "リンク", "こちら")


def _is_store_heading(text: str) -> bool:
    return any(kw in text for kw in STORE_HEADING_KEYWORDS)


def _walk_until_next_heading(start: Node) -> list[Node]:
    """Yield siblings after `start` until we hit another heading at same level."""
    out: list[Node] = []
    cur = start.next
    start_tag = start.tag
    while cur is not None:
        # stop at next heading of the same or higher level
        if cur.tag in ("h1", "h2", "h3", "h4"):
            break
        out.append(cur)
        cur = cur.next
    return out


def _pick_link(section: list[Node], aggregator_host: str) -> str | None:
    """From a store section, pick the most likely application/info URL.

    Strategy:
      1. Prefer <a> whose link text contains 詳細/公式/応募/予約/受付.
      2. Fallback to first http(s) <a> whose host is not the aggregator and
         not a social-media block.
    """
    candidates: list[tuple[int, str]] = []  # (priority, href)
    for n in section:
        if not hasattr(n, "css"):
            continue
        for a in n.css("a"):
            href = a.attributes.get("href") or ""
            if not href.startswith(("http://", "https://")):
                continue
            host = urlparse(href).netloc.lower()
            if host == aggregator_host or any(b in host for b in SOCIAL_BLOCKLIST):
                continue
            text = a.text(strip=True)
            if any(kw in text for kw in DETAIL_KEYWORDS):
                candidates.append((0, href))
            else:
                candidates.append((1, href))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]


class NyukaNowSource(Source):
    """Extract per-store lottery entries from a nyuka-now article page."""

    def fetch_items(self) -> list[Item]:
        html = self._fetch_html()
        parser = HTMLParser(html)
        strip_boilerplate(parser)
        content = parser.css_first(".postContents")
        if content is None:
            return []
        aggregator_host = urlparse(self.url).netloc.lower()
        items: list[Item] = []
        seen_keys: set[str] = set()
        for tag in STORE_HEADING_TAGS:
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
    NyukaNowSource(
        source_key="nyuka_now_hakushu_lottery",
        url="https://nyuka-now.com/archives/839",
        label="nyuka-now 白州抽選",
    ),
    NyukaNowSource(
        source_key="nyuka_now_yamazaki_lottery",
        url="https://nyuka-now.com/archives/834",
        label="nyuka-now 山崎・響・白州",
    ),
    NyukaNowSource(
        source_key="nyuka_now_restock",
        url="https://nyuka-now.com/archives/1022",
        label="nyuka-now 在庫・再販",
    ),
]
