from __future__ import annotations
from typing import Generic, Iterable, List, Optional, TypeVar

T = TypeVar("T")


class EmptyQueueError(IndexError):
    """Raised when attempting to dequeue or peek from an empty queue."""

    pass


class Queue(Generic[T]):
    """
    A simple FIFO (First-In, First-Out) queue implementation.

    Internally uses a dynamic list plus a head index to achieve O(1) amortized
    enqueue and dequeue operations.

    Performance:
        - enqueue: O(1) amortized
        - dequeue: O(1) amortized
        - peek:    O(1)
        - size:    O(1)
        - is_empty: O(1)
    """

    __slots__ = ("_data", "_head")

    def __init__(self, items: Optional[Iterable[T]] = None) -> None:
        """
        Initialize the queue.

        Args:
            items: Optional iterable of initial items to enqueue.
        """
        self._data: List[T] = []
        self._head: int = 0  # index of the current front element

        if items is not None:
            for item in items:
                self.enqueue(item)

    def enqueue(self, item: T) -> None:
        """
        Add an element to the back of the queue.

        Args:
            item: The element to be added.
        """
        self._data.append(item)

    def dequeue(self) -> T:
        """
        Remove and return the front element of the queue.

        Returns:
            The oldest enqueued element.

        Raises:
            EmptyQueueError: If the queue is empty.
        """
        if self.is_empty():
            raise EmptyQueueError("Cannot dequeue from an empty queue.")

        item = self._data[self._head]
        self._head += 1

        # Periodically compact the underlying list to avoid unbounded growth
        if self._head > 50 and self._head * 2 > len(self._data):
            self._data = self._data[self._head :]
            self._head = 0

        return item

    def peek(self) -> T:
        """
        Return the front element without removing it.

        Raises:
            EmptyQueueError: If the queue is empty.
        """
        if self.is_empty():
            raise EmptyQueueError("Cannot peek an empty queue.")
        return self._data[self._head]

    def is_empty(self) -> bool:
        """
        Check if the queue is empty.

        Returns:
            True if the queue has no elements, False otherwise.
        """
        return self.size() == 0

    def size(self) -> int:
        """
        Return the number of elements in the queue.

        Returns:
            Integer count of stored elements.
        """
        return len(self._data) - self._head

    def clear(self) -> None:
        """
        Remove all elements from the queue.
        """
        self._data.clear()
        self._head = 0

    def __len__(self) -> int:
        """
        Support len(queue) syntax.

        Returns:
            The number of items in the queue.
        """
        return self.size()

    def __repr__(self) -> str:
        """
        Developer-friendly representation of the queue.

        Returns:
            A string showing the logical contents of the queue.
        """
        logical = self._data[self._head :]
        return f"Queue({logical!r})"
