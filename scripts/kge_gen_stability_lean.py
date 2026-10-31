#!/usr/bin/env python3
"""Generate Lean 4 proofs that BDF-k has a characteristic root OUTSIDE the unit disc.

Certificate (see formal/ANSE/AlixStability.lean, generic part): if every root of a
polynomial p of degree n lies in the closed unit disc then every power sum
s_m = sum_i z_i^m of its roots has |s_m| <= n. The power sums are RATIONAL and are
computed exactly from the coefficients (Newton's identities for s_1..s_{n-1}, then the
linear recurrence), so one index m with |s_m| > n proves some root has |z| > 1
without ever locating it. Every numeral below is produced by exact Fraction
arithmetic from the coefficients; none is typed by hand.

The proof steps in Lean: Newton for s_1..s_{n-1} (Vieta supplies the e_i from the
coefficients), the recurrence for s_n..s_m, then a contradiction with the norm bound.
"""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kge_bdf_pilot import bdf  # noqa: E402


def power_sums(a: list[Fraction], M: int) -> list[Fraction]:
    n = len(a) - 1
    e = [Fraction(1)] + [(-1) ** i * a[n - i] for i in range(1, n + 1)]
    s = [Fraction(n)]
    for m in range(1, M + 1):
        if m <= n:
            val = sum((-1) ** (i - 1) * e[i] * s[m - i] for i in range(1, m)) + (-1) ** (m - 1) * m * e[m]
        else:
            val = sum((-1) ** (i - 1) * e[i] * s[m - i] for i in range(1, n + 1))
        s.append(val)
    return s


def num(x: Fraction) -> str:
    return f"({x.numerator} : ℂ)" if x.denominator == 1 else f"(({x.numerator} : ℂ) / {x.denominator})"


def find_certificate(a: list[Fraction], horizon: int = 400) -> tuple[int, list[Fraction]]:
    n = len(a) - 1
    s = power_sums(a, horizon)
    for m, v in enumerate(s):
        if abs(v) > n:
            return m, s[: m + 1]
    raise ValueError(f"no certificate within {horizon} terms")


def gen(k: int) -> str:
    a, _ = bdf(k)
    m, s = find_certificate(a)
    n = k
    r = f"rho{k}"
    poly = f"X ^ {n}" + "".join(
        f" + C {num(a[j])} * X ^ {j}" if j > 1 else (f" + C {num(a[1])} * X" if j == 1 else f" + C {num(a[0])}")
        for j in range(n - 1, -1, -1))
    out = [f"/-! ## BDF{k}: a root outside the unit disc, certified by |s_{m}| > {n}", ""
           f"s_{m} = {s[m].numerator}/{s[m].denominator} ≈ {float(s[m]):.6f} -/", "",
           f"noncomputable def {r} : ℂ[X] := {poly}", "",
           f"theorem {r}_monic : {r}.Monic := by unfold {r}; monicity!", "",
           f"theorem {r}_natDegree : {r}.natDegree = {n} := by unfold {r}; compute_degree!", "",
           f"theorem {r}_ne_zero : {r} ≠ 0 := {r}_monic.ne_zero", ""]
    for j in range(n):
        out.append(f"theorem {r}_coeff{j} : {r}.coeff {j} = {num(a[j])} := by\n"
                   f"  simp [{r}, coeff_X_pow, coeff_C_mul, coeff_X, coeff_C]")
    out.append(f"theorem {r}_coeff{n} : {r}.coeff {n} = 1 := by\n"
               f"  simp [{r}, coeff_X_pow, coeff_C_mul, coeff_X, coeff_C]")
    out.append("")
    coeff_simps = ", ".join(f"{r}_coeff{j}" for j in range(n + 1))
    out += [f"theorem {r}_s0 : psumRoots {r} 0 = {num(s[0])} := by\n"
            f"  rw [psumRoots_zero, {r}_natDegree]; norm_num", ""]
    prev = [f"{r}_s0"]
    for kk in range(1, n):
        out += [f"theorem {r}_s{kk} : psumRoots {r} {kk} = {num(s[kk])} := by",
                f"  rw [psumRoots_newton_range {r} {r}_monic {kk} (by norm_num) (by rw [{r}_natDegree]; norm_num), {r}_natDegree]",
                f"  norm_num [Finset.sum_range_succ, {coeff_simps}, {', '.join(prev)}]", ""]
        prev.append(f"{r}_s{kk}")
    for mm in range(n, m + 1):
        base = mm - n
        out += [f"theorem {r}_s{mm} : psumRoots {r} {mm} = {num(s[mm])} := by",
                f"  have h := psumRoots_recurrence {r} {r}_ne_zero {base}",
                f"  rw [{r}_natDegree] at h",
                f"  norm_num [Finset.sum_range_succ, {coeff_simps}, {', '.join(prev)}] at h",
                f"  linear_combination h", ""]
        prev.append(f"{r}_s{mm}")
    out += [f"/-- BDF{k} has a characteristic root with modulus greater than 1: it is not zero-stable. -/",
            f"theorem bdf{k}_has_root_outside_disc : ∃ z : ℂ, {r}.IsRoot z ∧ 1 < ‖z‖ := by",
            "  by_contra hcon",
            "  push Not at hcon",
            f"  have hb := norm_psumRoots_le {r} hcon {m}",
            f"  rw [card_roots_eq, {r}_natDegree, {r}_s{m}] at hb",
            "  norm_num [norm_div, norm_neg] at hb", ""]
    return "\n".join(out)




def assemble(lean_path: Path, ks: list[int]) -> None:
    """Regenerate the section between the markers and append an axiom line per theorem."""
    text = lean_path.read_text()
    text = text.split("\n#print axioms ")[0].rstrip("\n") + "\n"          # drop old axiom lines
    begin, end = "-- BEGIN GENERATED (scripts/kge_gen_stability_lean.py)", "-- END GENERATED"
    head, rest = text.split(begin, 1)
    _, tail = rest.split(end, 1)
    body = "\n".join(gen(k) for k in ks)
    text = head + begin + "\n" + body + "\n" + end + tail
    import re
    names = re.findall(r"^theorem ([A-Za-z0-9_']+)", text, flags=re.M)
    text += "\n" + "\n".join(f"#print axioms ANSE.Alix.Stab.{n}" for n in names) + "\n"
    lean_path.write_text(text)
    print(f"assembled {lean_path}: {len(names)} theorems")


def summary(path: Path, ks: list[int]) -> None:
    import json
    rows = []
    for k in ks:
        a, _ = bdf(k)
        m, s = find_certificate(a)
        rows.append({"k": k, "certificate_index_m": m, "bound_k": k, "s_m": f"{s[m].numerator}/{s[m].denominator}",
                     "s_m_float": float(s[m]), "lean_theorem": f"ANSE.Alix.Stab.bdf{k}_has_root_outside_disc"})
    controls = []
    for k in range(1, 7):
        try:
            find_certificate(bdf(k)[0], horizon=400)
            controls.append({"k": k, "certificate_found": True})
        except ValueError:
            controls.append({"k": k, "certificate_found": False})
    path.write_text(json.dumps({"certificates": rows, "stable_methods_no_certificate_within_400_terms": controls,
                                "lean_module": "formal/ANSE/AlixStability.lean"}, indent=2) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--summary"]:
        summary(Path(sys.argv[2]), [int(x) for x in sys.argv[3:]])
    elif sys.argv[1:2] == ["--assemble"]:
        assemble(Path(sys.argv[2]), [int(x) for x in sys.argv[3:]])
    else:
        for k in (int(x) for x in sys.argv[1:]):
            print(gen(k))
