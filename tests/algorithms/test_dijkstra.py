"""
Comprehensive test suite for Dijkstra's Shortest Path Algorithm.

Includes unit tests, edge-case analysis, and Hypothesis property-based tests
verifying triangle inequality and path reconstruction correctness.
"""

from __future__ import annotations

import math
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from anse.algorithms.dijkstra import dijkstra_shortest_paths, ShortestPathResult


class TestDijkstraUnitTests:
    """Unit tests for deterministic graph scenarios."""

    def test_single_node_graph(self) -> None:
        graph = {"A": []}
        res = dijkstra_shortest_paths(graph, "A")
        assert res.get_distance("A") == 0.0
        assert res.get_path("A") == ["A"]
        assert res.settled_count == 1

    def test_simple_linear_chain(self) -> None:
        graph = {
            "A": [("B", 2.0)],
            "B": [("C", 3.0)],
            "C": [("D", 1.5)],
        }
        res = dijkstra_shortest_paths(graph, "A")
        assert res.get_distance("A") == 0.0
        assert res.get_distance("B") == 2.0
        assert res.get_distance("C") == 5.0
        assert res.get_distance("D") == 6.5
        assert res.get_path("D") == ["A", "B", "C", "D"]

    def test_diamond_graph_shortest_branch(self) -> None:
        # A -> B (5), A -> C (2), C -> B (1), B -> D (1)
        # Path A -> C -> B -> D costs 2 + 1 + 1 = 4 (better than A -> B -> D = 6)
        graph = {
            "A": [("B", 5.0), ("C", 2.0)],
            "B": [("D", 1.0)],
            "C": [("B", 1.0)],
            "D": [],
        }
        res = dijkstra_shortest_paths(graph, "A")
        assert res.get_distance("D") == 4.0
        assert res.get_path("D") == ["A", "C", "B", "D"]

    def test_cyclic_graph_termination(self) -> None:
        # Graph with cycles
        graph = {
            "A": [("B", 1.0)],
            "B": [("C", 2.0), ("A", 5.0)],
            "C": [("A", 1.0), ("D", 4.0)],
            "D": [],
        }
        res = dijkstra_shortest_paths(graph, "A")
        assert res.get_distance("D") == 7.0
        assert res.get_path("D") == ["A", "B", "C", "D"]

    def test_unreachable_components(self) -> None:
        graph = {
            "A": [("B", 2.0)],
            "B": [],
            "Z": [("W", 1.0)],
            "W": [],
        }
        res = dijkstra_shortest_paths(graph, "A")
        assert res.get_distance("B") == 2.0
        assert res.get_distance("Z") == math.inf
        assert res.get_path("Z") is None
        assert not res.is_reachable("Z")

    def test_target_early_exit(self) -> None:
        # Large chain graph
        graph = {
            f"N{i}": [(f"N{i+1}", 1.0)] for i in range(100)
        }
        graph["N100"] = []
        # Target at N5
        res = dijkstra_shortest_paths(graph, "N0", target="N5")
        assert res.get_distance("N5") == 5.0
        assert res.get_path("N5") == ["N0", "N1", "N2", "N3", "N4", "N5"]
        # Must have settled far fewer than 100 nodes
        assert res.settled_count <= 6

    def test_negative_weight_raises_value_error(self) -> None:
        graph = {
            "A": [("B", 2.0), ("C", -1.0)],
            "B": [],
            "C": [],
        }
        with pytest.raises(ValueError, match="Negative edge weight encountered"):
            dijkstra_shortest_paths(graph, "A")

    def test_integer_vertices(self) -> None:
        graph = {
            1: [(2, 10.0), (3, 30.0)],
            2: [(3, 5.0)],
            3: [],
        }
        res = dijkstra_shortest_paths(graph, 1)
        assert res.get_distance(3) == 15.0
        assert res.get_path(3) == [1, 2, 3]


class TestDijkstraPropertyTests:
    """Hypothesis property-based tests for graph invariants."""

    @settings(max_examples=30, deadline=None)
    @given(
        nodes=st.lists(st.integers(min_value=0, max_value=20), min_size=2, max_size=10, unique=True),
        data=st.data(),
    )
    def test_triangle_inequality_property(self, nodes: list[int], data: st.DataObject) -> None:
        """Verify triangle inequality: d(v) <= d(u) + w(u, v) for all reachable edges."""
        graph: dict[int, list[tuple[int, float]]] = {n: [] for n in nodes}
        for u in nodes:
            # Generate random outgoing edges
            targets = data.draw(st.lists(st.sampled_from(nodes), max_size=3))
            for v in targets:
                weight = data.draw(st.floats(min_value=0.1, max_value=100.0, allow_nan=False, allow_infinity=False))
                graph[u].append((v, weight))

        source = nodes[0]
        res = dijkstra_shortest_paths(graph, source)

        # Invariant 1: Source has distance 0
        assert res.get_distance(source) == 0.0

        # Invariant 2: Triangle inequality holds on all edges
        for u in nodes:
            dist_u = res.get_distance(u)
            if math.isinf(dist_u):
                continue
            for v, weight in graph[u]:
                dist_v = res.get_distance(v)
                assert dist_v <= dist_u + weight + 1e-9

        # Invariant 3: Reconstructed path distances match computed distances
        for target in nodes:
            path = res.get_path(target)
            if path is not None:
                assert path[0] == source
                assert path[-1] == target
                # Compute path sum
                total = 0.0
                for i in range(len(path) - 1):
                    u_curr, v_next = path[i], path[i + 1]
                    matching_weights = [w for v_edge, w in graph[u_curr] if v_edge == v_next]
                    assert matching_weights, f"Missing edge {u_curr} -> {v_next}"
                    total += min(matching_weights)
                assert math.isclose(total, res.get_distance(target), rel_tol=1e-6, abs_tol=1e-6)
