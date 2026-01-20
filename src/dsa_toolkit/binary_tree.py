from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterator, List, Optional, TypeVar

from dsa_toolkit.queue import Queue

T = TypeVar("T")


class EmptyBinaryTreeError(IndexError):
    """Raised when attempting an invalid operation on an empty binary tree."""

    pass


@dataclass(slots=True)
class _Node(Generic[T]):
    value: T
    left: Optional[_Node[T]] = None
    right: Optional[_Node[T]] = None


class BinaryTree(Generic[T]):
    """
    Binary Tree (not a BST).

    Notes:
    - No ordering rules (this is NOT a Binary Search Tree).
    - Each node has at most two children: left and right.
    - Trees are traversed (DFS/BFS), not indexed.

    Traversals:
    - preorder:  Root -> Left -> Right
    - inorder:   Left -> Root -> Right
    - postorder: Left -> Right -> Root
    - bfs:       Level-order (uses Queue)
    """

    __slots__ = ("_root", "_size")

    def __init__(self, value: Optional[T] = None) -> None:
        self._root: Optional[_Node[T]] = None
        self._size: int = 0

        if value is not None:
            self._root = _Node(value=value)
            self._size = 1

    def is_empty(self) -> bool:
        return self._size == 0

    def size(self) -> int:
        return self._size

    def __len__(self) -> int:
        return self._size

    def root_value(self) -> T:
        if self._root is None:
            raise EmptyBinaryTreeError("Tree has no root (empty tree).")
        return self._root.value

    def insert_left(self, value: T) -> None:
        """
        Insert a new node as the left child of the root.
        If a left child already exists, it is pushed down (becomes left child of the new node).
        """
        if self._root is None:
            self._root = _Node(value=value)
            self._size = 1
            return

        new_node = _Node(value=value, left=self._root.left, right=None)
        self._root.left = new_node
        self._size += 1

    def insert_right(self, value: T) -> None:
        """
        Insert a new node as the right child of the root.
        If a right child already exists, it is pushed down (becomes right child of the new node).
        """
        if self._root is None:
            self._root = _Node(value=value)
            self._size = 1
            return

        new_node = _Node(value=value, left=None, right=self._root.right)
        self._root.right = new_node
        self._size += 1

    # ----------------------------
    # DFS traversals
    # ----------------------------
    def preorder(self) -> List[T]:
        """Root -> Left -> Right"""
        result: List[T] = []
        self._preorder(self._root, result)
        return result

    def inorder(self) -> List[T]:
        """Left -> Root -> Right"""
        result: List[T] = []
        self._inorder(self._root, result)
        return result

    def postorder(self) -> List[T]:
        """Left -> Right -> Root"""
        result: List[T] = []
        self._postorder(self._root, result)
        return result

    def _preorder(self, node: Optional[_Node[T]], out: List[T]) -> None:
        if node is None:
            return
        out.append(node.value)
        self._preorder(node.left, out)
        self._preorder(node.right, out)

    def _inorder(self, node: Optional[_Node[T]], out: List[T]) -> None:
        if node is None:
            return
        self._inorder(node.left, out)
        out.append(node.value)
        self._inorder(node.right, out)

    def _postorder(self, node: Optional[_Node[T]], out: List[T]) -> None:
        if node is None:
            return
        self._postorder(node.left, out)
        self._postorder(node.right, out)
        out.append(node.value)

    # ----------------------------
    # BFS traversal (level-order)
    # ----------------------------
    def bfs(self) -> List[T]:
        """Level-order traversal (uses Queue)."""
        if self._root is None:
            return []

        result: List[T] = []
        q: Queue[_Node[T]] = Queue()
        q.enqueue(self._root)

        while not q.is_empty():
            node = q.dequeue()
            result.append(node.value)

            if node.left is not None:
                q.enqueue(node.left)
            if node.right is not None:
                q.enqueue(node.right)

        return result

    def __iter__(self) -> Iterator[T]:
        """Default iteration: BFS (level-order)."""
        for v in self.bfs():
            yield v

    def __repr__(self) -> str:
        return f"BinaryTree({self.bfs()!r})"
