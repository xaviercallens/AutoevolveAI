"""Tests for the H4 v2 Lienard instrument (scripts/openai_math/hypotheses/night/h4_v2.py)."""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest
from numpy.polynomial import polynomial as P
from scipy.integrate import quad

ROOT = Path(__file__).resolve().parents[2]
H4V2 = ROOT / "scripts" / "openai_math" / "hypotheses" / "night" / "h4_v2.py"


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


h4 = _load("h4_v2_t", H4V2)


@pytest.mark.parametrize("method", ["Radau", "DOP853", "LSODA"])
def test_deadline_is_enforced_inside_the_integration(method: str) -> None:
    tiny = h4.land(h4.van_der_pol(), 2.0, +1, method, deadline_s=1e-6)
    assert tiny.status == "timeout"
    assert math.isnan(tiny.y)
    normal = h4.land(h4.van_der_pol(), 1.0, +1, method)
    assert normal.status == "ok" and normal.y < 0.0


def test_two_sided_map_brackets_the_van_der_pol_cycle_with_both_solvers() -> None:
    vdp = h4.van_der_pol()
    lo_r, st_lo = h4.two_sided(vdp, 1.0, "Radau", 1e-10, 1e-12)
    hi_r, st_hi = h4.two_sided(vdp, 3.0, "Radau", 1e-10, 1e-12)
    assert st_lo == "ok" and lo_r < 0.0
    # outside the attracting cycle the backward orbit escapes: surrogate must be used
    assert st_hi == "ok_fr" and hi_r > 0.0
    lo_d, _ = h4.two_sided(vdp, 1.0, "DOP853", 1e-12, 1e-14)
    assert abs(lo_r - lo_d) < 1e-6


def test_surrogate_sign_matches_two_sided_sign_where_both_exist() -> None:
    vdp = h4.van_der_pol()
    for y in (0.3, 1.0, 1.9):
        d, st = h4.two_sided(vdp, y, "DOP853", 1e-12, 1e-14)
        pr, st2 = h4.full_return(vdp, y)
        assert st == "ok" and st2 == "ok"
        assert math.copysign(1.0, d) == -math.copysign(1.0, pr)


def test_sdi_exact_integral_matches_quadrature_and_vanishes_for_even_f0() -> None:
    f0 = h4.f0_poly([0.3, 0.1, 0.0, 0.05])
    for x_r in (0.2, 0.5):
        val, x_l, _ = h4.sdi(f0, x_r)
        assert math.isfinite(val) and x_l < 0.0
        df = P.polyder(f0)
        ref = quad(lambda x: P.polyval(x, df) ** 2 / x, x_l, x_r, points=[0.0], limit=200)[0]
        assert abs(P.polyval(x_l, f0) - P.polyval(x_r, f0)) < 1e-12
        assert abs(val - ref) < 1e-9 * max(1.0, abs(ref))
    even = h4.f0_poly([0.0, -0.7, 0.0, 0.5])
    val, x_l, scale = h4.sdi(even, 0.6)
    assert abs(x_l + 0.6) < 1e-9
    assert abs(val) <= h4.SDI_NOISE * scale
    assert h4.sdi_profile(even)["sign_changes"] == 0


def test_sdi_degree_four_has_no_sign_change_consistent_with_li_llibre() -> None:
    # k simple SDI zeros give k+1 cycles for small eps; degree 4 has at most 1 cycle
    res = h4.sdi_design(4, seed=5, trials=60)
    assert sum(res["histogram"].values()) > 0
    assert set(res["histogram"]) == {0}


def test_classical_coeffs_is_the_slow_fast_rescaling() -> None:
    rng = np.random.default_rng(1)
    for _ in range(20):
        f0 = h4.f0_poly(rng.standard_normal(4).tolist())
        a, eps = float(rng.uniform(-0.1, 0.1)), float(10 ** rng.uniform(-3, -1))
        c = h4.classical_coeffs(f0, a, eps)
        assert len(c) == 7 and c[0] == 0.0
        x = float(rng.uniform(-2, 2))
        assert abs(P.polyval(x, c) - (a * x + P.polyval(x, f0)) / math.sqrt(eps)) < 1e-9 * (1 + abs(P.polyval(x, c)))


def test_best_level_counts_crossings_at_a_single_level() -> None:
    ys = np.linspace(0.0, 4.0 * math.pi, 200)
    curve = [{"y": float(y), "a": float(math.sin(y)) * (1 + 0.01 * y)} for y in ys]
    a_star, n = h4.best_level(curve)
    s = np.sign(np.array([c["a"] for c in curve]) - a_star)
    assert n == int(np.sum(s[1:] * s[:-1] < 0))
    assert n == 4
    mono = [{"y": float(y), "a": float(y)} for y in ys]
    assert h4.best_level(mono)[1] == 1
    top = h4.ranked_levels(curve, 3)
    assert top[0][1] == 4 and len(top) == 3
    assert len({lv for lv, _ in top}) == 3
    assert top[1][1] <= 4 and top[2][1] <= top[1][1]


def test_a_resolution_flags_ulp_level_curves() -> None:
    a0 = -1.8915705225562205e-4
    flat = [{"a": a0}, {"a": float(np.nextafter(a0, 0.0))}]
    assert h4.a_resolution_ulps(flat) < 64
    spread = [{"a": -3.57e-4}, {"a": -4.07e-4}, {"a": -4.47e-4}]
    assert h4.a_resolution_ulps(spread) > 1e6


def test_count_cycles_finds_the_van_der_pol_cycle_and_none_for_a_stable_focus() -> None:
    r = h4.count_cycles(h4.van_der_pol(), 0.5, 5.0, grid=12)
    assert r.n == 1
    assert 1.9 < r.confirmed[0] < 2.2
    # F = x/2 + x^3: divergence -F' < 0 everywhere, Bendixson: no periodic orbit
    r0 = h4.count_cycles(np.array([0.0, 0.5, 0.0, 1.0]), 0.1, 5.0, grid=10)
    assert r0.n == 0 and not r0.unconfirmed


def test_sdi_property_random_f0_exact_vs_quadrature() -> None:
    hyp = pytest.importorskip("hypothesis")
    st = pytest.importorskip("hypothesis.strategies")

    @hyp.given(st.lists(st.floats(-0.5, 0.5), min_size=4, max_size=4), st.floats(0.05, 0.3))
    @hyp.settings(max_examples=25, deadline=None)
    def prop(c: list[float], x_r: float) -> None:
        f0 = h4.f0_poly(c)
        val, x_l, _ = h4.sdi(f0, x_r)
        if not math.isfinite(val):
            return
        df = P.polyder(f0)
        ref = quad(lambda x: P.polyval(x, df) ** 2 / x, x_l, x_r, points=[0.0], limit=200)[0]
        assert abs(val - ref) < 1e-8 * max(1.0, abs(ref))

    prop()
