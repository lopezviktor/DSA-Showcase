from __future__ import annotations

from typing import Generic, List, Optional, Set, Tuple, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class KeyNotFoundError(KeyError):
    """Raised when a key is not found in the HashMap."""

    pass


class HashMap(Generic[K, V]):
    """
    A generic hash map using separate chaining for collision resolution.

    Each bucket holds a list of (key, value) pairs. When the load factor
    exceeds 0.75, the internal array doubles in size and all entries are
    rehashed — keeping average-case operations O(1) amortized.

    IDS use-cases:
        - O(1) lookup of suspicious IPs → alert counts
        - O(1) feature → normalized_value mapping during inference
        - Frequency counting of network traffic patterns

    Performance:
        - put:           O(1) amortized
        - get:           O(1) average
        - delete:        O(1) average
        - contains_key:  O(1) average
        - keys/values/items: O(n)
        - size/is_empty: O(1)
        - clear:         O(1)
    """

    __slots__ = ("_buckets", "_size", "_capacity")

    _DEFAULT_CAPACITY: int = 16
    _LOAD_FACTOR: float = 0.75

    def __init__(self) -> None:
        """Initialize an empty HashMap with default capacity of 16."""
        self._capacity: int = self._DEFAULT_CAPACITY
        self._size: int = 0
        self._buckets: List[List[Tuple[K, V]]] = [[] for _ in range(self._capacity)]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _index(self, key: K) -> int:
        """
        Compute the bucket index for a given key.

        Complexity: O(1)
        """
        return hash(key) % self._capacity

    def _resize(self) -> None:
        """
        Double the capacity and rehash all existing entries.

        Called automatically when load factor exceeds 0.75.

        Complexity: O(n)
        """
        old_buckets = self._buckets
        self._capacity *= 2
        self._buckets = [[] for _ in range(self._capacity)]
        self._size = 0
        for bucket in old_buckets:
            for key, value in bucket:
                self.put(key, value)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def put(self, key: K, value: V) -> None:
        """
        Insert or update the mapping key → value.

        If the key already exists, its value is updated in-place without
        incrementing the size. Triggers a resize when the load factor
        exceeds 0.75 after insertion.

        Args:
            key:   Hashable key.
            value: Associated value.

        Complexity: O(1) amortized
        """
        idx = self._index(key)
        bucket = self._buckets[idx]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self._size += 1
        if self._size / self._capacity > self._LOAD_FACTOR:
            self._resize()

    def get(self, key: K) -> V:
        """
        Return the value associated with key.

        Args:
            key: The key to look up.

        Returns:
            The value mapped to key.

        Raises:
            KeyNotFoundError: If key is not present in the map.

        Complexity: O(1) average
        """
        idx = self._index(key)
        for k, v in self._buckets[idx]:
            if k == key:
                return v
        raise KeyNotFoundError(key)

    def delete(self, key: K) -> None:
        """
        Remove the mapping for key.

        Args:
            key: The key to remove.

        Raises:
            KeyNotFoundError: If key is not present in the map.

        Complexity: O(1) average
        """
        idx = self._index(key)
        bucket = self._buckets[idx]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self._size -= 1
                return
        raise KeyNotFoundError(key)

    def contains_key(self, key: K) -> bool:
        """
        Return True if key exists in the map.

        Complexity: O(1) average
        """
        idx = self._index(key)
        return any(k == key for k, _ in self._buckets[idx])

    def keys(self) -> Set[K]:
        """
        Return a set of all keys in the map.

        Complexity: O(n)
        """
        return {k for bucket in self._buckets for k, _ in bucket}

    def values(self) -> List[V]:
        """
        Return a list of all values in the map.

        Complexity: O(n)
        """
        return [v for bucket in self._buckets for _, v in bucket]

    def items(self) -> Set[Tuple[K, V]]:
        """
        Return a set of all (key, value) pairs in the map.

        Complexity: O(n)
        """
        return {(k, v) for bucket in self._buckets for k, v in bucket}

    def size(self) -> int:
        """
        Return the number of key-value pairs stored.

        Complexity: O(1)
        """
        return self._size

    def is_empty(self) -> bool:
        """
        Return True if the map contains no entries.

        Complexity: O(1)
        """
        return self._size == 0

    def clear(self) -> None:
        """
        Remove all entries and reset to default capacity.

        Complexity: O(1)
        """
        self._capacity = self._DEFAULT_CAPACITY
        self._size = 0
        self._buckets = [[] for _ in range(self._capacity)]

    # ------------------------------------------------------------------
    # Dunder methods
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Support len(map) — delegates to size(). Complexity: O(1)."""
        return self.size()

    def __contains__(self, key: object) -> bool:
        """Support `key in map` — delegates to contains_key(). Complexity: O(1) average."""
        return self.contains_key(key)  # type: ignore[arg-type]

    def __repr__(self) -> str:
        """Return a developer-friendly representation. Complexity: O(n)."""
        return f"HashMap(size={self._size}, capacity={self._capacity})"
