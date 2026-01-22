import pytest

from dsa_toolkit.graph import Graph, NodeNotFoundError


def test_new_graph_is_empty() -> None:
    g: Graph[str] = Graph()
    assert g.nodes() == set()
    assert g.edges() == set()
    assert "Graph" in repr(g)


def test_add_node_and_has_node() -> None:
    g = Graph[str]()
    g.add_node("sensor")
    assert g.has_node("sensor") is True
    assert g.has_node("gateway") is False


def test_add_edge_auto_creates_nodes_and_deduplicates() -> None:
    g = Graph[str]()
    g.add_edge("sensor", "gateway")
    g.add_edge("sensor", "gateway")  # duplicate

    assert g.has_node("sensor") is True
    assert g.has_node("gateway") is True
    assert g.has_edge("sensor", "gateway") is True
    assert g.edges() == {("sensor", "gateway")}
    assert g.out_degree("sensor") == 1
    assert g.in_degree("gateway") == 1


def test_neighbors_and_missing_node() -> None:
    g = Graph[str]()
    g.add_edge("sensor", "gateway")

    assert g.neighbors("sensor") == {"gateway"}

    with pytest.raises(NodeNotFoundError):
        g.neighbors("cloud")


def test_degrees_missing_node_raise() -> None:
    g = Graph[str]()

    with pytest.raises(NodeNotFoundError):
        g.out_degree("x")
    with pytest.raises(NodeNotFoundError):
        g.in_degree("x")


def test_bfs_order_levels_ids_example() -> None:
    # IDS example:
    # sensor -> gateway
    # gateway -> cloud
    # laptop -> gateway
    # sensor -> laptop (rare)
    g = Graph[str]()
    g.add_edge("sensor", "gateway")
    g.add_edge("gateway", "cloud")
    g.add_edge("laptop", "gateway")
    g.add_edge("sensor", "laptop")

    bfs = g.bfs("sensor")
    # BFS should start from sensor and include all reachable nodes.
    # Exact order after the first node depends on set iteration; we assert properties.
    assert bfs[0] == "sensor"
    assert set(bfs) == {"sensor", "gateway", "laptop", "cloud"}


def test_dfs_reachability_ids_example() -> None:
    g = Graph[str]()
    g.add_edge("sensor", "gateway")
    g.add_edge("gateway", "cloud")
    g.add_edge("sensor", "laptop")
    g.add_edge("laptop", "gateway")

    dfs = g.dfs("sensor")
    assert dfs[0] == "sensor"
    assert set(dfs) == {"sensor", "gateway", "laptop", "cloud"}


def test_bfs_and_dfs_missing_start_raise() -> None:
    g = Graph[str]()
    with pytest.raises(NodeNotFoundError):
        g.bfs("missing")
    with pytest.raises(NodeNotFoundError):
        g.dfs("missing")


def test_dfs_fallback_when_neighbors_not_sortable() -> None:
    class Device:
        def __init__(self, name: str) -> None:
            self.name = name

        def __repr__(self) -> str:
            return f"Device({self.name})"

        def __hash__(self) -> int:
            return hash(self.name)

        def __eq__(self, other: object) -> bool:
            return isinstance(other, Device) and self.name == other.name

    a = Device("sensor")
    b = Device("gateway")
    c = Device("laptop")

    g: Graph[Device] = Graph()
    g.add_edge(a, b)
    g.add_edge(a, c)

    # Device is not orderable -> neighbor sorting raises TypeError -> except branch covered
    dfs = g.dfs(a)
    assert dfs[0] == a
    assert set(dfs) == {a, b, c}


def test_dfs_uses_sort_when_nodes_are_orderable() -> None:
    g: Graph[int] = Graph()
    # Start node has two neighbors so the internal `sort(reverse=True)` line executes.
    g.add_edge(1, 2)
    g.add_edge(1, 3)

    dfs = g.dfs(1)
    assert dfs[0] == 1
    assert set(dfs) == {1, 2, 3}


def test_dfs_covers_already_visited_continue_branch() -> None:
    # Arrange a graph where the same node (4) is pushed twice onto the stack
    # before it is visited:
    # 1 -> 2
    # 2 -> 3, 4
    # 3 -> 4
    # In DFS (stack-based), 2 is visited, then 3 is visited next, which pushes 4.
    # Node 4 is already on the stack from node 2, so it will be popped twice;
    # the second time it triggers: `if node in visited: continue`.
    g: Graph[int] = Graph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(2, 4)
    g.add_edge(3, 4)

    dfs = g.dfs(1)
    assert dfs[0] == 1
    assert set(dfs) == {1, 2, 3, 4}
