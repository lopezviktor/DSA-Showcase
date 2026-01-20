from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterator, Optional, TypeVar

from dsa_toolkit.linked_list import ValueNotFoundError

T = TypeVar("T")


class EmptyDoublyLinkedListError(IndexError):
    """Raised when attempting an invalid operation on an empty doubly linked list."""

    pass


@dataclass(slots=True)
class _Node(Generic[T]):
    value: T
    next: Optional[_Node[T]] = None
    prev: Optional[_Node[T]] = None


class DoublyLinkedList(Generic[T]):
    """
    Doubly Linked List implementation.

    Compared to a singly linked list:
    - Each node has both `next` and `prev`.
    - Enables O(1) removals/insertions when you already have node references.
    - Enables efficient reverse traversal.

    Complexity (typical):
    - prepend / append: O(1)
    - pop_front / pop_back: O(1)
    - find / remove by value: O(n) search
    """

    __slots__ = ("_head", "_tail", "_size")

    def __init__(self) -> None:
        self._head: Optional[_Node[T]] = None
        self._tail: Optional[_Node[T]] = None
        self._size: int = 0

    def prepend(self, value: T) -> None:
        """Insert value at the beginning. O(1)."""
        new_node = _Node(value=value, next=self._head, prev=None)

        if self._head is None:
            # Empty list -> head and tail are the same node.
            self._head = new_node
            self._tail = new_node
            self._size = 1
            return

        # Non-empty list
        self._head.prev = new_node
        self._head = new_node
        self._size += 1

    def append(self, value: T) -> None:
        """Insert value at the end. O(1)."""
        new_node = _Node(value=value, next=None, prev=self._tail)

        if self._tail is None:
            # Empty list
            self._head = new_node
            self._tail = new_node
            self._size = 1
            return

        # Non-empty list
        self._tail.next = new_node
        self._tail = new_node
        self._size += 1

    def pop_front(self) -> T:
        """Remove and return the first element. O(1)."""
        if self.is_empty():
            raise EmptyDoublyLinkedListError(
                "Cannot pop_front from an empty doubly linked list."
            )

        assert self._head is not None
        node = self._head
        new_head = node.next

        if new_head is None:
            # List had one element
            self._head = None
            self._tail = None
            self._size = 0
            return node.value

        new_head.prev = None
        self._head = new_head
        self._size -= 1
        return node.value

    def pop_back(self) -> T:
        """Remove and return the last element. O(1)."""
        if self.is_empty():
            raise EmptyDoublyLinkedListError(
                "Cannot pop_back from an empty doubly linked list."
            )

        assert self._tail is not None
        node = self._tail
        new_tail = node.prev

        if new_tail is None:
            # List had one element
            self._head = None
            self._tail = None
            self._size = 0
            return node.value

        new_tail.next = None
        self._tail = new_tail
        self._size -= 1
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
        Raises ValueNotFoundError if not present. O(n) search.
        """
        if self.is_empty():
            raise ValueNotFoundError("Value not found in doubly linked list.")

        current = self._head
        while current is not None:
            if current.value == value:
                # Removing head
                if current.prev is None:
                    self.pop_front()
                    return

                # Removing tail
                if current.next is None:
                    self.pop_back()
                    return

                # Removing middle node: O(1) relink
                assert current.prev is not None and current.next is not None
                current.prev.next = current.next
                current.next.prev = current.prev
                self._size -= 1
                return

            current = current.next

        raise ValueNotFoundError("Value not found in doubly linked list.")

    def clear(self) -> None:
        """Remove all elements."""
        self._head = None
        self._tail = None
        self._size = 0

    def is_empty(self) -> bool:
        return self._size == 0

    def size(self) -> int:
        return self._size

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[T]:
        current = self._head
        while current is not None:
            yield current.value
            current = current.next

    def __reversed__(self) -> Iterator[T]:
        current = self._tail
        while current is not None:
            yield current.value
            current = current.prev

    def __repr__(self) -> str:
        return f"DoublyLinkedList({list(self)!r})"
