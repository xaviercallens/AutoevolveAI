"""Tests for the night H5 lane instrument (scripts/openai_math/hypotheses/night/h5_multiscale.py).

`hypothesis` is not installed for /usr/bin/python3 on this machine, so property checks use
seeded loops over random inputs instead.
"""

from __future__ import annotations

import importlib.util
import sys
import time
from fractions import Fraction
from pathlib import Path
from types import ModuleType

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NIGHT = ROOT / "scripts" / "openai_math" / "hypotheses" / "night" / "h5_multiscale.py"


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ms = _load("h5_multiscale_t", NIGHT)
h5d = ms.h5d
h5x = ms.h5x


def _pm(rng: np.random.Generator, size: int) -> np.ndarray:
    return rng.choice(np.array([-1, 1], dtype=np.int64), size=(size, size))


def test_certify_agrees_with_h5_exact_and_float_ratio() -> None:
    rng = np.random.default_rng(101)
    for n in (2, 3, 4):
        signs = [_pm(rng, 2**n) for _ in range(3)]
        exact, _ = h5x.exact_ratio(signs)
        cert = ms.certify(signs, threshold=exact)
        assert Fraction(cert["ratio_cubed"]) == exact**3
        assert cert["exceeds"] is False
        ints = [rng.integers(-40, 41, size=(2**n, 2**n)) for _ in range(3)]
        c2 = ms.certify(ints)
        f = h5d.ratio([x.astype(float) for x in ints], n)
        assert abs(c2["ratio_float"] - f) <= 1e-12 * f


def test_threshold_decision_on_committed_witness_and_ones_lift() -> None:
    w4 = ms.witness_signs(4)
    assert ms.certify(w4)["exceeds"] is False
    assert ms.certify(w4, threshold=Fraction(5, 2) - Fraction(1, 10**9))["exceeds"] is True
    lifted = ms.kron_lift(w4, [np.ones((4, 4), dtype=np.int64)] * 3)
    assert lifted[0].shape == (64, 64)
    assert Fraction(ms.certify(lifted)["ratio_cubed"]) == Fraction(125, 8)


def test_int_parts_rejects_overflow_and_bad_shapes() -> None:
    big = [np.full((4, 4), 2**19, dtype=np.int64)] * 3
    try:
        ms.int_parts(big)
        raised = False
    except OverflowError:
        raised = True
    assert raised
    try:
        ms.int_parts([np.ones((3, 3), dtype=np.int64)] * 3)
        bad = False
    except ValueError:
        bad = True
    assert bad


def test_quantize_is_tight_and_preserves_ratio_closely() -> None:
    rng = np.random.default_rng(5)
    a = [rng.standard_normal((8, 8)) for _ in range(3)]
    q = ms.quantize(a)
    bits = (62 - 9) // 3 - 1
    assert all(int(np.abs(x).max()) == 2**bits - 1 for x in q)
    rel = abs(ms.certify(q)["ratio_float"] - h5d.ratio(a, 3)) / h5d.ratio(a, 3)
    assert rel < 1e-4


def test_gradient_matches_h5_dyadic_and_finite_differences_both_forms() -> None:
    rng = np.random.default_rng(9)
    a = [rng.standard_normal((8, 8)) for _ in range(3)]
    assert np.abs(ms.gradient(a, 3, True) - h5d.gradient_first(a, 3)).max() < 1e-14
    for haar in (True, False):
        g = ms.gradient(a, 3, haar)
        eps = 1e-6
        i, j = 3, 5
        bump = [x.copy() for x in a]
        bump[0][i, j] += eps
        fd = (h5d.form_sum(bump, 3, haar) - h5d.form_sum(a, 3, haar)) / eps
        assert abs(fd - g[i, j]) < 1e-6 * max(1.0, abs(g[i, j]))


def test_exhaustive_n1_equals_bruteforce_over_all_4096() -> None:
    res = ms.exhaust_range(1, 0, 8, time.time() + 60)
    brute = 0
    for idx in range(2**12):
        bits = np.array([(idx >> b) & 1 for b in range(12)], dtype=np.int64)
        mats = [(1 - 2 * bits[4 * v : 4 * v + 4]).reshape(2, 2) for v in range(3)]
        brute = max(brute, ms.int_parts(mats)[0])
    assert res["complete"] is True
    assert res["max_S"] == brute
    assert res["argmax_recheck_agrees"] is True


def test_pattern_maximum_equals_bruteforce_over_f2_at_n2() -> None:
    for seed in (1, 2):
        xs = ms.exhaust_crosscheck(np.random.default_rng(seed))
        assert xs["term_sum_equals_int_parts"] is True
        assert xs["pattern_max_equals_bruteforce_max"] is True
    assert len(ms.term_vectors(2)) == 6
    assert len(ms.term_vectors(3)) == 22


def test_sign_matrix_indexing_is_consistent() -> None:
    mats = ms.all_sign_matrices(1, fix_first=True)
    assert mats.shape == (8, 2, 2)
    assert all(int(m[0, 0]) == 1 for m in mats)
    for idx in (0, 3, 7):
        assert np.array_equal(mats[idx], ms.sign_matrix_from_index(idx, 1, fix_first=True))
    assert len({m.tobytes() for m in ms.all_sign_matrices(1, fix_first=False)}) == 16


def test_walsh_matrix_is_orthogonal_and_blocks_are_pm1() -> None:
    h = ms.walsh_matrix(3)
    assert np.array_equal(h @ h.T, 8 * np.eye(8, dtype=np.int64))
    blk = ms.walsh_block(2, 1, 3)
    assert set(np.unique(blk)) == {-1, 1}
    assert int(blk.sum()) == 0
    rng = np.random.default_rng(0)
    idx = ms.walsh_choice(rng, 2, coupled=True)
    assert idx[0][1] == idx[1][0] and idx[1][1] == idx[2][0] and idx[2][1] == idx[0][0]


def test_power_control_haar_free_form_is_certified_above_threshold() -> None:
    rng = np.random.default_rng(77)
    a0 = [rng.standard_normal((8, 8)) for _ in range(3)]
    a, val, sweeps, _ = ms.ascend_timed(a0, 3, 50, time.time() + 60, haar=False)
    cert = ms.certify_candidate(a, haar=False)
    assert val > 2.5 and sweeps >= 1
    assert cert["certified_exceeds"] is True
    a_h, val_h, _, _ = ms.ascend_timed([x.copy() for x in a0], 3, 50, time.time() + 60, haar=True)
    assert val_h >= h5d.ratio(a0, 3) - 1e-12


def test_explain_decomposition_sums_to_exact_ratio() -> None:
    rng = np.random.default_rng(31)
    signs = [_pm(rng, 8) for _ in range(3)]
    out = ms.explain(signs)
    exact, parts = h5x.exact_ratio(signs)
    assert out["exact_ratio"] == str(exact)
    for k, rows in out["triples"].items():
        assert sum(abs(Fraction(r["L"])) for r in rows) == Fraction(parts[k])
    assert len(out["walsh_spectra"]) == 3
    assert all(sp["support_size"] >= 1 for sp in out["walsh_spectra"])


def test_multiscale_inits_have_expected_shape_and_values() -> None:
    rng = np.random.default_rng(4)
    s = ms.multiscale_signs(rng, 4)
    assert all(x.shape == (16, 16) and set(np.unique(x)) <= {-1, 1} for x in s)
    g = ms.multiscale_gauss(rng, 4, 0.7)
    assert all(x.shape == (16, 16) and np.isfinite(x).all() for x in g)
    up = ms.upsample(np.array([[1, -1], [-1, 1]], dtype=np.int64), 3)
    assert up.shape == (8, 8) and int(up[3, 3]) == 1 and int(up[4, 3]) == -1


def test_big_parts_equals_int_parts_and_is_exactly_homogeneous() -> None:
    rng = np.random.default_rng(13)
    for n in (2, 3):
        q = [rng.integers(-30, 31, size=(2**n, 2**n)) for _ in range(3)]
        obj = [np.array([[int(v) for v in row] for row in x], dtype=object) for x in q]
        assert ms.big_parts(obj)[0] == ms.int_parts(q)[0]
        big = [x * (1 << 40) + 0 for x in obj]
        assert ms.big_parts(big)[0] == ms.int_parts(q)[0] * (1 << 120)
        assert ms.certify_big(big)["ratio_cubed"] == ms.certify(q)["ratio_cubed"]
    assert ms.big_parts(obj, haar=False)[0] == ms.int_parts(q, haar=False)[0]


def test_high_precision_path_runs_near_five_halves_and_does_not_exceed_on_witness() -> None:
    w = [x.astype(float) for x in ms.witness_signs(4)]
    cert = ms.certify_candidate(w)
    assert "high_precision" in cert
    assert Fraction(cert["high_precision"]["ratio_cubed"]) == Fraction(125, 8)
    assert cert["certified_exceeds"] is False
    hp = ms.quantize_hp([np.array([[0.5, -1.0], [0.25, 1.0]])] * 3)
    assert int(hp[0][0, 1]) == -(1 << 53) and int(hp[0][1, 0]) == 1 << 51
