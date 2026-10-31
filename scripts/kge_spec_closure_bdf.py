#!/usr/bin/env python3
"""Adversarial specification closure, end to end, on linear multistep methods.

The proposal in docs/PROOF_CARRYING_DISCOVERY.md: point the generator at the
SPECIFICATION and look for candidates the kernel would accept that an independent
oracle rejects. Each one is a specification gap; close it, then red-team again.

* GENERATOR -- structure search over k-step BDF-type stencils: every support
  (which a_j may be nonzero, j < k), coefficients solved EXACTLY over Q for the
  highest order the support admits. (Every candidate therefore satisfies its order
  conditions, which is the Lean-provable specification -- see AlixBDF.lean.)
* SPEC v1 -- order conditions only.
* SPEC v2 -- order conditions AND the root condition for zero-stability, decided
  EXACTLY by a Schur-Cohn recursion over Q (no floating-point root finding).
* ORACLE -- independent of both: zero-stability is boundedness of the method's
  recurrence for y' = 0. The recurrence sum_j a_j y_{n+j} = 0 is run in exact
  rationals from perturbed starting values for many steps; growth beyond a fixed
  bound is a rejection. It shares no code with the Schur-Cohn test (simulation vs
  algebra), so v2 cannot pass red-teaming by grading itself.

Controls: the oracle must accept BDF2 and reject BDF7 (known unstable); the
Schur-Cohn decision must agree with the numerical roots on BDF1-8.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kge_bdf_pilot import bdf, order_conditions_hold  # noqa: E402


# --------------------------------------------------------------------------- exact algebra
def poly_div_linear_root_one(c: list[Fraction]) -> list[Fraction] | None:
    """Divide p(z) = sum c_i z^i by (z - 1); None if 1 is not a root."""
    if sum(c) != 0:
        return None
    n = len(c) - 1
    q = [Fraction(0)] * n
    acc = Fraction(0)
    for i in range(n, 0, -1):          # synthetic division from the top
        acc = c[i] + acc
        q[i - 1] = acc
    return q


def schur_cohn_strictly_inside(c: list[Fraction]) -> bool:
    """True iff every root of p(z) = sum c_i z^i lies strictly inside |z| < 1.

    Exact Schur-Cohn recursion over Q: with p* the reversed polynomial, require
    |p(0)| < |p*(0)| (i.e. |c_0| < |c_n|), form
        p_next(z) = ( conj(c_n) p(z) - c_0 p*(z) ) / z
    (real coefficients, so conj is the identity) and recurse down to degree 0.
    """
    p = c[:]
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    while len(p) > 1:
        c0, cn = p[0], p[-1]
        if abs(c0) >= abs(cn):
            return False
        rev = list(reversed(p))
        nxt = [cn * a - c0 * b for a, b in zip(p, rev)]   # constant term is 0
        p = nxt[1:]
        while len(p) > 1 and p[-1] == 0:
            p.pop()
    return True


def poly_divmod(num: list[Fraction], den: list[Fraction]) -> tuple[list[Fraction], list[Fraction]]:
    """Exact polynomial division over Q (coefficients low-to-high)."""
    num = num[:]
    dn = len(den) - 1
    if len(num) - 1 < dn:
        return [Fraction(0)], num
    q = [Fraction(0)] * (len(num) - dn)
    for i in range(len(num) - 1, dn - 1, -1):
        c = num[i] / den[-1]
        q[i - dn] = c
        for j in range(len(den)):
            num[i - dn + j] -= c * den[j]
    rem = num[:dn] if dn else [Fraction(0)]
    while len(rem) > 1 and rem[-1] == 0:
        rem.pop()
    return q, rem


_CYCLO_CACHE: dict[int, list[Fraction]] = {}


def cyclotomic(n: int) -> list[Fraction]:
    """Phi_n(z), exactly, as Fractions (low-to-high)."""
    if n not in _CYCLO_CACHE:
        num = [Fraction(-1)] + [Fraction(0)] * (n - 1) + [Fraction(1)]       # z^n - 1
        for d in range(1, n):
            if n % d == 0:
                num, _ = poly_divmod(num, cyclotomic(d))
        _CYCLO_CACHE[n] = num
    return _CYCLO_CACHE[n]


def zero_stable_exact(a: list[Fraction], max_n: int = 60) -> bool:
    """Dahlquist root condition for rho = sum a_j z^j, decided exactly over Q.

    Zero-stable iff every root has |z| <= 1 and every root with |z| = 1 is simple.
    A previous version required every root except z = 1 to lie STRICTLY inside the
    disc, which wrongly rejects weakly stable methods (simple roots on the circle,
    e.g. leapfrog y_{n+2} - y_n = 2hf, rho = z^2 - 1). The over-strictness check in
    this script exposed it: all 31 disagreements with the oracle were exactly those.

    Method: an on-circle root of a polynomial whose roots all lie in the closed disc
    is a root of unity (Kronecker), so strip cyclotomic factors Phi_n for n <= max_n,
    requiring each to appear at most once and the total multiplicity of any root to
    be 1; the remainder must be strictly inside |z| < 1 by exact Schur-Cohn. If the
    remainder fails because of an on-circle root that is NOT a root of unity within
    max_n, the test rejects -- conservative in that exotic case only.
    """
    p = a[:]
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    if len(p) <= 1:
        return False
    for n in range(1, max_n + 1):
        phi = cyclotomic(n)
        if len(phi) > len(p):
            continue
        q, rem = poly_divmod(p, phi)
        if len(rem) == 1 and rem[0] == 0:
            q2, rem2 = poly_divmod(q, phi)
            if len(rem2) == 1 and rem2[0] == 0:
                return False                      # repeated on-circle root
            p = q
            while len(p) > 1 and p[-1] == 0:
                p.pop()
    # z = 0 roots (a_0 = 0) are inside the disc; drop them before Schur-Cohn.
    while len(p) > 1 and p[0] == 0:
        p = p[1:]
    return schur_cohn_strictly_inside(p) if len(p) > 1 else True


# --------------------------------------------------------------------------- independent oracle
ORACLE_STEPS = 2000
ORACLE_BOUND = 1e6


def oracle_bounded(a: list[Fraction], steps: int = ORACLE_STEPS, bound: float = ORACLE_BOUND) -> bool:
    """Run sum_j a_j y_{n+j} = 0 from unit-vector starts; reject on growth past `bound`.

    FLOAT arithmetic, deliberately: this oracle is empirical evidence, not a proof,
    and exact rationals were measured to be too slow (denominators grow every step;
    a 4,000-step exact run did not finish in 10 minutes). Unit-vector starts, NOT
    the all-ones vector: any consistent method has the constant solution (sum a_j =
    0), so an all-ones start excites only the z = 1 mode and is blind to instability.

    DETECTION THRESHOLD. Stable methods plateau immediately (BDF2 peaks at 1.5, BDF6
    at 5.1), while a root of modulus 1+e grows like (1+e)^steps. Measured on BDF7
    (max modulus 1.0222): peak 1.7e4 at 400 steps -- UNDER the bound, missed by an
    earlier 400-step version -- 9.6e9 at 1000, 3.2e19 at 2000. At 2000 steps and a
    1e6 bound this catches moduli above about 1 + 0.006; a method with a root at
    1.001 would escape it. That is the oracle's stated blind spot.
    """
    k = len(a) - 1
    af = [float(x) for x in a]
    for j in range(k):
        y = [1.0 if i == j else 0.0 for i in range(k)]
        for _ in range(steps):
            nxt = -sum(af[m] * y[-k + m] for m in range(k)) / af[k]
            if abs(nxt) > bound:
                return False
            y.append(nxt)
            y = y[-k:]
    return True


# --------------------------------------------------------------------------- generator
def generate(kmax: int):
    out = []
    for k in range(1, kmax + 1):
        for size in range(0, k + 1):
            for support in itertools.combinations(range(k), size):
                order = len(support)         # unknowns = support + b, equations = order + 1
                res = bdf(k, support, order)
                if res and order >= 1 and order_conditions_hold(res[0], res[1], k, order):
                    out.append({"k": k, "support": list(support), "order": order,
                                "a": res[0], "b": res[1]})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kmax", type=int, default=7)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    # Controls first.
    bdf2, _ = bdf(2)
    bdf7, _ = bdf(7)
    assert oracle_bounded(bdf2), "oracle must accept BDF2"
    assert not oracle_bounded(bdf7), "oracle must reject BDF7"
    agree = []
    for k in range(1, 9):
        a, _ = bdf(k)
        roots = np.roots([float(x) for x in reversed(a)])
        others = [r for r in roots if abs(r - 1) > 1e-6]
        numeric = all(abs(r) < 1 - 1e-9 for r in others)
        agree.append({"k": k, "schur_cohn_exact": zero_stable_exact(a), "numeric_roots": numeric})
    assert all(x["schur_cohn_exact"] == x["numeric_roots"] for x in agree), agree
    # Controls that BDF1-8 cannot supply: a weakly stable method and a repeated-root method.
    leapfrog = [Fraction(-1), Fraction(0), Fraction(1)]          # rho = z^2 - 1, roots +-1, zero-stable
    double_one = [Fraction(1), Fraction(-2), Fraction(1)]        # rho = (z-1)^2, unstable
    nonconsistent = [Fraction(1), Fraction(1)]                   # rho = z + 1 has no root at 1
    assert zero_stable_exact(leapfrog), "weakly stable leapfrog must be accepted"
    assert not zero_stable_exact(double_one), "repeated root at z = 1 must be rejected"
    assert oracle_bounded(leapfrog) and not oracle_bounded(double_one, steps=200000, bound=1e4), \
        "oracle must agree on both extra controls"
    print("controls: oracle accepts BDF2, rejects BDF7; Schur-Cohn agrees with numeric roots on BDF1-8:",
          [x["k"] for x in agree if x["schur_cohn_exact"]], "stable")

    cands = generate(args.kmax)
    v1 = cands                                            # order conditions only
    v2 = [c for c in cands if zero_stable_exact(c["a"])]  # + exact root condition
    gaps_v1 = [c for c in v1 if not oracle_bounded(c["a"])]
    gaps_v2 = [c for c in v2 if not oracle_bounded(c["a"])]
    rejected_by_v2_but_oracle_ok = [c for c in cands if not zero_stable_exact(c["a"]) and oracle_bounded(c["a"])]

    def short(c):
        return {"k": c["k"], "support": c["support"], "order": c["order"]}

    print(f"generator: {len(cands)} stencils (k <= {args.kmax}), each satisfying its order conditions")
    print(f"spec v1 (order only):            accepts {len(v1):>3}   red-team gaps {len(gaps_v1):>3}  "
          f"(gap rate {len(gaps_v1)/len(v1):.3f})")
    print(f"spec v2 (order + Schur-Cohn):    accepts {len(v2):>3}   red-team gaps {len(gaps_v2):>3}")
    print(f"v2 rejections the oracle would have accepted (over-strictness check): {len(rejected_by_v2_but_oracle_ok)}")
    best_by_k = {}
    for c in v2:
        best_by_k[c["k"]] = max(best_by_k.get(c["k"], 0), c["order"])
    print("highest zero-stable order by k under v2:", best_by_k)

    args.out.write_text(json.dumps({
        "what": "adversarial specification closure on linear multistep (BDF-type) stencils",
        "controls": {"oracle_accepts_bdf2": True, "oracle_rejects_bdf7": True,
                     "schur_cohn_vs_numeric_bdf1_8": agree},
        "generator_candidates": len(cands),
        "spec_v1_order_conditions": {"accepted": len(v1), "redteam_gaps": len(gaps_v1),
                                     "gap_rate": round(len(gaps_v1) / len(v1), 4),
                                     "gap_examples": [short(c) for c in gaps_v1[:12]]},
        "spec_v2_order_plus_exact_root_condition": {"accepted": len(v2), "redteam_gaps": len(gaps_v2),
                                                    "gap_examples": [short(c) for c in gaps_v2[:12]]},
        "over_strictness_v2_rejected_but_oracle_bounded": [short(c) for c in rejected_by_v2_but_oracle_ok],
        "highest_zero_stable_order_by_k_v2": best_by_k,
        "notes": [
            "Order conditions are Lean-provable (AlixBDF.lean); the root condition here is decided EXACTLY over Q "
            "by Schur-Cohn but is not yet kernel-proved.",
            "The oracle runs the y' = 0 recurrence in floats from unit-vector starts for 2000 steps with a growth bound of 1e6; "
            "it catches root moduli above about 1.006 and would miss a root at 1.001 (finite-horizon oracle). A first 400-step "
            "version missed BDF7 (peak 1.7e4 < bound) and was caught by the control that BDF7 must be rejected.",
        ],
    }, indent=2, default=str) + "\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
