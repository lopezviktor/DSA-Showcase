from __future__ import annotations

import math
from collections.abc import Iterator


class BloomFilterError(ValueError):
    """Raised for invalid BloomFilter configuration."""


class BloomFilter:
    """Probabilistic membership filter using a bit array and k hash functions.

    Answers membership queries in O(k) time and O(m) space.  May report
    false positives but *never* false negatives.

    Unlike most data structures in this toolkit, BloomFilter is not generic:
    items are hashed and never stored, so any hashable type is accepted without
    a TypeVar.

    IDS use-cases
    -------------
    - First-pass check for known-malicious IPs/domains before an expensive
      HashMap lookup.
    - Memory-constrained edge devices (Raspberry Pi) filtering packet signatures.
    - Deduplication of seen flow identifiers in high-throughput network streams.
    - False-positive-tolerant early-warning layer in a multi-stage IDS pipeline.

    Sizing formulas (standard Bloom Filter math)
    --------------------------------------------
    Given desired capacity n and target false-positive rate p::

        m = ceil(-n * ln(p) / (ln 2)^2)   # bit-array size
        k = round((m / n) * ln 2)          # number of hash functions, min 1

    Parameters
    ----------
    capacity:
        Expected maximum number of items to be added at the target error rate.
    error_rate:
        Desired false-positive probability in (0, 1).  Default 0.01 (1 %).

    Raises
    ------
    BloomFilterError
        If ``capacity < 1`` or ``error_rate`` is not in the open interval (0, 1).
    """

    __slots__ = (
        "_capacity",
        "_error_rate",
        "_bit_count",
        "_hash_count",
        "_bits",
        "_num_added",
    )

    def __init__(self, capacity: int, error_rate: float = 0.01) -> None:
        if capacity < 1:
            raise BloomFilterError(f"capacity must be >= 1, got {capacity}")
        if not (0 < error_rate < 1):
            raise BloomFilterError(
                f"error_rate must be in (0, 1), got {error_rate}"
            )

        self._capacity: int = capacity
        self._error_rate: float = error_rate

        ln2 = math.log(2)
        m = math.ceil(-capacity * math.log(error_rate) / (ln2 ** 2))
        k = max(1, round((m / capacity) * ln2))

        self._bit_count: int = m
        self._hash_count: int = k
        self._bits: bytearray = bytearray(math.ceil(m / 8))
        self._num_added: int = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _bit_positions(self, item: object) -> Iterator[int]:
        """Yield *k* independent bit positions for *item*.

        Complexity: O(k)
        """
        m = self._bit_count
        for seed in range(self._hash_count):
            yield hash((item, seed)) % m

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def add(self, item: object) -> None:
        """Set the k bits corresponding to *item*.

        Complexity: O(k)
        """
        for pos in self._bit_positions(item):
            self._bits[pos // 8] |= 1 << (pos % 8)
        self._num_added += 1

    def contains(self, item: object) -> bool:
        """Return True if *item* is possibly in the filter.

        A True result may be a false positive.  A False result is definitive.

        Complexity: O(k)
        """
        for pos in self._bit_positions(item):
            if not (self._bits[pos // 8] & (1 << (pos % 8))):
                return False
        return True

    # ------------------------------------------------------------------
    # Derived / aggregate properties
    # ------------------------------------------------------------------

    def false_positive_rate(self) -> float:
        """Analytical estimate of the current false-positive probability.

        Formula::

            p = (1 - e^(-k * n_added / m))^k

        Returns 0.0 when no items have been added.

        Complexity: O(1)
        """
        if self._num_added == 0:
            return 0.0
        exponent = -self._hash_count * self._num_added / self._bit_count
        return (1 - math.exp(exponent)) ** self._hash_count

    def bit_count(self) -> int:
        """Size of the underlying bit array in bits (m).

        Complexity: O(1)
        """
        return self._bit_count

    def hash_count(self) -> int:
        """Number of hash functions used (k).

        Complexity: O(1)
        """
        return self._hash_count

    def capacity(self) -> int:
        """Expected maximum items at the target error rate.

        Complexity: O(1)
        """
        return self._capacity

    def num_added(self) -> int:
        """Total items added (not deduplicated).

        Complexity: O(1)
        """
        return self._num_added

    def is_empty(self) -> bool:
        """Return True if no items have been added yet.

        Complexity: O(1)
        """
        return self._num_added == 0

    def clear(self) -> None:
        """Reset all bits and the item counter.

        Complexity: O(m)
        """
        for i in range(len(self._bits)):
            self._bits[i] = 0
        self._num_added = 0

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __contains__(self, item: object) -> bool:
        """Support the ``in`` operator.  Delegates to :meth:`contains`.

        Complexity: O(k)
        """
        return self.contains(item)

    def __len__(self) -> int:
        """Return the number of items added.  Delegates to :meth:`num_added`.

        Complexity: O(1)
        """
        return self._num_added

    def __repr__(self) -> str:
        """Return a concise summary of the filter's configuration and state.

        Complexity: O(1)
        """
        return (
            f"BloomFilter(capacity={self._capacity}, "
            f"error_rate={self._error_rate}, "
            f"bit_count={self._bit_count}, "
            f"hash_count={self._hash_count}, "
            f"num_added={self._num_added})"
        )
