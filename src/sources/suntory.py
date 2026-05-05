from __future__ import annotations

from src.sources.base import Source

# Brand product pages (hakushu/yamazaki/hibiki) share a layout where the main
# content lives under `#suntory_contents`.
PRODUCT_SELECTOR = "#suntory_contents"

# The distillery news page uses a different layout.
NEWS_SELECTOR = ".news__list, .news__container, main"

SOURCES = [
    Source(
        key="suntory_hakushu_product",
        url="https://www.suntory.co.jp/whisky/hakushu/",
        label="サントリー白州 商品ページ",
        selector=PRODUCT_SELECTOR,
    ),
    Source(
        key="suntory_yamazaki_product",
        url="https://www.suntory.co.jp/whisky/yamazaki/",
        label="サントリー山崎 商品ページ",
        selector=PRODUCT_SELECTOR,
    ),
    Source(
        key="suntory_hibiki_product",
        url="https://www.suntory.co.jp/whisky/hibiki/",
        label="サントリー響 商品ページ",
        selector=PRODUCT_SELECTOR,
    ),
    Source(
        key="suntory_hakushu_distillery_news",
        url="https://www.suntory.co.jp/factory/hakushu/news/",
        label="サントリー白州蒸溜所 News",
        selector=NEWS_SELECTOR,
    ),
]
