from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Generic, Iterable, List, Set, Tuple, TypeVar

from dsa_toolkit.queue import Queue
from dsa_toolkit.stack import Stack

T = TypeVar("T")


class NodeNotFoundError(KeyError):
    """Raised when a requested node does not exist in the graph."""

    pass


class Graph(Generic[T]):
    """
    Directed graph using an adjacency list.

    - Nodes are generic (T).
    - Adjacency uses sets to avoid duplicate edges.
    - add_edge() auto-creates missing nodes (useful for learning topology from traffic).
    - BFS uses Queue; DFS uses Stack.
    """

    __slots__ = ("_adj",)

    def __init__(self) -> None:
        self._adj: Dict[T, Set[T]] = {}

    # ----------------------------
    # Nodes
    # ----------------------------
    def add_node(self, node: T) -> None:
        self._adj.setdefault(node, set())

    def has_node(self, node: T) -> bool:
        return node in self._adj

    def nodes(self) -> Set[T]:
        return set(self._adj.keys())

    # ----------------------------
    # Edges
    # ----------------------------
    def add_edge(self, src: T, dst: T) -> None:
        # Auto-create nodes
        self.add_node(src)
        self.add_node(dst)
        self._adj[src].add(dst)

    def has_edge(self, src: T, dst: T) -> bool:
        return src in self._adj and dst in self._adj[src]

    def neighbors(self, node: T) -> Set[T]:
        if node not in self._adj:
            raise NodeNotFoundError(f"Node not found: {node!r}")
        return set(self._adj[node])

    def edges(self) -> Set[Tuple[T, T]]:
        out: Set[Tuple[T, T]] = set()
        for src, nbrs in self._adj.items():
            for dst in nbrs:
                out.add((src, dst))
        return out

    def out_degree(self, node: T) -> int:
        if node not in self._adj:
            raise NodeNotFoundError(f"Node not found: {node!r}")
        return len(self._adj[node])

    def in_degree(self, node: T) -> int:
        if node not in self._adj:
            raise NodeNotFoundError(f"Node not found: {node!r}")
        count = 0
        for src, nbrs in self._adj.items():
            if node in nbrs:
                count += 1
        return count

    # ----------------------------
    # Traversals
    # ----------------------------
    def bfs(self, start: T) -> List[T]:
        """Breadth-first traversal from start."""
        if start not in self._adj:
            raise NodeNotFoundError(f"Node not found: {start!r}")

        visited: Set[T] = set()
        order: List[T] = []

        q: Queue[T] = Queue()
        q.enqueue(start)
        visited.add(start)

        while not q.is_empty():
            node = q.dequeue()
            order.append(node)

            for nbr in self._adj[node]:
                if nbr not in visited:
                    visited.add(nbr)
                    q.enqueue(nbr)

        return order

    def dfs(self, start: T) -> List[T]:
        """Depth-first traversal from start (iterative using Stack)."""
        if start not in self._adj:
            raise NodeNotFoundError(f"Node not found: {start!r}")

        visited: Set[T] = set()
        order: List[T] = []

        st: Stack[T] = Stack()
        st.push(start)

        while not st.is_empty():
            node = st.pop()
            if node in visited:
                continue

            visited.add(node)
            order.append(node)

            # Push neighbors so that we go "deep". To make order deterministic,
            # we push in reverse sorted order when possible.
            # Since T may not be sortable, we fallback to arbitrary set order.
            nbrs = list(self._adj[node])
            try:
                nbrs.sort(reverse=True)  # type: ignore[call-arg]
            except TypeError:
                pass

            for nbr in nbrs:
                if nbr not in visited:
                    st.push(nbr)

        return order

    def __repr__(self) -> str:
        return f"Graph(nodes={len(self._adj)}, edges={len(self.edges())})"
