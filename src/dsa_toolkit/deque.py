from __future__ import annotations

from typing import Generic, Iterator, Iterable, List, Optional, TypeVar

T = TypeVar("T")


class EmptyDequeError(IndexError):
    """Raised when attempting to pop or peek from an empty deque."""

    pass


class Deque(Generic[T]):
    """
    A double-ended queue (deque) implementation.

    Supports 0(1) amortized inserts/removals at the both ends using a circular buffer.

    Perforrmance:
        - append_left / append_right: 0(1) amortized
        - pop_left / pop_right: 0(1) amortized
        - peek_left / peek_right: 0(1)
        - size / is_empty: 0(1)
    """

    __slots__ = ("_data", "_head", "_tail", "_size")

    def __init__(
        self, items: Optional[Iterable[T]] = None, *, initial_capacity: int = 8
    ) -> None:
        if initial_capacity < 1:
            raise ValueError("initial_capacity must be >= 1")

        # Capacity is always at least 1; we grow as needed.
        self._data: List[Optional[T]] = [None] * initial_capacity
        self._head: int = 0  # index of the leftmost element
        self._tail: int = 0  # index one past the rightmost element
        self._size: int = 0

        if items is not None:
            for item in items:
                self.append_right(item)

    def append_left(self, item: T) -> None:
        """Insert item at the left end."""
        self._ensure_capacity_for_one_more()
        self._head = (self._head - 1) % len(self._data)
        self._data[self._head] = item
        self._size += 1

    def append_right(self, item: T) -> None:
        """Insert item at the right end."""
        self._ensure_capacity_for_one_more()
        self._data[self._tail] = item
        self._tail = (self._tail + 1) % len(self._data)
        self._size += 1

    def pop_left(self) -> T:
        """Remove and return the leftmost item."""
        if self.is_empty():
            raise EmptyDequeError("Cannot pop_left from an empty deque.")

        item = self._data[self._head]
        self._data[self._head] = None
        self._head = (self._head + 1) % len(self._data)
        self._size -= 1

        # item cannot be None here logically
        return item  # type: ignore[return-value]

    def pop_right(self) -> T:
        """Remove and return the rightmost item."""
        if self.is_empty():
            raise EmptyDequeError("Cannot pop_right from an empty deque.")

        self._tail = (self._tail - 1) % len(self._data)
        item = self._data[self._tail]
        self._data[self._tail] = None
        self._size -= 1

        return item  # type: ignore[return-value]

    def peek_left(self) -> T:
        """Return the leftmost item without removing it."""
        if self.is_empty():
            raise EmptyDequeError("Cannot peek_left on an empty deque.")
        item = self._data[self._head]
        return item  # type: ignore[return-value]

    def peek_right(self) -> T:
        """Return the rightmost item without removing it."""
        if self.is_empty():
            raise EmptyDequeError("Cannot peek_right on an empty deque.")
        idx = (self._tail - 1) % len(self._data)
        item = self._data[idx]
        return item  # type: ignore[return-value]

    def clear(self) -> None:
        """Remove all items."""
        self._data = [None] * len(self._data)
        self._head = 0
        self._tail = 0
        self._size = 0

    def is_empty(self) -> bool:
        """Return True if deque has no items."""
        return self._size == 0

    def size(self) -> int:
        """Return the number of items stored."""
        return self._size

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[T]:
        for i in range(self._size):
            idx = (self._head + i) % len(self._data)
            item = self._data[idx]
            yield item  # type: ignore[misc]

    def __repr__(self) -> str:
        return f"Deque({list(self)!r})"

    def _ensure_capacity_for_one_more(self) -> None:
        if self._size < len(self._data):
            return

        # Grow to double capacity
        old = self._data
        new_capacity = max(1, len(old) * 2)
        new: List[Optional[T]] = [None] * new_capacity

        # Copy logical order into new buffer starting at 0
        for i in range(self._size):
            new[i] = old[(self._head + i) % len(old)]

        self._data = new
        self._head = 0
        self._tail = self._size
