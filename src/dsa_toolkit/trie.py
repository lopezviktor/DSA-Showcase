from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, TypeVar

V = TypeVar("V")


class TrieKeyError(KeyError):
    """Raised when a word is not found in the Trie."""

    pass


@dataclass
class _TrieNode(Generic[V]):
    """Internal node for the Trie. Not part of the public API."""

    children: dict[str, _TrieNode[V]] = field(default_factory=dict)
    value: V | None = None
    is_end: bool = False


class Trie(Generic[V]):
    """
    A generic Trie (prefix tree) mapping string keys to values.

    Each character of a key occupies one node level. Search, insert, and
    delete are all O(m) where m is the length of the key — independent of
    the number of stored words.

    IDS use-cases:
        - IP prefix matching: insert CIDR prefixes (e.g. "192.168.1."),
          use starts_with() or words_with_prefix() to detect blacklisted ranges.
        - Domain blacklist: insert known C&C domains, use contains() for exact
          lookup, starts_with() to detect subdomains of a malicious TLD.
        - Autocomplete / enumeration: words_with_prefix() lists all matching
          domains or IPs under a given prefix.

    Performance:
        - insert:              O(m)
        - search:              O(m)
        - contains:            O(m)
        - starts_with:         O(m)
        - words_with_prefix:   O(m + k), k = total chars in matching words
        - delete:              O(m)
        - size / is_empty:     O(1)
        - __len__:             O(1)
        - __contains__:        O(m)
        - __repr__:            O(n), n = total stored words
    """

    __slots__ = ("_root", "_size")

    def __init__(self) -> None:
        """Initialize an empty Trie."""
        self._root: _TrieNode[V] = _TrieNode()
        self._size: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def insert(self, word: str, value: V) -> None:
        """
        Insert *word* with an associated *value*.

        If the word already exists its value is overwritten; the size
        counter is only incremented for genuinely new words.

        Args:
            word:  The string key (may be empty).
            value: Arbitrary value to associate with the word.

        Complexity: O(m), m = len(word)
        """
        node = self._root
        for char in word:
            if char not in node.children:
                node.children[char] = _TrieNode()
            node = node.children[char]
        if not node.is_end:
            self._size += 1
        node.is_end = True
        node.value = value

    def search(self, word: str) -> V:
        """
        Return the value associated with *word*.

        Args:
            word: The exact string key to look up.

        Returns:
            The value stored for *word*.

        Raises:
            TrieKeyError: If *word* is not present.

        Complexity: O(m), m = len(word)
        """
        node = self._find_node(word)
        if node is None or not node.is_end:
            raise TrieKeyError(word)
        return node.value  # type: ignore[return-value]

    def contains(self, word: str) -> bool:
        """
        Return True if *word* exists as a complete key.

        Complexity: O(m), m = len(word)
        """
        node = self._find_node(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        """
        Return True if any stored word begins with *prefix*.

        An empty prefix always returns True when the trie is non-empty
        (and True on an empty trie, because no word contradicts it).

        Complexity: O(m), m = len(prefix)
        """
        return self._find_node(prefix) is not None

    def words_with_prefix(self, prefix: str) -> list[str]:
        """
        Return all stored words that begin with *prefix*, sorted lexicographically.

        Returns an empty list if no words match.

        Args:
            prefix: The prefix to search for (empty string matches all words).

        Returns:
            Sorted list of matching words.

        Complexity: O(m + k), m = len(prefix), k = total chars in results
        """
        node = self._find_node(prefix)
        if node is None:
            return []
        results: list[str] = []
        self._collect(node, prefix, results)
        return sorted(results)

    def delete(self, word: str) -> None:
        """
        Remove *word* from the Trie, pruning now-unused nodes.

        Args:
            word: The exact string key to remove.

        Raises:
            TrieKeyError: If *word* is not present.

        Complexity: O(m), m = len(word)
        """
        self._delete_recursive(self._root, word, 0)
        self._size -= 1

    def is_empty(self) -> bool:
        """
        Return True if the Trie contains no words.

        Complexity: O(1)
        """
        return self._size == 0

    def size(self) -> int:
        """
        Return the number of words stored.

        Complexity: O(1)
        """
        return self._size

    # ------------------------------------------------------------------
    # Dunder methods
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Support len(trie). Complexity: O(1)."""
        return self._size

    def __contains__(self, word: object) -> bool:
        """Support `word in trie` — delegates to contains(). Complexity: O(m)."""
        if not isinstance(word, str):
            return False
        return self.contains(word)

    def __repr__(self) -> str:
        """Return a developer-friendly representation. Complexity: O(n)."""
        return f"Trie(size={self._size})"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find_node(self, prefix: str) -> _TrieNode[V] | None:
        """
        Traverse the trie following *prefix* and return the final node.

        Returns None if any character in *prefix* is missing.
        """
        node = self._root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def _collect(self, node: _TrieNode[V], current: str, results: list[str]) -> None:
        """DFS accumulator: append every complete word reachable from *node*."""
        if node.is_end:
            results.append(current)
        for char, child in node.children.items():
            self._collect(child, current + char, results)

    def _delete_recursive(self, node: _TrieNode[V], word: str, depth: int) -> None:
        """
        Recursively delete *word* starting at *node* / *depth*.

        Raises TrieKeyError if the path doesn't exist or the terminal node
        is not marked as a word end.

        Post-order pruning: a node is removed from its parent's children dict
        when it has no remaining children and is not itself a word end.
        """
        if depth == len(word):
            if not node.is_end:
                raise TrieKeyError(word)
            node.is_end = False
            node.value = None
            return

        char = word[depth]
        child = node.children.get(char)
        if child is None:
            raise TrieKeyError(word)

        self._delete_recursive(child, word, depth + 1)

        # Prune child if it became a dead leaf
        if not child.is_end and not child.children:
            del node.children[char]
