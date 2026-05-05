from __future__ import annotations

from src.sources.base import Source

# Tokyu and Itoyokado online stores can't be scraped directly: Tokyu's whisky
# offers are members-only (TOKYU CARD ClubQ login wall) and Itoyokado's net
# shop is heavily SPA'd (item search returns 404 server-side). norifune
# maintains a curated, single-page aggregator for each, which is what we use
# instead -- still aggregator-based but page-specific to those retailers.
SOURCES = [
    Source(
        key="norifune_hakushu",
        url="https://norifune.com/liqueur/whisky/japanese/hakusyu-buy",
        label="ノリフネ 白州",
        selector=".cps-post-main, .entry-content, article",
    ),
    Source(
        key="norifune_tokyucard",
        url="https://norifune.com/liqueur/whisky/japanese/tokyucard-whisky",
        label="ノリフネ 東急カード会員限定ウイスキー",
        selector=".cps-post-main, .entry-content, article",
    ),
    Source(
        key="norifune_lottery_whisky",
        url="https://norifune.com/liqueur/whisky/lottery-whisky",
        label="ノリフネ 希少ウイスキー抽選販売まとめ（イトーヨーカドー含む）",
        selector=".cps-post-main, .entry-content, article",
    ),
]
