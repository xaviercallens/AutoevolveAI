"""
Tests for k-D Tree Vector Memory.

Validates 1-NN and k-NN search correctness against brute-force baseline,
empty and single-element edge cases, and dimension mismatch validation.
"""

from __future__ import annotations

import math
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from anse.algorithms.kdtree import KDTree, KDNeighbor


class TestKDTreeDeterministic:
    """Deterministic tests for KDTree operations."""

    def test_empty_tree(self) -> None:
        tree: KDTree[str] = KDTree([])
        assert len(tree) == 0
        assert tree.query_nearest([1.0, 2.0]) is None
        assert tree.query_knn([1.0, 2.0], k=3) == []

    def test_single_point(self) -> None:
        tree = KDTree([([1.0, 2.0], "item1")])
        assert len(tree) == 1
        res = tree.query_nearest([1.0, 2.0])
        assert res is not None
        assert res.distance == 0.0
        assert res.payload == "item1"

        res2 = tree.query_nearest([4.0, 6.0])
        assert res2 is not None
        assert math.isclose(res2.distance, 5.0)

    def test_dimension_mismatch_raises(self) -> None:
        with pytest.raises(ValueError, match="Inconsistent dimensionality"):
            KDTree([([1.0, 2.0], "a"), ([1.0, 2.0, 3.0], "b")])

        tree = KDTree([([1.0, 2.0], "a")])
        with pytest.raises(ValueError, match="Query dimensionality mismatch"):
            tree.query_nearest([1.0, 2.0, 3.0])

    def test_knn_search_ordered(self) -> None:
        points = [
            ([0.0, 0.0], "origin"),
            ([1.0, 0.0], "right"),
            ([0.0, 2.0], "up"),
            ([5.0, 5.0], "far"),
        ]
        tree = KDTree(points)
        knn = tree.query_knn([0.0, 0.1], k=3)
        assert len(knn) == 3
        # Closest is origin (dist 0.1), then right (dist ~1.005), then up (dist 1.9)
        assert knn[0].payload == "origin"
        assert knn[1].payload == "right"
        assert knn[2].payload == "up"
        assert knn[0].distance < knn[1].distance < knn[2].distance


class TestKDTreePropertyBased:
    """Hypothesis property-based tests verifying KDTree against brute force."""

    @settings(max_examples=25, deadline=None)
    @given(
        pts=st.lists(
            st.tuples(
                st.floats(min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False),
                st.floats(min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False),
                st.floats(min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False),
            ),
            min_size=5,
            max_size=30,
        ),
        q=st.tuples(
            st.floats(min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False),
            st.floats(min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False),
            st.floats(min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        ),
    )
    def test_kdtree_matches_brute_force(
        self, pts: list[tuple[float, float, float]], q: tuple[float, float, float]
    ) -> None:
        items = [(list(p), idx) for idx, p in enumerate(pts)]
        tree = KDTree(items)

        # Brute force 1-NN
        def brute_dist(p: tuple[float, float, float]) -> float:
            return math.sqrt(sum((a - b) ** 2 for a, b in zip(p, q)))

        min_brute_dist = min(brute_dist(p) for p in pts)

        # KDTree 1-NN
        kd_res = tree.query_nearest(list(q))
        assert kd_res is not None
        assert math.isclose(kd_res.distance, min_brute_dist, rel_tol=1e-5, abs_tol=1e-5)

        # KDTree k-NN (k=3)
        k = 3
        sorted_brute = sorted(brute_dist(p) for p in pts)[:k]
        knn_res = tree.query_knn(list(q), k=k)
        assert len(knn_res) == min(k, len(pts))
        for i in range(len(knn_res)):
            assert math.isclose(knn_res[i].distance, sorted_brute[i], rel_tol=1e-5, abs_tol=1e-5)
