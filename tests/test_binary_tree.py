import pytest

from dsa_toolkit.binary_tree import BinaryTree, EmptyBinaryTreeError


def test_new_tree_is_empty_by_default() -> None:
    t: BinaryTree[int] = BinaryTree()
    assert t.is_empty() is True
    assert t.size() == 0
    assert len(t) == 0
    assert t.bfs() == []
    assert t.preorder() == []
    assert t.inorder() == []
    assert t.postorder() == []
    assert list(t) == []
    assert "BinaryTree" in repr(t)


def test_root_value_on_empty_raises() -> None:
    t: BinaryTree[int] = BinaryTree()
    with pytest.raises(EmptyBinaryTreeError):
        _ = t.root_value()


def test_tree_with_root_value() -> None:
    t = BinaryTree(10)
    assert t.is_empty() is False
    assert t.size() == 1
    assert len(t) == 1
    assert t.root_value() == 10
    assert t.bfs() == [10]
    assert t.preorder() == [10]
    assert t.inorder() == [10]
    assert t.postorder() == [10]


def test_insert_left_on_empty_creates_root() -> None:
    t: BinaryTree[int] = BinaryTree()
    t.insert_left(1)
    assert t.root_value() == 1
    assert t.size() == 1
    assert t.bfs() == [1]


def test_insert_right_on_empty_creates_root() -> None:
    t: BinaryTree[int] = BinaryTree()
    t.insert_right(1)
    assert t.root_value() == 1
    assert t.size() == 1
    assert t.bfs() == [1]


def test_insert_left_and_right_under_root() -> None:
    # Build:
    #     A
    #    / \
    #   B   C
    t = BinaryTree("A")
    t.insert_left("B")
    t.insert_right("C")

    assert t.size() == 3
    # BFS visits by levels: A, B, C
    assert t.bfs() == ["A", "B", "C"]
    # DFS traversals
    assert t.preorder() == ["A", "B", "C"]
    assert t.inorder() == ["B", "A", "C"]
    assert t.postorder() == ["B", "C", "A"]


def test_insert_left_pushes_down_existing_left_child() -> None:
    # After first insert_left:
    #     A
    #    /
    #   B
    # After second insert_left (push-down):
    #     A
    #    /
    #   C
    #  /
    # B
    t = BinaryTree("A")
    t.insert_left("B")
    t.insert_left("C")

    assert t.size() == 3
    assert t.bfs() == ["A", "C", "B"]
    assert t.preorder() == ["A", "C", "B"]
    assert t.inorder() == ["B", "C", "A"]
    assert t.postorder() == ["B", "C", "A"]


def test_insert_right_pushes_down_existing_right_child() -> None:
    # After first insert_right:
    #   A
    #    \
    #     B
    # After second insert_right (push-down):
    #   A
    #    \
    #     C
    #      \
    #       B
    t = BinaryTree("A")
    t.insert_right("B")
    t.insert_right("C")

    assert t.size() == 3
    assert t.bfs() == ["A", "C", "B"]
    assert t.preorder() == ["A", "C", "B"]
    assert t.inorder() == ["A", "C", "B"]
    assert t.postorder() == ["B", "C", "A"]


def test_iter_is_bfs_and_repr_contains_values() -> None:
    t = BinaryTree(1)
    t.insert_left(2)
    t.insert_right(3)

    assert list(t) == [1, 2, 3]  # __iter__ uses BFS
    r = repr(t)
    assert "BinaryTree" in r
    assert "1" in r and "2" in r and "3" in r
