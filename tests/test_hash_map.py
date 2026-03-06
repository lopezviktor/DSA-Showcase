"""Tests for HashMap — targeting 100% coverage of hash_map.py."""
from __future__ import annotations

import pytest

from dsa_toolkit.hash_map import HashMap, KeyNotFoundError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _CollidingKey:
    """A key whose hash is always 0, forcing every entry into bucket 0."""

    def __init__(self, value: int) -> None:
        self.value = value

    def __hash__(self) -> int:
        return 0

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _CollidingKey) and self.value == other.value


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------

def test_initial_state() -> None:
    m: HashMap[str, int] = HashMap()
    assert m.is_empty()
    assert m.size() == 0
    assert len(m) == 0
    assert m.keys() == set()
    assert m.values() == []
    assert m.items() == set()


# ---------------------------------------------------------------------------
# put / get basics
# ---------------------------------------------------------------------------

def test_put_and_get() -> None:
    m: HashMap[str, int] = HashMap()
    m.put("a", 1)
    assert m.get("a") == 1
    assert m.size() == 1
    assert not m.is_empty()


def test_put_updates_existing_key() -> None:
    m: HashMap[str, int] = HashMap()
    m.put("x", 10)
    m.put("x", 99)
    assert m.get("x") == 99
    assert m.size() == 1  # size must not grow on update


def test_get_missing_key_raises() -> None:
    m: HashMap[str, int] = HashMap()
    with pytest.raises(KeyNotFoundError):
        m.get("missing")


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------

def test_delete_removes_entry() -> None:
    m: HashMap[str, int] = HashMap()
    m.put("a", 1)
    m.put("b", 2)
    m.delete("a")
    assert m.size() == 1
    assert not m.contains_key("a")
    assert m.get("b") == 2


def test_delete_missing_key_raises() -> None:
    m: HashMap[str, int] = HashMap()
    with pytest.raises(KeyNotFoundError):
        m.delete("ghost")


# ---------------------------------------------------------------------------
# contains_key / __contains__
# ---------------------------------------------------------------------------

def test_contains_key() -> None:
    m: HashMap[str, int] = HashMap()
    m.put("k", 42)
    assert m.contains_key("k")
    assert not m.contains_key("nope")


def test_in_operator() -> None:
    m: HashMap[str, int] = HashMap()
    m.put("hello", 7)
    assert "hello" in m
    assert "world" not in m


# ---------------------------------------------------------------------------
# keys / values / items
# ---------------------------------------------------------------------------

def test_keys_values_items() -> None:
    m: HashMap[str, int] = HashMap()
    m.put("a", 1)
    m.put("b", 2)
    m.put("c", 3)

    assert m.keys() == {"a", "b", "c"}
    assert set(m.values()) == {1, 2, 3}
    assert m.items() == {("a", 1), ("b", 2), ("c", 3)}


# ---------------------------------------------------------------------------
# clear
# ---------------------------------------------------------------------------

def test_clear_resets_map() -> None:
    m: HashMap[str, int] = HashMap()
    for i in range(20):
        m.put(str(i), i)
    m.clear()
    assert m.is_empty()
    assert m.size() == 0
    assert m._capacity == HashMap._DEFAULT_CAPACITY


# ---------------------------------------------------------------------------
# __len__ / __repr__
# ---------------------------------------------------------------------------

def test_len() -> None:
    m: HashMap[str, int] = HashMap()
    assert len(m) == 0
    m.put("a", 1)
    assert len(m) == 1


def test_repr() -> None:
    m: HashMap[str, int] = HashMap()
    assert repr(m) == f"HashMap(size=0, capacity={HashMap._DEFAULT_CAPACITY})"
    m.put("x", 1)
    assert "size=1" in repr(m)


# ---------------------------------------------------------------------------
# Dynamic resizing
# ---------------------------------------------------------------------------

def test_resize_triggered() -> None:
    """Inserting 13 elements (> 16 * 0.75 = 12) must trigger a resize to 32."""
    m: HashMap[int, int] = HashMap()
    for i in range(13):
        m.put(i, i * 10)

    assert m._capacity == 32
    assert m.size() == 13
    # All entries must survive the rehash
    for i in range(13):
        assert m.get(i) == i * 10


def test_resize_preserves_all_entries() -> None:
    m: HashMap[str, str] = HashMap()
    data = {f"key{i}": f"val{i}" for i in range(50)}
    for k, v in data.items():
        m.put(k, v)
    for k, v in data.items():
        assert m.get(k) == v


# ---------------------------------------------------------------------------
# Collision handling (forced via _CollidingKey)
# ---------------------------------------------------------------------------

def test_collision_put_get() -> None:
    m: HashMap[_CollidingKey, str] = HashMap()
    k1 = _CollidingKey(1)
    k2 = _CollidingKey(2)
    m.put(k1, "one")
    m.put(k2, "two")
    assert m.get(k1) == "one"
    assert m.get(k2) == "two"
    assert m.size() == 2


def test_collision_update() -> None:
    m: HashMap[_CollidingKey, int] = HashMap()
    k1 = _CollidingKey(1)
    k2 = _CollidingKey(2)
    m.put(k1, 10)
    m.put(k2, 20)
    m.put(k1, 99)  # update, not insert
    assert m.get(k1) == 99
    assert m.size() == 2


def test_collision_delete() -> None:
    m: HashMap[_CollidingKey, str] = HashMap()
    k1 = _CollidingKey(1)
    k2 = _CollidingKey(2)
    m.put(k1, "a")
    m.put(k2, "b")
    m.delete(k1)
    assert m.size() == 1
    assert m.get(k2) == "b"
    with pytest.raises(KeyNotFoundError):
        m.get(k1)


def test_collision_contains() -> None:
    m: HashMap[_CollidingKey, int] = HashMap()
    k1 = _CollidingKey(1)
    k2 = _CollidingKey(2)
    m.put(k1, 1)
    assert m.contains_key(k1)
    assert not m.contains_key(k2)


# ---------------------------------------------------------------------------
# IDS / IoT context scenarios
# ---------------------------------------------------------------------------

def test_ids_ip_alert_count() -> None:
    """Simulate an IDS accumulating alert counts per source IP."""
    alert_map: HashMap[str, int] = HashMap()
    events = [
        "192.168.1.5",
        "10.0.0.2",
        "192.168.1.5",
        "192.168.1.5",
        "10.0.0.3",
    ]
    for ip in events:
        if ip in alert_map:
            alert_map.put(ip, alert_map.get(ip) + 1)
        else:
            alert_map.put(ip, 1)

    assert alert_map.get("192.168.1.5") == 3
    assert alert_map.get("10.0.0.2") == 1
    assert alert_map.get("10.0.0.3") == 1
    assert alert_map.size() == 3


def test_ids_feature_normalization() -> None:
    """Simulate caching normalized feature values for IoT inference."""
    feature_map: HashMap[str, float] = HashMap()
    raw_features = {
        "packet_size": 1500.0,
        "flow_duration": 0.03,
        "byte_rate": 50000.0,
    }
    # Normalize to [0, 1] range (min=0 assumed)
    max_vals = {"packet_size": 65535.0, "flow_duration": 1.0, "byte_rate": 1e6}
    for feat, val in raw_features.items():
        feature_map.put(feat, val / max_vals[feat])

    assert abs(feature_map.get("packet_size") - 1500 / 65535) < 1e-9
    assert abs(feature_map.get("flow_duration") - 0.03) < 1e-9
    assert abs(feature_map.get("byte_rate") - 0.05) < 1e-9
    assert feature_map.size() == 3
