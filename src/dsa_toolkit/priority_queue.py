from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, List, Optional, Protocol, Tuple, TypeVar


P = TypeVar("P", bound="_Comparable")
T = TypeVar("T")


class _Comparable(Protocol):
    def __lt__(self, other: Any, /) -> bool: ...

    def __gt__(self, other: Any, /) -> bool: ...


class EmptyPriorityQueueError(IndexError):
    """Raised when attempting to peek/pop from an empty priority queue."""

    pass


@dataclass(slots=True)
class _Entry(Generic[P, T]):
    priority: P
    order: int  # smaller order = earlier insertion (FIFO on ties)
    item: T


class PriorityQueue(Generic[P, T]):
    """
    Max Priority Queue implemented with a binary heap (array-backed).

    - Higher priority is returned first.
    - Stable for ties: if two entries have equal priority, the one inserted earlier wins.

    Operations:
      - push:  O(log n)
      - peek:  O(1)
      - pop:   O(log n)
      - top_k: O(k log n) (non-destructive)
    """

    __slots__ = ("_data", "_next_order")

    def __init__(self) -> None:
        self._data: List[_Entry[P, T]] = []
        self._next_order: int = 0

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def size(self) -> int:
        return len(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def clear(self) -> None:
        self._data.clear()
        self._next_order = 0

    def push(self, priority: P, item: T) -> None:
        """Insert an item with the given priority."""
        entry = _Entry(priority=priority, order=self._next_order, item=item)
        self._next_order += 1
        self._push_entry(entry)

    def peek(self) -> Tuple[P, T]:
        """Return (priority, item) with maximum priority without removing it."""
        if self.is_empty():
            raise EmptyPriorityQueueError("Cannot peek from an empty priority queue.")
        top = self._data[0]
        return (top.priority, top.item)

    def pop(self) -> Tuple[P, T]:
        """Remove and return (priority, item) with maximum priority."""
        if self.is_empty():
            raise EmptyPriorityQueueError("Cannot pop from an empty priority queue.")

        top = self._data[0]
        last = self._data.pop()

        if self._data:
            self._data[0] = last
            self._heapify_down(0)

        return (top.priority, top.item)

    def top_k(self, k: int) -> List[Tuple[P, T]]:
        """
        Return the top-k items as a list of (priority, item) WITHOUT modifying the queue.
        If k <= 0 -> [].
        If k > size -> returns all in priority order.
        """
        if k <= 0 or self.is_empty():
            return []

        k = min(k, self.size())

        removed: List[_Entry[P, T]] = []
        result: List[Tuple[P, T]] = []

        for _ in range(k):
            # Pop full entries to preserve stability when re-inserting
            entry = self._pop_entry()
            removed.append(entry)
            result.append((entry.priority, entry.item))

        # Restore entries exactly as they were (same priority & order)
        for entry in removed:
            self._push_entry(entry)

        return result

    def __repr__(self) -> str:
        # Represent as priority-sorted snapshot (non-destructive)
        return f"PriorityQueue({self.top_k(self.size())!r})"

    # ----------------------------
    # Internal heap operations
    # ----------------------------
    def _push_entry(self, entry: _Entry[P, T]) -> None:
        self._data.append(entry)
        self._heapify_up(len(self._data) - 1)

    def _pop_entry(self) -> _Entry[P, T]:
        """Pop and return full entry (internal), used by top_k()."""
        if not self._data:
            raise EmptyPriorityQueueError("Cannot pop from an empty priority queue.")

        top = self._data[0]
        last = self._data.pop()

        if self._data:
            self._data[0] = last
            self._heapify_down(0)

        return top

    def _is_higher(self, a: _Entry[P, T], b: _Entry[P, T]) -> bool:
        """
        Return True if 'a' should be above 'b' in a max-heap.

        Higher priority wins.
        On tie, smaller order wins (stable: earlier insertion first).
        """
        if a.priority > b.priority:
            return True
        if a.priority < b.priority:
            return False
        return a.order < b.order

    def _heapify_up(self, idx: int) -> None:
        while idx > 0:
            parent = (idx - 1) // 2
            if self._is_higher(self._data[idx], self._data[parent]):
                self._data[idx], self._data[parent] = (
                    self._data[parent],
                    self._data[idx],
                )
                idx = parent
            else:
                break

    def _heapify_down(self, idx: int) -> None:
        n = len(self._data)
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            best = idx

            if left < n and self._is_higher(self._data[left], self._data[best]):
                best = left
            if right < n and self._is_higher(self._data[right], self._data[best]):
                best = right

            if best == idx:
                break

            self._data[idx], self._data[best] = self._data[best], self._data[idx]
            idx = best
