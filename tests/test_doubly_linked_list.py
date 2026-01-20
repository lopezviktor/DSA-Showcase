import pytest

from dsa_toolkit.doubly_linked_list import DoublyLinkedList, EmptyDoublyLinkedListError
from dsa_toolkit.linked_list import ValueNotFoundError


def test_new_list_is_empty() -> None:
    dll: DoublyLinkedList[int] = DoublyLinkedList()
    assert dll.is_empty() is True
    assert dll.size() == 0
    assert len(dll) == 0
    assert list(dll) == []
    assert list(reversed(dll)) == []


def test_prepend_single_element() -> None:
    dll = DoublyLinkedList[int]()
    dll.prepend(10)

    assert dll.is_empty() is False
    assert dll.size() == 1
    assert list(dll) == [10]
    assert list(reversed(dll)) == [10]


def test_append_single_element() -> None:
    dll = DoublyLinkedList[int]()
    dll.append(20)

    assert dll.size() == 1
    assert list(dll) == [20]
    assert list(reversed(dll)) == [20]


def test_prepend_multiple_elements() -> None:
    dll = DoublyLinkedList[int]()
    dll.prepend(10)
    dll.prepend(20)
    dll.prepend(30)

    assert list(dll) == [30, 20, 10]
    assert list(reversed(dll)) == [10, 20, 30]


def test_append_multiple_elements() -> None:
    dll = DoublyLinkedList[int]()
    dll.append(10)
    dll.append(20)
    dll.append(30)

    assert list(dll) == [10, 20, 30]
    assert list(reversed(dll)) == [30, 20, 10]


def test_mixed_prepend_and_append() -> None:
    dll = DoublyLinkedList[int]()
    dll.append(10)  # [10]
    dll.prepend(5)  # [5, 10]
    dll.append(20)  # [5, 10, 20]

    assert list(dll) == [5, 10, 20]
    assert list(reversed(dll)) == [20, 10, 5]


def test_pop_front_removes_head() -> None:
    dll = DoublyLinkedList[int]()
    dll.append(10)
    dll.append(20)

    value = dll.pop_front()
    assert value == 10
    assert list(dll) == [20]
    assert dll.size() == 1


def test_pop_back_removes_tail() -> None:
    dll = DoublyLinkedList[int]()
    dll.append(10)
    dll.append(20)

    value = dll.pop_back()
    assert value == 20
    assert list(dll) == [10]
    assert dll.size() == 1


def test_pop_front_on_single_element() -> None:
    dll = DoublyLinkedList[int]()
    dll.append(99)

    value = dll.pop_front()
    assert value == 99
    assert dll.is_empty() is True
    assert dll.size() == 0
    assert list(dll) == []


def test_pop_back_on_single_element() -> None:
    dll = DoublyLinkedList[int]()
    dll.append(77)

    value = dll.pop_back()
    assert value == 77
    assert dll.is_empty() is True
    assert dll.size() == 0
    assert list(dll) == []


def test_pop_on_empty_raises() -> None:
    dll = DoublyLinkedList[int]()

    with pytest.raises(EmptyDoublyLinkedListError):
        dll.pop_front()

    with pytest.raises(EmptyDoublyLinkedListError):
        dll.pop_back()


def test_find_existing_and_missing() -> None:
    dll = DoublyLinkedList[int]()
    dll.append(10)
    dll.append(20)

    assert dll.find(10) is True
    assert dll.find(20) is True
    assert dll.find(99) is False


def test_remove_middle_element() -> None:
    dll = DoublyLinkedList[int]()
    dll.append(10)
    dll.append(20)
    dll.append(30)

    dll.remove(20)
    assert list(dll) == [10, 30]
    assert list(reversed(dll)) == [30, 10]
    assert dll.size() == 2


def test_remove_head_element() -> None:
    dll = DoublyLinkedList[int]()
    dll.append(10)
    dll.append(20)

    dll.remove(10)
    assert list(dll) == [20]
    assert dll.size() == 1


def test_remove_tail_element() -> None:
    dll = DoublyLinkedList[int]()
    dll.append(10)
    dll.append(20)
    dll.append(30)

    dll.remove(30)
    assert list(dll) == [10, 20]
    assert dll.size() == 2


def test_remove_on_empty_raises_value_not_found() -> None:
    dll = DoublyLinkedList[int]()

    with pytest.raises(ValueNotFoundError):
        dll.remove(123)


def test_remove_non_existing_raises_value_not_found() -> None:
    dll = DoublyLinkedList[int]()
    dll.append(10)

    with pytest.raises(ValueNotFoundError):
        dll.remove(99)


def test_clear_empties_list() -> None:
    dll = DoublyLinkedList[int]()
    dll.append(1)
    dll.append(2)

    dll.clear()
    assert dll.is_empty() is True
    assert dll.size() == 0
    assert list(dll) == []
    assert list(reversed(dll)) == []


def test_repr_is_readable() -> None:
    dll = DoublyLinkedList[int]()
    dll.append(1)
    dll.append(2)

    text = repr(dll)
    assert "DoublyLinkedList" in text
    assert "1" in text
    assert "2" in text
