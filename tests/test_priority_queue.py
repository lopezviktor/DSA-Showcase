import pytest

from dsa_toolkit.priority_queue import PriorityQueue, EmptyPriorityQueueError


def test_new_queue_is_empty() -> None:
    pq: PriorityQueue[float, str] = PriorityQueue()
    assert pq.is_empty() is True
    assert pq.size() == 0
    assert len(pq) == 0
    assert pq.top_k(3) == []
    assert "PriorityQueue" in repr(pq)


def test_peek_and_pop_on_empty_raise() -> None:
    pq: PriorityQueue[int, str] = PriorityQueue()

    with pytest.raises(EmptyPriorityQueueError):
        pq.peek()

    with pytest.raises(EmptyPriorityQueueError):
        pq.pop()

    # Internal helper is used by top_k(); cover its empty-queue guard.
    with pytest.raises(EmptyPriorityQueueError):
        pq._pop_entry()


def test_push_peek_pop_max_priority() -> None:
    pq = PriorityQueue[float, str]()
    pq.push(0.2, "NORMAL")
    pq.push(0.9, "CRITICAL")
    pq.push(0.5, "SUSPICIOUS")

    assert pq.peek() == (0.9, "CRITICAL")
    assert pq.pop() == (0.9, "CRITICAL")
    assert pq.pop() == (0.5, "SUSPICIOUS")
    assert pq.pop() == (0.2, "NORMAL")
    assert pq.is_empty() is True


def test_stable_order_on_ties_fifo() -> None:
    pq = PriorityQueue[int, str]()
    pq.push(10, "first")
    pq.push(10, "second")
    pq.push(10, "third")

    assert pq.pop() == (10, "first")
    assert pq.pop() == (10, "second")
    assert pq.pop() == (10, "third")


def test_mixed_priorities_with_ties() -> None:
    pq = PriorityQueue[int, str]()
    pq.push(5, "low1")
    pq.push(10, "high1")
    pq.push(10, "high2")
    pq.push(7, "mid")

    assert pq.pop() == (10, "high1")
    assert pq.pop() == (10, "high2")
    assert pq.pop() == (7, "mid")
    assert pq.pop() == (5, "low1")


def test_top_k_non_destructive() -> None:
    pq = PriorityQueue[int, str]()
    pq.push(5, "low")
    pq.push(10, "high")
    pq.push(7, "mid")

    top2 = pq.top_k(2)
    assert top2 == [(10, "high"), (7, "mid")]

    # Queue must remain unchanged
    assert pq.size() == 3
    assert pq.pop() == (10, "high")
    assert pq.pop() == (7, "mid")
    assert pq.pop() == (5, "low")


def test_top_k_edge_cases() -> None:
    pq = PriorityQueue[int, str]()
    pq.push(1, "a")
    pq.push(2, "b")

    assert pq.top_k(0) == []
    assert pq.top_k(-5) == []
    assert pq.top_k(10) == [(2, "b"), (1, "a")]  # k > size => all


def test_clear_resets_queue() -> None:
    pq = PriorityQueue[int, str]()
    pq.push(1, "a")
    pq.clear()

    assert pq.is_empty() is True
    assert pq.size() == 0
    with pytest.raises(EmptyPriorityQueueError):
        pq.peek()
