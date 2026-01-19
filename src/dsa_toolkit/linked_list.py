from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterator, Optional, TypeVar

T = TypeVar("T")


class EmptyLinkedListError(IndexError):
    """Raised when attempting to access an element from an empty linked list."""

    pass


class ValueNotFoundError(ValueError):
    """Raised when a specified value is not found in the linked list."""

    pass


@dataclass(slots=True)
class _Node(Generic[T]):
    value: T
    next: Optional[_Node[T]] = None


class LinkedList(Generic[T]):
    """
    Singly Linked List implementation.
    Key ideas:
    - Nodes are linked via references (no contiguous memory like arrays).
    - Efficient operations at the head: prepend / pop_front are O(1).
    - With a tail reference, append is O(1).
    - Searching/removing by value is O(n).
    Public API is intentionally restricted to preserve the abstraction.
    """

    __slots__ = ("_head", "_tail", "_size")

    def __init__(self) -> None:
        self._head: Optional[_Node[T]] = None
        self._tail: Optional[_Node[T]] = None
        self._size: int = 0

    def prepend(self, value: T) -> None:
        """Insert value at the beginning of the list. O(1)."""
        new_node = _Node(value=value, next=self._head)
        self._head = new_node

        if self._tail is None:
            # List was empty, head and tail are the same node.
            self._tail = new_node

        self._size += 1

    def append(self, value: T) -> None:
        """Insert value at the end of the list. O(1) with tail."""
        new_node = _Node(value=value)

        if self._head is None:
            # Empty list
            self._head = new_node
            self._tail = new_node
            self._size = 1
            return

        # Non-empty list: tail must exist
        assert self._tail is not None
        self._tail.next = new_node
        self._tail = new_node
        self._size += 1

    def pop_front(self) -> T:
        """Remove and return the first element. O(1)."""
        if self.is_empty():
            raise EmptyLinkedListError("Cannot pop_front from an empty linked list.")

        assert self._head is not None
        node = self._head
        self._head = node.next
        self._size -= 1

        if self._head is None:
            # List became empty
            self._tail = None

        return node.value

    def find(self, value: T) -> bool:
        """Return True if value exists in the list, otherwise False. O(n)."""
        current = self._head
        while current is not None:
            if current.value == value:
                return True
            current = current.next
        return False

    def remove(self, value: T) -> None:
        """
        Remove the first occurrence of value.
        Raises ValueNotFoundError if value is not present. O(n).
        """
        if self.is_empty():
            raise ValueNotFoundError("Value not found in linked list.")

        # Special case: removing the head
        assert self._head is not None
        if self._head.value == value:
            self.pop_front()
            return

        prev = self._head
        current = self._head.next

        while current is not None:
            if current.value == value:
                prev.next = current.next
                self._size -= 1

                # If we removed the tail, update it
                if current.next is None:
                    self._tail = prev

                return

            prev = current
            current = current.next

        raise ValueNotFoundError("Value not found in linked list.")

    def clear(self) -> None:
        """Remove all elements."""
        self._head = None
        self._tail = None
        self._size = 0

    def is_empty(self) -> bool:
        """Return True if the list has no elements."""
        return self._size == 0

    def size(self) -> int:
        """Return number of elements in the list."""
        return self._size

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[T]:
        current = self._head
        while current is not None:
            yield current.value
            current = current.next

    def __repr__(self) -> str:
        return f"LinkedList({list(self)!r})"
