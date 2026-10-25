#!/usr/bin/env python3
"""Pilot: certified synthesis of BDF integrator coefficients (rusty-SUNDIALS domain).

The k-step BDF method  sum_{j=0..k} a_j y_{n+j} = h b y'_{n+k}  (a_k = 1) has order k
exactly when  sum_j a_j j^q = q b k^(q-1)  for q = 0..k. These conditions are LINEAR
in the unknowns (a_0..a_{k-1}, b), so the exact lifetime-learning step does not
assist a search here -- it replaces it: fix the structure (the stencil), solve the
coefficients exactly over Q, and hand the result to the Lean kernel.

Three outputs per k:
* the exact coefficients, cross-checked against the textbook values for k = 2, 3;
* a Lean theorem file proving each order condition by norm_num, plus a NEGATIVE
  control (BDF2 with one coefficient perturbed must violate a condition);
* zero-stability of the characteristic polynomial rho, computed NUMERICALLY (labelled
  as such): the kernel proves only what was specified, and order conditions do not
  specify stability -- BDF7 and above satisfy every order condition and are useless.

Then a structure search: over all supports (which a_j may be nonzero) for a
given step count, exact linear algebra decides which supports admit a method of the
requested order at all -- the "search structure, solve coefficients" pattern.
"""

from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]


def solve_exact(rows: list[list[Fraction]], rhs: list[Fraction]) -> list[Fraction] | None:
    """Gaussian elimination over Q; None if singular or inconsistent."""
    n, m = len(rows), len(rows[0])
    a = [r[:] + [b] for r, b in zip(rows, rhs)]
    piv = []
    r = 0
    for c in range(m):
        p = next((i for i in range(r, n) if a[i][c] != 0), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        inv = 1 / a[r][c]
        a[r] = [x * inv for x in a[r]]
        for i in range(n):
            if i != r and a[i][c] != 0:
                f = a[i][c]
                a[i] = [x - f * y for x, y in zip(a[i], a[r])]
        piv.append(c)
        r += 1
    if len(piv) < m:
        return None
    if any(all(x == 0 for x in a[i][:m]) and a[i][m] != 0 for i in range(n)):
        return None
    sol = [Fraction(0)] * m
    for i, c in enumerate(piv):
        sol[c] = a[i][m]
    return sol


def bdf(k: int, support: tuple[int, ...] | None = None, order: int | None = None):
    """Coefficients (a_0..a_k, b) of a k-step BDF-type method of the given order.

    `support` lists the indices j < k whose a_j may be nonzero (default: all).
    Unknowns are those a_j and b; a_k = 1. Returns None if no such method exists.
    """
    order = k if order is None else order
    support = tuple(range(k)) if support is None else support
    unknowns = list(support) + ["b"]
    rows, rhs = [], []
    for q in range(order + 1):
        row = []
        for u in unknowns:
            if u == "b":
                row.append(Fraction(-q * k ** (q - 1)) if q > 0 else Fraction(0))
            else:
                row.append(Fraction(u) ** q if not (u == 0 and q == 0) else Fraction(1))
        rows.append(row)
        rhs.append(-(Fraction(k) ** q))
    if len(unknowns) > len(rows):
        return None
    sol = solve_exact(rows, rhs)
    if sol is None:
        return None
    a = [Fraction(0)] * (k + 1)
    for u, v in zip(support, sol[:-1]):
        a[u] = v
    a[k] = Fraction(1)
    return a, sol[-1]


def order_conditions_hold(a: list[Fraction], b: Fraction, k: int, order: int) -> bool:
    return all(
        sum(a[j] * (Fraction(j) ** q if not (j == 0 and q == 0) else 1) for j in range(k + 1))
        == (q * b * Fraction(k) ** (q - 1) if q > 0 else 0)
        for q in range(order + 1)
    )


def zero_stable(a: list[Fraction]) -> tuple[bool, float]:
    """Root condition for rho(z) = sum a_j z^j, NUMERICALLY (numpy roots)."""
    roots = np.roots([float(x) for x in reversed(a)])
    mags = np.abs(roots)
    inside = all(m < 1 - 1e-9 or abs(m - 1) < 1e-9 for m in mags)
    on_circle = [r for r, m in zip(roots, mags) if abs(m - 1) < 1e-9]
    simple = len(on_circle) == len({complex(round(r.real, 6), round(r.imag, 6)) for r in on_circle})
    return bool(inside and simple), float(max(mags))


def lean_rat(x: Fraction) -> str:
    return f"({x.numerator} : ℚ)" if x.denominator == 1 else f"(({x.numerator} : ℚ) / {x.denominator})"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kmax", type=int, default=8)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--lean", type=Path, required=True)
    args = ap.parse_args()

    textbook = {2: ([Fraction(1, 3), Fraction(-4, 3), Fraction(1)], Fraction(2, 3)),
                3: ([Fraction(-2, 11), Fraction(9, 11), Fraction(-18, 11), Fraction(1)], Fraction(6, 11))}
    rows, lean = [], ["import Mathlib.Tactic.NormNum", "",
                      "/-! BDF order conditions, generated by scripts/kge_bdf_pilot.py from exact solves.",
                      "Each theorem proves that the solved coefficients satisfy the order-k conditions",
                      "sum_j a_j j^q = q b k^(q-1), q = 0..k. Zero-stability is NOT proved here. -/", "",
                      "namespace ANSE.Alix.BDF", ""]
    names = []
    for k in range(1, args.kmax + 1):
        a, b = bdf(k)
        ok = order_conditions_hold(a, b, k, k)
        stable, rmax = zero_stable(a)
        tb = textbook.get(k)
        matches = (tb is None) or (a == tb[0] and b == tb[1])
        rows.append({"k": k, "a": [str(x) for x in a], "b": str(b), "order_conditions_exact": ok,
                     "matches_textbook": matches if tb else None,
                     "zero_stable_numeric": stable, "max_root_modulus_numeric": round(rmax, 6)})
        print(f"  BDF{k}: b={str(b):<10} order-{k} exact={ok}  textbook={'yes' if tb and matches else ('-' if not tb else 'NO')}  "
              f"zero-stable(numeric)={stable}  max|root|={rmax:.4f}")
        conj = " ∧\n    ".join(
            f"({' + '.join(f'{lean_rat(a[j])} * {j}^{q}' for j in range(k + 1))}) = "
            f"({q} * {lean_rat(b)} * {k}^{q - 1})" if q > 0 else
            f"({' + '.join(lean_rat(a[j]) for j in range(k + 1))}) = 0"
            for q in range(k + 1))
        name = f"bdf{k}_order_conditions"
        names.append(name)
        lean += [f"theorem {name} :\n    {conj} := by\n  norm_num", ""]
    # Negative control: perturb BDF2's a_1 by 1/100.
    a2, b2 = bdf(2)
    bad = a2[:]
    bad[1] += Fraction(1, 100)
    assert not order_conditions_hold(bad, b2, 2, 2)
    lean += ["/-- Negative control: BDF2 with a₁ perturbed by 1/100 violates the q=1 condition. -/",
             f"theorem bdf2_perturbed_fails :\n    ({lean_rat(bad[0])} * 0^1 + {lean_rat(bad[1])} * 1^1 + {lean_rat(bad[2])} * 2^1) ≠ "
             f"(1 * {lean_rat(b2)} * 2^0) := by\n  norm_num", ""]
    names.append("bdf2_perturbed_fails")
    lean += ["end ANSE.Alix.BDF", ""] + [f"#print axioms ANSE.Alix.BDF.{n}" for n in names]
    args.lean.write_text("\n".join(lean) + "\n")

    # Structure search: 4-step methods, every support for a_0..a_3, maximum order each.
    k = 4
    structures = []
    for size in range(0, k + 1):
        for support in itertools.combinations(range(k), size):
            best = None
            for order in range(1, 2 * k + 2):
                if len(support) + 1 != order + 1:
                    continue
                res = bdf(k, support, order)
                if res and order_conditions_hold(res[0], res[1], k, order):
                    st, _ = zero_stable(res[0])
                    best = {"support": list(support), "order": order, "zero_stable_numeric": st,
                            "a": [str(x) for x in res[0]], "b": str(res[1])}
            if best:
                structures.append(best)
    stable_max = max((s["order"] for s in structures if s["zero_stable_numeric"]), default=0)
    print(f"  structure search (k=4): {len(structures)} supports admit an exact method; "
          f"highest zero-stable order {stable_max}")
    args.out.write_text(json.dumps({
        "what": "exact BDF coefficient synthesis, Lean-proved order conditions, numeric zero-stability",
        "bdf": rows, "structure_search_k4": structures,
        "lean_file": str(args.lean),
        "the_limit_this_shows": ("order conditions are exact polynomial identities and the kernel proves them for "
                                 "every k, including k >= 7 where the method is not zero-stable and therefore "
                                 "useless; the kernel certifies the specification, not its sufficiency"),
    }, indent=2) + "\n")
    print(f"  wrote {args.out} and {args.lean}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
