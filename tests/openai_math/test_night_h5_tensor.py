"""Tests for the H5 lane's exploratory tools (deviations.md items 5 and 7).

Covers results/openai_math/hypotheses/night_2026-10-07/H5/{verify_tensor.py, holder_bound.py}.
`hypothesis` is not installed for /usr/bin/python3, so property checks use seeded loops.
"""

from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path
from types import ModuleType

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
LANE = ROOT / "results" / "openai_math" / "hypotheses" / "night_2026-10-07" / "H5"
HYP = ROOT / "scripts" / "openai_math" / "hypotheses"


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


vt = _load("h5_verify_tensor_t", LANE / "verify_tensor.py")
hb = _load("h5_holder_bound_t", LANE / "holder_bound.py")
hx = _load("h5_exact_t", HYP / "h5_exact.py")


def _witness() -> list[np.ndarray]:
    z = np.load(ROOT / "results" / "openai_math" / "hypotheses" / "H5" / "best_inputs_N4.npz")
    return [np.where(z[k] >= 0, 1, -1).astype(np.int64) for k in z.files]


def test_direct_matches_h5_exact_on_random_pm1() -> None:
    rng = np.random.default_rng(11)
    for n in (2, 3):
        for _ in range(5):
            q = [rng.choice(np.array([-1, 1]), size=(2**n, 2**n)) for _ in range(3)]
            r, h, t = vt.pm1_ratio(q)
            assert r == hx.exact_ratio(q)[0]
            assert t == Fraction(hx.exact_ratio(q)[1]["T"])
            assert h == r - Fraction(hx.exact_ratio(q)[1]["T"])


def test_direct_ratio_constant_and_witness() -> None:
    ones = [np.ones((8, 8), dtype=np.int64)] * 3
    assert vt.direct_ratio_cubed(ones) == 1
    r, h, t = vt.pm1_ratio(_witness())
    assert r == Fraction(5, 2)
    assert (h, t) == (Fraction(9, 4), Fraction(1, 4))


def test_product_rule_on_random_pm1_pairs() -> None:
    rng = np.random.default_rng(12)
    for _ in range(6):
        f = [rng.choice(np.array([-1, 1]), size=(4, 4)) for _ in range(3)]
        g = [rng.choice(np.array([-1, 1]), size=(4, 4)) for _ in range(3)]
        rf = vt.pm1_ratio(f)[0]
        _, hg, tg = vt.pm1_ratio(g)
        lhs = vt.pm1_ratio([np.kron(a, b) for a, b in zip(f, g)])[0]
        assert lhs == hg + tg * rf
        assert lhs == hx.exact_ratio([np.kron(a, b) for a, b in zip(f, g)])[0]


def test_tensor_of_witness_beats_five_halves() -> None:
    w4 = _witness()
    w44 = [np.kron(a, a) for a in w4]
    exact = hx.exact_ratio(w44)[0]
    assert exact == Fraction(23, 8)
    assert vt.pm1_ratio(w44)[0] == Fraction(23, 8)


def test_holder_bound_small_n_and_haarfree() -> None:
    assert hb.holder_bound(1)["B_cubed"] == "1"
    b2 = hb.holder_bound(2)
    assert b2["complete"] and b2["B_cubed"] == "8"
    assert hb.holder_bound(2, haar=False)["B_cubed"] == "27"


def test_holder_bound_dominates_random_real_inputs() -> None:
    bound = Fraction(hb.holder_bound(2)["B_cubed"])
    check = hb.random_real_check(2, bound, 200, 13)
    assert check["below_bound"]
    assert 0.0 < check["max_ratio"] <= 2.0 + 1e-12
