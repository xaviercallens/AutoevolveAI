"""Build the Elenchus claim ledger for the certified zero-point-curvature paper (papers/p2_certified_zero_point).

Modelled on papers/prog_zero_point_optimality/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not be filed
above anything in its depends_on. Ball-arithmetic enclosures (C-ball) and human arguments (C-human) are both Tier C in the ledger;
the evidence blob carries a "subtier" field ("C-ball" or "C-human") so the distinction survives the gate.
Run:  /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I build_ledger.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
EV = HERE / "evidence"
DATA = PAPER / "data"
LEAN = DATA / "lean"
TOOLCHAIN = "Lean 4.34.1 + Mathlib through scripts/certified_numerics/lean_pinned.py (module imports Programmes.ZeroPoint.Basic and Mathlib submodules; no import Mathlib)"
ALLOW = ["propext", "Classical.choice", "Quot.sound"]
STATUS = ("producer-checked by the B2 lane; independent AI-agent audit (papers/p2_certified_zero_point/AUDIT.md, ACCEPT_WITH_CORRECTIONS) and statement lock "
          "(results/proposal2/2026-10-26/B2/STATEMENT_LOCK.json, source sha256 d6947d201166...) recorded; no human audit of statement adequacy")
AI_AUDIT = {"auditor": "separate Claude Opus agent instance (producer != verifier, same pipeline)", "human": False,
            "report": "papers/p2_certified_zero_point/AUDIT.md", "verdict": "ACCEPT_WITH_CORRECTIONS",
            "statement_lock": "results/proposal2/2026-10-26/B2/STATEMENT_LOCK.json",
            "statement_lock_source_sha256": "d6947d201166fcf578e8e2ba130bd1d87057a906df6bc23ecca226af9ba6bd24",
            "note": "AI audit, not a person: the gate field audit is left null so LEDGER_UNAUDITED_TIER_A stays open"}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def blob(obj: dict) -> str:
    raw = json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False).encode()
    d = sha(raw)
    EV.mkdir(parents=True, exist_ok=True)
    (EV / f"{d}.json").write_bytes(raw)
    return f"sha256:{d}"


def fref(p: Path) -> dict:
    return {"path": str(p.relative_to(PAPER)), "sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict) -> dict:
    r = {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
         "depends_on": depends, "evidence": blob(ev), "audit": None}
    if tier == "A":
        r["ai_audit"] = AI_AUDIT
    return r


LB = json.loads((DATA / "lean_basic.json").read_text())
LC = json.loads((DATA / "lean_controls.json").read_text())


def axl(names: list[str], j: dict) -> list[str]:
    lines = [l.strip() for l in j["output"].split("\n") if any(f"'ProgZeroPointCert.{n}' " in l for n in names)]
    if len(lines) != len(names):
        raise SystemExit(f"axiom lines missing for {names}: {lines}")
    return lines


def lean_ev(names: list[str], j: dict, f: str) -> dict:
    return {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output": axl(names, j), "allowlist": ALLOW,
            "compile_transcript": fref(DATA / ("lean_basic.json" if j is LB else "lean_controls.json")),
            "sources": [fref(LEAN / f)], "status": STATUS, "statement_adequacy": "not audited by a human"}


def ball(files: list[str], note: str, sub: str = "C-ball") -> dict:
    return {"kind": "argument", "subtier": sub, "note": note, "files": [fref(DATA / f) for f in files],
            "instrument": "code/b2_certify.py, python-flint 0.6.0 (Arb ball arithmetic, 96 bits), outward rounded; not kernel-checked"}


def human(text: str) -> dict:
    return {"kind": "argument", "subtier": "C-human", "text": text, "source_note": fref(DATA / "CERTIFIED_CURVATURE.md")}


def num(files: list[str], note: str) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True, "note": note, "files": [fref(DATA / f) for f in files]}


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    c = [
        rec("CZP-A-0001", "A", "lean_axioms",
            "ProgZeroPointCert.quad_nonneg, two_trace_le_of_inverse, two_trace_eq_of_eq: for symmetric 2x2 real X, S with P = X^-1 positive definite, 2 tr S <= tr X + tr(P S^2), with equality at S = X.",
            [], lean_ev(["quad_nonneg", "two_trace_le_of_inverse", "two_trace_eq_of_eq"], LB, "Basic.lean")),
        rec("CZP-A-0002", "A", "lean_axioms",
            "ProgZeroPointCert.sum_lt_of_majorant_window, not_isLocalMin_of_majorant, lt_of_majorant_window_symm: if E <= U on [-t0,t0], U(0) = E(0) and U(t)+U(-t)-2U(0) <= t^2 B with B < 0 for 0 < t <= t0, then E(t)+E(-t) < 2E(0), 0 is not a local minimum of E, and with E(-t) = E(t) also E(t) < E(0).",
            [], lean_ev(["sum_lt_of_majorant_window", "not_isLocalMin_of_majorant", "lt_of_majorant_window_symm"], LB, "Basic.lean")),
        rec("CZP-A-0003", "A", "lean_axioms",
            "ProgZeroPointCert.t0_pos, cert_B_neg, cert_stability, cert_window: with the rational endpoints Upp0_hi, trW_hi, esum_hi, lmin_lo, dB_hi of the a=1 shear run, Upp0_hi + trW_hi*esum_hi < 0 and lmin_lo - dB_hi > 0, and the bound Upp0 + trW*esum <= Upp0_hi + trW_hi*esum_hi is monotone in its inputs. (That the endpoints are enclosures of the stated integrals is NOT part of this claim; see CZP-C-0001.)",
            [], lean_ev(["t0_pos", "cert_B_neg", "cert_stability", "cert_window"], LB, "Basic.lean")),
        rec("CZP-A-0004", "A", "lean_axioms",
            "LeanFlow lean.certify (unmodified) renders the endpoint claims Upp0.hi + pert.hi < 0 and lmin.lo - dB.hi > 0 of the a=1 run into Int statements and verifies both (status ok, code verified, tier A for the arithmetic statement only, axiom lists empty). Arithmetic about the stated numbers, not their provenance.",
            [], {"kind": "lean_axioms", "toolchain": "Lean 4.34.1 (LeanFlow lean.certify)", "axiom_output": ["cert_0: does not depend on any axioms", "cert_1: does not depend on any axioms"],
                 "allowlist": ALLOW, "compile_transcript": fref(DATA / "leanflow_cert_a1.json"), "sources": [fref(DATA / "leanflow_claim_a1.json")], "status": STATUS,
                 "statement_adequacy": "not audited by a human"}),
        rec("CZP-A-0005", "A", "lean_axioms",
            "ProgZeroPointCert.triangular_not_localMin_of_certificate: conditional on the explicit hypotheses (E <= U on |t| <= t0, U 0 = E 0, the second-difference window bound with Upp0 <= Upp0_hi, 0 <= trW <= trW_hi, 0 <= esum <= esum_hi, and E(-t) = E(t)), E has no local minimum at 0 and E(t) < E(0) for 0 < t <= 1/100000. The hypotheses are the C-ball and C-human inputs; this statement does not discharge them.",
            ["CZP-A-0002", "CZP-A-0003"], lean_ev(["triangular_not_localMin_of_certificate"], LB, "Basic.lean")),
        rec("CZP-A-0006", "A", "lean_axioms",
            "ProgZeroPointCert.hasDerivAt_lin, hasDerivAt_quad, hasDerivAt_qS, hasDerivAt_q1S, hasDerivAt_gaussS, hasDerivAt_gaussS', hasDerivAt_entry': derivatives of |P_t R0|^2 along the shear path, the first two derivatives of the Gaussian weight exp(-pi a q(t)), and the double product rule for one Hessian entry e*M. They do not assemble the Hessian formula used in the code (see CZP-C-0009).",
            [], lean_ev(["hasDerivAt_lin", "hasDerivAt_quad", "hasDerivAt_qS", "hasDerivAt_q1S", "hasDerivAt_gaussS", "hasDerivAt_gaussS'", "hasDerivAt_entry'"], LB, "Basic.lean")),
        rec("CZP-A-0007", "A", "lean_axioms",
            "ProgZeroPointCert.tampered_false and a2_not_certifiable (Controls.lean): the sign-flipped certificate inequality is false, and for the a=2 enclosure Upp0 >= 3173413321863/250000000000 > 0 no trW, esum >= 0 can give Upp0 + trW*esum < 0.",
            [], lean_ev(["tampered_false", "a2_not_certifiable"], LC, "Controls.lean")),
        rec("CZP-A-0008", "A", "lean_axioms",
            "Planted controls are caught: ctl_sorry depends on sorryAx and ctl_axiom on the planted axiom ProgZeroPointCert.ctl_cheat, although Controls.lean compiles with rc 0; the kernel rejects (rc 1, goal False) the tampered certificate (RejectTampered.lean) and the a=2 certificate (RejectA2.lean); LeanFlow rejects the a=2 claim (false-statement).",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": [l.strip() for l in LC["output"].split("\n") if "ctl_sorry'" in l or "ctl_axiom'" in l],
                 "allowlist": ALLOW, "compile_transcript": fref(DATA / "lean_controls.json"),
                 "rejections": [fref(DATA / "lean_reject_tampered.json"), fref(DATA / "lean_reject_a2.json"), fref(DATA / "leanflow_cert_a2.json")],
                 "sources": [fref(LEAN / "Controls.lean"), fref(LEAN / "RejectTampered.lean"), fref(LEAN / "RejectA2.lean")], "status": STATUS,
                 "statement_adequacy": "not audited by a human"}),
        # ---------------------------------------------------------------- C-ball
        rec("CZP-C-0001", "C", "argument",
            "C-ball. Ball-arithmetic enclosures at a=1 on the shear path (206,468 cells, 0 failed, 42 lattice pairs, tails < 1e-21): U''(0) in [-1.947713,-1.900168]; int tr X^-1 in [1.825520,1.833534]; esum <= 0.0319642; hence B_hi = Upp0_hi + trW_hi*esum_hi = -1.841560. The rational endpoints in Basic.lean match the run file (lean_literal_provenance all_match).",
            [], ball(["run_a1_shear_main.json", "result.json"], "Arb enclosures; the cell-wise mean-value bounds and the lattice tails are not kernel-checked.")),
        rec("CZP-C-0002", "C", "argument",
            "C-ball. Stability of L_t for |t| <= 1e-5 at a=1: lambda_min(B_0) >= 0.918889 on every cell and ||B_t - B_0|| <= 0.007528, margin 0.911361 > 0, so D_t(kappa) > 0 for kappa != 0 and E(t) is defined.",
            [], ball(["run_a1_shear_main.json"], "same instrument as CZP-C-0001")),
        rec("CZP-C-0003", "C", "argument",
            "C-ball. Engine positive controls at a=1: the E(0) enclosure [1.498719,1.507934] contains P2's spectral value 1.50335235220736; the cell value of <tr D> [5.26378,5.29693] contains the exact lattice sum 5.2804187, which overlaps 4 pi - 2 pi theta_L(1); a second path diag(1+t,1/(1+t)) gives U''(0) in [-1.945739,-1.902147] overlapping the shear path.",
            [], ball(["run_a1_shear_main.json", "run_a1_diag_ctl.json"], "positive controls of the cell engine")),
        rec("CZP-C-0004", "C", "argument",
            "C-ball, NOT preregistered. The same certificate at a=1/2 (P2 Tier X: triangular is a local maximum there): U''(0) in [-1.043919,-0.982646], B_hi = -0.918357 < 0, stability margin 0.3648; LeanFlow tier A for its arithmetic. It is not covered by the Lean Basic.lean theorem, which is a=1 only.",
            [], ball(["run_a05_shear_limit.json", "leanflow_cert_a05.json"], "by-product run, reported as such")),
        rec("CZP-C-0005", "C", "argument",
            "C-ball. Negative control a=2 (P2: triangular is a local minimum): U''(0) in [12.69365, 12.75701] > 0, B in [12.772, 12.836]; the certificate is NOT obtained, as required. Stability margin 0.1452 > 0; E(0) enclosure [0.540969,0.542887] contains P2's 0.5419325.",
            ["CZP-A-0007"], ball(["run_a2_shear_negctl.json", "run_a2_shear_negctl.log"], "negative control of the method")),
        # ---------------------------------------------------------------- C-human
        rec("CZP-C-0006", "C", "argument",
            "C-human. E(t) = (1/2) int tr D_t^{1/2} dkappa with D_t = sum_{n != 0}(1 - cos 2 pi kappa.n) Hess exp(-pi a |P_t R_n|^2) at fixed reduced kappa and labels n is the harmonic zero-point energy of L_t and is P2's E_zp (basis independence of the zone mean); its E(0) enclosure contains P2's spectral value.",
            ["CZP-C-0003"], human("CERTIFIED_CURVATURE.md section 2.1")),
        rec("CZP-C-0007", "C", "argument",
            "C-human. E <= U on |t| <= t0 with U(0) = E(0): apply two_trace_le_of_inverse (CZP-A-0001) pointwise at kappa != 0 with S = D_t^{1/2}, X = D_0^{1/2}, then integrate (integrable since tr X^-1 D_t <= ||D_t|| tr X^-1 and int tr X^-1 <= 1.8336); equality from two_trace_eq_of_eq.",
            ["CZP-A-0001", "CZP-C-0002", "CZP-C-0001"], human("CERTIFIED_CURVATURE.md section 2.2")),
        rec("CZP-C-0008", "C", "argument",
            "C-human. Window identity and bound: U is affine in D_t; the second-order mean value theorem entrywise gives H(t)+H(-t)-2H(0) = t^2 H''(xi), |xi| < t, and summing and integrating (absolute convergence) gives (U(t)+U(-t)-2U(0))/t^2 <= Upp0 + (int tr X^-1)*esum for 0 < t <= t0.",
            ["CZP-A-0006", "CZP-C-0009"], human("CERTIFIED_CURVATURE.md sections 1 and 2.3")),
        rec("CZP-C-0009", "C", "argument",
            "C-human. The entry formula of hess_and_dd (M, M', M'' of 4 pi^2 a^2 R_i R_j - 2 pi a delta_ij along P_t, combined with e, e', e'' of CZP-A-0006) as evaluated by b2_certify.py is the correct second t-derivative of Hess V(R_n(t)); finite differences agree to 7e-7 (Tier X cross-check, reported in the paper only).",
            ["CZP-A-0006"], human("CERTIFIED_CURVATURE.md table row 'assembling these into the entry formula'")),
        rec("CZP-C-0010", "C", "argument",
            "C-human. Mirror symmetry E(-t) = E(t): sigma = diag(1,-1) maps L_rho to itself, sigma P_t sigma = P_{-t}, so L_{-t} = sigma L_t, and E depends only on the lattice up to isometry.",
            [], human("CERTIFIED_CURVATURE.md section 2.4")),
        rec("CZP-C-0011", "C", "argument",
            "C-human. The shape of L_t is tau(t) = rho + sqrt3 t + O(t^2), so small t != 0 gives lattice shapes different from rho (mod SL2(Z)) arbitrarily close to rho; |tau'(0)|^2/y^2 = 4.",
            [], human("CERTIFIED_CURVATURE.md section 2.5; code/b2_tau_speed.py")),
        rec("CZP-C-0012", "C", "argument",
            "HEADLINE (C): for the Gaussian exp(-pi r^2) (a=1), E(t) < E(0) for every 0 < |t| <= 1e-5, E has no local minimum at t = 0, and so the triangular lattice is not a local minimum of the harmonic zero-point energy over unit-covolume Bravais lattice shapes. Certified quantity: (U(t)+U(-t)-2U(0))/t^2 <= B_hi = -1.84156, an upper bound on the curvature, not a two-sided enclosure of Lap E_zp. Tier A part: the logic and the rational arithmetic (CZP-A-0005); tier C-ball: CZP-C-0001, CZP-C-0002; tier C-human: the glue.",
            ["CZP-A-0005", "CZP-A-0004", "CZP-C-0001", "CZP-C-0002", "CZP-C-0006", "CZP-C-0007", "CZP-C-0008", "CZP-C-0010", "CZP-C-0011"],
            human("Assembly of the A, C-ball and C-human pieces as in the paper, sections 3 and 4.")),
        rec("CZP-C-0013", "C", "argument",
            "C-human, extra hypotheses. Lap E_zp(rho) <= B_hi/2 = -0.92078 < 0, valid only if E is C^2 at t = 0, E_zp is of class C^2 near rho, and rho is critical with isotropic Hessian (both by the order-3 stabilizer; P2 section 3.1, itself Tier C), via E''(0) = 2 Lap E_zp(rho). One-sided; P2's Tier X value is -3.848.",
            ["CZP-C-0012", "CZP-C-0011"], human("CERTIFIED_CURVATURE.md section 2.6")),
        # ---------------------------------------------------------------- X
        rec("CZP-X-0001", "X", "numeric",
            "Floating-point cross-checks (never supporting a claim): Gauss-Legendre (N=64) U''(0) = -1.923973 inside the enclosure; finite differences of U give -1.92383; E''(0) = -7.696 against 2 x (-3.848) from P2; E(h) - E(-h) = 0.0 to all printed digits; closed-form H'' vs finite differences max abs difference 7e-7. The b2_explore2.py run log is not in the bundle (output quoted from CERTIFIED_CURVATURE.md).",
            ["CZP-C-0009"], num(["CERTIFIED_CURVATURE.md", "result.json"], "source text of CERTIFIED_CURVATURE.md only; the exploratory log was not archived")),
        rec("CZP-X-0002", "X", "numeric",
            "Repository guards at the time of the B2 run: antigravity_guard.py FAILS (hollow tests in tests/test_k3_anse_improvements.py and tests/test_scientific_rigor_v14.py; hallucinated-import reports for packages not installed in the venv) and test_rigor_guard.py FAILS (stub detection). These failures are in files this paper does not touch; the outputs are archived verbatim.",
            [], num(["guard_antigravity.txt", "guard_test_rigor.txt"], "verbatim guard outputs")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
