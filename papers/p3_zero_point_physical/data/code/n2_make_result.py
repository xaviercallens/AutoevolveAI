"""N2: assemble result.json from the run records, LeanFlow certificates and Lean compile records (no numbers typed by
hand: every number is read from a file produced by a tool).

usage: python -I n2_make_result.py N2_DIR
"""

from __future__ import annotations

import json
import os
import re
import sys


def load(path: str) -> dict | None:
    return json.load(open(path)) if os.path.exists(path) else None


def run_summary(r: dict | None) -> dict | None:
    if r is None:
        return None
    keys = ("potential", "param", "N", "t0", "qmax", "refine_tol", "max_depth", "cell_rule_order", "n_lattice_half",
            "seconds", "M_window_curvature_bound", "U_lin_pp0_B2_majorant", "E0", "positivity_ok",
            "certified_not_local_min", "cert_rationals", "controls", "script_sha256")
    out = {k: r.get(k) for k in keys}
    out["stats"] = {k: v for k, v in r["stats"].items() if k != "width_by_band"}
    out["tails"] = r.get("tails")
    return out


def axiom_blocks(output: str) -> list[str]:
    """Full `#print axioms` reports (multi-line reports joined), verbatim up to whitespace."""
    out, cur = [], None
    for ln in output.splitlines():
        if "depends on axioms" in ln or "does not depend on any axioms" in ln:
            cur = ln.strip()
        elif cur is not None:
            cur += " " + ln.strip()
        if cur is not None and ("]" in cur or "does not depend" in cur):
            out.append(cur)
            cur = None
    return out


def tierx(path: str) -> dict:
    rows = {}
    if not os.path.exists(path):
        return rows
    for line in open(path):
        m = re.match(r"(\S+):(\S+) N=(\d+) rc=(\S+) .*E0=(\S+) U''\(0\)=(\S+) E''\(0\)~(\S+) ", line)
        if m:
            rows[f"{m.group(1)}:{m.group(2)}"] = {"rc": float(m.group(4)), "E0": float(m.group(5)),
                                                 "U_lin_pp0_B2": float(m.group(6)), "E_pp0": float(m.group(7))}
    return rows


def main() -> None:
    d = sys.argv[1]
    R = lambda p: load(os.path.join(d, p))  # noqa: E731
    lf = {k: R(f"leanflow_cert_{k}.json") for k in ("yuk1", "yuk2", "gauss1", "gauss2")}
    lean = {k: R(f"lean_{k}.json") for k in ("taylor", "basic", "controls", "reject_gauss2")}
    res = {
        "item": "N2", "date": "2026-10-26",
        "statement": "triangular lattice is not a local minimum of the harmonic zero-point energy E_zp (unit-covolume "
                     "planar Bravais lattices, hbar = m = 1) along the symmetric shear P_t = [[1,t],[t,1+t^2]]; "
                     "E(t) < E(0) for 0 < |t| <= 1e-5",
        "method": "second-order (t-dependent) majorant U2(t) = 1/4 int [tr X_t + tr X_t^-1 D_t], X_t = D_0^(1/2) + t Y, "
                  "X Y + Y X = D_0'; U2 >= E, U2(0) = E(0), U2''(0) = E''(0); window bound by Arb enclosure of "
                  "1/4 int sup_|u|<=t0 f_kappa''(u) with a second-order Taylor cell rule (python-flint 0.6.0)",
        "tierx_scan_rc40": tierx(os.path.join(d, "tierx_scan_rc40.txt")),
        "tierx_scan_rc100": tierx(os.path.join(d, "tierx_scan_rc100.txt")),
        "runs": {
            "yukawa1_main": run_summary(R("runs/o2_y1_merged.json")),
            "yukawa1_first_attempt_not_certified": run_summary(R("runs/o2_y1_N64.json")),
            "yukawa2_main": run_summary(R("runs/o2_y2_N64.json")),
            "gauss1_positive_control": run_summary(R("runs/o2_g1_N64d1.json")),
            "gauss2_negative_control": run_summary(R("runs/negctl_g2_N64.json")),
        },
        "leanflow": {k: (None if v is None else {"status": v["status"], "code": v["code"], "tier": v["tier"],
                                                 "verified": v["verified"], "failed": v["failed"]})
                     for k, v in lf.items()},
        "lean": {k: (None if v is None else {"file": v["file"], "rc": v["rc"], "seconds": v["seconds"],
                                             "axioms": axiom_blocks(v["output"]),
                                             "errors": [ln for ln in v["output"].splitlines() if "error" in ln][:5]})
                 for k, v in lean.items()},
    }
    y1 = res["runs"]["yukawa1_main"]
    y2 = res["runs"]["yukawa2_main"]
    res["per_potential"] = {
        "yukawa:1": {"certified": bool(y1 and y1["certified_not_local_min"]),
                     "M_hi": y1 and y1["cert_rationals"]["M_hi"]},
        "yukawa:2": {"certified": bool(y2 and y2["certified_not_local_min"]),
                     "M_hi": y2 and y2["cert_rationals"]["M_hi"]},
        "riesz:3": {"certified": False, "obstacle": "algebraic r^-5 Hessian tail: real-space tails of B = D/s^2 and of "
                    "its cell partials do not converge fast enough (|k|^3 non-analytic term); needs an Ewald / "
                    "Gaussian-mixture split with reciprocal-space jets, not implemented in budget"},
        "dipolar:0.1": {"certified": False, "obstacle": "same as riesz:3 (r^-3 tail, P2 normalisation)"},
        "dipolar:0.5": {"certified": False, "obstacle": "same as riesz:3 (r^-3 tail, P2 normalisation)"},
        "riesz:4": {"certified": False, "obstacle": "not attempted: Tier X E''(0) > 0 (P2 curvature table: local MIN; "
                    "P2 refuted riesz:4 only by a far competitor tau = 0.3 + 0.954i), so the local statement is false "
                    "at Tier X"},
    }
    json.dump(res, open(os.path.join(d, "result.json"), "w"), indent=1)
    print(json.dumps(res["per_potential"], indent=1))
    print(json.dumps(res["leanflow"], indent=1))


if __name__ == "__main__":
    main()
