"""Tests for LRUCache — 100% coverage required."""

from __future__ import annotations

import pytest

from dsa_toolkit.lru_cache import LRUCache, LRUCacheKeyError


# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------


def test_valid_capacity() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=5)
    assert cache.capacity() == 5
    assert cache.is_empty()
    assert cache.size() == 0


def test_capacity_one() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=1)
    assert cache.capacity() == 1


def test_capacity_zero_raises() -> None:
    with pytest.raises(ValueError):
        LRUCache(capacity=0)


def test_capacity_negative_raises() -> None:
    with pytest.raises(ValueError):
        LRUCache(capacity=-3)


# ---------------------------------------------------------------------------
# get / put / contains
# ---------------------------------------------------------------------------


def test_put_and_get_single_entry() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=3)
    cache.put("a", 1)
    assert cache.get("a") == 1


def test_get_missing_key_raises() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=3)
    with pytest.raises(LRUCacheKeyError):
        cache.get("missing")


def test_update_existing_key_value() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=3)
    cache.put("a", 1)
    cache.put("a", 99)
    assert cache.get("a") == 99
    assert cache.size() == 1


def test_update_existing_key_moves_to_mru() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    # Update "a" — it should now be MRU; "b" becomes LRU
    cache.put("a", 10)
    # Filling capacity should evict "b", not "a"
    cache.put("c", 3)
    assert "a" in cache
    assert "c" in cache
    assert "b" not in cache


def test_contains_true() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=3)
    cache.put("x", 42)
    assert cache.contains("x") is True


def test_contains_false() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=3)
    assert cache.contains("x") is False


def test_dunder_contains() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=3)
    cache.put("k", 7)
    assert "k" in cache
    assert "z" not in cache


# ---------------------------------------------------------------------------
# Eviction order
# ---------------------------------------------------------------------------


def test_eviction_at_capacity() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)  # "a" should be evicted
    assert "a" not in cache
    assert "b" in cache
    assert "c" in cache


def test_insert_abc_capacity_two_evicts_a() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=2)
    cache.put("A", 1)
    cache.put("B", 2)
    cache.put("C", 3)
    assert "A" not in cache
    assert "B" in cache
    assert "C" in cache


def test_get_promotes_to_mru() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    # Access "a" — now "b" is LRU
    cache.get("a")
    cache.put("c", 3)  # "b" evicted
    assert "b" not in cache
    assert "a" in cache
    assert "c" in cache


def test_peek_does_not_change_eviction_order() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    # peek "a" should NOT promote it; "a" remains LRU
    cache.peek("a")
    cache.put("c", 3)  # "a" should be evicted, not "b"
    assert "a" not in cache
    assert "b" in cache
    assert "c" in cache


# ---------------------------------------------------------------------------
# peek
# ---------------------------------------------------------------------------


def test_peek_returns_correct_value() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=3)
    cache.put("k", 55)
    assert cache.peek("k") == 55


def test_peek_missing_key_raises() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=3)
    with pytest.raises(LRUCacheKeyError):
        cache.peek("nope")


# ---------------------------------------------------------------------------
# evict()
# ---------------------------------------------------------------------------


def test_evict_returns_lru_entry() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=3)
    cache.put("a", 1)
    cache.put("b", 2)
    key, val = cache.evict()
    assert key == "a"
    assert val == 1
    assert "a" not in cache
    assert cache.size() == 1


def test_evict_empty_cache_raises() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=3)
    with pytest.raises(LRUCacheKeyError):
        cache.evict()


def test_evict_updates_size() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=2)
    cache.put("x", 10)
    cache.put("y", 20)
    cache.evict()
    assert cache.size() == 1


def test_evict_all_entries() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=3)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    cache.evict()
    cache.evict()
    cache.evict()
    assert cache.is_empty()


# ---------------------------------------------------------------------------
# is_empty / size / capacity / len
# ---------------------------------------------------------------------------


def test_initial_state() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=4)
    assert cache.is_empty() is True
    assert cache.size() == 0
    assert cache.capacity() == 4
    assert len(cache) == 0


def test_size_after_puts() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=5)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.size() == 2
    assert len(cache) == 2
    assert cache.is_empty() is False


def test_size_stable_after_update() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=5)
    cache.put("a", 1)
    cache.put("a", 2)
    assert cache.size() == 1


def test_size_after_eviction() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)  # evicts "a"
    assert cache.size() == 2


# ---------------------------------------------------------------------------
# IDS scenarios
# ---------------------------------------------------------------------------


def test_ip_reputation_cache() -> None:
    """Simulate caching IP reputation scores; verify LRU eviction."""
    cache: LRUCache[str, float] = LRUCache(capacity=3)
    cache.put("192.168.1.1", 0.9)
    cache.put("10.0.0.5", 0.2)
    cache.put("172.16.0.3", 0.7)

    # Access 192.168.1.1 and 10.0.0.5 → 172.16.0.3 becomes LRU
    cache.get("192.168.1.1")
    cache.get("10.0.0.5")

    # Adding a 4th IP evicts the LRU (172.16.0.3)
    cache.put("203.0.113.42", 0.5)
    assert "172.16.0.3" not in cache
    assert "192.168.1.1" in cache
    assert "10.0.0.5" in cache
    assert "203.0.113.42" in cache


def test_rate_limit_cache() -> None:
    """Simulate per-source-IP request counters with automatic LRU eviction."""
    cache: LRUCache[str, int] = LRUCache(capacity=2)
    cache.put("1.2.3.4", 1)
    cache.put("5.6.7.8", 1)

    # Update request count for 1.2.3.4 — it becomes MRU
    cache.put("1.2.3.4", cache.peek("1.2.3.4") + 1)

    # New IP arrives; 5.6.7.8 is evicted (LRU)
    cache.put("9.10.11.12", 1)
    assert "5.6.7.8" not in cache
    assert cache.get("1.2.3.4") == 2
    assert cache.get("9.10.11.12") == 1


# ---------------------------------------------------------------------------
# __repr__
# ---------------------------------------------------------------------------


def test_repr_non_empty() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=3)
    cache.put("a", 1)
    cache.put("b", 2)
    r = repr(cache)
    assert "LRUCache" in r
    assert "capacity=3" in r
    assert "'a'" in r
    assert "'b'" in r


def test_repr_empty() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=2)
    r = repr(cache)
    assert "LRUCache" in r
    assert "entries=[]" in r


def test_repr_mru_order() -> None:
    """MRU entry should appear first in repr."""
    cache: LRUCache[str, int] = LRUCache(capacity=3)
    cache.put("first", 1)
    cache.put("second", 2)
    cache.put("third", 3)
    r = repr(cache)
    assert r.index("'third'") < r.index("'second'") < r.index("'first'")
