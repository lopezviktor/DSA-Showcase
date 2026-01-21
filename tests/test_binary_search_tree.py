from __future__ import annotations

from dsa_toolkit.binary_search_tree import BinarySearchTree


def test_new_tree_is_empty() -> None:
    bst: BinarySearchTree[float, str] = BinarySearchTree()
    assert bst.is_empty() is True
    assert bst.size() == 0
    assert len(bst) == 0
    assert bst.inorder() == []
    assert list(bst) == []
    assert "BinarySearchTree" in repr(bst)


def test_insert_and_find_exact_match() -> None:
    bst = BinarySearchTree[float, str]()
    bst.insert(0.2, "NORMAL")
    bst.insert(0.5, "SUSPICIOUS")
    bst.insert(0.8, "CRITICAL")

    assert bst.is_empty() is False
    assert bst.size() == 3

    assert bst.find(0.2) == "NORMAL"
    assert bst.find(0.5) == "SUSPICIOUS"
    assert bst.find(0.8) == "CRITICAL"
    assert bst.find(0.3) is None


def test_contains() -> None:
    bst = BinarySearchTree[int, str]()
    bst.insert(10, "A")

    assert bst.contains(10) is True
    assert bst.contains(9) is False


def test_insert_overwrites_on_duplicate_key() -> None:
    bst = BinarySearchTree[int, str]()
    bst.insert(10, "OLD")
    bst.insert(10, "NEW")

    assert bst.size() == 1  # size should NOT increase
    assert bst.find(10) == "NEW"
    assert bst.inorder() == [(10, "NEW")]


def test_inorder_returns_sorted_pairs() -> None:
    bst = BinarySearchTree[int, str]()
    bst.insert(50, "root")
    bst.insert(20, "left")
    bst.insert(80, "right")
    bst.insert(10, "ll")
    bst.insert(30, "lr")

    # inorder should be sorted by key
    assert bst.inorder() == [
        (10, "ll"),
        (20, "left"),
        (30, "lr"),
        (50, "root"),
        (80, "right"),
    ]

    # __iter__ yields inorder pairs
    assert list(bst) == bst.inorder()


def test_floor_on_empty_returns_none() -> None:
    bst = BinarySearchTree[float, str]()
    assert bst.floor(0.5) is None


def test_floor_exact_match() -> None:
    bst = BinarySearchTree[float, str]()
    bst.insert(0.2, "NORMAL")
    bst.insert(0.5, "SUSPICIOUS")
    bst.insert(0.8, "CRITICAL")

    assert bst.floor(0.5) == (0.5, "SUSPICIOUS")


def test_floor_between_thresholds() -> None:
    bst = BinarySearchTree[float, str]()
    bst.insert(0.2, "NORMAL")
    bst.insert(0.5, "SUSPICIOUS")
    bst.insert(0.8, "CRITICAL")

    # 0.67 should map to the greatest threshold <= 0.67 -> 0.5
    assert bst.floor(0.67) == (0.5, "SUSPICIOUS")


def test_floor_below_min_threshold_returns_none() -> None:
    bst = BinarySearchTree[float, str]()
    bst.insert(0.2, "NORMAL")
    bst.insert(0.5, "SUSPICIOUS")

    assert bst.floor(0.1) is None


def test_floor_above_max_threshold_returns_max() -> None:
    bst = BinarySearchTree[float, str]()
    bst.insert(0.2, "NORMAL")
    bst.insert(0.5, "SUSPICIOUS")
    bst.insert(0.8, "CRITICAL")

    assert bst.floor(0.99) == (0.8, "CRITICAL")


def test_repr_contains_values() -> None:
    bst = BinarySearchTree[int, str]()
    bst.insert(2, "B")
    bst.insert(1, "A")
    bst.insert(3, "C")

    r = repr(bst)
    assert "BinarySearchTree" in r
    assert "1" in r and "2" in r and "3" in r
