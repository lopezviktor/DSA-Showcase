import pytest

from dsa_toolkit.deque import Deque, EmptyDequeError

def test_new_deque_is_empty():
    d: Deque[int] = Deque()
    assert d.is_empty() is True
    assert d.size() == 0
    assert len(d) == 0

def test_append_right_and_pop_left_fifo_behavior() -> None:
    d = Deque([1, 2, 3])
    assert d.pop_left() == 1
    assert d.pop_left() == 2
    assert d.pop_left() == 3
    assert d.is_empty() is True

def test_append_left_and_pop_left_lifo_like_behavior() -> None:
    d = Deque()
    d.append_left(1)
    d.append_left(2)
    d.append_left(3)
    assert d.pop_left() == 3
    assert d.pop_left() == 2
    assert d.pop_left() == 1
    assert d.is_empty() is True

def test_append_right_and_pop_right_lifo_behavior() -> None:
    d = Deque()
    d.append_right(1)
    d.append_right(2)
    d.append_right(3)
    assert d.pop_right() == 3
    assert d.pop_right() == 2
    assert d.pop_right() == 1
    assert d.is_empty() is True

def test_mixed_operations_both_ends() -> None:
    d = Deque()
    d.append_right(1)
    d.append_right(2)
    d.append_left(0)
    assert d.peek_left() == 0
    assert d.peek_right() == 2
    assert d.pop_right() == 2
    assert d.pop_left() == 0
    assert d.pop_left() == 1
    assert d.is_empty() is True

def test_peek_does_not_remove() -> None:
    d = Deque([10, 20])
    assert d.peek_left() == 10
    assert d.peek_left() == 10
    assert d.peek_right() == 20
    assert d.peek_right() == 20
    assert list(d) == [10, 20]


def test_pop_on_empty_raises() -> None:
    d = Deque()
    with pytest.raises(EmptyDequeError):
        d.pop_left()
    with pytest.raises(EmptyDequeError):
        d.pop_right()
    with pytest.raises(EmptyDequeError):
        d.peek_left()
    with pytest.raises(EmptyDequeError):
        d.peek_right()


def test_grows_capacity_transparently() -> None:
    d = Deque(initial_capacity=2)
    for i in range(50):
        d.append_right(i)
    assert d.size() == 50
    assert d.pop_left() == 0
    assert d.pop_right() == 49
    assert d.size() == 48


def test_initial_capacity_must_be_positive() -> None:
    with pytest.raises(ValueError):
        Deque(initial_capacity=0)


def test_len_iter_and_repr_are_consistent() -> None:
    d = Deque([1, 2, 3])
    assert len(d) == 3
    assert list(d) == [1, 2, 3]
    assert "Deque" in repr(d)


def test_clear_empties_deque() -> None:
    d = Deque([1, 2, 3])
    d.clear()
    assert d.is_empty() is True
    assert d.size() == 0
    with pytest.raises(EmptyDequeError):
        d.peek_left()
    with pytest.raises(EmptyDequeError):
        d.peek_right()


def test_no_resize_path_is_executed() -> None:
    d = Deque(initial_capacity=10)
    d.append_right(1)
    d.append_left(0)
    assert list(d) == [0, 1]