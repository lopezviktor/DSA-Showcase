from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, Iterator, List, Optional, Protocol, Tuple, TypeVar


class _Comparable(Protocol):
    def __lt__(self, other: Any, /) -> bool: ...

    def __gt__(self, other: Any, /) -> bool: ...


K = TypeVar("K", bound=_Comparable)
V = TypeVar("V")


@dataclass(slots=True)
class _Node(Generic[K, V]):
    key: K
    value: V
    left: Optional[_Node[K, V]] = None
    right: Optional[_Node[K, V]] = None


class BinarySearchTree(Generic[K, V]):
    """
    Binary Search Tree (BST).

    Invariant:
        - left subtree keys  < node.key
        - right subtree keys > node.key

    Notes:
    - This is NOT a balanced BST.
    - insert() overwrites the value if the key already exists.
    - inorder() returns items sorted by key.
    - floor(key) returns the greatest key <= given key (useful for threshold mapping).
    """

    __slots__ = ("_root", "_size")

    def __init__(self) -> None:
        self._root: Optional[_Node[K, V]] = None
        self._size: int = 0

    def is_empty(self) -> bool:
        return self._size == 0

    def size(self) -> int:
        return self._size

    def __len__(self) -> int:
        return self._size

    def insert(self, key: K, value: V) -> None:
        """Insert (key, value). If key exists, overwrite value."""
        self._root = self._insert(self._root, key, value)

    def _insert(self, node: Optional[_Node[K, V]], key: K, value: V) -> _Node[K, V]:
        if node is None:
            self._size += 1
            return _Node(key=key, value=value)

        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            # key already exists -> overwrite
            node.value = value

        return node

    def find(self, key: K) -> Optional[V]:
        """Return the value for key if present, else None."""
        node = self._root
        while node is not None:
            if key < node.key:
                node = node.left
            elif key > node.key:
                node = node.right
            else:
                return node.value
        return None

    def contains(self, key: K) -> bool:
        return self.find(key) is not None

    def floor(self, key: K) -> Optional[Tuple[K, V]]:
        """
        Return (k, v) where k is the greatest key <= input key.
        Returns None if no such key exists (i.e., all keys > input).
        """
        node = self._root
        best: Optional[_Node[K, V]] = None

        while node is not None:
            if key < node.key:
                node = node.left
            elif key > node.key:
                best = node
                node = node.right
            else:
                return (node.key, node.value)

        if best is None:
            return None
        return (best.key, best.value)

    def inorder(self) -> List[Tuple[K, V]]:
        """Return (key, value) pairs sorted by key."""
        out: List[Tuple[K, V]] = []
        self._inorder(self._root, out)
        return out

    def _inorder(self, node: Optional[_Node[K, V]], out: List[Tuple[K, V]]) -> None:
        if node is None:
            return
        self._inorder(node.left, out)
        out.append((node.key, node.value))
        self._inorder(node.right, out)

    def __iter__(self) -> Iterator[Tuple[K, V]]:
        """Default iteration: inorder (sorted by key)."""
        for item in self.inorder():
            yield item

    def __repr__(self) -> str:
        return f"BinarySearchTree({self.inorder()!r})"