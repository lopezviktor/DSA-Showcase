from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, TypeVar

from .hash_map import HashMap

K = TypeVar("K")
V = TypeVar("V")


class LRUCacheKeyError(KeyError):
    """Raised when a key is not found in the LRUCache."""


@dataclass
class _Node(Generic[K, V]):
    """Internal doubly-linked list node for LRU Cache.

    Stores a key-value pair along with prev/next pointers so the cache
    can reorder nodes in O(1) without a linear scan.
    """

    key: K
    value: V
    prev: _Node[K, V] | None = field(default=None, repr=False)
    next: _Node[K, V] | None = field(default=None, repr=False)


class LRUCache(Generic[K, V]):
    """
    Least-Recently-Used Cache backed by a HashMap and an internal doubly-linked list.

    Combining these two structures achieves O(1) get and put:
    - HashMap provides O(1) key → node lookup.
    - Doubly-linked list provides O(1) node reordering (promote to MRU).

    Two sentinel nodes (_head / _tail) eliminate all boundary checks:
    - Nodes just after _head are the LRU end.
    - Nodes just before _tail are the MRU end.

    IDS use-cases:
        - Caching recent IP reputation lookups (evict stale entries automatically).
        - Rate-limiting per source IP (O(1) counter update, LRU eviction of idle IPs).
        - Caching DNS resolution results with bounded memory.

    Performance:
        - get:      O(1)
        - put:      O(1) amortized
        - contains: O(1)
        - peek:     O(1)
        - evict:    O(1)
        - size:     O(1)
        - capacity: O(1)
        - __repr__: O(n)
    """

    __slots__ = ("_capacity", "_map", "_head", "_tail")

    def __init__(self, capacity: int) -> None:
        """
        Initialise an empty LRU Cache.

        Args:
            capacity: Maximum number of entries the cache can hold (≥ 1).

        Raises:
            ValueError: If capacity is less than 1.

        Complexity: O(1)
        """
        if capacity < 1:
            raise ValueError(f"capacity must be >= 1, got {capacity}")
        self._capacity: int = capacity
        self._map: HashMap[K, _Node[K, V]] = HashMap()
        # Sentinels: _head.next is LRU; _tail.prev is MRU.
        self._head: _Node[K, V] = _Node(key=None, value=None)  # type: ignore[arg-type]
        self._tail: _Node[K, V] = _Node(key=None, value=None)  # type: ignore[arg-type]
        self._head.next = self._tail
        self._tail.prev = self._head

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _detach(self, node: _Node[K, V]) -> None:
        """Unlink *node* from its current position in the list. O(1)."""
        prev = node.prev
        nxt = node.next
        if prev is not None:
            prev.next = nxt
        if nxt is not None:
            nxt.prev = prev
        node.prev = None
        node.next = None

    def _attach_mru(self, node: _Node[K, V]) -> None:
        """Insert *node* immediately before the tail sentinel (MRU position). O(1)."""
        prev = self._tail.prev
        prev.next = node  # type: ignore[union-attr]
        node.prev = prev
        node.next = self._tail
        self._tail.prev = node

    def _move_to_mru(self, node: _Node[K, V]) -> None:
        """Detach *node* from its current position and reattach as MRU. O(1)."""
        self._detach(node)
        self._attach_mru(node)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, key: K) -> V:
        """
        Return the value associated with *key* and promote it to MRU.

        Args:
            key: The key to look up.

        Returns:
            The cached value.

        Raises:
            LRUCacheKeyError: If the key is not in the cache.

        Complexity: O(1)
        """
        if not self._map.contains_key(key):
            raise LRUCacheKeyError(key)
        node: _Node[K, V] = self._map.get(key)
        self._move_to_mru(node)
        return node.value

    def put(self, key: K, value: V) -> None:
        """
        Insert or update *key* → *value* in the cache.

        If the key already exists, its value is updated and the entry is
        promoted to MRU. If the cache is at capacity, the LRU entry is
        evicted before inserting.

        Args:
            key:   Hashable key.
            value: Value to cache.

        Complexity: O(1) amortized
        """
        if self._map.contains_key(key):
            node: _Node[K, V] = self._map.get(key)
            node.value = value
            self._move_to_mru(node)
            return

        if self._map.size() == self._capacity:
            lru_node = self._head.next
            assert lru_node is not None and lru_node is not self._tail
            self._detach(lru_node)
            self._map.delete(lru_node.key)

        new_node: _Node[K, V] = _Node(key=key, value=value)
        self._attach_mru(new_node)
        self._map.put(key, new_node)

    def contains(self, key: K) -> bool:
        """
        Return True if *key* is present in the cache. Does not alter order.

        Complexity: O(1)
        """
        return self._map.contains_key(key)

    def peek(self, key: K) -> V:
        """
        Return the value for *key* without changing its position in the cache.

        Args:
            key: The key to look up.

        Returns:
            The cached value.

        Raises:
            LRUCacheKeyError: If the key is not in the cache.

        Complexity: O(1)
        """
        if not self._map.contains_key(key):
            raise LRUCacheKeyError(key)
        return self._map.get(key).value

    def evict(self) -> tuple[K, V]:
        """
        Manually evict and return the LRU (least-recently-used) entry.

        Returns:
            A (key, value) tuple for the evicted entry.

        Raises:
            LRUCacheKeyError: If the cache is empty.

        Complexity: O(1)
        """
        if self.is_empty():
            raise LRUCacheKeyError("cache is empty")
        lru_node = self._head.next
        assert lru_node is not None and lru_node is not self._tail
        self._detach(lru_node)
        self._map.delete(lru_node.key)
        return lru_node.key, lru_node.value

    def is_empty(self) -> bool:
        """Return True if the cache contains no entries. Complexity: O(1)."""
        return self._map.is_empty()

    def size(self) -> int:
        """Return the current number of cached entries. Complexity: O(1)."""
        return self._map.size()

    def capacity(self) -> int:
        """Return the maximum number of entries this cache can hold. Complexity: O(1)."""
        return self._capacity

    # ------------------------------------------------------------------
    # Dunder methods
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Support len(cache) — delegates to size(). Complexity: O(1)."""
        return self.size()

    def __contains__(self, key: object) -> bool:
        """Support `key in cache` — delegates to contains(). Complexity: O(1)."""
        return self.contains(key)  # type: ignore[arg-type]

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation ordered MRU → LRU.

        Complexity: O(n)
        """
        entries: list[str] = []
        node = self._tail.prev
        while node is not None and node is not self._head:
            entries.append(f"{node.key!r}: {node.value!r}")
            node = node.prev
        inner = ", ".join(entries)
        return f"LRUCache(capacity={self._capacity}, entries=[{inner}])"
