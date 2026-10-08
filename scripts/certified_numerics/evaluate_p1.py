#!/usr/bin/env python3
"""Evaluate pilot P1 against its preregistration (results/certified_numerics/P1_bao/preregistration.json).

Inputs: the kernel-checked rational bounds (bounds_*.json, emitted alongside the Lean files that the kernel checked),
the rusty-SUNDIALS audit output (rust_audit.jsonl), astropy (system python), the DESI DR2 data vector, and the
Lean compile/axiom logs. Comparisons with rational bounds are exact (Fraction); EdS closed form compared exactly by
squaring.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
R = REPO / "results" / "certified_numerics" / "P1_bao"
DR2 = Path("/mnt/disks/disk-socrateai-local-1/dualscale-data-r3/desi_sdss_bao/desi_bao_dr2")
C_OVER_100_HRD = Fraction(299792458, 10154300)
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}


def frac(s: str) -> Fraction:
    n, d = s.split("/")
    return Fraction(int(n), int(d))


def load_bounds(name: str) -> dict[str, dict[str, object]]:
    return json.loads((R / f"bounds_{name}.json").read_text())["redshifts"]


def inside(x: float, lo: Fraction, hi: Fraction) -> bool:
    fx = Fraction(x)
    return lo <= fx <= hi


def main() -> int:
    fit, om101, eds = load_bounds("Fit"), load_bounds("FitOm101"), load_bounds("EdS")
    labels = list(fit)
    zs = [float(Fraction(fit[k]["z"])) for k in labels]
    out: dict[str, object] = {"pilot": "P1", "labels": labels}

    # Lean status
    comp = {n: json.loads((R / f"compile_{n}.json").read_text()) for n in ("Core", "Fit", "EdS", "FitOm101", "Tampered", "Axioms")}
    ax_lines = [l for l in str(comp["Axioms"]["output"]).splitlines() if "depends on axioms" in l]
    ax = {l.split("'")[1]: [a.strip() for a in l.split("[")[1].rstrip("]").split(",")] for l in ax_lines}
    certified = {k: v for k, v in ax.items() if not k.startswith("ctl_")}
    out["lean"] = {
        "compile_rc": {n: comp[n]["rc"] for n in comp},
        "compile_seconds": {n: comp[n]["seconds"] for n in comp},
        "axioms": ax,
        "all_certified_within_whitelist": all(set(v) <= ALLOWED for v in certified.values()),
        "native_decide_in_sources": sum((REPO / "formal_cert" / "BAOCert" / f"{n}.lean").read_text().count("native_decide") for n in ("Core", "Fit", "EdS", "FitOm101")),
        "sorry_in_sources": sum((REPO / "formal_cert" / "BAOCert" / f"{n}.lean").read_text().count("sorry") for n in ("Core", "Fit", "EdS", "FitOm101")),
    }
    widths = {k: fit[k]["chi_rel_width"] for k in labels}
    h1 = (out["lean"]["compile_rc"]["Fit"] == 0 and out["lean"]["compile_rc"]["Core"] == 0 and out["lean"]["all_certified_within_whitelist"]
          and out["lean"]["native_decide_in_sources"] == 0 and out["lean"]["sorry_in_sources"] == 0 and max(widths.values()) <= 5e-4)
    out["H1"] = {"pass": h1, "max_rel_width": max(widths.values()), "rel_widths": widths}

    # Controls
    c1 = {}
    for k in labels:
        z = Fraction(eds[k]["z"])
        lo, hi = frac(eds[k]["chi_lo"]), frac(eds[k]["chi_hi"])
        # closed form 2 - 2/sqrt(1+z) >= lo  <=>  4/(1+z) <= (2-lo)^2   (2-lo > 0); <= hi  <=>  4/(1+z) >= (2-hi)^2  (2-hi > 0)
        ok_lo = 2 - lo > 0 and Fraction(4) / (1 + z) <= (2 - lo) ** 2
        ok_hi = 2 - hi > 0 and Fraction(4) / (1 + z) >= (2 - hi) ** 2
        c1[k] = bool(ok_lo and ok_hi)
    tamper_out = str(comp["Tampered"]["output"])
    ctl_axioms = {k: v for k, v in ax.items() if k.startswith("ctl_")}
    out["controls"] = {
        "C1_EdS_closed_form_inside": c1, "C1_pass": all(c1.values()) and comp["EdS"]["rc"] == 0,
        "C2_tampered_rejected": comp["Tampered"]["rc"] != 0 and "kernel" in tamper_out,
        "C2_first_error": tamper_out.strip().splitlines()[0][:300] if tamper_out.strip() else "",
        "C3_sorry_flagged": "sorryAx" in ctl_axioms.get("ctl_sorry", []),
        "C3_axiom_flagged": "ctl_cheat" in ctl_axioms.get("ctl_axiom", []),
    }
    out["controls"]["all_pass"] = all(out["controls"][k] for k in ("C1_pass", "C2_tampered_rejected", "C3_sorry_flagged", "C3_axiom_flagged"))

    # External values
    runs = {json.loads(l)["label"]: json.loads(l) for l in (R / "rust_audit.jsonl").read_text().splitlines() if l.strip()}
    from astropy.cosmology import FlatLambdaCDM
    import astropy.units as u
    cosmo = FlatLambdaCDM(H0=70.0, Om0=0.29743, Tcmb0=0 * u.K)
    dh = 299792.458 / 70.0
    astro = [float(cosmo.comoving_distance(z).value) / dh for z in zs]

    def check(vals: list[float], b: dict[str, dict[str, object]]) -> dict[str, object]:
        res = {}
        for k, v in zip(labels, vals):
            lo, hi = frac(b[k]["chi_lo"]), frac(b[k]["chi_hi"])
            res[k] = {"value": v, "inside": inside(v, lo, hi),
                      "below_lo_by": float(lo - Fraction(v)) if Fraction(v) < lo else 0.0,
                      "above_hi_by": float(Fraction(v) - hi) if Fraction(v) > hi else 0.0}
        return res

    h2 = {"rust_cvode_default": check(runs["cvode_default"]["chi"], fit),
          "rust_quadrature_default": check(runs["quadrature_default"]["chi"], fit),
          "astropy_6.1.7_Tcmb0_0": check(astro, fit),
          "rust_quadrature_Om101_vs_Om101_bounds": check(runs["quadrature_default_Om101"]["chi"], om101),
          "rust_quadrature_EdS_vs_EdS_bounds": check(runs["quadrature_default_EdS"]["chi"], eds)}
    out["H2"] = {"pass": all(r["inside"] for grp in h2.values() for r in grp.values()), "detail": h2}

    disjoint = {}
    for k in labels:
        a_lo, a_hi = frac(fit[k]["chi_lo"]), frac(fit[k]["chi_hi"])
        b_lo, b_hi = frac(om101[k]["chi_lo"]), frac(om101[k]["chi_hi"])
        disjoint[k] = bool(b_hi < a_lo or a_hi < b_lo)
    h3_req = [k for k, z in zip(labels, zs) if z >= 0.5]
    out["H3"] = {"pass": all(disjoint[k] for k in h3_req), "disjoint": disjoint, "required_labels": h3_req}

    loose = {r: check(runs[r]["chi"], fit) for r in ("cvode_rtol1e-2", "cvode_rtol1e-3")}
    out["H4"] = {"pass": any(not v["inside"] for v in loose["cvode_rtol1e-2"].values()), "detail": loose,
                 "note": "rusty-SUNDIALS checkout: ~/rusty-SUNDIALS-wt-cvode-adams (branch fix/cvode-adams-order-and-stderr, b25f152, PR #63), not origin/main"}
    out["H5"] = {"status": "NOT_ATTEMPTED", "note": "certified chi^2 in Lean was preregistered as secondary and was not attempted in this session"}

    # D_M/r_d, D_H/r_d enclosures and DESI pulls (pull intervals use the diagonal errors; exact rational arithmetic)
    mean = [l.split() for l in (DR2 / "desi_gaussian_bao_ALL_GCcomb_mean.txt").read_text().splitlines() if l.strip() and not l.startswith("#")]
    cov = [[float(x) for x in l.split()] for l in (DR2 / "desi_gaussian_bao_ALL_GCcomb_cov.txt").read_text().splitlines() if l.strip()]
    rows = []
    for j, (zs_, val, qty) in enumerate(mean):
        z = Fraction(zs_).limit_denominator(2000)
        k = next(kk for kk in labels if Fraction(fit[kk]["z"]) == z)
        if qty == "DM_over_rs":
            lo, hi = C_OVER_100_HRD * frac(fit[k]["chi_lo"]), C_OVER_100_HRD * frac(fit[k]["chi_hi"])
        elif qty == "DH_over_rs":
            lo, hi = C_OVER_100_HRD * frac(fit[k]["invE_lo"]), C_OVER_100_HRD * frac(fit[k]["invE_hi"])
        else:
            rows.append({"z": float(z), "quantity": qty, "measured": float(val), "certified": "D_V not certified in Lean (needs a cube root); see note"})
            continue
        sig = cov[j][j] ** 0.5
        rows.append({"z": float(z), "quantity": qty, "measured": float(val), "sigma": sig, "pred_lo": float(lo), "pred_hi": float(hi),
                     "rel_width": float((hi - lo) / lo), "pull_lo": (float(val) - float(hi)) / sig, "pull_hi": (float(val) - float(lo)) / sig})
    out["desi_dr2_comparison"] = rows
    out["verdict"] = ("VOID" if not out["controls"]["all_pass"] else
                      "P1_OK" if all(out[h]["pass"] for h in ("H1", "H2", "H3", "H4")) else "P1_PARTIAL")
    (R / "result.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"verdict": out["verdict"], "H1": out["H1"]["pass"], "max_width": out["H1"]["max_rel_width"], "H2": out["H2"]["pass"],
                      "H3": out["H3"]["pass"], "H4": out["H4"]["pass"], "controls": out["controls"]["all_pass"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
