"""Tests for sorting algorithms in dsa_toolkit.sorting."""
from __future__ import annotations

import random
from typing import Callable, List

import pytest

from dsa_toolkit.sorting import heap_sort, insertion_sort, merge_sort, quick_sort

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SortFn = Callable[[List], None]
ALL_SORTS: list[tuple[str, SortFn]] = [
    ("insertion_sort", insertion_sort),
    ("merge_sort", merge_sort),
    ("quick_sort", quick_sort),
    ("heap_sort", heap_sort),
]


def _check(sort_fn: SortFn, arr: list) -> None:
    """Sort arr and assert it matches Python's built-in sort."""
    expected = sorted(arr)
    sort_fn(arr)
    assert arr == expected


# ---------------------------------------------------------------------------
# Parametrised baseline tests (all four algorithms)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name,sort_fn", ALL_SORTS)
def test_empty(name: str, sort_fn: SortFn) -> None:
    arr: list[int] = []
    sort_fn(arr)
    assert arr == []


@pytest.mark.parametrize("name,sort_fn", ALL_SORTS)
def test_single_element(name: str, sort_fn: SortFn) -> None:
    arr = [42]
    sort_fn(arr)
    assert arr == [42]


@pytest.mark.parametrize("name,sort_fn", ALL_SORTS)
def test_already_sorted(name: str, sort_fn: SortFn) -> None:
    _check(sort_fn, [1, 2, 3, 4, 5])


@pytest.mark.parametrize("name,sort_fn", ALL_SORTS)
def test_reverse_sorted(name: str, sort_fn: SortFn) -> None:
    _check(sort_fn, [5, 4, 3, 2, 1])


@pytest.mark.parametrize("name,sort_fn", ALL_SORTS)
def test_duplicates(name: str, sort_fn: SortFn) -> None:
    _check(sort_fn, [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5])


@pytest.mark.parametrize("name,sort_fn", ALL_SORTS)
def test_all_same(name: str, sort_fn: SortFn) -> None:
    _check(sort_fn, [7, 7, 7, 7, 7])


@pytest.mark.parametrize("name,sort_fn", ALL_SORTS)
def test_negative_and_zero(name: str, sort_fn: SortFn) -> None:
    _check(sort_fn, [0, -3, 5, -1, 2, -7, 4])


@pytest.mark.parametrize("name,sort_fn", ALL_SORTS)
def test_two_elements_sorted(name: str, sort_fn: SortFn) -> None:
    _check(sort_fn, [1, 2])


@pytest.mark.parametrize("name,sort_fn", ALL_SORTS)
def test_two_elements_reversed(name: str, sort_fn: SortFn) -> None:
    _check(sort_fn, [2, 1])


@pytest.mark.parametrize("name,sort_fn", ALL_SORTS)
def test_large_random(name: str, sort_fn: SortFn) -> None:
    rng = random.Random(42)
    arr = [rng.randint(-1000, 1000) for _ in range(500)]
    _check(sort_fn, arr)


@pytest.mark.parametrize("name,sort_fn", ALL_SORTS)
def test_floats(name: str, sort_fn: SortFn) -> None:
    _check(sort_fn, [3.14, 1.41, 2.71, 0.0, -1.5])


# ---------------------------------------------------------------------------
# IDS-specific: sort alert tuples (severity, ip) — stable sorts only
# ---------------------------------------------------------------------------

STABLE_SORTS: list[tuple[str, SortFn]] = [
    ("insertion_sort", insertion_sort),
    ("merge_sort", merge_sort),
]


@pytest.mark.parametrize("name,sort_fn", STABLE_SORTS)
def test_ids_alerts_by_severity_stable(name: str, sort_fn: SortFn) -> None:
    """
    Alerts are (severity, ip) tuples. Equal-severity alerts must preserve
    their original relative order (stability guarantee).
    """
    alerts = [
        (3, "192.168.1.10"),
        (1, "10.0.0.1"),
        (3, "192.168.1.20"),  # same severity as first, must come after
        (2, "172.16.0.5"),
        (1, "10.0.0.2"),     # same severity as second, must come after
    ]
    sort_fn(alerts)  # type: ignore[arg-type]
    expected = sorted(alerts)  # Python sort is stable
    assert alerts == expected
    # Verify relative order of equal-severity alerts explicitly
    sev1 = [ip for sev, ip in alerts if sev == 1]
    assert sev1 == ["10.0.0.1", "10.0.0.2"]
    sev3 = [ip for sev, ip in alerts if sev == 3]
    assert sev3 == ["192.168.1.10", "192.168.1.20"]


# ---------------------------------------------------------------------------
# IDS-specific: sort feature importances (floats)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name,sort_fn", ALL_SORTS)
def test_ids_feature_importances(name: str, sort_fn: SortFn) -> None:
    """Sort ML feature importances (floats) to rank features for edge deployment."""
    importances = [0.12, 0.45, 0.07, 0.33, 0.45, 0.22]
    _check(sort_fn, importances)


# ---------------------------------------------------------------------------
# Edge case: nearly-sorted (insertion_sort shines here)
# ---------------------------------------------------------------------------


def test_insertion_sort_nearly_sorted() -> None:
    """Insertion sort is O(n) on nearly-sorted data."""
    arr = list(range(100))
    # Introduce a few out-of-place elements
    arr[10], arr[11] = arr[11], arr[10]
    arr[50], arr[52] = arr[52], arr[50]
    _check(insertion_sort, arr)


# ---------------------------------------------------------------------------
# Stress test: already-sorted large array (median-of-three prevents O(n²))
# ---------------------------------------------------------------------------


def test_quick_sort_sorted_input_no_stack_overflow() -> None:
    """Median-of-three pivot ensures quicksort handles sorted input efficiently."""
    arr = list(range(1000))
    _check(quick_sort, arr)


def test_quick_sort_reverse_sorted_no_stack_overflow() -> None:
    arr = list(range(1000, 0, -1))
    _check(quick_sort, arr)


# ---------------------------------------------------------------------------
# heap_sort: verify O(1) extra space algorithm on edge-device-sized input
# ---------------------------------------------------------------------------


def test_heap_sort_medium_array() -> None:
    rng = random.Random(7)
    arr = [rng.randint(0, 255) for _ in range(200)]
    _check(heap_sort, arr)
