from __future__ import annotations

from src.sources.base import Source

SOURCES = [
    Source(
        key="takashimaya_takasaki_home",
        url="https://www.takashimaya.co.jp/takasaki/",
        label="高崎高島屋 トップ（イベント・抽選告知）",
        selector=".information-list, .important-info-list, .banner-list, main, #main",
    ),
    # The /shopping/search.html endpoints are client-side rendered (static HTML
    # only contains a "あなたへのおすすめ" widget, not real search results).
    # The curated /shopping/special/<id>/ feature pages, however, ARE statically
    # rendered. ウイスキーラウンジ (id=0900008539) lists ~27 whisky products and
    # adds new bottles / lottery items as they appear.
    Source(
        key="takashimaya_whisky_lounge",
        url="https://www.takashimaya.co.jp/shopping/special/0900008539/",
        label="高島屋オンラインストア ウイスキーラウンジ",
        selector=".c-productitembox",
    ),
]
