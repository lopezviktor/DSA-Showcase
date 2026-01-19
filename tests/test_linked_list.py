import pytest

from dsa_toolkit.linked_list import (
    LinkedList,
    EmptyLinkedListError,
    ValueNotFoundError,
)


def test_new_list_is_empty() -> None:
    ll: LinkedList[int] = LinkedList()
    assert ll.is_empty() is True
    assert ll.size() == 0
    assert len(ll) == 0
    assert list(ll) == []


def test_prepend_single_element() -> None:
    ll = LinkedList[int]()
    ll.prepend(10)

    assert ll.is_empty() is False
    assert ll.size() == 1
    assert list(ll) == [10]


def test_append_single_element() -> None:
    ll = LinkedList[int]()
    ll.append(20)

    assert ll.size() == 1
    assert list(ll) == [20]


def test_prepend_multiple_elements() -> None:
    ll = LinkedList[int]()
    ll.prepend(10)
    ll.prepend(20)
    ll.prepend(30)

    assert list(ll) == [30, 20, 10]


def test_append_multiple_elements() -> None:
    ll = LinkedList[int]()
    ll.append(10)
    ll.append(20)
    ll.append(30)

    assert list(ll) == [10, 20, 30]


def test_mixed_prepend_and_append() -> None:
    ll = LinkedList[int]()
    ll.append(10)  # [10]
    ll.prepend(5)  # [5, 10]
    ll.append(20)  # [5, 10, 20]

    assert list(ll) == [5, 10, 20]


def test_pop_front_removes_head() -> None:
    ll = LinkedList[int]()
    ll.append(10)
    ll.append(20)

    value = ll.pop_front()
    assert value == 10
    assert list(ll) == [20]
    assert ll.size() == 1


def test_pop_front_on_single_element() -> None:
    ll = LinkedList[int]()
    ll.append(99)

    value = ll.pop_front()
    assert value == 99
    assert ll.is_empty() is True
    assert ll.size() == 0


def test_pop_front_on_empty_raises() -> None:
    ll = LinkedList[int]()

    with pytest.raises(EmptyLinkedListError):
        ll.pop_front()


def test_find_existing_value() -> None:
    ll = LinkedList[int]()
    ll.append(10)
    ll.append(20)

    assert ll.find(10) is True
    assert ll.find(20) is True


def test_find_non_existing_value() -> None:
    ll = LinkedList[int]()
    ll.append(10)

    assert ll.find(99) is False


def test_remove_middle_element() -> None:
    ll = LinkedList[int]()
    ll.append(10)
    ll.append(20)
    ll.append(30)

    ll.remove(20)
    assert list(ll) == [10, 30]
    assert ll.size() == 2


def test_remove_head_element() -> None:
    ll = LinkedList[int]()
    ll.append(10)
    ll.append(20)

    ll.remove(10)
    assert list(ll) == [20]
    assert ll.size() == 1


def test_remove_tail_element_updates_tail() -> None:
    ll = LinkedList[int]()
    ll.append(10)
    ll.append(20)
    ll.append(30)

    ll.remove(30)
    assert list(ll) == [10, 20]
    assert ll.size() == 2


def test_remove_non_existing_raises() -> None:
    ll = LinkedList[int]()
    ll.append(10)

    with pytest.raises(ValueNotFoundError):
        ll.remove(99)


def test_clear_empties_list() -> None:
    ll = LinkedList[int]()
    ll.append(1)
    ll.append(2)

    ll.clear()
    assert ll.is_empty() is True
    assert list(ll) == []
    assert ll.size() == 0


def test_repr_is_readable() -> None:
    ll = LinkedList[int]()
    ll.append(1)
    ll.append(2)

    text = repr(ll)
    assert "LinkedList" in text
    assert "1" in text
    assert "2" in text


def test_remove_on_empty_raises() -> None:
    ll = LinkedList[int]()

    with pytest.raises(ValueNotFoundError):
        ll.remove(123)
