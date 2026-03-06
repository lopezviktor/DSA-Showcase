from __future__ import annotations

from typing import Dict, Generic, List, Optional, Set, Tuple, TypeVar

from dsa_toolkit.priority_queue import PriorityQueue
from dsa_toolkit.queue import Queue
from dsa_toolkit.stack import Stack

T = TypeVar("T")


class NodeNotFoundError(KeyError):
    """Raised when a requested node does not exist in the graph."""

    pass


class Graph(Generic[T]):
    """
    Directed weighted graph using an adjacency list.

    - Nodes are generic (T).
    - Adjacency uses dicts mapping neighbor -> weight (float) to support weighted edges.
      Iterating the dict yields keys (neighbors), so BFS/DFS are unchanged.
    - add_edge() auto-creates missing nodes (useful for learning topology from traffic).
    - BFS uses Queue; DFS uses Stack.
    - Dijkstra uses PriorityQueue (max-heap with negated distances as min-heap).
    """

    __slots__ = ("_adj",)

    def __init__(self) -> None:
        self._adj: Dict[T, Dict[T, float]] = {}

    # ----------------------------
    # Nodes
    # ----------------------------
    def add_node(self, node: T) -> None:
        self._adj.setdefault(node, {})

    def has_node(self, node: T) -> bool:
        return node in self._adj

    def nodes(self) -> Set[T]:
        return set(self._adj.keys())

    # ----------------------------
    # Edges
    # ----------------------------
    def add_edge(self, src: T, dst: T, weight: float = 1.0) -> None:
        # Auto-create nodes
        self.add_node(src)
        self.add_node(dst)
        self._adj[src][dst] = weight

    def has_edge(self, src: T, dst: T) -> bool:
        return src in self._adj and dst in self._adj[src]

    def weight(self, src: T, dst: T) -> float:
        """Return the weight of edge (src, dst). Raises NodeNotFoundError if edge absent."""
        if not self.has_edge(src, dst):
            raise NodeNotFoundError(f"Edge not found: ({src!r}, {dst!r})")
        return self._adj[src][dst]

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

    def weighted_edges(self) -> Set[Tuple[T, T, float]]:
        """Return all edges as (src, dst, weight) triples."""
        out: Set[Tuple[T, T, float]] = set()
        for src, nbrs in self._adj.items():
            for dst, w in nbrs.items():
                out.add((src, dst, w))
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

    # ----------------------------
    # Shortest paths
    # ----------------------------
    def bfs_shortest_path(self, start: T, end: T) -> Optional[List[T]]:
        """
        Return the shortest path (fewest hops) from start to end using BFS.

        Returns [start] if start == end.
        Returns None if end is not reachable from start.
        Raises NodeNotFoundError if start or end do not exist.

        Complexity: O(V + E)
        """
        if start not in self._adj:
            raise NodeNotFoundError(f"Node not found: {start!r}")
        if end not in self._adj:
            raise NodeNotFoundError(f"Node not found: {end!r}")

        if start == end:
            return [start]

        visited: Set[T] = {start}
        parent: Dict[T, T] = {}

        q: Queue[T] = Queue()
        q.enqueue(start)

        while not q.is_empty():
            node = q.dequeue()
            for nbr in self._adj[node]:
                if nbr not in visited:
                    visited.add(nbr)
                    parent[nbr] = node
                    if nbr == end:
                        # Reconstruct path
                        path: List[T] = []
                        cur: T = end
                        while cur != start:
                            path.append(cur)
                            cur = parent[cur]
                        path.append(start)
                        path.reverse()
                        return path
                    q.enqueue(nbr)

        return None

    def dijkstra(self, start: T) -> Dict[T, float]:
        """
        Compute shortest distances from start to all reachable nodes (Dijkstra).

        Uses PriorityQueue as a min-heap by negating distances.
        Returns {node: distance} for every reachable node (including start at 0.0).
        Raises NodeNotFoundError if start does not exist.

        Complexity: O((V + E) log V)
        """
        if start not in self._adj:
            raise NodeNotFoundError(f"Node not found: {start!r}")

        # Max-heap used as min-heap: store (-distance) as priority.
        dist: Dict[T, float] = {start: 0.0}
        pq: PriorityQueue[float, T] = PriorityQueue()
        pq.push(-0.0, start)

        while not pq.is_empty():
            neg_d, node = pq.pop()
            d = -neg_d
            if d > dist.get(node, float("inf")):
                continue  # stale entry
            for nbr, w in self._adj[node].items():
                new_d = d + w
                if new_d < dist.get(nbr, float("inf")):
                    dist[nbr] = new_d
                    pq.push(-new_d, nbr)

        return dist

    def shortest_path(self, start: T, end: T) -> Optional[List[T]]:
        """
        Return the shortest weighted path from start to end using Dijkstra.

        Returns [start] if start == end.
        Returns None if end is not reachable from start.
        Raises NodeNotFoundError if start or end do not exist.

        Complexity: O((V + E) log V)
        """
        if start not in self._adj:
            raise NodeNotFoundError(f"Node not found: {start!r}")
        if end not in self._adj:
            raise NodeNotFoundError(f"Node not found: {end!r}")

        if start == end:
            return [start]

        dist: Dict[T, float] = {start: 0.0}
        parent: Dict[T, T] = {}

        pq: PriorityQueue[float, T] = PriorityQueue()
        pq.push(-0.0, start)

        while not pq.is_empty():
            neg_d, node = pq.pop()
            d = -neg_d
            if d > dist.get(node, float("inf")):
                continue  # stale entry
            if node == end:
                break
            for nbr, w in self._adj[node].items():
                new_d = d + w
                if new_d < dist.get(nbr, float("inf")):
                    dist[nbr] = new_d
                    parent[nbr] = node
                    pq.push(-new_d, nbr)

        if end not in dist:
            return None

        # Reconstruct path
        path: List[T] = []
        cur: T = end
        while cur != start:
            path.append(cur)
            cur = parent[cur]
        path.append(start)
        path.reverse()
        return path

    def __repr__(self) -> str:
        return f"Graph(nodes={len(self._adj)}, edges={len(self.edges())})"
