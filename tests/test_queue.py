import pytest
from dsa_toolkit import Queue, EmptyQueueError


def test_queue_enqueue_dequeue_peek_and_size():
    q = Queue[int]()
    assert q.is_empty()
    q.enqueue(10)
    q.enqueue(20)

    assert q.size() == 2
    assert len(q) == 2
    assert not q.is_empty()
    assert q.peek() == 10

    assert q.dequeue() == 10
    assert q.dequeue() == 20
    assert q.is_empty()


def test_queue_init_with_iterable():
    q = Queue(items=[1, 2, 3])
    assert len(q) == 3
    assert q.peek() == 1


def test_dequeue_on_empty_raises():
    q = Queue()
    with pytest.raises(EmptyQueueError):
        q.dequeue()


def test_peek_on_empty_raises():
    q = Queue()
    with pytest.raises(EmptyQueueError):
        q.peek()


def test_queue_clear_and_repr():
    q = Queue(items=[1, 2, 3])
    rep = repr(q)
    assert "Queue(" in rep

    q.clear()
    assert q.is_empty()
    assert q.size() == 0


def test_queue_compaction_does_not_break_order():
    # Force internal compaction logic to run
    q = Queue[int]()
    for i in range(100):
        q.enqueue(i)

    # Dequeue enough elements to trigger compaction
    for _ in range(60):
        _ = q.dequeue()

    # Remaining elements should be in correct order
    expected = list(range(60, 100))
    result = [q.dequeue() for _ in range(q.size())]
    assert result == expected
    assert q.is_empty()
