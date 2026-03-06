# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (editable + dev extras)
pip install -e ".[dev]"

# Run all tests with coverage
pytest

# Run a single test file
pytest tests/test_stack.py

# Run a single test by name
pytest tests/test_stack.py::test_push_pop

# Lint
ruff check src tests

# Type check
mypy src
```

CI enforces `--cov-fail-under=95`.

## Architecture

All data structures live in `src/dsa_toolkit/` as individual modules and are re-exported from `__init__.py`. Each module follows the same pattern:

- **Custom exception** subclassing a stdlib error (e.g. `EmptyStackError(IndexError)`, `NodeNotFoundError(KeyError)`)
- **Generic class** using `TypeVar` and `Generic[T]`
- `__slots__` on every class
- Docstrings with explicit complexity annotations per method

**Cross-module dependencies** (intentional, to demonstrate composition):
- `Graph` imports and uses `Queue` (for BFS) and `Stack` (for DFS)
- `PriorityQueue` is array-backed with a tie-breaking insertion counter for stable ordering

**Conventions:**
- Python ≥ 3.11 required
- `from __future__ import annotations` in every module
- Errors are raised (never returned); empty-state checks always precede mutation
- `src/` layout — import as `from dsa_toolkit.stack import Stack`, not relative imports from outside the package
