"""Build the Elenchus claim ledger for the N2 paper (papers/p3_zero_point_physical).

Modelled on papers/p2_certified_zero_point/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not be filed above
anything in its depends_on. C-ball and C-human are both Tier C in the ledger; the evidence blob carries a "subtier" field.
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
TOOLCHAIN = ("Lean 4.34.1 + Mathlib through scripts/certified_numerics/lean_pinned.py (modules import Programmes.ZeroPointCert.Basic, "
             "Programmes.ZeroPointPhys.Taylor and Mathlib submodules; no import Mathlib)")
ALLOW = ["propext", "Classical.choice", "Quot.sound"]
STATUS = ("producer-checked by the N2 lane; independent AI-agent audit (papers/p3_zero_point_physical/AUDIT.md, ACCEPT_WITH_CORRECTIONS) "
          "recorded; leanchecker replay rc 0 (data/leanchecker_replay.json); no human audit of statement adequacy; no statement lock")
AI_AUDIT = {"auditor": "independent AI audit agent (producer != verifier), 2026-10-26", "human": False,
            "report": "papers/p3_zero_point_physical/AUDIT.md", "verdict": "ACCEPT_WITH_CORRECTIONS",
            "kernel_replay": "papers/p3_zero_point_physical/data/leanchecker_replay.json (Taylor, Basic, ZeroPointCert.Basic: rc 0)",
            "note": "AI audit, not a person: the gate field audit is left null so LEDGER_UNAUDITED_TIER_A stays open; no statement lock"}


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
    return {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
            "depends_on": depends, "evidence": blob(ev), "audit": None}
    if tier == "A":
        r["ai_audit"] = AI_AUDIT


LT = json.loads((DATA / "lean_taylor.json").read_text())
LB = json.loads((DATA / "lean_basic.json").read_text())
LC = json.loads((DATA / "lean_controls.json").read_text())


def axl(names: list[str], j: dict) -> list[str]:
    lines = [l.strip() for l in j["output"].split("\n") if any(f"'ProgZeroPointPhys.{n}' " in l for n in names)]
    if len(lines) != len(names):
        raise SystemExit(f"axiom lines missing for {names}: {lines}")
    return lines


def lean_ev(names: list[str], j: dict, jf: str, srcs: list[str]) -> dict:
    return {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output": axl(names, j), "allowlist": ALLOW,
            "compile_transcript": fref(DATA / jf), "sources": [fref(LEAN / s) for s in srcs], "status": STATUS,
            "statement_adequacy": "not audited by a human"}


def ball(files: list[str], note: str) -> dict:
    return {"kind": "argument", "subtier": "C-ball", "note": note, "files": [fref(DATA / f) for f in files],
            "instrument": "data/code/n2_certify.py, python-flint 0.6.0 (Arb ball arithmetic, 80 bits), outward rounded; not kernel-checked"}


def human(text: str, sec: str) -> dict:
    return {"kind": "argument", "subtier": "C-human", "text": text, "source_note": fref(DATA / "CERTIFICATES.md"), "where": sec}


def num(files: list[str], note: str) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True, "note": note, "files": [fref(DATA / f) for f in files]}


def lf_axioms() -> list[str]:
    """Verbatim axiom lines from the LeanFlow output_excerpt of the three verified certificates."""
    out: list[str] = []
    for n in ("yuk1", "yuk2", "gauss1"):
        j = json.loads((DATA / f"leanflow_cert_{n}.json").read_text())
        out += [f"{n}: {l.strip()}" for l in j["output_excerpt"].split("\n") if "axioms" in l]
    if len(out) != 12:
        raise SystemExit(f"unexpected LeanFlow axiom lines: {out}")
    return out


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    c = [
        rec("PZP-A-0001", "A", "lean_axioms",
            "ProgZeroPointPhys.second_diff_le_of_deriv2_le: if f has derivative f1 and f1 has derivative f2 at every point of [-t,t], t >= 0, and f2 <= K there, then f t + f (-t) - 2 f 0 <= t^2 K.",
            [], lean_ev(["second_diff_le_of_deriv2_le"], LT, "lean_taylor.json", ["Taylor.lean"])),
        rec("PZP-A-0002", "A", "lean_axioms",
            "ProgZeroPointPhys.window_of_deriv2, not_localMin_of_window_cert, not_localMin_of_deriv_cert: if E <= U on |t| <= t0, U 0 = E 0, U has derivative U1 and U1 has derivative U2pp on |t| <= t0 with U2pp <= M <= M_hi < 0, and E(-t) = E(t), then E is not locally minimal at 0 and E t < E 0 for 0 < t <= t0.",
            ["PZP-A-0001"], lean_ev(["window_of_deriv2", "not_localMin_of_window_cert", "not_localMin_of_deriv_cert"], LB, "lean_basic.json", ["Basic.lean"])),
        rec("PZP-A-0003", "A", "lean_axioms",
            "ProgZeroPointPhys.yuk1_cert and yukawa1_not_localMin_of_certificate: for the rational yuk1_M_hi = -1018521206953/500000000000 the four inequalities M_hi < 0, lmin_lo > 0, lminu_lo > 0, qpd_lo > 0 hold, and the conditional assembly (hypotheses = the non-kernel-checked inputs) concludes not IsLocalMin E 0 and E t < E 0 on 0 < t <= 1/100000. That the endpoints enclose the stated integrals is NOT part of this claim (see PZP-C-0002). The positivity rationals lmin_lo, lminu_lo, qpd_lo are proved positive but are not consumed by the assembled theorem (it uses only yuk1_cert.1; positivity enters through the hypothesis hEU); they were rounded to nearest via float() in the certifier, not outward, with margins >= 0.57.",
            ["PZP-A-0002"], lean_ev(["yuk1_cert", "yukawa1_not_localMin_of_certificate"], LB, "lean_basic.json", ["Basic.lean"])),
        rec("PZP-A-0004", "A", "lean_axioms",
            "ProgZeroPointPhys.yuk2_cert and yukawa2_not_localMin_of_certificate: same as PZP-A-0003 for yuk2_M_hi = -1868541510831/10^12 (kappa = 2). The endpoint-enclosure fact is PZP-C-0001. As in PZP-A-0003, the three positivity rationals are not consumed by the assembled theorem.",
            ["PZP-A-0002"], lean_ev(["yuk2_cert", "yukawa2_not_localMin_of_certificate"], LB, "lean_basic.json", ["Basic.lean"])),
        rec("PZP-A-0005", "A", "lean_axioms",
            "ProgZeroPointPhys.gauss1_cert and gauss1_not_localMin_of_certificate (positive control, Gaussian a = 1): gauss1_M_hi = -357889170157/(5*10^10) < 0 and the conditional assembly.",
            ["PZP-A-0002"], lean_ev(["gauss1_cert", "gauss1_not_localMin_of_certificate"], LB, "lean_basic.json", ["Basic.lean"])),
        rec("PZP-A-0006", "A", "lean_axioms",
            "ProgZeroPointPhys.not_certifiable_of_lo_pos and gauss2_not_certifiable (negative control, Gaussian a = 2): from M >= gauss2_M_lo = 172480128863/(5*10^10) > 0 one cannot have M < 0, so no negative window constant can be certified from the a = 2 enclosure.",
            [], lean_ev(["not_certifiable_of_lo_pos", "gauss2_not_certifiable"], LB, "lean_basic.json", ["Basic.lean"])),
        rec("PZP-A-0007", "A", "lean_axioms",
            "LeanFlow lean.certify (unmodified): the endpoint claims (M.hi < 0, lmin.lo > 0, lminu.lo > 0, qpd.lo > 0) of the Yukawa kappa = 1, kappa = 2 and Gaussian a = 1 runs are verified (status ok, tier A for the arithmetic statement only, axiom lists empty); the Gaussian a = 2 claim is rejected (false-statement, cert_0). Arithmetic about the stated numbers, not their provenance.",
            [], {"kind": "lean_axioms", "toolchain": "Lean 4.34.1 (LeanFlow lean.certify)",
                 "axiom_output": lf_axioms(),
                 "allowlist": ALLOW, "compile_transcript": fref(DATA / "leanflow_cert_yuk1.json"),
                 "other_transcripts": [fref(DATA / "leanflow_cert_yuk2.json"), fref(DATA / "leanflow_cert_gauss1.json"), fref(DATA / "leanflow_cert_gauss2.json")],
                 "sources": [fref(DATA / "leanflow_claim_yuk1.json"), fref(DATA / "leanflow_claim_yuk2.json"), fref(DATA / "leanflow_claim_gauss1.json"), fref(DATA / "leanflow_claim_gauss2.json")],
                 "status": STATUS, "statement_adequacy": "not audited by a human"}),
        rec("PZP-A-0008", "A", "lean_axioms",
            "Planted controls are caught: ctl_sorry depends on sorryAx and ctl_axiom on the planted axiom ProgZeroPointPhysCtl.ctl_cheat although Controls.lean compiles with rc 0; the kernel rejects (rc 1, goal False) the false claim that the a = 2 upper endpoint 4463084749303/10^12 is negative (RejectGauss2.lean).",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": [l.strip() for l in LC["output"].split("\n") if "ctl_sorry'" in l or "ctl_axiom'" in l],
                 "allowlist": ALLOW, "compile_transcript": fref(DATA / "lean_controls.json"),
                 "rejections": [fref(DATA / "lean_reject_gauss2.json")],
                 "sources": [fref(LEAN / "Controls.lean"), fref(LEAN / "RejectGauss2.lean")], "status": STATUS,
                 "statement_adequacy": "not audited by a human"}),
        # ---------------------------------------------------------------- C-ball
        rec("PZP-C-0001", "C", "argument",
            "C-ball. Yukawa kappa = 2 (V = e^{-2r}/r), shear path, t0 = 1e-5: 26,714 cells (6,174 refined), 0 failed, 273 lattice pairs, tails explicit; the window curvature bound M = sup_{|u|<=t0} (1/4) int f_kappa''(u) dkappa is enclosed in [-3.21751, -1.86854], M_hi = -1868541510831/10^12 < 0.",
            [], ball(["runs/o2_y2_N64.json", "runs/o2_y2_N64.log"], "Arb enclosures; cell rule, Duffy map and tails are not kernel-checked")),
        rec("PZP-C-0002", "C", "argument",
            "C-ball. Yukawa kappa = 1 (V = e^{-r}/r), same settings: 59,867 cells (17,225 refined), 0 failed, 1,173 lattice pairs; M in [-4.16483, -2.03704], M_hi = -1018521206953/(5*10^11) < 0. The run is the exact merge of two disjoint s-index halves computed on separate cores.",
            [], ball(["runs/o2_y1_merged.json", "runs/y1_partA.json", "runs/y1_partB.json"], "Arb enclosures; merge by data/code/n2_merge.py")),
        rec("PZP-C-0003", "C", "argument",
            "C-ball. Positivity on every cell and every |u| <= t0: det B_u > 0 and tr B_u > 0 (lambda_min lower bound lminu_lo = 0.8748 for kappa = 1, 0.6753 for kappa = 2), and det(Q + u Yt) > 0, tr > 0 (qpd_lo = 0.6633, 0.5739): the strained lattices are dynamically stable and X_u = D_0^{1/2} + uY is positive definite, so the majorant inequality applies.",
            [], ball(["runs/o2_y1_merged.json", "runs/o2_y2_N64.json"], "positivity margins from the same two runs")),
        rec("PZP-C-0004", "C", "argument",
            "C-ball. B2's linear-response majorant fails here, rigorously for Yukawa: the enclosures of U_lin''(0) are [2.39298, 2.46426] (kappa = 1) and [2.68830, 2.72310] (kappa = 2), both > 0, although the window curvature bound M of the moving-matrix majorant is negative.",
            ["PZP-C-0001", "PZP-C-0002"], ball(["runs/o2_y1_merged.json", "runs/o2_y2_N64.json"], "U_lin'' field of the run files")),
        rec("PZP-C-0005", "C", "argument",
            "C-ball. Controls through the same certifier (sha256 6fa38af9...): Gaussian a = 1 positive control certified, M in [-8.23325, -7.15778]; Gaussian a = 2 negative control M in [+3.44960, +4.46308], not certified. U_lin''(0) of the new code, [-1.93965, -1.90847] (a = 1) and [12.7109, 12.7393] (a = 2), lies inside B2's independent enclosures [-1.94771, -1.90017] and [12.69365, 12.75701].",
            ["PZP-A-0006"], ball(["runs/o2_g1_N64d1.json", "runs/negctl_g2_N64.json"], "controls")),
        rec("PZP-C-0006", "C", "argument",
            "C-ball. The E(0) enclosures contain P2's spectral E_zp: Yukawa 1 [1.765657, 1.766136] contains 1.7658983; Yukawa 2 [1.459124, 1.459391] contains 1.4592747; Gaussian 1 [1.503147, 1.503478] contains 1.50335235; Gaussian 2 [0.541863, 0.541967] contains 0.5419325.",
            [], ball(["runs/o2_y1_merged.json", "runs/o2_y2_N64.json", "runs/o2_g1_N64d1.json", "runs/negctl_g2_N64.json"], "E0 field of each run")),
        # ---------------------------------------------------------------- C-human
        rec("PZP-C-0007", "C", "argument",
            "C-human. Moving comparison matrix: with X = D_0^{1/2}, Y solving XY + YX = D_0' and X_t = X + tY positive definite on the window (PZP-C-0003), the pointwise 2x2 inequality 2 tr D_t^{1/2} <= tr X_t + tr(X_t^{-1} D_t) holds (B2's Lean lemma two_trace_le_of_inverse with X := X_t); integrating, E <= U2 on |t| <= t0, and U2(0) = E(0) by the equality case.",
            ["PZP-C-0003"], human("Apply B2's pointwise lemma at each kappa != 0 with S = D_t^{1/2}, X := X_t; integrate.", "CERTIFICATES.md section 1")),
        rec("PZP-C-0008", "C", "argument",
            "C-human. U2''(0) = E''(0) exactly: S_t = D_t^{1/2} has S_0 = X and S_0' = Y (differentiate S^2 = D), so X_t is the tangent line of S_t, S_t - X_t = O(t^2) and the pointwise gap tr(X_t^{-1}(S_t - X_t)^2) is O(t^4); equivalently f'' = tr(X^{-1}D'') - 2 tr(X^{-1}Y^2) = 2 tr S'' at t = 0. Hence U_lin''(0) - E''(0) = (1/2) int tr(X^{-1}Y^2) >= 0.",
            ["PZP-C-0007"], human("Derivation in section 3 of the paper; the integral version needs the Duffy scaling D = s^2 B near Gamma.", "CERTIFICATES.md section 1")),
        rec("PZP-C-0009", "C", "argument",
            "C-human. Differentiation under the integral sign: U2 is twice differentiable on |t| <= t0 with U2''(u) = (1/4) int f_kappa''(u) dkappa, because the integrand and its first two t-derivatives are bounded on cells x window (the Arb run bounds them). The Lean hypotheses hd1/hd2 at u = +-t0 need U2 differentiable on a neighbourhood of +-t0; the checks cover only the closed window, and the gap is closed by continuity since the margins are strict (stated, not separately certified).",
            ["PZP-C-0001", "PZP-C-0002"], human("Dominated convergence on the Duffy cells; bounds from the same Arb run.", "CERTIFICATES.md section 3")),
        rec("PZP-C-0010", "C", "argument",
            "C-human. Mirror symmetry E(-t) = E(t) for every radial V (sigma = diag(1,-1) maps L_rho to itself and sigma P_t sigma = P_{-t}); and the shape statement tau(t) = rho + sqrt3 t + O(t^2), so E(t) < E(0) for small t != 0 means rho is not a local minimum over lattice shapes.",
            [], human("As B2 steps 4 and 8.", "CERTIFICATES.md section 3; B2 paper")),
        rec("PZP-C-0011", "C", "argument",
            "C-human. Isotropy: the Hessian of E_zp over lattice shapes at rho is isotropic (order-3 stabilizer, P2 3.1), so E''(0) is independent of the strain direction and, since U2'' = E'' at 0, the shear path loses nothing for any potential; valid only if E_zp is C^2 at rho and for paths with equal |tau'(0)|. Not used by the headline.",
            ["PZP-C-0008"], human("Stabilizer argument of P2 section 3.1 (Tier C there).", "CERTIFICATES.md section 1")),
        rec("PZP-C-0012", "C", "argument",
            "HEADLINE (C): for the planar Yukawa potentials e^{-kappa r}/r, kappa = 1 and 2, with E the harmonic zero-point energy of the unit-covolume lattices L_t = P_t L_rho (hbar = m = 1), E(t) < E(0) for every 0 < |t| <= 1e-5, E has no local minimum at t = 0, and the triangular lattice is not a local minimum of the zero-point energy over lattice shapes. Tier A part: the logic and the rational arithmetic (PZP-A-0001..0004, 0007); tier C-ball: PZP-C-0001..0003; tier C-human: the glue.",
            ["PZP-A-0003", "PZP-A-0004", "PZP-A-0007", "PZP-C-0001", "PZP-C-0002", "PZP-C-0003", "PZP-C-0007", "PZP-C-0008", "PZP-C-0009", "PZP-C-0010"],
            human("Assembly of the A, C-ball and C-human pieces as in sections 3 to 5 of the paper.", "paper sections 3-5")),
        rec("PZP-C-0013", "C", "argument",
            "C-human, extra hypotheses (E twice differentiable at 0, E_zp of class C^2 near rho, rho critical with isotropic Hessian, |tau'(0)|^2/y^2 = 4): Lap E_zp(rho) = E''(0)/2 lies in [-2.0824, -1.0185] (kappa = 1) and [-1.6088, -0.9343] (kappa = 2); Gaussian a = 1 [-4.1166, -3.5789]; Gaussian a = 2 [+1.7248, +2.2315]. Two-sided, but conditional.",
            ["PZP-C-0001", "PZP-C-0002", "PZP-C-0005", "PZP-C-0008", "PZP-C-0011"], human("Enclosure of U2''(0) = E''(0) halved.", "CERTIFICATES.md section 5, by-product")),
        # ---------------------------------------------------------------- X
        rec("PZP-X-0001", "X", "numeric",
            "Tier X curvatures E''(0) (finite differences, N 32, real-space cutoff 40): Yukawa 1 -3.107, Yukawa 2 -2.549, Gaussian 1 -7.699, Gaussian 2 +3.944, Riesz 3 -2.439, Riesz 4 +2.754, Riesz 6 +27.24, dipolar d=0.1 -2.616, d=0.5 -4.767; B2's U_lin''(0) is positive for all six physical potentials (Yukawa +2.43/+2.71, Riesz 3 +17.1, Riesz 4 +33.2, dipolar +16.6/+9.3). Riesz 3 and dipolar values unchanged at cutoff 100. Never supports a claim.",
            [], num(["tierx_scan_rc40.txt", "tierx_scan_rc100.txt"], "scan output of data/code/n2_explore.py")),
        rec("PZP-X-0002", "X", "numeric",
            "Riesz 3 tail obstacle (floating-point evaluation of the shell bound of data/code/n2_riesz3_tail.py): tail bound of the entries of B over the annulus [Rc, 2Rc) is at least 818, 291, 140, 68.6, 34.0 for Rc = 10, 25, 50, 100, 200 (about 6800/Rc), against lambda_min(B) >= 3.8 (Tier X, 0.39 x (2 pi)^2 / 4). The shell bound as used for Yukawa therefore cannot certify r^-3 at a feasible cutoff. Evidence for an obstacle, not a theorem.",
            [], num(["riesz3_tail_obstacle.txt"], "verbatim output")),
        rec("PZP-X-0003", "X", "numeric",
            "Repository guards at writing: antigravity_guard.py rc 1, test_rigor_guard.py rc 1, pytest tests/ rc 2 (28 collection errors), all on pre-existing files; archived verbatim. No N2 file is cited.",
            [], num(["guard_antigravity.txt", "guard_test_rigor.txt", "pytest_tests.txt"], "verbatim outputs")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
