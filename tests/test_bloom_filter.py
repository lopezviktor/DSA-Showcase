"""Tests for BloomFilter — 100 % coverage required."""
from __future__ import annotations

import math

import pytest

from dsa_toolkit.bloom_filter import BloomFilter, BloomFilterError


# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------


def test_default_construction() -> None:
    bf = BloomFilter(100)
    assert bf.capacity() == 100
    assert bf.bit_count() > 0
    assert bf.hash_count() >= 1
    assert bf.num_added() == 0
    assert bf.is_empty()


def test_custom_error_rate() -> None:
    bf = BloomFilter(500, error_rate=0.001)
    assert bf.capacity() == 500
    # lower error_rate → more bits
    bf_default = BloomFilter(500)
    assert bf.bit_count() > bf_default.bit_count()


def test_capacity_too_small() -> None:
    with pytest.raises(BloomFilterError):
        BloomFilter(0)


def test_capacity_negative() -> None:
    with pytest.raises(BloomFilterError):
        BloomFilter(-5)


def test_error_rate_zero() -> None:
    with pytest.raises(BloomFilterError):
        BloomFilter(100, error_rate=0.0)


def test_error_rate_one() -> None:
    with pytest.raises(BloomFilterError):
        BloomFilter(100, error_rate=1.0)


def test_error_rate_negative() -> None:
    with pytest.raises(BloomFilterError):
        BloomFilter(100, error_rate=-0.1)


def test_error_rate_above_one() -> None:
    with pytest.raises(BloomFilterError):
        BloomFilter(100, error_rate=1.5)


# ---------------------------------------------------------------------------
# add / contains / __contains__
# ---------------------------------------------------------------------------


def test_add_then_contains_true() -> None:
    bf = BloomFilter(100)
    bf.add("hello")
    assert bf.contains("hello") is True


def test_unknown_item_contains_false() -> None:
    bf = BloomFilter(1000)
    for i in range(50):
        bf.add(f"item-{i}")
    # "nope" was never added — very high confidence it returns False
    assert bf.contains("definitely-not-added-xyzzy") is False


def test_in_operator_true() -> None:
    bf = BloomFilter(100)
    bf.add(42)
    assert 42 in bf


def test_in_operator_false() -> None:
    bf = BloomFilter(1000)
    bf.add(1)
    assert 999 not in bf


def test_various_hashable_types() -> None:
    bf = BloomFilter(200)
    bf.add("string")
    bf.add(3.14)
    bf.add((1, 2, 3))
    bf.add(frozenset({1, 2}))
    assert "string" in bf
    assert 3.14 in bf
    assert (1, 2, 3) in bf
    assert frozenset({1, 2}) in bf


# ---------------------------------------------------------------------------
# is_empty / num_added / __len__
# ---------------------------------------------------------------------------


def test_is_empty_initially() -> None:
    bf = BloomFilter(50)
    assert bf.is_empty() is True
    assert bf.num_added() == 0
    assert len(bf) == 0


def test_not_empty_after_add() -> None:
    bf = BloomFilter(50)
    bf.add("x")
    assert bf.is_empty() is False
    assert bf.num_added() == 1
    assert len(bf) == 1


def test_repeated_add_increments_counter() -> None:
    bf = BloomFilter(100)
    bf.add("dup")
    bf.add("dup")
    bf.add("dup")
    # num_added is NOT deduplicated
    assert bf.num_added() == 3
    assert len(bf) == 3


def test_multiple_items_counter() -> None:
    bf = BloomFilter(100)
    for i in range(10):
        bf.add(i)
    assert bf.num_added() == 10


# ---------------------------------------------------------------------------
# clear
# ---------------------------------------------------------------------------


def test_clear_resets_counter() -> None:
    bf = BloomFilter(100)
    for i in range(5):
        bf.add(i)
    bf.clear()
    assert bf.num_added() == 0
    assert bf.is_empty()
    assert len(bf) == 0


def test_clear_resets_bits() -> None:
    bf = BloomFilter(100)
    bf.add("secret")
    bf.clear()
    # After clearing, previously-added item should NOT be found
    assert bf.contains("secret") is False


def test_add_after_clear() -> None:
    bf = BloomFilter(100)
    bf.add("a")
    bf.clear()
    bf.add("b")
    assert bf.contains("b") is True
    assert bf.num_added() == 1


# ---------------------------------------------------------------------------
# false_positive_rate
# ---------------------------------------------------------------------------


def test_fpr_zero_when_empty() -> None:
    bf = BloomFilter(1000)
    assert bf.false_positive_rate() == 0.0


def test_fpr_in_valid_range_after_adds() -> None:
    bf = BloomFilter(1000, error_rate=0.01)
    for i in range(100):
        bf.add(f"item-{i}")
    fpr = bf.false_positive_rate()
    assert 0.0 <= fpr < 1.0


def test_fpr_increases_with_load() -> None:
    bf = BloomFilter(100, error_rate=0.05)
    prev = 0.0
    for i in range(1, 6):
        bf.add(f"x{i}")
        current = bf.false_positive_rate()
        assert current >= prev
        prev = current


def test_fpr_after_clear_is_zero() -> None:
    bf = BloomFilter(100)
    for i in range(20):
        bf.add(i)
    bf.clear()
    assert bf.false_positive_rate() == 0.0


# ---------------------------------------------------------------------------
# bit_count / hash_count / capacity — determinism & monotonicity
# ---------------------------------------------------------------------------


def test_same_params_deterministic() -> None:
    bf1 = BloomFilter(500, error_rate=0.02)
    bf2 = BloomFilter(500, error_rate=0.02)
    assert bf1.bit_count() == bf2.bit_count()
    assert bf1.hash_count() == bf2.hash_count()


def test_hash_count_at_least_one() -> None:
    bf = BloomFilter(1, error_rate=0.5)
    assert bf.hash_count() >= 1


def test_larger_capacity_larger_bit_count() -> None:
    small = BloomFilter(100)
    large = BloomFilter(10_000)
    assert large.bit_count() > small.bit_count()


def test_lower_error_rate_larger_bit_count_and_hash_count() -> None:
    loose = BloomFilter(1000, error_rate=0.1)
    tight = BloomFilter(1000, error_rate=0.001)
    assert tight.bit_count() > loose.bit_count()
    assert tight.hash_count() >= loose.hash_count()


def test_capacity_accessor() -> None:
    bf = BloomFilter(777, error_rate=0.05)
    assert bf.capacity() == 777


def test_bit_count_matches_formula() -> None:
    n, p = 1000, 0.01
    ln2 = math.log(2)
    expected_m = math.ceil(-n * math.log(p) / (ln2 ** 2))
    bf = BloomFilter(n, error_rate=p)
    assert bf.bit_count() == expected_m


def test_hash_count_matches_formula() -> None:
    n, p = 1000, 0.01
    ln2 = math.log(2)
    m = math.ceil(-n * math.log(p) / (ln2 ** 2))
    expected_k = max(1, round((m / n) * ln2))
    bf = BloomFilter(n, error_rate=p)
    assert bf.hash_count() == expected_k


# ---------------------------------------------------------------------------
# IDS scenarios
# ---------------------------------------------------------------------------


def test_ids_malicious_ip_blocklist() -> None:
    """Bloom Filter as first-pass IP blocklist (capacity=1000, error_rate=0.001)."""
    bf = BloomFilter(1000, error_rate=0.001)
    malicious_ips = [f"192.168.1.{i}" for i in range(200)]
    for ip in malicious_ips:
        bf.add(ip)
    # All known-malicious IPs must be found
    for ip in malicious_ips:
        assert ip in bf
    # Legitimate IPs should mostly not be found (deterministic non-member)
    assert "10.0.0.1" not in bf
    assert "172.16.0.1" not in bf


def test_ids_packet_signature_filter() -> None:
    """50 known attack signatures loaded into a small filter."""
    bf = BloomFilter(50, error_rate=0.01)
    signatures = [f"sig-{i:03d}" for i in range(50)]
    for sig in signatures:
        bf.add(sig)
    assert bf.num_added() == 50
    for sig in signatures:
        assert sig in bf


def test_ids_edge_deployment_memory_budget() -> None:
    """Edge deployment: filter with capacity=10_000 and 1 % FPR stays under 20 KB."""
    bf = BloomFilter(10_000, error_rate=0.01)
    # bytearray backing store size in bytes
    byte_size = math.ceil(bf.bit_count() / 8)
    assert byte_size < 20_000  # well under 20 KB


def test_ids_deduplication_of_flow_ids() -> None:
    """Deduplicating seen flow IDs with a Bloom Filter."""
    bf = BloomFilter(5000, error_rate=0.005)
    seen_flows = [f"flow-{i}" for i in range(100)]
    for flow in seen_flows:
        bf.add(flow)
    # All previously seen flows are recognised
    for flow in seen_flows:
        assert flow in bf
    # A genuinely new flow is not (deterministic non-member)
    assert "flow-99999" not in bf


# ---------------------------------------------------------------------------
# __repr__
# ---------------------------------------------------------------------------


def test_repr_contains_class_name() -> None:
    bf = BloomFilter(100)
    assert "BloomFilter" in repr(bf)


def test_repr_contains_capacity() -> None:
    bf = BloomFilter(256)
    assert "256" in repr(bf)


def test_repr_contains_error_rate() -> None:
    bf = BloomFilter(100, error_rate=0.05)
    assert "0.05" in repr(bf)


def test_repr_updates_after_add() -> None:
    bf = BloomFilter(100)
    bf.add("x")
    assert "num_added=1" in repr(bf)
