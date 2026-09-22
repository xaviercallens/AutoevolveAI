"""
Tests for Tarjan's Strongly Connected Components (SCC) and DAG Condenser.

Validates linear-time decomposition, cycle detection, topological ordering,
and quotient DAG condensation.
"""

from __future__ import annotations

import pytest

from anse.algorithms.tarjan_scc import find_strongly_connected_components, SCCResult


class TestTarjanSCC:
    """Test suite for Tarjan SCC decomposition."""

    def test_pure_dag_no_cycles(self) -> None:
        graph = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": [],
        }
        res = find_strongly_connected_components(graph)
        assert res.is_dag is True
        assert len(res.cyclic_components) == 0
        assert len(res.components) == 4
        # Every node is in its own singleton component
        for c in res.components:
            assert len(c) == 1
        # Topological order exists and covers all 4 components
        assert len(res.topological_order) == 4
        # A must precede B, C, D in topological order
        comp_a = res.node_to_component["A"]
        comp_d = res.node_to_component["D"]
        assert res.topological_order.index(comp_a) < res.topological_order.index(comp_d)

    def test_single_directed_cycle(self) -> None:
        # A -> B -> C -> A (3-node cycle), and C -> D (exit to DAG)
        graph = {
            "A": ["B"],
            "B": ["C"],
            "C": ["A", "D"],
            "D": [],
        }
        res = find_strongly_connected_components(graph)
        assert res.is_dag is False
        assert len(res.cyclic_components) == 1
        assert set(res.cyclic_components[0]) == {"A", "B", "C"}
        # There should be 2 components: {A, B, C} and {D}
        assert len(res.components) == 2
        # Condensed DAG has edge from cycle to D
        cycle_comp = res.node_to_component["A"]
        d_comp = res.node_to_component["D"]
        assert d_comp in res.condensed_dag[cycle_comp]
        assert res.topological_order == [cycle_comp, d_comp]

    def test_self_loop_detected_as_cycle(self) -> None:
        graph = {
            "A": ["A", "B"],
            "B": [],
        }
        res = find_strongly_connected_components(graph)
        assert res.is_dag is False
        assert len(res.cyclic_components) == 1
        assert res.cyclic_components[0] == ["A"]

    def test_disconnected_subgraphs(self) -> None:
        graph = {
            "A": ["B"],
            "B": ["A"],
            "X": ["Y"],
            "Y": ["X"],
            "Z": [],
        }
        res = find_strongly_connected_components(graph)
        assert res.is_dag is False
        assert len(res.components) == 3
        assert len(res.cyclic_components) == 2
        # Two 2-node cycles {A, B} and {X, Y}
        cycles = [set(c) for c in res.cyclic_components]
        assert {"A", "B"} in cycles
        assert {"X", "Y"} in cycles
