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


def test_add_edge_with_explicit_weight() -> None:
    g = Graph[str]()
    g.add_edge("sensor", "gateway", weight=2.5)
    assert g.has_edge("sensor", "gateway") is True
    assert g.weight("sensor", "gateway") == 2.5


def test_weight_default_is_one() -> None:
    g = Graph[str]()
    g.add_edge("a", "b")
    assert g.weight("a", "b") == 1.0


def test_weight_missing_edge_raises() -> None:
    g = Graph[str]()
    g.add_node("a")
    with pytest.raises(NodeNotFoundError):
        g.weight("a", "b")


def test_weighted_edges_returns_triples() -> None:
    g = Graph[str]()
    g.add_edge("sensor", "gateway", weight=3.0)
    g.add_edge("gateway", "cloud", weight=1.5)
    we = g.weighted_edges()
    assert ("sensor", "gateway", 3.0) in we
    assert ("gateway", "cloud", 1.5) in we
    assert len(we) == 2


def test_weighted_edges_is_consistent_with_edges() -> None:
    g = Graph[str]()
    g.add_edge("a", "b", weight=7.0)
    g.add_edge("b", "c")
    assert {(s, d) for s, d, _ in g.weighted_edges()} == g.edges()


# ----------------------------
# bfs_shortest_path
# ----------------------------

def test_bfs_shortest_path_direct() -> None:
    g = Graph[str]()
    g.add_edge("sensor", "gateway")
    assert g.bfs_shortest_path("sensor", "gateway") == ["sensor", "gateway"]


def test_bfs_shortest_path_multi_hop() -> None:
    g = Graph[str]()
    g.add_edge("sensor", "gateway")
    g.add_edge("gateway", "cloud")
    path = g.bfs_shortest_path("sensor", "cloud")
    assert path == ["sensor", "gateway", "cloud"]


def test_bfs_shortest_path_prefers_fewer_hops() -> None:
    # sensor -> gateway -> cloud (2 hops)
    # sensor -> cloud          (1 hop, direct)
    g = Graph[str]()
    g.add_edge("sensor", "gateway")
    g.add_edge("gateway", "cloud")
    g.add_edge("sensor", "cloud")
    path = g.bfs_shortest_path("sensor", "cloud")
    assert path == ["sensor", "cloud"]


def test_bfs_shortest_path_unreachable_returns_none() -> None:
    g = Graph[str]()
    g.add_edge("sensor", "gateway")
    g.add_node("cloud")
    assert g.bfs_shortest_path("sensor", "cloud") is None


def test_bfs_shortest_path_same_node() -> None:
    g = Graph[str]()
    g.add_node("sensor")
    assert g.bfs_shortest_path("sensor", "sensor") == ["sensor"]


def test_bfs_shortest_path_missing_start_raises() -> None:
    g = Graph[str]()
    g.add_node("gateway")
    with pytest.raises(NodeNotFoundError):
        g.bfs_shortest_path("missing", "gateway")


def test_bfs_shortest_path_missing_end_raises() -> None:
    g = Graph[str]()
    g.add_node("sensor")
    with pytest.raises(NodeNotFoundError):
        g.bfs_shortest_path("sensor", "missing")


def test_bfs_shortest_path_ids_example() -> None:
    g = Graph[str]()
    g.add_edge("sensor", "gateway")
    g.add_edge("gateway", "cloud")
    g.add_edge("sensor", "laptop")
    g.add_edge("laptop", "gateway")
    path = g.bfs_shortest_path("sensor", "cloud")
    # Shortest hop path: sensor -> gateway -> cloud (2 hops)
    assert path is not None
    assert path[0] == "sensor"
    assert path[-1] == "cloud"
    assert len(path) == 3


# ----------------------------
# dijkstra
# ----------------------------

def test_dijkstra_basic() -> None:
    g = Graph[str]()
    g.add_edge("a", "b", weight=1.0)
    g.add_edge("b", "c", weight=2.0)
    g.add_edge("a", "c", weight=10.0)
    dist = g.dijkstra("a")
    assert dist["a"] == 0.0
    assert dist["b"] == 1.0
    assert dist["c"] == 3.0  # a->b->c cheaper than a->c


def test_dijkstra_isolated_node_not_in_result() -> None:
    g = Graph[str]()
    g.add_edge("a", "b")
    g.add_node("isolated")
    dist = g.dijkstra("a")
    assert "isolated" not in dist


def test_dijkstra_start_only() -> None:
    g = Graph[str]()
    g.add_node("sensor")
    dist = g.dijkstra("sensor")
    assert dist == {"sensor": 0.0}


def test_dijkstra_missing_start_raises() -> None:
    g = Graph[str]()
    with pytest.raises(NodeNotFoundError):
        g.dijkstra("missing")


def test_dijkstra_ids_topology() -> None:
    # sensor -1-> gateway -1-> cloud
    # sensor -5-> cloud (more expensive)
    g = Graph[str]()
    g.add_edge("sensor", "gateway", weight=1.0)
    g.add_edge("gateway", "cloud", weight=1.0)
    g.add_edge("sensor", "cloud", weight=5.0)
    dist = g.dijkstra("sensor")
    assert dist["sensor"] == 0.0
    assert dist["gateway"] == 1.0
    assert dist["cloud"] == 2.0  # via gateway


# ----------------------------
# shortest_path (Dijkstra with path reconstruction)
# ----------------------------

def test_shortest_path_basic() -> None:
    g = Graph[str]()
    g.add_edge("a", "b", weight=1.0)
    g.add_edge("b", "c", weight=2.0)
    g.add_edge("a", "c", weight=10.0)
    path = g.shortest_path("a", "c")
    assert path == ["a", "b", "c"]


def test_shortest_path_same_node() -> None:
    g = Graph[str]()
    g.add_node("sensor")
    assert g.shortest_path("sensor", "sensor") == ["sensor"]


def test_shortest_path_unreachable_returns_none() -> None:
    g = Graph[str]()
    g.add_edge("sensor", "gateway")
    g.add_node("cloud")
    assert g.shortest_path("sensor", "cloud") is None


def test_shortest_path_missing_start_raises() -> None:
    g = Graph[str]()
    g.add_node("gateway")
    with pytest.raises(NodeNotFoundError):
        g.shortest_path("missing", "gateway")


def test_shortest_path_missing_end_raises() -> None:
    g = Graph[str]()
    g.add_node("sensor")
    with pytest.raises(NodeNotFoundError):
        g.shortest_path("sensor", "missing")


def test_shortest_path_ids_topology() -> None:
    # sensor -1-> gateway -1-> cloud
    # sensor -5-> cloud (more expensive direct link)
    g = Graph[str]()
    g.add_edge("sensor", "gateway", weight=1.0)
    g.add_edge("gateway", "cloud", weight=1.0)
    g.add_edge("sensor", "cloud", weight=5.0)
    path = g.shortest_path("sensor", "cloud")
    assert path == ["sensor", "gateway", "cloud"]


def test_shortest_path_stale_entry_skipped() -> None:
    # a->b (1), a->c (2), b->c (0.5), c->d (1)
    # Dijkstra: a=0, b=1, c=1.5 (via b), d=2.5.
    # c is pushed twice: once at cost 2 (direct), once at cost 1.5 (via b).
    # After processing c@1.5, pq still holds c@2 (stale) with priority -2 and d@2.5
    # with priority -2.5. Since -2 > -2.5 in the max-heap, stale c@2 is popped BEFORE
    # d, triggering the `d > dist[c]` (2 > 1.5) -> `continue` branch in shortest_path.
    g = Graph[str]()
    g.add_edge("a", "b", weight=1.0)
    g.add_edge("a", "c", weight=2.0)
    g.add_edge("b", "c", weight=0.5)
    g.add_edge("c", "d", weight=1.0)
    path = g.shortest_path("a", "d")
    assert path == ["a", "b", "c", "d"]


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
