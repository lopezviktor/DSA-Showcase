# DSA-Showcase

Showcase of **Data Structures & Algorithms implemented from scratch in Python**, with a strong focus on:
- clean abstractions
- correct complexity guarantees
- defensive APIs
- full unit test coverage
- CI validation

This repository is designed as a **foundational engineering portfolio**, not as a collection of coding exercises.

---

## 🎯 Goals of this project

- Build a **deep understanding** of core data structures
- Learn to reason about **trade-offs, constraints and guarantees**
- Practice writing **production-quality code** (tests, CI, clear APIs)
- Create a solid base for future work in:
  - Backend engineering
  - Systems design
  - AI / ML
  - Advanced algorithms

This project prioritizes **clarity and correctness over cleverness**.

---

## 🧱 Implemented Data Structures

### Stack
**LIFO (Last-In, First-Out)** abstraction.

**Typical use cases**
- Call stack
- Undo / backtracking
- Expression evaluation

**Key properties**
- Restricted access (top only)
- All core operations are **O(1)**
- Clear error handling for empty stack

---

### Queue
**FIFO (First-In, First-Out)** abstraction.

**Typical use cases**
- Task queues
- Request processing
- Event handling
- Producer / consumer patterns

**Key properties**
- Guarantees order of arrival
- Decouples producers and consumers
- O(1) operations via index-based design (no shifting)

---

### Deque (Double-Ended Queue)
A **controlled combination of Stack and Queue**.

**Typical use cases**
- Sliding window algorithms
- Undo / redo systems
- Caches
- Algorithms requiring access to both ends

**Key properties**
- Insert/remove from both ends
- Circular buffer implementation
- O(1) amortized operations
- Still a restricted abstraction (not a list)

---

### Linked List (Singly)
A **node-based linear structure** where elements are linked via references instead of contiguous memory.

**Typical use cases**
- Dynamic collections with frequent insertions/removals
- Building blocks for trees and graphs
- Scenarios where index-based access is not required

**Key properties**
- Non-contiguous memory layout
- O(1) insertions/removals at the head
- O(1) append with tail reference
- O(n) search and access

---

### Linked List (Doubly)
A **bidirectional node-based linear structure** where each element keeps references to both the next and previous nodes.

**Typical use cases**
- Navigation systems (forward / backward)
- LRU caches
- Undo / redo mechanisms
- Algorithms requiring efficient removals from both ends

**Key properties**
- Each node stores `next` and `prev` references
- O(1) insertions/removals at both head and tail
- Efficient backward traversal via `prev`
- Higher memory cost compared to singly linked lists

---

### Binary Tree
A **hierarchical, node-based structure** where each node has up to two children (`left` and `right`).
This implementation represents a **generic Binary Tree** (not a Binary Search Tree).

**Typical use cases**
- Decision engines and rule evaluation
- Hierarchical data modeling (configs, permissions)
- Expression trees
- Foundations for more advanced trees (BST, heaps, balanced trees)

**Key properties**
- Non-linear, hierarchical structure
- Nodes are traversed, not indexed
- Supports DFS traversals (pre-order, in-order, post-order)
- Supports BFS traversal (level-order) using a queue

---

### Binary Search Tree (BST)
A **Binary Tree with an ordering invariant**, where for each node:
- keys in the left subtree are smaller than the node key
- keys in the right subtree are greater than the node key

This implementation is **generic and unbalanced**, focusing on clarity and correctness rather than self-balancing.

**Typical use cases**
- Threshold-based decision systems
- Efficient lookup of ordered rules
- Mapping numeric scores to actions or labels
- Foundations for decision trees and interpretable ML models

**Key properties**
- Key–value structure (`key` determines order, `value` stores associated data)
- Efficient search and insertion on average (O(log n))
- In-order traversal returns elements sorted by key
- Supports `floor(key)` queries (largest key ≤ input), useful for threshold mapping

---

### Priority Queue (Heap)
A **Priority Queue** is an abstraction that always processes the element with the highest priority first.
Internally, it is implemented using a **binary heap**, but the exposed API focuses on *behavior*, not structure.

This implementation is a **stable max-priority queue**:
- higher priority values are processed first
- when priorities are equal, insertion order (FIFO) is preserved

**Typical use cases**
- Alert prioritization in monitoring and IDS systems
- Task scheduling
- Top-K queries (e.g. most critical events)
- Event-driven systems where urgency matters

**Key properties**
- Insert (`push`) and remove (`pop`) in O(log n)
- Peek highest-priority element in O(1)
- Stable ordering for equal priorities
- Array-backed heap for predictable memory usage
- Supports non-destructive `top_k(k)` queries

---

### Graphs (Directed, Weighted)
A **directed graph** models entities (nodes) and directional relationships (edges) between them.
This implementation uses an **adjacency list**, supports **optional edge weights**, and integrates the previously built `Queue` (BFS) and `Stack` (DFS).

**Typical use cases**
- Network and topology modeling
- Intrusion Detection Systems (IDS) and lateral-movement analysis
- Dependency graphs and reachability checks
- Shortest-path routing between IoT nodes (edge vs cloud cost modelling)

**Key properties**
- Directed edges with automatic node creation on edge insertion
- Adjacency-list representation; optional float weights per edge
- Breadth-First Search (BFS) using `Queue` — level-based reachability and unweighted shortest path
- Depth-First Search (DFS) using `Stack` — path existence
- **Dijkstra's algorithm** for weighted shortest path (O((V + E) log V))
- `shortest_path` dispatcher: Dijkstra when weights are present, BFS otherwise
- Explicit error handling for missing nodes

---

### HashMap
A **generic hash map** using **separate chaining** for collision resolution.

**Typical use cases**
- O(1) lookup of suspicious IPs → alert counts in IDS
- Feature → normalized-value mapping during ML inference
- Frequency counting of network traffic patterns

**Key properties**
- Dynamic resizing: doubles capacity when load factor exceeds 0.75
- `put`, `get`, `delete`, `contains_key` all O(1) amortized
- `keys()`, `values()`, `items()` in O(n)
- `__contains__` and `__len__` dunder support

---

### Sorting Algorithms
Four classic comparison-based sorting algorithms, each implemented as a standalone function operating on a list in-place (where applicable).

| Algorithm | Best | Average | Worst | Space | Notes |
|-----------|------|---------|-------|-------|-------|
| `insertion_sort` | O(n) | O(n²) | O(n²) | O(1) | Stable; efficient on nearly-sorted data |
| `merge_sort` | O(n log n) | O(n log n) | O(n log n) | O(n) | Stable; divide-and-conquer |
| `quick_sort` | O(n log n) | O(n log n) | O(n²) | O(log n) | Unstable; median-of-three pivot |
| `heap_sort` | O(n log n) | O(n log n) | O(n log n) | O(1) | Unstable; in-place heapify |

**Typical use cases**
- Ranking network events by severity or timestamp
- Preprocessing feature vectors before ML inference
- Demonstrating trade-offs between stability, memory, and worst-case guarantees

---

### Trie (Prefix Tree)
A **Trie** stores string keys character by character, giving O(m) search, insert, and delete independent of the number of stored words (where m is the key length).

**Typical use cases**
- **IP prefix matching**: insert CIDR prefixes, use `starts_with` to detect blacklisted address ranges
- **Domain blacklists**: exact C&C domain lookup with `contains`; subdomain detection with `starts_with`
- **Autocomplete / enumeration**: `words_with_prefix` lists all matching domains or IPs under a given prefix

**Key properties**
- Generic key → value mapping (`Trie[V]`)
- `insert`, `search`, `contains`, `starts_with`, `words_with_prefix` all O(m)
- `delete` with recursive post-order **node pruning** — dead leaf nodes are removed automatically
- `words_with_prefix("")` enumerates all stored words (sorted)
- `__contains__` and `__len__` dunder support

---

### LRU Cache
A **Least Recently Used Cache** that evicts the least recently accessed item when capacity is exceeded. Implemented via **composition** of `HashMap` (O(1) lookup) and `DoublyLinkedList` (O(1) eviction).

**Typical use cases**
- Caching repeated DNS resolutions in a network monitor
- Bounding memory usage in high-throughput packet processing
- Storing recent alert records in a sliding window

**Key properties**
- `get` and `put` both O(1)
- Strict capacity enforcement — oldest item is evicted automatically
- `__contains__`, `__len__`, and `__getitem__` / `__setitem__` dunder support

---

### Bloom Filter
A **probabilistic membership filter** that answers "is this item in the set?" in O(k) time using a bit array of size m and k independent hash functions. May return false positives, never false negatives.

**Typical use cases**
- First-pass check for known-malicious IPs/domains before an expensive HashMap lookup
- Memory-constrained edge devices (Raspberry Pi) filtering packet signatures
- Deduplication of seen flow identifiers in high-throughput network streams
- False-positive-tolerant early-warning layer in a multi-stage IDS pipeline

**Key properties**
- No third-party dependencies — `bytearray` bit array, hash functions via `hash((item, seed)) % m`
- Sized from desired capacity `n` and target false-positive rate `p` using standard Bloom Filter math
- `add` and `contains` in O(k); analytical `false_positive_rate()` in O(1)
- No deletion — only `clear()` resets the filter
- Accepts any hashable type (no `Generic[T]` needed — items are never stored)

---

## 🧪 Testing strategy

Tests are organized following the **testing pyramid**:

**Unit tests** (`test_*.py` per module) — each data structure is tested in isolation:
- All public methods and error paths
- Internal branches and edge cases
- Current coverage: **100% across all modules**

**Integration tests** (`test_ids_pipeline.py`) — a multi-stage IDS pipeline chains three structures together:

```
Packet IP → BloomFilter (O(k), probabilistic first-pass)
          → HashMap     (O(1), exact lookup — eliminates false positives)
          → PriorityQueue (max-heap, severity-ordered alert queue)
```

This tests cross-module composition under realistic IoT/IDS workloads (mixed traffic, high-throughput streams, full pipeline reset and reload).

Tests are written using `pytest`.

---

## 🔁 Continuous Integration

This project uses **GitHub Actions** to automatically:

- Run tests on multiple Python versions
- Enforce coverage thresholds
- Prevent regressions

CI is treated as a **first-class requirement**, not an afterthought.

---

## 🗂 Project structure

```text
src/dsa_toolkit/
├── stack.py
├── queue.py
├── deque.py
├── linked_list.py
├── doubly_linked_list.py
├── binary_tree.py
├── binary_search_tree.py
├── priority_queue.py
├── graph.py
├── hash_map.py
├── sorting.py
├── trie.py
├── lru_cache.py
├── bloom_filter.py
└── __init__.py

tests/
├── test_stack.py
├── test_queue.py
├── test_deque.py
├── test_linked_list.py
├── test_doubly_linked_list.py
├── test_binary_tree.py
├── test_binary_search_tree.py
├── test_priority_queue.py
├── test_graph.py
├── test_hash_map.py
├── test_sorting.py
├── test_trie.py
├── test_lru_cache.py
├── test_bloom_filter.py
└── test_ids_pipeline.py   ← integration tests
```

The `src/` layout is intentionally used to avoid import ambiguities and mirror real-world Python packages.

---

## 🚀 How to run locally

Create a virtual environment and install dependencies:
```bash
pip install -e ".[dev]"
```
Run tests:
```bash
pytest -q
```

## Roadmap

Potential upcoming additions:
- Balanced BST (AVL or Red-Black Tree)
- Union-Find (Disjoint Set)
- Skip List
- Dynamic programming patterns

Each addition will follow the same principles:
clear abstractions -> correct complexity -> tests -> CI.

## Philosophy

Data structures are not about storing data.
They are about controlling how data can be accessed.

This repository exists to internalize that idea.
