from __future__ import annotations

from typing import Any, List, Protocol, TypeVar


class _Comparable(Protocol):
    def __lt__(self, other: Any, /) -> bool: ...


T = TypeVar("T", bound="_Comparable")


def insertion_sort(arr: List[T]) -> None:
    """
    Sort *arr* in-place using insertion sort.

    Stable. Adaptive: O(n) on nearly-sorted data.

    Time:  O(n²) worst/average, O(n) best (already sorted)
    Space: O(1)

    IDS use-case: small alert batches or nearly-sorted timestamp streams.
    """
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


def merge_sort(arr: List[T]) -> None:
    """
    Sort *arr* in-place using top-down merge sort.

    Stable. Guaranteed O(n log n) regardless of input shape.

    Time:  O(n log n) worst/average/best
    Space: O(n) auxiliary (temporary slice during merge)

    IDS use-case: ordering alerts by timestamp where stability matters
    (equal timestamps preserve original relative order).
    """
    if len(arr) <= 1:
        return
    _merge_sort_helper(arr, 0, len(arr) - 1)


def _merge_sort_helper(arr: List[T], lo: int, hi: int) -> None:
    if lo >= hi:
        return
    mid = (lo + hi) // 2
    _merge_sort_helper(arr, lo, mid)
    _merge_sort_helper(arr, mid + 1, hi)
    _merge(arr, lo, mid, hi)


def _merge(arr: List[T], lo: int, mid: int, hi: int) -> None:
    left = arr[lo : mid + 1]
    right = arr[mid + 1 : hi + 1]
    i = j = 0
    k = lo
    while i < len(left) and j < len(right):
        # Use <= (not <) to preserve stability: left wins on tie
        if not right[j] < left[i]:
            arr[k] = left[i]
            i += 1
        else:
            arr[k] = right[j]
            j += 1
        k += 1
    while i < len(left):
        arr[k] = left[i]
        i += 1
        k += 1
    while j < len(right):
        arr[k] = right[j]
        j += 1
        k += 1


def quick_sort(arr: List[T]) -> None:
    """
    Sort *arr* in-place using quicksort with median-of-three pivot selection.

    Not stable. Median-of-three avoids O(n²) on already-sorted or reverse-sorted input.

    Time:  O(n log n) average, O(n²) worst (degenerate partitions)
    Space: O(log n) call stack average

    IDS use-case: large network traffic log files where raw speed matters
    and stability is not required.
    """
    if len(arr) <= 1:
        return
    _quick_sort_helper(arr, 0, len(arr) - 1)


def _quick_sort_helper(arr: List[T], lo: int, hi: int) -> None:
    if lo >= hi:
        return
    pivot_idx = _partition(arr, lo, hi)
    _quick_sort_helper(arr, lo, pivot_idx - 1)
    _quick_sort_helper(arr, pivot_idx + 1, hi)


def _median_of_three(arr: List[T], lo: int, hi: int) -> int:
    """Return index of the median among arr[lo], arr[mid], arr[hi]."""
    mid = (lo + hi) // 2
    # Sort lo, mid, hi in-place so arr[mid] is the median
    if arr[hi] < arr[lo]:
        arr[lo], arr[hi] = arr[hi], arr[lo]
    if arr[mid] < arr[lo]:
        arr[lo], arr[mid] = arr[mid], arr[lo]
    if arr[hi] < arr[mid]:
        arr[mid], arr[hi] = arr[hi], arr[mid]
    return mid


def _partition(arr: List[T], lo: int, hi: int) -> int:
    """Lomuto partition with median-of-three pivot. Returns final pivot index."""
    pivot_idx = _median_of_three(arr, lo, hi)
    arr[pivot_idx], arr[hi] = arr[hi], arr[pivot_idx]
    pivot = arr[hi]
    i = lo - 1
    for j in range(lo, hi):
        if arr[j] < pivot or not pivot < arr[j]:  # arr[j] <= pivot
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
    return i + 1


def heap_sort(arr: List[T]) -> None:
    """
    Sort *arr* in-place using heapsort.

    Not stable. Guaranteed O(n log n) with O(1) extra space — ideal for
    memory-constrained edge devices (e.g. Raspberry Pi in IDS deployments).

    Time:  O(n log n) worst/average/best
    Space: O(1)

    IDS use-case: sorting feature vectors on edge hardware where auxiliary
    memory is a hard constraint.
    """
    n = len(arr)
    # Build max-heap
    for i in range(n // 2 - 1, -1, -1):
        _sift_down(arr, n, i)
    # Extract elements from heap one by one
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        _sift_down(arr, i, 0)


def _sift_down(arr: List[T], n: int, i: int) -> None:
    """Sift down element at index *i* in a max-heap of size *n*."""
    while True:
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        if left < n and arr[largest] < arr[left]:
            largest = left
        if right < n and arr[largest] < arr[right]:
            largest = right
        if largest == i:
            break
        arr[i], arr[largest] = arr[largest], arr[i]
        i = largest
