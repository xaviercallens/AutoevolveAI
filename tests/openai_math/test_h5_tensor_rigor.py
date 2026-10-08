"""Tests for scripts/openai_math/hypotheses/tensor/h5_tensor_rigor.py (independent exact evaluator)."""

from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
TENSOR = ROOT / "scripts" / "openai_math" / "hypotheses" / "tensor"
sys.path.insert(0, str(TENSOR))
sys.path.insert(0, str(ROOT / "scripts" / "openai_math" / "hypotheses"))


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


rig = _load("h5_tensor_rigor", TENSOR / "h5_tensor_rigor.py")
h5x = _load("h5_exact_cmp", ROOT / "scripts" / "openai_math" / "hypotheses" / "h5_exact.py")


def rand_pm1(rng: np.random.Generator, N: int) -> list[np.ndarray]:
    return [rng.choice([-1, 1], size=(2**N, 2**N)).astype(np.int64) for _ in range(3)]


def test_constant_input_has_ratio_one_and_haar_free_grows() -> None:
    ones = [np.ones((8, 8), dtype=np.int64)] * 3
    assert rig.R_pm1(ones) == 1
    parts = rig.exact_parts(ones)
    assert parts["T"] == 1 and all(v == 0 for k, v in parts.items() if k != "T")
    # Haar-free power control: every level contributes exactly 1 when the signs are all +1.
    original = rig.haar_sign
    try:
        rig.haar_sign = lambda b: np.ones(b, dtype=np.int64)
        assert rig.R_pm1(ones) == 4  # N = 3 -> N + 1
    finally:
        rig.haar_sign = original


def test_agrees_with_the_earlier_exact_evaluator_on_random_inputs() -> None:
    rng = np.random.default_rng(5)
    for N in (1, 2, 3, 4):
        f = rand_pm1(rng, N)
        mine = rig.R_pm1(f)
        theirs, _ = h5x.exact_ratio(f)
        assert mine == theirs
        assert isinstance(mine, Fraction)


def test_committed_witnesses() -> None:
    p = ROOT / "results" / "openai_math" / "hypotheses" / "H5" / "best_inputs_N4.npz"
    if not p.exists():
        pytest.skip("witness file not present")
    z = np.load(p)
    w4 = [np.where(z[k] >= 0, 1, -1).astype(np.int64) for k in z.files]
    assert rig.R_pm1(w4) == Fraction(5, 2)
    assert rig.R_pm1(rig.kron(w4, w4)) == Fraction(23, 8)


def test_product_rule_pm1_and_general() -> None:
    rng = np.random.default_rng(9)
    out = rig.check_product_rule_pm1(rng, n_pairs=6)
    assert out["all_pass"] and len(out["checks"]) == 6
    gen = rig.check_product_rule_general(rng, n_pairs=4)
    assert gen["all_pass"]
    assert all(c["T_mult"] and c["norms_mult"] for c in gen["checks"])


def test_closure_lemma_phi_of_product_does_not_exceed_max_phi() -> None:
    rng = np.random.default_rng(21)
    for _ in range(8):
        f, g = rand_pm1(rng, 1), rand_pm1(rng, 2)
        pf, pg, pfg = rig.phi_pm1(f), rig.phi_pm1(g), rig.phi_pm1(rig.kron(f, g))
        if pf is None or pg is None or pfg is None:
            continue
        assert pfg <= max(pf, pg)


def test_seed_powers_follow_closed_form() -> None:
    g = rig.seed_from_lane()
    if g is None:
        pytest.skip("seed witness not present")
    assert rig.exact_H(g) == Fraction(3, 2) and abs(rig.exact_T(g)) == Fraction(1, 2)
    assert rig.phi_pm1(g) == 3
    rows = rig.tensor_powers(g, 3)
    assert [r["R"] for r in rows] == ["2", "5/2", "11/4"]
    assert rig.tensor_powers_predicted(g, 4) == ["2", "5/2", "11/4", "23/8"]


def test_exhaustive_N1_maxima() -> None:
    out = rig.exhaustive_N1()
    assert out["count"] == 4096
    assert out["max_R"] == "1" and out["max_phi"] == "1"
