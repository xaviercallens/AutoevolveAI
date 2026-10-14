"""Tests for the openai_math hypothesis lab instruments (scripts/openai_math/hypotheses/)."""

from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path
from types import ModuleType

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HYP = ROOT / "scripts" / "openai_math" / "hypotheses"
sys.path.insert(0, str(ROOT / "scripts" / "openai_math"))
sys.path.insert(0, str(HYP))


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


h5 = _load("h5_dyadic_t", HYP / "h5_dyadic.py")
h5x = _load("h5_exact_t", HYP / "h5_exact.py")
h4 = _load("h4_lienard_t", HYP / "h4_lienard.py")
h2 = _load("h2_class_numbers_t", HYP / "h2_class_numbers.py")
scan = _load("scan_solution_t", ROOT / "scripts" / "openai_math" / "scan_solution.py")


def test_h5_vectorised_terms_match_direct_loop() -> None:
    rng = np.random.default_rng(7)
    a = [rng.standard_normal((8, 8)) for _ in range(3)]
    for k in (-2, -1, 0):
        terms = h5.scale_terms(a, 3, k)
        m = 2 ** (-k)
        assert terms.shape == (m, m)
        for i0 in range(m):
            for i1 in range(m):
                assert abs(terms[i0, i1] - h5.brute_force_term(a, 3, k, i0, i1)) < 1e-12


def test_h5_controls_constant_input_and_haar_free_growth() -> None:
    ones = [np.ones((16, 16)) for _ in range(3)]
    assert abs(h5.ratio(ones, 4) - 1.0) < 1e-12
    assert abs(h5.ratio(ones, 4, haar=False) - 5.0) < 1e-9
    assert abs(h5.ratio([np.ones((8, 8))] * 3, 3, haar=False) - 4.0) < 1e-9


def test_h5_ascent_is_monotone_and_scale_invariant_in_amplitude() -> None:
    rng = np.random.default_rng(3)
    a = [rng.standard_normal((8, 8)) for _ in range(3)]
    start = h5.ratio(a, 3)
    _, best = h5.ascend(a, 3, sweeps=20)
    assert best >= start - 1e-12
    scaled = [2.5 * a[0], -3.0 * a[1], 0.1 * a[2]]
    assert abs(h5.ratio(scaled, 3) - start) < 1e-9


def test_h5_exact_ratio_matches_float_for_sign_inputs() -> None:
    rng = np.random.default_rng(11)
    signs = [rng.choice([-1, 1], size=(16, 16)) for _ in range(3)]
    exact, parts = h5x.exact_ratio(signs)
    assert isinstance(exact, Fraction)
    assert abs(float(exact) - h5.ratio([s.astype(float) for s in signs], 4)) < 1e-12
    assert set(parts) == {"T", "-3", "-2", "-1", "0"}
    ones, _ = h5x.exact_ratio([np.ones((8, 8), dtype=int)] * 3)
    assert ones == Fraction(1)


def test_h4_controls_van_der_pol_one_cycle_linear_focus_none() -> None:
    assert len(h4.count_cycles(h4.van_der_pol(), grid=60)) == 1
    focus = np.array([0.0, 0.3])  # F = 0.3 x: stable focus, no periodic orbit
    assert h4.count_cycles(focus, grid=40) == []


def test_h4_melnikov_poly_has_prescribed_shape() -> None:
    rng = np.random.default_rng(5)
    c = h4.melnikov_poly(rng, 5, 0.01)
    assert c.shape == (6,)
    assert c[0] == 0.0
    assert abs(c[5]) > 0


def test_h2_window_min_picks_smallest_in_range() -> None:
    rows = [(10, 0.9), (20, 0.4), (40, 0.1), (80, 0.05)]
    assert h2.window_min(rows, 15, 50) == (0.1, 40)
    val, arg = h2.window_min(rows, 100, 200)
    assert arg == 0 and val != val  # nan when empty


def test_scan_flags_ignore_comments_and_keep_line_numbers() -> None:
    src = "theorem a : True := trivial\n-- sorry in a comment\n/- sorry\n block -/\naxiom cheat : False\ntheorem b : 1 = 1 := by sorry\n"
    flags = scan.flag_lines(src, "X.lean")
    assert flags["axiom"] == ["X.lean:5"]
    assert flags["sorry"] == ["X.lean:6"]
    assert "admit" not in flags
