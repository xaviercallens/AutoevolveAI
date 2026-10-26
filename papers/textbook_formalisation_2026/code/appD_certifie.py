"""Annexe D : exemple complet de calcul numérique certifié, de la virgule flottante au noyau de Lean.

Trois étapes, chacune avec un témoin positif et un témoin négatif :
  1. Arithmétique d'intervalles à arrondi dirigé (math.nextafter) : la somme de dix copies de 1/10.
     Positif : l'intervalle arrondi vers l'extérieur contient exactement 1 (vérifié en Fraction).
     Négatif : la somme flottante naïve vaut 0.9999999999999999, et un « intervalle » dont les bornes sont arrondies
     au plus proche exclut 1.
  2. Arithmétique de boules (Arb, via python-flint) : I = int_0^1 exp(-x^2) dx, à 96 bits.
     Positif : la boule recoupe la boule indépendante sqrt(pi)/2 * erf(1).
     Négatif : la méthode du point milieu en flottants (n = 10) tombe hors de la boule : un flottant n'est pas un
     encadrement.
  3. Certificat rationnel décidé par le noyau de Lean via LeanFlow (lean.certify, tactique decide_kernel) :
     on arrondit la boule vers l'extérieur en deux décimaux à 30 chiffres, puis
     positif : 0.7468 < I.lo et I.hi < 0.7469 (statut ok, niveau A pour l'énoncé arithmétique seul) ;
     négatif : I.hi < 0.7468 doit être rejeté (false-statement).

Usage : python -I appD_certifie.py SORTIE [--flint-path DIR] [--lean PATH] [--leanflow-src DIR]
Par défaut : python-flint 0.6.0 de .scratchpad/b2_pylib (celui de l'étude B2), Lean 4.34.1 de ~/.elan, LeanFlow de
~/LeanFlow-wt-p1/src. Code de sortie 1 si un témoin ne se comporte pas comme prévu.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

HOME = Path("/home/callensxavier_gmail_com")
WORKTREE = HOME / "AutoevolveAI/.claude/worktrees/openai-math-discovery"


def interval_sum_tenths() -> dict[str, Any]:
    """Étape 1 : dix fois 1/10, en flottant naïf et en intervalles arrondis vers l'extérieur."""
    x_hi = 0.1  # le flottant le plus proche de 1/10 ; il est AU-DESSUS de 1/10
    x_lo = math.nextafter(x_hi, -math.inf)
    assert Fraction(x_lo) < Fraction(1, 10) < Fraction(x_hi)
    naive = 0.0
    lo, hi = 0.0, 0.0
    near_lo, near_hi = 0.0, 0.0
    for _ in range(10):
        naive += x_hi
        lo = math.nextafter(lo + x_lo, -math.inf)  # chaque addition arrondie vers le bas...
        hi = math.nextafter(hi + x_hi, math.inf)  # ... ou vers le haut (élargissement d'un ulp, toujours sûr)
        near_lo, near_hi = near_lo + x_lo, near_hi + x_hi  # bornes arrondies au plus proche : faux encadrement
    one = Fraction(1)
    return {"naive_sum": repr(naive), "naive_equals_1": naive == 1.0,
            "outward": [repr(lo), repr(hi)], "outward_contains_1": Fraction(lo) <= one <= Fraction(hi),
            "nearest": [repr(near_lo), repr(near_hi)],
            "nearest_contains_1": Fraction(near_lo) <= one <= Fraction(near_hi)}


def ball_integral(flint_path: Path) -> dict[str, Any]:
    """Étape 2 : la boule Arb de I, son contrôle indépendant par erf, et le témoin flottant."""
    sys.path.insert(0, str(flint_path))
    import flint  # noqa: PLC0415
    from flint import acb, arb, ctx  # noqa: PLC0415

    ctx.prec = 96
    ball = acb.integral(lambda x, _analytic: (-x * x).exp(), 0, 1).real
    via_erf = arb(1).erf() * arb.pi().sqrt() / 2
    n = 10
    midpoint = sum(math.exp(-(((k + 0.5) / n) ** 2)) for k in range(n)) / n
    m, e = ball.mid().man_exp()
    rm, re_ = ball.rad().man_exp()
    centre = Fraction(int(m)) * Fraction(2) ** int(e)
    radius = Fraction(int(rm)) * Fraction(2) ** int(re_)
    lo, hi = centre - radius, centre + radius
    digits = 10 ** 30
    lo_dec = Fraction(math.floor(lo * digits), digits)  # arrondi vers le bas : lo_dec <= lo
    hi_dec = Fraction(math.ceil(hi * digits), digits)  # arrondi vers le haut : hi <= hi_dec
    return {"python_flint": flint.__version__, "prec_bits": 96, "ball": str(ball), "erf_ball": str(via_erf),
            "erf_overlaps": bool(ball.overlaps(via_erf)), "radius": float(radius),
            "midpoint_float_n10": repr(midpoint),
            "midpoint_inside_ball": bool(lo <= Fraction(midpoint) <= hi),
            "enclosure_30_digits": [f"{lo_dec.numerator}/{lo_dec.denominator}",
                                    f"{hi_dec.numerator}/{hi_dec.denominator}"],
            "enclosure_decimal": [f"{float(lo_dec):.17g}", f"{float(hi_dec):.17g}"]}


def leanflow_certificates(enclosure: list[str], lean: Path, leanflow_src: Path) -> dict[str, Any]:
    """Étape 3 : deux affirmations sur l'encadrement rationnel, décidées par le noyau de Lean."""
    sys.path.insert(0, str(leanflow_src))
    from leanflow_mcp.lean import LeanConfig, certify  # noqa: PLC0415

    cfg = LeanConfig(lean_cmd=(str(lean),), timeout_s=300)
    claims = {
        "pos_I_between_0.7468_and_0.7469": {
            "name": "gaussI", "tactic": "decide_kernel", "enclosures": {"I": enclosure},
            "assertions": [{"label": "I.lo > 0.7468", "endpoint": "I.lo", "op": ">", "rhs": "7468/10000"},
                           {"label": "I.hi < 0.7469", "endpoint": "I.hi", "op": "<", "rhs": "7469/10000"}]},
        "neg_I_below_0.7468": {
            "name": "gaussIfalse", "tactic": "decide_kernel", "enclosures": {"I": enclosure},
            "assertions": [{"label": "I.hi < 0.7468 (faux)", "endpoint": "I.hi", "op": "<", "rhs": "7468/10000"}]},
    }
    out: dict[str, Any] = {}
    for key, claim in claims.items():
        res = certify(claim, cfg)
        out[key] = {"status": res.status, "code": res.code, "tier": res.tier, "failed": list(res.failed),
                    "seconds": res.seconds, "lean_version": res.lean_version}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path)
    ap.add_argument("--flint-path", type=Path, default=WORKTREE / ".scratchpad/b2_pylib")
    ap.add_argument("--lean", type=Path, default=HOME / ".elan/toolchains/leanprover--lean4---v4.34.1/bin/lean")
    ap.add_argument("--leanflow-src", type=Path, default=HOME / "LeanFlow-wt-p1" / "src")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    step1 = interval_sum_tenths()
    step2 = ball_integral(a.flint_path)
    step3 = leanflow_certificates(step2["enclosure_30_digits"], a.lean, a.leanflow_src)
    checks = {
        "step1_pos_outward_contains_1": step1["outward_contains_1"],
        "step1_neg_naive_not_1": not step1["naive_equals_1"],
        "step1_neg_nearest_excludes_1": not step1["nearest_contains_1"],
        "step2_pos_erf_overlaps": step2["erf_overlaps"],
        "step2_neg_midpoint_outside_ball": not step2["midpoint_inside_ball"],
        "step3_pos_ok": step3["pos_I_between_0.7468_and_0.7469"]["status"] == "ok",
        "step3_neg_rejected": step3["neg_I_below_0.7468"]["status"] == "rejected",
    }
    result = {"step1_interval": step1, "step2_ball": step2, "step3_leanflow": step3, "checks": checks,
              "all_controls_pass": all(checks.values())}
    (a.out / "appD_result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))
    return 0 if result["all_controls_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
