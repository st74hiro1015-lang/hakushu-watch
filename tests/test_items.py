from src.sources.base import Item, stable_key
from src.sources.nyuka_now import _is_store_heading


def test_stable_key_deterministic():
    assert stable_key("a", "b") == stable_key("a", "b")
    assert stable_key("a", "b") != stable_key("a", "c")


def test_store_heading_detector():
    assert _is_store_heading("高島屋京都店")
    assert _is_store_heading("イトーヨーカドーネット通販")
    assert _is_store_heading("やまや")
    # Section headers / generic text should not match
    assert not _is_store_heading("抽選販売を行っているストア")
    assert not _is_store_heading("更新履歴")


def test_item_hashable_and_dedup():
    a = Item(key="k1", title="A", url="https://a.example.com")
    b = Item(key="k1", title="A", url="https://a.example.com")
    assert a == b
    assert hash(a) == hash(b)
