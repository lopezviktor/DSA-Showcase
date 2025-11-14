from __future__ import annotations
from typing import Generic, Iterable, List, Optional, TypeVar

T = TypeVar("T")


class EmptyStackError(IndexError):
    """Raised when attempting to pop or peek from an empty stack."""

    pass


class Stack(Generic[T]):
    """
    A simple LIFO (Last-In, First-Out) stack implementation using a dynamic list.

    Performance:
        - push: O(1) amortized
        - pop:  O(1)
        - peek: O(1)
        - size: O(1)
        - is_empty: O(1)
    """

    __slots__ = ("_data",)

    def __init__(self, items: Optional[Iterable[T]] = None) -> None:
        """
        Initialize the stack.

        Args:
            items: Optional iterable of initial items to push onto the stack.
        """
        self._data: List[T] = []

        # Populate initial items, if provided
        if items is not None:
            for item in items:
                self.push(item)

    def push(self, item: T) -> None:
        """
        Push an element onto the top of the stack.

        Args:
            item: The element to be added.
        """
        self._data.append(item)

    def pop(self) -> T:
        """
        Remove and return the top element of the stack.

        Returns:
            The last pushed element.

        Raises:
            EmptyStackError: If the stack is empty.
        """
        if not self._data:
            raise EmptyStackError("Cannot pop from an empty stack.")
        return self._data.pop()

    def peek(self) -> T:
        """
        Return the top element without removing it.

        Returns:
            The top element.

        Raises:
            EmptyStackError: If the stack is empty.
        """
        if not self._data:
            raise EmptyStackError("Cannot peek an empty stack.")
        return self._data[-1]

    def is_empty(self) -> bool:
        """
        Check if the stack is empty.

        Returns:
            True if stack is empty, False otherwise.
        """
        return not self._data

    def size(self) -> int:
        """
        Return the number of elements in the stack.

        Returns:
            Integer count of stored elements.
        """
        return len(self._data)

    def clear(self) -> None:
        """
        Remove all elements from the stack.
        """
        self._data.clear()

    def __len__(self) -> int:
        """
        Support len(stack) syntax.

        Returns:
            The number of items in the stack.
        """
        return len(self._data)

    def __repr__(self) -> str:
        """
        Developer-friendly representation of the stack.

        Returns:
            A string showing the internal list.
        """
        return f"Stack({self._data!r})"
