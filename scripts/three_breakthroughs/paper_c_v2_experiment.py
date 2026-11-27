"""Paper C, edition 2: which Hecke eigenforms govern 2-isogeny returns to the SQIsign curve E_0?

Question
--------
E_0 : y^2 = x^3 + x (j = 1728) over F_{p^2}, p = 3 mod 4, has End(E_0) = O_0 = Z<1, i, (i+j)/2, (1+k)/2>
in B_{p,inf} (i^2 = -1, j^2 = -p): the order edition 1 formalised and SQIsign's starting curve. The
number of primitive elements of reduced norm 2^e,
    N_e(p) = #{alpha in O_0 \\ 2 O_0 : Nrd(alpha) = 2^e}  (= r(2^e) - r(2^{e-2}), Lean: o0Norm_half),
counts cyclic 2^e-endomorphisms of E_0 times |O_0^x|, i.e. closed non-backtracking 2-isogeny walks.
Which weight-2 newforms of level p actually appear in N_e?

Pre-registered predictions (fixed 2026-10-21 before the full run; pilot numbers in the audit):
  P1  N_e(p) = 36 * 2^e / (p - 1) + O_p(2^{e/2}); exact for class number one (p = 3, 7).
  P2  The minimal recurrence of (N_e)_{e>=2} has roots {2} and the Ihara roots of x^2 - a_f(2) x + 2
      (all of modulus sqrt 2) for exactly the newform orbits f whose projection in theta_{O_0} is non-zero
      ("visible" orbits).
  P3  (Gross 1987) f is visible iff L(f,1) L(f x chi_{-4},1) != 0; hence no root-number -1 orbit is
      visible, and a root-number +1 orbit is invisible only when one of the two central values vanishes.

Methods (all number-theoretic ground truth from PARI/GP via paper_c_v2_pari_worker.py)
  M1  exact lattice counts of O_0 (numpy, integer arithmetic), p in P83, e <= E_MAX;
  M2  Brandt-module counts r(2^e) = |O_0^x| (B(2^e))_{E_0,E_0} from the supersingular 2-isogeny graph over
      F_{p^2} (PARI polmodular + factor over F_{p^2}), recursion B(2^{k+1}) = B(2) B(2^k) - 2 B(2^{k-1});
  M3  visibility of each Hecke orbit in e_{E_0} on the isogeny graph (Frobenius = T_p gives a_p = root
      number), p < P_VIS_MAX;
  M4  independent visibility by projecting theta_{O_0} (PARI qfrep) on newform orbits from modular symbols
      (msinit/mssplit/msqexpansion/msatkinlehner), p < P_VISA_MAX;
  M5  L(f,1) and L(f x chi_{-4},1) (PARI lfun, functional-equation check) for orbits of dimension <= 3.

Falsification criteria (any one refutes the contribution)
  (a) N_e(3) != 18 * 2^e or N_e(7) != 6 * 2^e for some e <= E_MAX;
  (b) a recovered non-trivial recurrence root has |z|^2 != 2, a cusp Hecke eigenvalue on the graph has
      |a_2| > 2 sqrt 2, or the recurrence polynomial differs from (x - 2) prod_{visible} x^d P_f(x + 2/x);
  (c) [WITHDRAWN 21 Oct 2026, edition 3] an orbit with root number -1 is visible. This cannot occur:
      j(E_0) = 1728 is F_p-rational, so Frobenius fixes e_{E_0}, commutes with the Brandt matrices and
      acts by w on the f-component, forcing pi_f e_{E_0} = 0 whenever w = -1 (Lean:
      formal/ANSE/PaperC_ForcedVisibility.lean, frobenius_forces_vanishing). Independently, w = -1 gives
      an odd functional equation, so L(f,1) = 0 and Gross predicts invisibility from ANY base point. The
      criterion is retained in the record but removed from `refuted`; it is replaced by (c');
  (c') [ADDED 21 Oct 2026, edition 3] a w = +1 orbit is discordant, i.e. visible with a vanishing central
      value or invisible with both central values non-zero. Nothing forces this half: Frobenius acts by
      +1 there, so the hypotheses leave visibility free (Lean: frobenius_forces_nothing_at_w_one). This
      is the criterion that carries the Gross test;
  (d) an invisible root-number +1 orbit has |L(f,1)| > 1e-10 and |L(f x chi_{-4},1)| > 1e-10 with both
      functional-equation checks below -30 bits;
  (e) for some p, max_{12<=e<=22} |D_e| > 2 max_{2<=e<=11} |D_e|, D_e = (N_e - 36 2^e/(p-1)) / 2^{e/2}.

Controls
  positive: (i) class number one exact laws; (ii) PARI qfrep = numpy counts, graph counts = lattice counts;
            (iii) p = 11 recovers a_2(11a) = -2 and L(11a,1) = 0.2538...; (iv) p = 139 Gross vanishing;
            (v) Frey (15,16,31): conductor 465, Delta_min 216225; (vi) visible root-number +1 orbits of
            dimension <= 3 have non-zero L(f,1) L(f x chi,1); (vii) [ADDED 21 Oct 2026, edition 3] the
            w = +1 stratum test: visibility agrees with L-nonvanishing on every w = +1 orbit, with an
            EXACT within-prime permutation p-value < 1e-3. This replaces negative control (iv) in the
            `controls_ok` gate. Unlike (iv) it can come out non-significant, which tests/
            test_paper_c_w_plus_stratum.py demonstrates by breaking the association on purpose.
  negative: (i) the Lipschitz order Z<1,i,j,k> at p = 3 must FAIL the exact law; (ii) (-1,-313) is ramified
            at {2, inf} (not B_{313,inf}) and its counts must not follow 36 2^e / 312; (iii) edition 1's
            sigma = 128 + 128 j and the scalar 256 are in 2 O_0 (non-primitive) yet the Rust function
            accepts them (cargo probe); (iv) [WITHDRAWN 21 Oct 2026, edition 3] shuffling root numbers
            across orbits (10^4 permutations) must destroy the "w = -1 => invisible" pattern. The observed
            statistic is forced to 0 by (c) above, so this control is significant whatever the data say and
            measures nothing; it is removed from `controls_ok`, kept in the JSON as a descriptive record,
            and replaced by positive control (vii); (v) (3,6,9) is not semistable.

Output: papers/three_breakthroughs/paper_c/paper_c_v2_results.json
Run:    PAPER_C_PARI_PYTHON=<python with cypari2> .venv/bin/python scripts/three_breakthroughs/paper_c_v2_experiment.py
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import random
import subprocess
import sys
import tempfile
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "papers" / "three_breakthroughs" / "paper_c" / "paper_c_v2_results.json"
WORKER = Path(__file__).resolve().parent / "paper_c_v2_pari_worker.py"
PROBE = Path(__file__).resolve().parent / "paper_c_v2_rust_probe"
FALLBACK_PARI_PYTHON = Path(
    "/mnt/data/xdev-cache/tmp/claude-1000/-home-xavkal-xdev-AutoevolveAI/"
    "da32aa4f-c38b-4872-8c90-64448f5fc915/scratchpad/pari-venv/bin/python"
)

P83: tuple[int, ...] = (3, 7, 11, 19, 23, 31, 43, 47, 59, 67, 71, 79, 83)
E_MAX = 22
E_GRAPH = 48
P_VIS_MAX = 2000
P_VISA_MAX = 700
P_LCTRL_MAX = 400
LVAL_DIMLIM = 3
N_PERM = 10_000
SEED = 20261021
FAMILY_PRIMES: tuple[int, ...] = (5, 7, 11, 13, 17, 19, 23)
PROCS = int(os.environ.get("PAPER_C_PROCS", "8"))
L_ZERO_TOL = 1e-20
FEQ_BITS = -30
X = sp.symbols("x")


# ----------------------------------------------------------------------------- PARI worker bridge
def pari_python() -> Path | None:
    env = os.environ.get("PAPER_C_PARI_PYTHON")
    if env and Path(env).exists():
        return Path(env)
    return FALLBACK_PARI_PYTHON if FALLBACK_PARI_PYTHON.exists() else None


def worker(task: str, args: dict[str, Any], timeout: int = 7200) -> Any:
    """Run one PARI task in the cypari2 interpreter (isolated mode) and parse its JSON output."""
    py = pari_python()
    if py is None:
        raise RuntimeError("BLOCKED: no Python with cypari2 (set PAPER_C_PARI_PYTHON)")
    res = subprocess.run([str(py), "-I", str(WORKER), task, json.dumps(args)], capture_output=True,
                         text=True, timeout=timeout, check=False)
    if res.returncode != 0:
        raise RuntimeError(f"PARI worker task {task} failed:\n{res.stderr[-3000:]}")
    return json.loads(res.stdout)


# ----------------------------------------------------------------------------- M1 exact lattice counts
class TwoSquareTable:
    """R[pa, pb, M] = #{(a, b) in Z^2 : a^2 + b^2 = M, a = pa, b = pb (mod 2)} for M <= nmax."""

    def __init__(self, nmax: int) -> None:
        s = math.isqrt(nmax)
        a = np.arange(-s, s + 1, dtype=np.int64)
        sq, par = a * a, np.abs(a) % 2
        self.nmax = nmax
        self.R = np.zeros((2, 2, nmax + 1), dtype=np.int32)
        for pa in (0, 1):
            a2 = sq[par == pa]
            for pb in (0, 1):
                b2 = sq[par == pb]
                for chunk in np.array_split(a2, 32):
                    tot = (chunk[:, None] + b2[None, :]).ravel()
                    tot = tot[tot <= nmax]
                    self.R[pa, pb] += np.bincount(tot, minlength=nmax + 1).astype(np.int32)
        self.all = self.R.sum(axis=(0, 1), dtype=np.int64)

    def count(self, target: int, p: int, maximal: bool) -> int:
        """#{(a,b,c,d): a^2 + b^2 + p (c^2 + d^2) = target}, with a = d, b = c (mod 2) if maximal."""
        cmax = math.isqrt(target // p)
        c = np.arange(-cmax, cmax + 1, dtype=np.int64)
        cc, dd = np.meshgrid(c, c, indexing="ij")
        m = target - p * (cc * cc + dd * dd)
        ok = m >= 0
        m, cc, dd = m[ok], cc[ok], dd[ok]
        if maximal:
            return int(self.R[np.abs(dd) % 2, np.abs(cc) % 2, m].astype(np.int64).sum())
        return int(self.all[m].sum())


def r_O0(tab: TwoSquareTable, n: int, p: int) -> int:
    """Number of alpha in O_0 subset B_{p,inf} with Nrd(alpha) = n (4 Nrd = a^2+b^2+p(c^2+d^2))."""
    return tab.count(4 * n, p, maximal=True)


def r_lip(tab: TwoSquareTable, n: int, p: int) -> int:
    """Number of a + bi + cj + dk in Z<1,i,j,k> subset (-1,-p) with Nrd = n."""
    return tab.count(n, p, maximal=False)


def primitive_from_r(r: list[int]) -> list[int]:
    """N_0 = r(1), N_1 = r(2), N_e = r(2^e) - r(2^{e-2}) (halving lemma o0Norm_half)."""
    return [r[0], r[1]] + [r[e] - r[e - 2] for e in range(2, len(r))]


def main_term(p: int, e: int) -> Fraction:
    return Fraction(36 * 2**e, p - 1)


# ----------------------------------------------------------------------------- BM / Ihara
def berlekamp_massey(seq: list[int]) -> list[Fraction]:
    """Minimal connection polynomial C (C_0 = 1) over Q with sum_i C_i s_{n-i} = 0."""
    s = [Fraction(v) for v in seq]
    c, b = [Fraction(1)], [Fraction(1)]
    ell, m, bb = 0, 1, Fraction(1)
    for n in range(len(s)):
        d = s[n] + sum(c[i] * s[n - i] for i in range(1, ell + 1))
        if d == 0:
            m += 1
            continue
        t = c[:]
        coef = d / bb
        c = c + [Fraction(0)] * (len(b) + m - len(c))
        for i in range(len(b)):
            c[i + m] -= coef * b[i]
        if 2 * ell <= n:
            ell, b, bb, m = n + 1 - ell, t, d, 1
        else:
            m += 1
    return c[: ell + 1]


def char_poly_from_connection(c: list[Fraction]) -> sp.Expr:
    ell = len(c) - 1
    return sp.expand(sum(sp.Rational(v.numerator, v.denominator) * X ** (ell - i) for i, v in enumerate(c)))


def ihara_factor(cp: str) -> sp.Expr:
    """x^d P(x + 2/x): the product of x^2 - a x + 2 over the roots a of the a_2-charpoly P."""
    poly = sp.Poly(sp.sympify(cp.replace("^", "**")), X)
    d = poly.degree()
    return sp.expand(sp.cancel(X**d * poly.as_expr().subs(X, X + 2 / X)))


def roots_of(expr: sp.Expr, digits: int = 40) -> list[complex]:
    return [complex(z) for z in sp.Poly(expr, X).nroots(n=digits, maxsteps=200)]


def real_roots(cp: str) -> list[float]:
    return [float(z) for z in sp.Poly(sp.sympify(cp.replace("^", "**")), X).nroots(n=30)]


# ----------------------------------------------------------------------------- helpers
def primes_3mod4(lo: int, hi: int) -> list[int]:
    return [q for q in sp.primerange(lo, hi) if q % 4 == 3]


def o0_coords(a: int, b: int, c: int, d: int) -> tuple[int, int, int, int] | None:
    """O_0 coordinates of (a + bi + cj + dk)/2, or None if it is not in O_0."""
    if (a - d) % 2 or (b - c) % 2:
        return None
    return ((a - d) // 2, (b - c) // 2, c, d)


def o0_norm(m: int, x: tuple[int, int, int, int]) -> int:
    x0, x1, x2, x3 = x
    return x0 * x0 + x1 * x1 + (m + 1) * x2 * x2 + (m + 1) * x3 * x3 + x0 * x3 + x1 * x2


def is_primitive(x: tuple[int, int, int, int]) -> bool:
    return any(v % 2 for v in x)


def primitive_witnesses(p: int, e: int) -> dict[str, Any]:
    """Smallest primitive elements of norm 2^e in O_0 (nonnegative O_0 coordinates, minimal l1 norm)
    and in the Lipschitz lattice (nonnegative a, b, c, d with a + bi + cj + dk primitive in O_0)."""
    m, n = (p - 3) // 4, 2**e
    best_o0: tuple[int, tuple[int, int, int, int]] | None = None
    cmax = math.isqrt(4 * n // p)
    for c in range(0, cmax + 1):
        for d in range(0, cmax + 1):
            rem = 4 * n - p * (c * c + d * d)
            if rem < 0:
                break
            for a in range(0, math.isqrt(rem) + 1):
                b2 = rem - a * a
                b = math.isqrt(b2)
                x = o0_coords(a, b, c, d) if b * b == b2 else None
                if x is not None and all(v >= 0 for v in x) and is_primitive(x):
                    if best_o0 is None or sum(x) < best_o0[0]:
                        best_o0 = (sum(x), x)
    best_lip: tuple[int, tuple[int, int, int, int]] | None = None
    cmax = math.isqrt(n // p)
    for c in range(0, cmax + 1):
        for d in range(0, cmax + 1):
            rem = n - p * (c * c + d * d)
            if rem < 0:
                break
            for a in range(0, math.isqrt(rem) + 1):
                b2 = rem - a * a
                b = math.isqrt(b2)
                if b * b == b2:
                    x = o0_coords(2 * a, 2 * b, 2 * c, 2 * d)
                    if x is not None and is_primitive(x) and (best_lip is None or a + b + c + d < best_lip[0]):
                        best_lip = (a + b + c + d, (a, b, c, d))
    assert best_o0 is not None and best_lip is not None
    assert o0_norm(m, best_o0[1]) == n
    return {"p": p, "e": e, "smallest_primitive_O0_coords": list(best_o0[1]),
            "smallest_primitive_lipschitz_abcd": list(best_lip[1])}


# ----------------------------------------------------------------------------- Rust probe
def rust_probe(cases: list[tuple[str, int, int, int, int]]) -> dict[str, Any]:
    cargo = subprocess.run(["which", "cargo"], capture_output=True, text=True, check=False).stdout.strip()
    if not cargo:
        return {"status": "BLOCKED", "reason": "cargo not found"}
    target = os.environ.get("PAPER_C_CARGO_TARGET", str(Path(tempfile.gettempdir()) / "paper_c_v2_cargo_target"))
    args = [f"{lab}:{a}:{b}:{c}:{d}" for lab, a, b, c, d in cases]
    res = subprocess.run([cargo, "run", "--release", "--quiet", "--offline", "--", *args], cwd=PROBE,
                         capture_output=True, text=True, check=False,
                         env={**os.environ, "CARGO_TARGET_DIR": target})
    if res.returncode != 0:
        return {"status": "BLOCKED", "reason": res.stderr[-2000:]}
    rows = [json.loads(line) for line in res.stdout.splitlines() if line.startswith("{")]
    return {"status": "RAN", "function": "sqisign_flt_verifier::verify_sqisign_response(q, 2, 16, 6561)",
            "rows": rows}


def w_plus_stratum_test(gross_rows: list[dict[str, Any]],
                        exc_lvals: list[dict[str, Any]]) -> dict[str, Any]:
    """The informative half of P3: does graph visibility track L-nonvanishing when w = +1?

    The w = -1 half of P3 cannot fail (see negative_controls.iv_permutation_test), so it
    carries no evidence. The w = +1 half is free: Frobenius acts by +1 on the f-component,
    so pi_f e_{E_0} = pi_f e_{E_0} is vacuous and nothing constrains visibility. Here the
    Brandt-matrix projection (M3/M4) and the analytic L-values (M5, PARI lfun) are two
    independent computations, and Gross 1987 predicts they agree orbit by orbit.

    Statistic: the number of w = +1 orbits on which visibility agrees with L-nonvanishing.
    Null: within each prime, the L-vanishing labels are reassigned uniformly among that
    prime's w = +1 orbits, which removes any confound that varies with p. Only primes
    carrying both a visible and an invisible w = +1 orbit contribute; the rest are constant
    under the null and are reported separately. The p-value is exact (a hypergeometric
    convolution, not Monte Carlo), so unlike control (iv) it can come out large.
    """
    # The matching unit is the Hecke class: within one class every orbit shares (a_2 charpoly, w),
    # and the graph side and the L side are counted against each other class by class. Expand each
    # class into its orbits so that the permutation below runs at orbit granularity. A class that is
    # mixed on BOTH sides at once would not determine which orbit carries which label; none occur in
    # the tested range, and any that did is reported rather than resolved silently.
    orbits: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []
    for g in gross_rows:
        if g["root_number"] != 1:
            continue
        vis, inv = int(g["graph_visible"]), int(g["graph_invisible"])
        nz, z = int(g["L_nonvanishing"]), int(g["L_vanishing"])
        if min(vis, inv) > 0 and min(nz, z) > 0:
            ambiguous.append(dict(g))
        # Hand out the class's L labels concordantly as far as the counts allow: nonvanishing to the
        # visible orbits first, vanishing to the invisible ones first. Any leftover is a discordance
        # the counts force, so this neither invents nor hides one.
        vis_nz, inv_z = min(vis, nz), min(inv, z)
        labels = ([True] * vis_nz + [False] * (vis - vis_nz)
                  + [True] * inv_z + [False] * (inv - inv_z))
        for i, concordant in enumerate(labels):
            visible = i < vis
            orbits.append({"p": int(g["p"]), "visible": visible,
                           "L_vanishing": visible != concordant})

    per_prime: dict[int, dict[str, int]] = {}
    for o in orbits:
        a = per_prime.setdefault(o["p"], {"visible": 0, "invisible": 0, "Lnz": 0, "Lz": 0})
        a["visible" if o["visible"] else "invisible"] += 1
        a["Lz" if o["L_vanishing"] else "Lnz"] += 1

    # Observed concordance, and the exact null distribution of the concordance count.
    dist: dict[int, Fraction] = {0: Fraction(1)}
    observed, fixed, informative_primes = 0, 0, []
    for p, a in sorted(per_prime.items()):
        here = [o for o in orbits if o["p"] == p]
        vis, inv, n = a["visible"], a["invisible"], len(here)
        observed += sum(1 for o in here if o["visible"] != o["L_vanishing"])
        if vis == 0 or inv == 0 or a["Lz"] != inv:
            fixed += n  # constant under the null: nothing left to permute
            continue
        informative_primes.append({"p": p, "visible": vis, "invisible": inv})
        # k vanishing labels land on the inv invisible orbits -> concordance vis - inv + 2k.
        step: dict[int, Fraction] = {}
        for k in range(max(0, inv - vis), inv + 1):
            w = Fraction(math.comb(inv, k) * math.comb(vis, inv - k), math.comb(n, inv))
            c = vis - inv + 2 * k
            for prev, pw in dist.items():
                step[prev + c] = step.get(prev + c, Fraction(0)) + pw * w
        dist = step
    free = sum(d["visible"] + d["invisible"] for d in informative_primes)
    tail = sum(w for c, w in dist.items() if c >= observed - fixed)

    rank2 = [o for o in exc_lvals if "L(f,1)" in o["vanishing_factor"]]
    return {
        "orbits_total": len(orbits),
        "orbits_concordant": observed,
        "classes_ambiguous": ambiguous,
        "orbits_free_under_null": free,
        "orbits_constant_under_null": fixed,
        "informative_primes": informative_primes,
        "within_prime_exact_p_value": float(tail),
        "within_prime_exact_p_value_exact": f"{tail.numerator}/{tail.denominator}",
        "null_mean_concordance": float(fixed + sum(c * w for c, w in dist.items())),
        "agrees_everywhere": observed == len(orbits),
        "analytic_rank_at_least_2_orbits": len(rank2),
        "analytic_rank_at_least_2_detail": rank2,
        "note": ("Frobenius forces nothing here, so this test can fail. The orbits with w = +1 and "
                 "L(f,1) = 0 have even analytic rank >= 2, which the functional equation does not "
                 "force either; they are the sharpest cases in the range."),
    }


# ----------------------------------------------------------------------------- main
def main() -> int:
    t_start = time.time()
    results: dict[str, Any] = {
        "paper": "Paper C edition 2",
        "date": "2026-10-21",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "worker_sha256": hashlib.sha256(WORKER.read_bytes()).hexdigest(),
        "parameters": {"P83": list(P83), "E_MAX": E_MAX, "E_GRAPH": E_GRAPH, "P_VIS_MAX": P_VIS_MAX,
                       "P_VISA_MAX": P_VISA_MAX, "P_LCTRL_MAX": P_LCTRL_MAX, "LVAL_DIMLIM": LVAL_DIMLIM,
                       "N_PERM": N_PERM, "SEED": SEED, "L_ZERO_TOL": L_ZERO_TOL, "FEQ_BITS": FEQ_BITS},
    }
    results["pari"] = worker("version", {})
    print("PARI", results["pari"], flush=True)

    # ---------------- M1: lattice counts
    t0 = time.time()
    tab = TwoSquareTable(4 * 2**E_MAX)
    lattice: dict[str, Any] = {}
    for p in P83:
        r = [r_O0(tab, 2**e, p) for e in range(E_MAX + 1)]
        n_e = primitive_from_r(r)
        dev = [float((Fraction(n_e[e]) - main_term(p, e)) / 1) / 2 ** (e / 2) for e in range(E_MAX + 1)]
        lattice[str(p)] = {"units": r[0], "r_2e": r, "N_e": n_e, "D_e": dev}
    lip3 = [r_lip(tab, 2**e, 3) for e in range(E_MAX + 1)]
    lip313 = [r_lip(tab, 2**e, 313) for e in range(E_MAX + 1)]
    results["lattice_counts"] = lattice
    results["timing_lattice_s"] = round(time.time() - t0, 1)
    print("lattice counts done", results["timing_lattice_s"], flush=True)

    # ---------------- positive control (i): class number one
    exact3 = all(lattice["3"]["N_e"][e] == 18 * 2**e for e in range(1, E_MAX + 1))
    exact7 = all(lattice["7"]["N_e"][e] == 6 * 2**e for e in range(1, E_MAX + 1))
    units_ok = lattice["3"]["units"] == 12 and all(lattice[str(p)]["units"] == 4 for p in P83 if p != 3)
    pos: dict[str, Any] = {"i_class_number_one": {"p3_N_e_eq_18_2e_all_e": exact3, "p7_N_e_eq_6_2e_all_e": exact7,
                                                  "units_12_at_3_and_4_otherwise": units_ok}}

    # ---------------- positive control (ii): qfrep and graph counts
    qf = worker("qfrep", {"primes": list(P83), "nmax": 2**11})
    qf_ok = {str(p): [qf[str(p)][2**e - 1] for e in range(12)] == lattice[str(p)]["r_2e"][:12] for p in P83}
    gc = worker("graph_counts", {"primes": list(P83), "emax": E_GRAPH, "procs": PROCS})
    graph_rows: dict[str, Any] = {}
    for row in gc:
        p = row["p"]
        units = 12 if p == 3 else 4
        r_graph = [units * v for v in row["B2e_00"]]
        graph_rows[str(p)] = {"vertices": row["vertices"], "dim_S2": row["dim_S2"],
                              "vertices_eq_dim_plus_1": row["vertices"] == row["dim_S2"] + 1,
                              "r_2e_graph": r_graph,
                              "graph_eq_lattice_e_le_22": r_graph[: E_MAX + 1] == lattice[str(p)]["r_2e"]}
    pos["ii_qfrep_equals_numpy_e_le_11"] = qf_ok
    pos["ii_graph_equals_lattice_e_le_22"] = {p: v["graph_eq_lattice_e_le_22"] for p, v in graph_rows.items()}
    pos["ii_vertices_eq_dimS2_plus_1"] = {p: v["vertices_eq_dim_plus_1"] for p, v in graph_rows.items()}
    results["graph_counts"] = graph_rows
    print("qfrep/graph controls", all(qf_ok.values()), all(pos["ii_graph_equals_lattice_e_le_22"].values()), flush=True)

    # ---------------- M4 visibility via modular symbols (p < P_VISA_MAX)
    t0 = time.time()
    visA = worker("visA", {"primes": primes_3mod4(3, P_VISA_MAX), "procs": PROCS})
    visA_by_p = {row["p"]: row for row in visA}
    results["timing_visA_s"] = round(time.time() - t0, 1)
    print("visA done", results["timing_visA_s"], flush=True)

    # ---------------- P2: recurrence of N_e vs visible Ihara factors (p in P83)
    recurrence: dict[str, Any] = {}
    for p in P83:
        seq_lat = lattice[str(p)]["N_e"][2:]
        r_g = graph_rows[str(p)]["r_2e_graph"]
        seq_g = primitive_from_r(r_g)[2:]
        c_lat = berlekamp_massey(seq_lat)
        c_g = berlekamp_massey(seq_g)
        char_g = char_poly_from_connection(c_g)
        char_lat = char_poly_from_connection(c_lat)
        vis_cps = sorted({o["a2_charpoly"] for o in visA_by_p[p]["orbits"] if o["visible"]})
        invis = [o for o in visA_by_p[p]["orbits"] if not o["visible"]]
        pred = sp.expand((X - 2) * sp.prod([ihara_factor(cp) for cp in vis_cps])) if vis_cps else X - 2
        rts = roots_of(char_g)
        nontriv = [z for z in rts if abs(z - 2) > 1e-12]
        mod2 = [abs(z) ** 2 for z in nontriv]
        inv_roots = []
        for o in invis:
            for a in real_roots(o["a2_charpoly"]):
                disc = complex(a * a - 8)
                s = disc ** 0.5
                inv_roots.append({"a2": a, "root_number": o["root_number"],
                                  "roots": [[((a + s) / 2).real, ((a + s) / 2).imag], [((a - s) / 2).real, ((a - s) / 2).imag]]})
        recurrence[str(p)] = {
            "L_lattice": len(c_lat) - 1, "terms_lattice": len(seq_lat),
            "determined_by_lattice": 2 * (len(c_lat) - 1) + 2 <= len(seq_lat),
            "L_graph": len(c_g) - 1, "terms_graph": len(seq_g),
            "determined_by_graph": 2 * (len(c_g) - 1) + 2 <= len(seq_g),
            "lattice_poly_equals_graph_poly": bool(sp.expand(char_lat - char_g) == 0),
            "char_poly": str(sp.factor(char_g)),
            "predicted": str(sp.factor(pred)),
            "char_equals_predicted": bool(sp.expand(char_g - pred) == 0),
            "visible_a2_charpolys": vis_cps,
            "roots": [[z.real, z.imag] for z in rts],
            "max_abs_modsq_minus_2": max((abs(v - 2) for v in mod2), default=0.0),
            "invisible_orbit_roots": inv_roots,
        }
    results["recurrence"] = recurrence
    print("recurrence:", {p: (v["determined_by_graph"], v["char_equals_predicted"]) for p, v in recurrence.items()}, flush=True)

    # positive control (iii): p = 11
    rec11 = recurrence["11"]
    pos["iii_p11_ihara_factor_x2_2x_2"] = "x**2 + 2*x + 2" in rec11["char_poly"]

    # ---------------- M3 visibility on the isogeny graph (p < P_VIS_MAX)
    t0 = time.time()
    visB = worker("visB", {"primes": primes_3mod4(3, P_VIS_MAX), "procs": PROCS})
    results["timing_visB_s"] = round(time.time() - t0, 1)
    print("visB done", results["timing_visB_s"], flush=True)
    vis_rows, orbit_w, orbit_vis, orbit_p = [], [], [], []
    ram_viol, eis_ok, exceptional = [], True, []
    gap_rows = []
    for row in visB:
        p = row["p"]
        eis = [o for o in row["orbits"] if o["a2_charpoly"] == "x - 3"]
        if len(eis) != 1 or not eis[0]["visible"] or eis[0]["frobenius_sign"] != 1:
            eis_ok = False
        cusp = [o for o in row["orbits"] if o["a2_charpoly"] != "x - 3"]
        lam_glob = max((o["max_abs_eigenvalue"] for o in cusp), default=None)
        lam_vis = max((o["max_abs_eigenvalue"] for o in cusp if o["visible"]), default=None)
        if cusp:
            gap_rows.append({"p": p, "lambda_global": lam_glob, "lambda_visible": lam_vis})
        for o in cusp:
            orbit_w.append(o["frobenius_sign"])
            orbit_vis.append(o["visible"])
            orbit_p.append(p)
            if o["max_abs_eigenvalue"] > 2 * math.sqrt(2) + 1e-12 or o["max_abs_imag_part"] > 1e-20:
                ram_viol.append({"p": p, **o})
            if o["frobenius_sign"] == 1 and not o["visible"]:
                exceptional.append({"p": p, "a2_charpoly": o["a2_charpoly"], "dim": o["dim"]})
        vis_rows.append({"p": p, "vertices": row["vertices"], "dim_S2": row["dim_S2"],
                         "extra_hecke_ops": row["extra_hecke_ops"], "orbits": row["orbits"]})
    w_arr, v_arr = np.array(orbit_w), np.array(orbit_vis)
    viol = int(np.sum((w_arr == -1) & v_arr))
    summary = {
        "primes": len(visB), "cusp_orbits": int(len(w_arr)),
        "w_plus_visible": int(np.sum((w_arr == 1) & v_arr)), "w_plus_invisible": int(np.sum((w_arr == 1) & ~v_arr)),
        "w_minus_visible": viol, "w_minus_invisible": int(np.sum((w_arr == -1) & ~v_arr)),
        "sign_not_pm1": int(np.sum(np.abs(w_arr) != 1)),
        "eisenstein_unique_visible": eis_ok, "ramanujan_violations": ram_viol,
        "max_abs_a2_over_all_cusp_orbits": max(o["max_abs_eigenvalue"] for r_ in visB for o in r_["orbits"]
                                               if o["a2_charpoly"] != "x - 3"),
        "exceptional_w_plus_invisible": exceptional,
        "primes_with_lambda_visible_lt_lambda_global": [g["p"] for g in gap_rows if g["lambda_visible"] is not None
                                                        and g["lambda_visible"] < g["lambda_global"] - 1e-9],
    }
    results["visibility_graph"] = {"summary": summary, "rows": vis_rows, "spectral_gap_at_E0": gap_rows}
    print("visibility summary", {k: v for k, v in summary.items() if k not in ("exceptional_w_plus_invisible",
                                                                             "primes_with_lambda_visible_lt_lambda_global")}, flush=True)

    # cross-check M3 vs M4
    cross = {}
    for row in visB:
        p = row["p"]
        if p not in visA_by_p:
            continue
        a = sorted((o["a2_charpoly"], o["dim"], o["root_number"], o["visible"]) for o in visA_by_p[p]["orbits"])
        b = sorted((o["a2_charpoly"], o["dim"], o["frobenius_sign"], o["visible"]) for o in row["orbits"]
                   if o["a2_charpoly"] != "x - 3")
        cross[str(p)] = a == b
    pos["ii_graph_visibility_equals_modular_symbol_theta_projection"] = cross
    print("cross-check M3=M4:", all(cross.values()), len(cross), flush=True)

    # ---------------- negative control (iv): permutation test
    rng = random.Random(SEED)
    w_list = list(orbit_w)
    perm_global, perm_within = [], []
    by_p: dict[int, list[int]] = {}
    for i, p in enumerate(orbit_p):
        by_p.setdefault(p, []).append(i)
    for _ in range(N_PERM):
        sh = w_list[:]
        rng.shuffle(sh)
        perm_global.append(sum(1 for i in range(len(sh)) if sh[i] == -1 and orbit_vis[i]))
        sw = w_list[:]
        for idx in by_p.values():
            vals = [w_list[i] for i in idx]
            rng.shuffle(vals)
            for i, v in zip(idx, vals):
                sw[i] = v
        perm_within.append(sum(1 for i in range(len(sw)) if sw[i] == -1 and orbit_vis[i]))
    neg: dict[str, Any] = {"iv_permutation_test": {
        "statistic": "#orbits with root number -1 and visible", "observed": viol,
        "global_shuffle_mean": float(np.mean(perm_global)), "global_shuffle_min": int(min(perm_global)),
        "global_p_value": (1 + sum(1 for v in perm_global if v <= viol)) / (1 + N_PERM),
        "within_prime_shuffle_mean": float(np.mean(perm_within)), "within_prime_shuffle_min": int(min(perm_within)),
        "within_prime_p_value": (1 + sum(1 for v in perm_within if v <= viol)) / (1 + N_PERM),
        "informative": False,
        "withdrawn_because": (
            "The observed statistic is forced to 0 and cannot take any other value, so the small "
            "p-value measures nothing. Our base point E_0 has j = 1728 in F_p, so Frobenius fixes "
            "e_{E_0}; F commutes with the Brandt matrices and acts by w on the f-component, whence "
            "pi_f e_{E_0} = w pi_f e_{E_0}, which gives pi_f e_{E_0} = 0 whenever w = -1, at every "
            "prime. Independently, w = -1 forces an odd functional equation, so L(f,1) = 0 and Gross "
            "predicts invisibility from any base point. This entry is retained as a descriptive "
            "record and is excluded from controls_ok; the informative test is "
            "positive_controls.vii_gross_w_plus_stratum, where visibility is not forced.")}}

    # ---------------- M5 L-values (Gross)
    exc_primes = sorted({e["p"] for e in exceptional})
    l_primes = sorted(set(q for q in primes_3mod4(11, P_LCTRL_MAX)) | set(exc_primes))
    t0 = time.time()
    lv = worker("lvals", {"primes": l_primes, "dimlim": LVAL_DIMLIM, "procs": PROCS}, timeout=6 * 3600)
    results["timing_lvals_s"] = round(time.time() - t0, 1)
    print("lvals done", results["timing_lvals_s"], flush=True)
    vis_by_p = {row["p"]: row for row in visB}
    gross_rows, gross_fail, feq_bad = [], [], []
    exc_lvals = []
    for row in lv:
        p = row["p"]
        classes: dict[tuple[str, int], dict[str, int]] = {}
        for o in row["orbits"]:
            key = (o["a2_charpoly"], o["root_number"])
            cl = classes.setdefault(key, {"L_nonvanishing": 0, "L_vanishing": 0, "graph_visible": 0, "graph_invisible": 0})
            embs = o["embeddings"]
            for e in embs:
                if e["feq_L"] > FEQ_BITS or e["feq_Ltwist"] > FEQ_BITS:
                    feq_bad.append({"p": p, **o})
            nz = [abs(e["L_f_1"]) > L_ZERO_TOL and abs(e["L_ftwist_1"]) > L_ZERO_TOL for e in embs]
            if all(nz):
                cl["L_nonvanishing"] += 1
            elif not any(nz):
                cl["L_vanishing"] += 1
            else:
                gross_fail.append({"p": p, "reason": "vanishing differs between embeddings", **o})
            if o["root_number"] == 1:
                which = ["L(f,1)" if abs(e["L_f_1"]) <= L_ZERO_TOL else ("L(f x chi_-4,1)" if abs(e["L_ftwist_1"]) <= L_ZERO_TOL else "none")
                         for e in embs]
                exc_lvals.append({"p": p, "a2_charpoly": o["a2_charpoly"], "dim": o["dim"],
                                  "min_abs_L_f_1": min(abs(e["L_f_1"]) for e in embs),
                                  "min_abs_L_twist_1": min(abs(e["L_ftwist_1"]) for e in embs),
                                  "max_abs_L_f_1": max(abs(e["L_f_1"]) for e in embs),
                                  "max_abs_L_twist_1": max(abs(e["L_ftwist_1"]) for e in embs),
                                  "vanishing_factor": which})
        for o in vis_by_p[p]["orbits"]:
            if o["a2_charpoly"] == "x - 3" or o["dim"] > LVAL_DIMLIM:
                continue
            key = (o["a2_charpoly"], o["frobenius_sign"])
            cl = classes.setdefault(key, {"L_nonvanishing": 0, "L_vanishing": 0, "graph_visible": 0, "graph_invisible": 0})
            cl["graph_visible" if o["visible"] else "graph_invisible"] += 1
        for key, cl in classes.items():
            agree = cl["L_nonvanishing"] == cl["graph_visible"] and cl["L_vanishing"] == cl["graph_invisible"]
            gross_rows.append({"p": p, "a2_charpoly": key[0], "root_number": key[1], **cl, "agree": agree})
            if not agree:
                gross_fail.append({"p": p, "a2_charpoly": key[0], "root_number": key[1], **cl})
    results["gross_lvalues"] = {"primes": l_primes, "classes": gross_rows, "failures": gross_fail,
                                "feq_check_failures": feq_bad, "w_plus_orbits": exc_lvals,
                                "n_coefficients": {str(r_["p"]): r_["n_coefficients"] for r_ in lv},
                                "seconds": {str(r_["p"]): r_["seconds"] for r_ in lv}}
    l11 = [o for r_ in lv if r_["p"] == 11 for o in r_["orbits"]]
    pos["iii_L_11a_1"] = l11[0]["embeddings"][0]["L_f_1"] if l11 else None
    l139 = [o for r_ in lv if r_["p"] == 139 for o in r_["orbits"] if o["a2_charpoly"] == "x - 1"]
    pos["iv_p139_x_minus_1"] = l139[0]["embeddings"][0] if l139 else None
    vis_w1 = [g for g in gross_rows if g["root_number"] == 1 and g["graph_visible"] > 0]
    pos["vi_visible_w_plus_classes_all_nonvanishing"] = all(g["L_nonvanishing"] >= g["graph_visible"] for g in vis_w1)
    pos["vi_visible_w_plus_classes_tested"] = len(vis_w1)
    pos["vii_gross_w_plus_stratum"] = w_plus_stratum_test(gross_rows, exc_lvals)

    # ---------------- Frey side
    frey = worker("frey", {"pairs": [[15, 16], [3, 6]]})
    family = worker("family", {"primes": list(FAMILY_PRIMES)})
    results["frey"] = frey
    results["frey_family_3p_4p"] = family
    pos["v_frey_15_16_31"] = {"conductor": frey[0]["conductor"], "disc_min": frey[0]["disc_min"],
                              "ok": frey[0]["conductor"] == 465 and frey[0]["disc_min"] == 216225}
    neg["v_noncoprime_3_6_9"] = {"conductor": frey[1]["conductor"], "c4_min": frey[1]["c4_min"],
                                 "not_semistable": any(v["f"] >= 2 for v in frey[1]["local_reduction"].values())}

    # ---------------- quaternion data, Gram index
    results["quaternion_ramification"] = worker("quat", {"primes": [3, 7, 311, 313, 331]})
    results["gram_index"] = worker("gram", {"primes": [3, 7, 11, 311, 331]})

    # ---------------- negative controls (i), (ii)
    n_lip3 = primitive_from_r(lip3)
    neg["i_lipschitz_p3"] = {"N_e_e1_to_6": n_lip3[1:7], "required_by_law": [18 * 2**e for e in range(1, 7)],
                             "fails_law": any(n_lip3[e] != 18 * 2**e for e in range(1, E_MAX + 1))}
    n313 = primitive_from_r(lip313)
    ratio313 = [float(Fraction(n313[e]) / main_term(313, e)) for e in range(E_MAX + 1)]
    neg["ii_minus1_minus313_lipschitz"] = {"N_e": n313, "ratio_to_36_2e_over_312": ratio313,
                                           "ramified_places": results["quaternion_ramification"][3]["ramified_places"],
                                           "ratio_at_e22": ratio313[-1]}

    # ---------------- sigma, scalar 256, primitive witnesses, Rust probe
    sigma = o0_coords(256, 0, 256, 0)
    scal = o0_coords(512, 0, 0, 0)
    assert sigma is not None and scal is not None
    wit = primitive_witnesses(3, 16)
    lip = wit["smallest_primitive_lipschitz_abcd"]
    probe = rust_probe([("edition1_sigma_128+128j", 128, 0, 128, 0), ("scalar_256", 256, 0, 0, 0),
                        ("128+128k", 128, 0, 0, 128), ("primitive_" + "_".join(map(str, lip)), *lip),
                        ("wrong_norm", 255, 1, 1, 0)])
    neg["iii_sigma_and_scalar"] = {
        "sigma_O0_coords": list(sigma), "sigma_primitive": is_primitive(sigma), "sigma_norm": o0_norm(0, sigma),
        "scalar256_O0_coords": list(scal), "scalar256_primitive": is_primitive(scal),
        "rust_probe": probe,
        "rust_accepts_nonprimitive": probe.get("status") == "RAN"
        and all(r_["verified"] for r_ in probe["rows"] if r_["label"] in ("edition1_sigma_128+128j", "scalar_256")),
    }
    wit["primitive_count_N16_from_lattice"] = lattice["3"]["N_e"][16]
    results["primitive_witness_p3_e16"] = wit

    results["positive_controls"] = pos
    results["negative_controls"] = neg

    # ---------------- falsification
    d_growth = {}
    for p in P83:
        de = lattice[str(p)]["D_e"]
        early = max(abs(v) for v in de[2:12])
        late = max(abs(v) for v in de[12:23])
        d_growth[str(p)] = {"max_early": early, "max_late": late, "grows": early > 0 and late > 2 * early}
    fals = {
        "a_class_number_one_fails": not (exact3 and exact7),
        "b_root_off_circle": any(v["max_abs_modsq_minus_2"] > 1e-15 for v in recurrence.values()),
        "b_ramanujan_violation_on_graph": bool(ram_viol),
        "b_recurrence_differs_from_prediction": [p for p, v in recurrence.items()
                                                 if v["determined_by_graph"] and not v["char_equals_predicted"]],
        "c_w_minus_visible_WITHDRAWN": {
            "value": viol,
            "withdrawn_because": ("forced to 0 by Frobenius at j = 1728 and, independently, by the odd "
                                  "functional equation; it is not a falsification criterion and does "
                                  "not enter `refuted`. See negative_controls.iv_permutation_test."),
        },
        "c_w_plus_discordant": (pos["vii_gross_w_plus_stratum"]["orbits_total"]
                                - pos["vii_gross_w_plus_stratum"]["orbits_concordant"]),
        "d_invisible_w_plus_with_both_L_nonzero": [g for g in gross_rows if g["root_number"] == 1
                                                   and g["graph_invisible"] > g["L_vanishing"]],
        "e_deviation_grows": [p for p, v in d_growth.items() if v["grows"]],
        "D_e_growth_table": d_growth,
    }
    refuted = (fals["a_class_number_one_fails"] or fals["b_root_off_circle"] or fals["b_ramanujan_violation_on_graph"]
               or bool(fals["b_recurrence_differs_from_prediction"]) or fals["c_w_plus_discordant"] > 0
               or bool(fals["d_invisible_w_plus_with_both_L_nonzero"]) or bool(fals["e_deviation_grows"]))
    controls_ok = (exact3 and exact7 and units_ok and all(qf_ok.values())
                   and all(pos["ii_graph_equals_lattice_e_le_22"].values()) and all(cross.values())
                   and pos["iii_p11_ihara_factor_x2_2x_2"] and pos["v_frey_15_16_31"]["ok"]
                   and neg["i_lipschitz_p3"]["fails_law"] and neg["v_noncoprime_3_6_9"]["not_semistable"]
                   and not is_primitive(sigma)
                   and pos["vii_gross_w_plus_stratum"]["within_prime_exact_p_value"] < 1e-3)
    fals["controls_passed"] = controls_ok
    fals["verdict"] = ("NOT REPORTED: a control failed" if not controls_ok else
                       ("REFUTED" if refuted else "SURVIVED (P1-P3 not falsified on the tested range)"))
    results["falsification"] = fals
    results["edition1_claims"] = {
        "sigma_128_128j_non_backtracking": "FALSE (sigma in 2 O_0; Lean paper_sigma_in_two_O0)",
        "rust_function_is_sqisign_verifier": "FALSE (accepts scalar 256; only checks a norm)",
        "ribet_strips_to_level_2_for_3p_4p": "FALSE (7 survives for p != 7; Lean seven_survives_serre_level)",
    }
    results["timing_total_s"] = round(time.time() - t_start, 1)
    OUT.write_text(json.dumps(results, indent=1))
    print("verdict:", fals["verdict"], "| total", results["timing_total_s"], "s ->", OUT, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
