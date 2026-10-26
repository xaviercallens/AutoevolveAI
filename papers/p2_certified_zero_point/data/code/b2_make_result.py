"""Assemble results/proposal2/2026-10-26/B2/result.json from the run records and the Lean / LeanFlow outputs.

usage: python -I b2_make_result.py B2_DIR
Every number is copied from a machine-written file in B2_DIR; nothing is typed in by hand.
"""

import hashlib
import json
import os
import re
import sys
from fractions import Fraction


def load(d: str, name: str) -> dict | None:
    p = os.path.join(d, name)
    return json.load(open(p)) if os.path.exists(p) else None


def sha(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def summary(run: dict | None) -> dict | None:
    if run is None:
        return None
    keys = ("a", "path", "N", "t0", "qmax", "refine_tol", "max_depth", "seconds", "Upp0", "int_trW", "sum_e", "B", "E0",
            "trD_cells", "trD_direct", "theta_L_a", "stats", "stability", "certified_B_negative", "cert_rationals",
            "controls", "script_sha256", "python_flint", "arb_prec_bits", "n_lattice_half")
    return {k: run.get(k) for k in keys}


def lean_summary(j: dict | None) -> dict | None:
    if j is None:
        return None
    out = j.get("output", "")
    ax = [ln for ln in out.splitlines() if "depends on axioms" in ln or "does not depend on any axioms" in ln]
    errs = [ln for ln in out.splitlines() if ": error" in ln]
    return {"file": j.get("file"), "module": j.get("module"), "rc": j.get("rc"), "seconds": j.get("seconds"),
            "axioms_verbatim": ax, "n_errors": len(errs), "first_errors": errs[:4],
            "file_sha256": sha(j["file"]) if j.get("file") and os.path.exists(j["file"]) else None}


def literal_check(d: str) -> dict:
    """Regex the rational literals out of the Lean files and compare them with the run records (machine provenance)."""
    lean_dir = os.path.abspath(os.path.join(d, "..", "..", "..", "..", "formal_cert", "Programmes", "ZeroPointCert"))
    basic = open(os.path.join(lean_dir, "Basic.lean")).read()
    ctl = open(os.path.join(lean_dir, "Controls.lean")).read()
    rej = open(os.path.join(lean_dir, "RejectA2.lean")).read()
    a1 = load(d, "run_a1_shear_main.json")["cert_rationals"]
    a2 = load(d, "run_a2_shear_negctl.json")["cert_rationals"]
    out: dict = {}

    def lit(src: str, name: str) -> Fraction:
        m = re.search(r"def " + name + r" : ℝ := (-?\d+) / (\d+)", src)
        return Fraction(int(m.group(1)), int(m.group(2)))

    for lean_name, key in (("Upp0_hi", "Upp0_hi"), ("trW_hi", "trW_hi"), ("esum_hi", "esum_hi"), ("lmin_lo", "lmin_lo"),
                           ("dB_hi", "dB_hi")):
        out["Basic." + lean_name] = lit(basic, lean_name) == Fraction(a1[key])
    out["Controls.Upp0_lo_a2"] = lit(ctl, "Upp0_lo_a2") == Fraction(a2["Upp0_lo"])
    m = re.search(r"\((\d+) / (\d+) : ℝ\) \+ \((\d+) / (\d+)\) \* \((\d+) / (\d+)\) < 0", rej)
    vals = [Fraction(int(m.group(i)), int(m.group(i + 1))) for i in (1, 3, 5)]
    out["RejectA2.literals"] = vals == [Fraction(a2["Upp0_hi"]), Fraction(a2["trW_hi"]), Fraction(a2["esum_hi"])]
    out["all_match"] = all(out.values())
    return out


def main() -> None:
    d = sys.argv[1]
    main_run = load(d, "run_a1_shear_main.json")
    res = {
        "item": "B2",
        "title": "Kernel-checked theorem: the triangular lattice is not a local minimum of the harmonic zero-point energy "
                 "for the Gaussian exp(-pi r^2) (a = 1)",
        "verdict": None,
        "conventions": {
            "lattice": "L_rho = c Z(1,0) + c Z(1/2, sqrt3/2), c^2 = 2/sqrt3 (unit covolume)",
            "path": "L_t = P_t L_rho, P_t = [[1, t], [t, 1 + t^2]] (det 1, symmetric shear; tau(t) = rho + sqrt3 t + O(t^2))",
            "coupling": "fixed integer labels n and fixed reduced kappa in [-1/2,1/2]^2 for all t; strain frame, no rotation",
            "E": "E(t) = (1/2) int tr D_t(kappa)^{1/2} dkappa, D_t = sum_{n != 0} (1 - cos 2 pi kappa.n) Hess exp(-pi a |P_t R_n|^2)",
            "U": "U(t) = (1/4) int [tr X + tr X^{-1} D_t] dkappa, X = D_0^{1/2}",
            "window": "t0 = 1/100000",
        },
        "runs": {
            "main_a1_shear": summary(main_run),
            "positive_control_a1_diag": summary(load(d, "run_a1_diag_ctl.json")),
            "negative_control_a2_shear": summary(load(d, "run_a2_shear_negctl.json")),
            "extra_a0.5_shear": summary(load(d, "run_a05_shear_limit.json")),
        },
        "lean": {
            "basic": lean_summary(load(d, "lean_basic.json")),
            "controls": lean_summary(load(d, "lean_controls.json")),
            "reject_tampered": lean_summary(load(d, "lean_reject_tampered.json")),
            "reject_a2": lean_summary(load(d, "lean_reject_a2.json")),
        },
        "leanflow": {
            "a1": load(d, "leanflow_cert_a1.json"),
            "a2": load(d, "leanflow_cert_a2.json"),
            "a05": load(d, "leanflow_cert_a05.json"),
        },
        "tau_speed": "k = |tau'(0)|^2/y^2 = 4 for both paths (b2_tau_speed.py), so E''(0) = 2 Lap E_zp(rho) if E is C^2 and isotropic at rho",
    }
    for k in ("a1", "a2", "a05"):
        lf = res["leanflow"][k]
        if lf:
            res["leanflow"][k] = {x: lf.get(x) for x in ("status", "code", "tier", "verified", "message", "failed", "lean_version",
                                                       "claim_sha256", "statement_sha256", "assertions", "axioms")}
    ok = (main_run is not None and main_run["certified_B_negative"] and res["lean"]["basic"] is not None
          and res["lean"]["basic"]["rc"] == 0)
    res["verdict"] = "CERTIFIED (Tier A logic + arithmetic; Tier C ball-arithmetic enclosures and analytic glue)" if ok else "NOT CERTIFIED"
    code_dir = os.path.join(d, "code")
    res["lean_literal_provenance"] = literal_check(d)
    res["code_sha256"] = {f: sha(os.path.join(code_dir, f)) for f in sorted(os.listdir(code_dir)) if f.endswith(".py")}
    json.dump(res, open(os.path.join(d, "result.json"), "w"), indent=1)
    print(res["verdict"])


if __name__ == "__main__":
    main()
