"""Tests for the streaming H2(b) extension runner (scripts/openai_math/hypotheses/night/h2_extend.py)."""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "openai_math" / "hypotheses" / "night" / "h2_extend.py"


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


h2x = _load("h2_extend_t", RUNNER)


def _squarefree(n: int) -> bool:
    p = 2
    while p * p <= n:
        if n % (p * p) == 0:
            return False
        p += 1
    return True


def _is_fundamental_negative(a: int) -> bool:
    """Independent pure-Python test that D = -a is a fundamental discriminant."""
    d = -a
    if d % 4 == 1:
        return _squarefree(a)
    if d % 4 == 0:
        m = d // 4
        return m % 4 in (2, 3) and _squarefree(abs(m))
    return False


def test_fundamental_rows_match_independent_definition_and_known_h() -> None:
    pytest.importorskip("cypari2")
    rows = h2x.fundamental_rows(2, 400)
    got = [a for a, _ in rows]
    expected = [a for a in range(3, 401) if _is_fundamental_negative(a)]
    assert got == expected
    h = dict(rows)
    assert h[23] == 3 and h[47] == 5 and h[71] == 7 and h[163] == 1
    assert sorted(a for a, hh in rows if hh == 1) == h2x.HEEGNER_ABS
    assert h2x.quadclassunit_h(163) == 1 and h2x.quadclassunit_h(71) == 7


def test_dyadic_k_edges_are_half_open_on_the_left() -> None:
    assert h2x.dyadic_k(2**24) == 23
    assert h2x.dyadic_k(2**24 + 1) == 24
    assert h2x.dyadic_k(10**7 + 1) == 23
    assert h2x.dyadic_k(10**8) == 26
    with pytest.raises(ValueError):
        h2x.dyadic_k(1)


def test_chunk_bounds_tile_and_tiling_check_detects_gap_and_overlap() -> None:
    bounds = h2x.chunk_bounds(10**7, 10**8, 500_000)
    assert len(bounds) == 180 and bounds[0] == (10**7, 10**7 + 500_000) and bounds[-1][1] == 10**8
    chunks = [{"lo_excl": lo, "hi_incl": hi} for lo, hi in bounds]
    assert h2x.check_tiling(chunks, 10**7, 10**8) == []
    gap = chunks[:10] + chunks[11:]
    assert h2x.check_tiling(gap, 10**7, 10**8) == [f"gap ({bounds[9][1]}, {bounds[11][0]}]"]
    overlap = chunks + [{"lo_excl": bounds[3][0] + 1, "hi_incl": bounds[3][1]}]
    assert any(p.startswith("overlap") for p in h2x.check_tiling(overlap, 10**7, 10**8))
    assert h2x.check_tiling(chunks[:-1], 10**7, 10**8) == [f"gap ({bounds[-1][0]}, {10**8}]"]


def test_summarize_chunk_minima_windows_and_recheck_mismatch() -> None:
    rows = [(23, 3), (31, 3), (35, 2), (39, 4), (40, 2), (43, 1)]
    good = h2x.summarize_chunk(rows, 20, 44, recheck=dict(rows).__getitem__)
    s = {a: math.pi * h / math.sqrt(a) * math.log(math.log(a)) for a, h in rows}
    a_min = min(s, key=s.__getitem__)
    assert good["argmin_S_D"] == -a_min and abs(good["min_S"] - s[a_min]) < 1e-15
    assert good["h1_count"] == 1 and good["h1_absD"] == [43]
    assert good["recheck_agrees"] is True
    ks = [w["k"] for w in good["windows"]]
    assert ks == [4, 5]  # 23, 31 in (16, 32]; 35..43 in (32, 64]
    assert sum(w["n"] for w in good["windows"]) == 6
    wrong = dict(rows)
    wrong[a_min] = 99
    bad = h2x.summarize_chunk(rows, 20, 44, recheck=wrong.__getitem__)
    assert bad["recheck_agrees"] is False and bad["recheck_mismatches"][0]["absD"] == a_min


def test_merge_windows_keeps_global_minimum_per_window() -> None:
    c1 = {"windows": [{"k": 5, "n": 2, "min_S": 0.7, "argmin_S_absD": 40, "h_at_min_S": 2,
                       "min_L": 0.9, "argmin_L_absD": 40, "h_at_min_L": 2}]}
    c2 = {"windows": [{"k": 5, "n": 3, "min_S": 0.6, "argmin_S_absD": 55, "h_at_min_S": 4,
                       "min_L": 1.1, "argmin_L_absD": 59, "h_at_min_L": 3},
                      {"k": 6, "n": 1, "min_S": 0.8, "argmin_S_absD": 70, "h_at_min_S": 4,
                       "min_L": 1.0, "argmin_L_absD": 70, "h_at_min_L": 4}]}
    merged = h2x.merge_windows([c1, c2])
    assert [w["k"] for w in merged] == [5, 6]
    assert merged[0]["n"] == 5 and merged[0]["argmin_S_absD"] == 55 and merged[0]["argmin_L_absD"] == 40


def test_exact_s_below_agrees_with_float_away_from_tie() -> None:
    pytest.importorskip("mpmath")
    assert h2x.exact_s_below(163, 1, 0.41) is True
    assert h2x.exact_s_below(163, 1, 0.40) is False


def test_decide_requires_matching_preregistered_hash_and_controls() -> None:
    assert h2x.decide(True, True, False) == "PASS"
    assert h2x.decide(True, True, True) == "FAIL"
    assert h2x.decide(True, False, False).startswith("CRASH (runner changed")
    assert h2x.decide(False, True, True).startswith("CRASH (control failed")


def test_dyadic_k_property() -> None:
    hyp = pytest.importorskip("hypothesis")
    st = pytest.importorskip("hypothesis.strategies")

    @hyp.given(st.integers(min_value=2, max_value=10**12))
    def prop(a: int) -> None:
        k = h2x.dyadic_k(a)
        assert 2**k < a <= 2 ** (k + 1)

    prop()
