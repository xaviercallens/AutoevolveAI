"""
Tests for A* Search Algorithm.

Validates path optimality, consistency with Dijkstra, obstacle avoidance,
and node exploration reduction.
"""

from __future__ import annotations

import math
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from anse.algorithms.astar import astar_search, AStarResult
from anse.algorithms.dijkstra import dijkstra_shortest_paths


class TestAStarDeterministic:
    """Unit tests for deterministic spatial and grid scenarios."""

    def test_source_equals_target(self) -> None:
        def neighbors(n: tuple[int, int]) -> list[tuple[tuple[int, int], float]]:
            return []

        def h(a: tuple[int, int], b: tuple[int, int]) -> float:
            return 0.0

        res = astar_search(neighbors, h, (0, 0), (0, 0))
        assert res is not None
        assert res.cost == 0.0
        assert res.path == [(0, 0)]
        assert res.nodes_settled == 1

    def test_2d_grid_with_wall(self) -> None:
        # Grid 5x5, obstacle at (1, 1), (1, 2), (1, 3)
        obstacles = {(1, 1), (1, 2), (1, 3)}

        def neighbors(pos: tuple[int, int]) -> list[tuple[tuple[int, int], float]]:
            x, y = pos
            moves = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            result = []
            for nx, ny in moves:
                if 0 <= nx <= 4 and 0 <= ny <= 4 and (nx, ny) not in obstacles:
                    result.append(((nx, ny), 1.0))
            return result

        def manhattan(a: tuple[int, int], b: tuple[int, int]) -> float:
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        start = (0, 2)
        goal = (3, 2)
        res = astar_search(neighbors, manhattan, start, goal)
        assert res is not None
        assert res.cost == 7.0
        assert len(res.path) == 8
        assert res.path[0] == start
        assert res.path[-1] == goal
        for p in res.path:
            assert p not in obstacles

    def test_unreachable_target(self) -> None:
        # Target completely surrounded by walls
        def neighbors(pos: int) -> list[tuple[int, float]]:
            if pos == 1:
                return [(2, 1.0)]
            if pos == 2:
                return [(1, 1.0)]
            return []

        def zero_h(a: int, b: int) -> float:
            return 0.0

        res = astar_search(neighbors, zero_h, 1, 99)
        assert res is None

    def test_negative_weight_exception(self) -> None:
        def neighbors(pos: int) -> list[tuple[int, float]]:
            return [(2, -5.0)]

        def zero_h(a: int, b: int) -> float:
            return 0.0

        with pytest.raises(ValueError, match="Negative transition cost"):
            astar_search(neighbors, zero_h, 1, 2)

    def test_astar_settles_fewer_nodes_than_dijkstra(self) -> None:
        # 20x20 grid, start at (0, 0), target at (19, 19)
        size = 20

        def grid_neighbors(p: tuple[int, int]) -> list[tuple[tuple[int, int], float]]:
            x, y = p
            moves = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            return [((nx, ny), 1.0) for nx, ny in moves if 0 <= nx < size and 0 <= ny < size]

        def euclidean(a: tuple[int, int], b: tuple[int, int]) -> float:
            return math.hypot(a[0] - b[0], a[1] - b[1])

        # A* search
        astar_res = astar_search(grid_neighbors, euclidean, (0, 0), (19, 19))
        assert astar_res is not None

        # Build full graph dictionary for Dijkstra
        graph: dict[tuple[int, int], list[tuple[tuple[int, int], float]]] = {
            (x, y): grid_neighbors((x, y)) for x in range(size) for y in range(size)
        }
        dijkstra_res = dijkstra_shortest_paths(graph, (0, 0), target=(19, 19))

        # Both find the identical optimal distance
        assert astar_res.cost == dijkstra_res.get_distance((19, 19))
        # A* with Euclidean heuristic expands significantly fewer nodes than full Dijkstra
        assert astar_res.nodes_settled < dijkstra_res.settled_count
