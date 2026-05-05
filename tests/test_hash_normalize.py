from src.core.hash import hash_normalized, normalize


def test_timestamp_stripped():
    a = "白州12年抽選販売 更新: 2026年5月5日 12:34"
    b = "白州12年抽選販売 更新: 2026年5月6日 09:00"
    assert hash_normalized(a) == hash_normalized(b)


def test_iso_timestamp_stripped():
    a = "更新2026-05-05T12:34:00+09:00 内容"
    b = "更新2026-05-06T01:00:00+09:00 内容"
    assert hash_normalized(a) == hash_normalized(b)


def test_query_param_stripped():
    a = "<a href='/x?nonce=abc123'>link</a>"
    b = "<a href='/x?nonce=def456'>link</a>"
    assert hash_normalized(a) == hash_normalized(b)


def test_view_count_stripped():
    a = "閲覧数: 12,345 白州抽選"
    b = "閲覧数: 99,999 白州抽選"
    assert hash_normalized(a) == hash_normalized(b)


def test_meaningful_change_detected():
    a = "白州12年抽選 受付期間 6月1日まで"
    b = "白州12年抽選 受付期間 6月15日まで"
    assert hash_normalized(a) != hash_normalized(b)


def test_unicode_normalization():
    # Half-width vs full-width
    a = "ｻﾝﾄﾘｰ 白州12年"
    b = "サントリー 白州12年"
    assert normalize(a) == normalize(b)


def test_whitespace_collapsed():
    a = "白州   抽選\n\n販売"
    b = "白州 抽選 販売"
    assert hash_normalized(a) == hash_normalized(b)
