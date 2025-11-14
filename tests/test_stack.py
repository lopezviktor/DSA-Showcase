import pytest
from dsa_toolkit import Stack, EmptyStackError


def test_stack_push_pop_peek_and_size():
    s = Stack[int]()
    assert s.is_empty()
    s.push(10)
    s.push(20)

    assert s.size() == 2
    assert len(s) == 2
    assert not s.is_empty()
    assert s.peek() == 20

    assert s.pop() == 20
    assert s.pop() == 10
    assert s.is_empty()


def test_stack_init_with_iterable():
    s = Stack(items=[1, 2, 3])
    assert len(s) == 3
    assert s.peek() == 3


def test_pop_on_empty_raises():
    s = Stack()
    with pytest.raises(EmptyStackError):
        s.pop()


def test_peek_on_empty_raises():
    s = Stack()
    with pytest.raises(EmptyStackError):
        s.peek()


def test_stack_clear_and_repr():
    s = Stack(items=[1, 2, 3])
    # __repr__ should return a helpful string, not crash
    rep = repr(s)
    assert "Stack(" in rep

    # clear should empty the stack
    s.clear()
    assert s.is_empty()
    assert s.size() == 0
