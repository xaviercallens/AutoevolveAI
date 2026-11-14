"""Build the Elenchus claim ledger for the M1 paper (papers/p4_zero_point_dipolar).

Modelled on papers/p3_zero_point_physical (N2) and papers/p4_yukawa_bcc_fcc_check. Tier discipline (tools/ledger.py): a claim may not be
filed above anything in its depends_on, and the kind caps the tier (lean_axioms A, citation L, argument C, numeric X).
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
TOOLCHAIN = ("Lean 4.34.1 + Mathlib through scripts/certified_numerics/lean_pinned.py (modules import Mathlib.Tactic and "
             "Programmes.ZeroPointPhys.Basic; no import Mathlib)")
ALLOW = ["propext", "Classical.choice", "Quot.sound"]
STATUS = ("producer-checked by the M1 lane; leanchecker replay rc 0 for Programmes.ZeroPointDipolar.Basic (data/replay.json, run by the "
          "producer, default mode, imports trusted); an independent AI audit (separate agent instance, producer != verifier, AUDIT.md, ACCEPT_WITH_CORRECTIONS) re-ran the kernel replay (leanchecker rc 0, five modules) "
          "and recomputed E(0), E''(0) by two independent Tier X methods but did NOT independently re-derive the M enclosures; no human audit exists; no statement lock")
ADEQ = ("AI-audited (AUDIT.md) but not by any person; the final theorems are conditional on the non-kernel inputs (hEU, h0, hd1, hd2, hK, hM, hsym), "
        "which are the Tier C inputs of the paper")
SRC_COMMIT = "28a1ac0b8d53e59d489b8e5821c956c395ff0729 (contains the 46 M1 result/code files and the three Lean files; paper committed later in 4094011)"
AI_AUDIT = {"auditor": "independent AI audit agent (separate instance, producer != verifier), 2026-10-28", "human": False,
            "report": "papers/p4_zero_point_dipolar/AUDIT.md", "verdict": "ACCEPT_WITH_CORRECTIONS",
            "scope": "own brute-force and Ewald numerics (Tier X) agree with all seven enclosures; own Lean rebuild, leanchecker rc 0 on five modules; escape-hatch grep",
            "not_scope": "did NOT independently re-derive the M enclosures (producer Tier C-ball, depends on N2 certifier)",
            "note": "AI audit, not a person: the gate field audit is left null so LEDGER_UNAUDITED_TIER_A stays open; no statement lock"}
CERT_SHA = "360ebbcbb9b958ee6eefbc3a03f07856800b1a88dfb9984c4ade8edc2811b929"


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



def axioms_from(path: Path, names: list[str]) -> list[str]:
    out = json.loads(path.read_text())["output"]
    flat = out.replace("\n", " ")
    lines: list[str] = []
    for n in names:
        i = flat.find(f"'{n}'")
        if i < 0:
            raise SystemExit(f"axiom line missing for {n}")
        j = flat.find("]", i)
        lines.append(" ".join(flat[i:j + 1].split()))
    return lines


def lean_ev(names: list[str], srcs: list[str]) -> dict:
    return {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
            "axiom_output": axioms_from(DATA / "lean_basic.json", ["ProgZeroPointDipolar." + n for n in names]),
            "allowlist": ALLOW, "compile_transcript": fref(DATA / "lean_basic.json"),
            "sources": [fref(LEAN / s) for s in srcs],
            "leanchecker_replay": fref(DATA / "replay.json"),
            "grep_scan": fref(DATA / "grep.json"),
            "status": STATUS, "statement_adequacy": ADEQ}


def cite(source: str, where: str, text: str) -> dict:
    return {"kind": "citation", "source": source, "where": where, "text": text,
            "note": "own predecessor preprint, taken as stated; not re-proved or re-audited here"}


def arg(subtier: str, text: str, files: list[Path], instrument: str) -> dict:
    return {"kind": "argument", "subtier": subtier, "text": text, "files": [fref(f) for f in files],
            "instrument": instrument, "source_commit": SRC_COMMIT, "certifier_sha256": CERT_SHA}


def num(files: list[Path], note: str) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True, "note": note,
            "files": [fref(f) for f in files]}


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    d = DATA / "data"
    runs = [d / f for f in ["riesz3.json", "dipolar_d0.1.json", "dipolar_d0.5.json", "dipolar_da0.06.json", "dipolar_da0.09.json",
                            "dipolar_da0.1.json", "dipolar_da0.5.json"]]
    res = DATA / "result.json"
    c = [
        rec("ZPD-A-0001", "A", "lean_axioms",
            "ProgZeroPointDipolar.riesz3_cert: riesz3_M_hi = -1663096717477/10^12 < 0 and the three positivity rationals are > 0; "
            "ProgZeroPointDipolar.riesz3_not_localMin_of_certificate: for any E, U, U1, U2pp, M with E <= U and U(0) = E(0) on |t| <= t0, "
            "U'' = U2pp <= M <= riesz3_M_hi and E(-t) = E(t), E is not a local minimum at 0 and E t < E 0 for 0 < t <= t0 (conditional on those "
            "hypotheses, which are the non-kernel inputs). Reuses N2's not_localMin_of_deriv_cert.",
            [], lean_ev(["riesz3_cert", "riesz3_not_localMin_of_certificate"], ["Basic.lean"])),
        rec("ZPD-A-0002", "A", "lean_axioms",
            "The same two statements for the bilayer point dipole at d = 1/10 (dip01_M_hi = -925923850457/(5*10^11)) and d = 1/2 "
            "(dip05_M_hi = -4115980950373/10^12): dip01_cert, dipolar01_not_localMin_of_certificate, dip05_cert, dipolar05_not_localMin_of_certificate.",
            [], lean_ev(["dip01_cert", "dipolar01_not_localMin_of_certificate", "dip05_cert", "dipolar05_not_localMin_of_certificate"],
                        ["Basic.lean"])),
        rec("ZPD-A-0003", "A", "lean_axioms",
            "The same two statements for the four preregistered ratios d/a = 0.06, 0.09, 0.1, 0.5 (rational d = 129/2000, 967/10000, 1075/10000, 5373/10000): "
            "dipA006, dipA009, dipA01, dipA05 _cert and dipolarA006, dipolarA009, dipolarA01, dipolarA05 _not_localMin_of_certificate.",
            [], lean_ev(["dipA006_cert", "dipolarA006_not_localMin_of_certificate", "dipA009_cert", "dipolarA009_not_localMin_of_certificate",
                         "dipA01_cert", "dipolarA01_not_localMin_of_certificate", "dipA05_cert", "dipolarA05_not_localMin_of_certificate"],
                        ["Basic.lean"])),
        rec("ZPD-A-0004", "A", "lean_axioms",
            "Lean controls: Controls.lean compiles with rc 0 (warning: declaration uses sorry); m1_gauss2_not_certifiable prints only the allowlist; "
            "the planted ctl_sorry prints sorryAx and the planted ctl_axiom prints ProgZeroPointDipolarCtl.ctl_cheat in #print axioms, so the axiom gate "
            "catches both. RejectGauss2.lean (claim M_hi(Gaussian a=2) = 4463084749303/10^12 < 0) fails to compile, rc 1, unsolved goals False. "
            "leanchecker Programmes.ZeroPointDipolar.Basic rc 0 (producer-run). Grep for skipKernelTC|addDecl|native_decide|implemented_by|implementedBy: 0 hits.",
            [],
            {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
             "axiom_output": axioms_from(DATA / "lean_controls.json",
                                         ["ProgZeroPointDipolarCtl.m1_gauss2_not_certifiable", "ProgZeroPointDipolarCtl.ctl_sorry",
                                          "ProgZeroPointDipolarCtl.ctl_axiom"]),
             "allowlist": ALLOW, "compile_transcript": fref(DATA / "lean_controls.json"),
             "rejections": [fref(DATA / "lean_reject_gauss2.json")],
             "sources": [fref(LEAN / s) for s in ["Controls.lean", "RejectGauss2.lean"]],
             "leanchecker_replay": fref(DATA / "replay.json"), "grep_scan": fref(DATA / "grep.json"),
             "status": STATUS, "statement_adequacy": ADEQ,
             "note": "the sentinel lines for ctl_sorry and ctl_axiom are the verbatim #print axioms output; they show the gate CATCHES the planted sorry and axiom"}),
        # ------------------------------------------------------------------ L
        rec("ZPD-L-0001", "L", "citation",
            "N2 (doi:10.5281/zenodo.23663551): the setting (E(t) along P_t L_rho, unit covolume), the moving comparison matrix and majorant U2 with U2''(0) = E''(0), "
            "the Duffy-cell certifier n2_certify.py (sha256 6fa38af9...), the shell tail lemma, the Lean window lemmas of Programmes.ZeroPointPhys.Basic, "
            "the glue (E <= U2 integrated, differentiation under the integral, mirror symmetry), and the report that Riesz s=3 and the dipolar potentials "
            "were not certified because of the r^-3 real-space tail. B2 (doi:10.5281/zenodo.23655392): the 2x2 trace inequality and Programmes.ZeroPointCert.Basic.",
            [], cite("doi:10.5281/zenodo.23663551; doi:10.5281/zenodo.23655392", "N2 Sections 3-5 and 7; B2 Lean module",
                     "Own predecessor preprints (N2, B2); statements pinned as stated; the same author, so not an independent source")),
        # ------------------------------------------------------------------ C
        rec("ZPD-C-0001", "C", "argument",
            "Arb enclosures of the window curvature M (python-flint 0.6.0, 80 bits, N 64, depth 2, tol 0.5, Qmax 300, alpha 1/10, t0 1e-5) for seven potentials, all with "
            "M_hi < 0 and no failed cell: Riesz r^-3 [-3.17029,-1.66310]; dipole d=1/10 [-3.33620,-1.85185]; d=1/2 [-5.38812,-4.11598]; d=129/2000 (d/a 0.06) "
            "[-3.23699,-1.74649]; d=967/10000 (0.09) [-3.32496,-1.84069]; d=1075/10000 (0.1) [-3.36115,-1.88023]; d=5373/10000 (0.5) [-5.49473,-4.24958]. "
            "The Tier X E''(0) (-2.439, -2.616, -4.767, -2.51419, -2.60506, -2.64284, -4.88677) lies inside each. Positivity (det B_u > 0, X_u positive definite) passed on every cell. "
            "Not kernel-checked.",
            ["ZPD-L-0001", "ZPD-C-0002"], arg("C-ball", "data/data/{riesz3,dipolar_d0.1,dipolar_d0.5,dipolar_da0.06,dipolar_da0.09,dipolar_da0.1,dipolar_da0.5}.json",
                                              runs, "python-flint 0.6.0 (Arb); data/code/m1_certify.py with N2's n2_certify.py imported unchanged")),
        rec("ZPD-C-0002", "C", "argument",
            "The Ewald split certificate: r^-3 and the dipole as Gaussian mixtures split at alpha = 1/10 (the dipole mixture split as a whole). Short part in real space "
            "with incomplete-gamma closed forms (completely monotone, majorant C_j exp(-alpha q), q >= 1) and N2's shell tail lemma at Qmax 300 (r_tail 18.64, 537 half-lattice pairs; tail balls about 4e-11 on B, 1.1e-3 on the worst second partial). "
            "Long part in reciprocal space with the exact transform Vh_3(x) = 4 sqrt(pi alpha) exp(-x^2/(4 alpha)) - 2 pi x erfc(x/(2 sqrt alpha)); dipole series truncated at m = 6 with Cramer-Hermite remainder at most 6.8e-25 (d=1/10) and 4.3e-15 (d=1/2), 1.2e-14 (d=5373/10000); "
            "G0 = 0 term and (for s >= 1/4) the first shell exact; the rest by Cauchy-estimate balls on a polydisc (1/20, 1/20, 1/100), pairs summed to Q <= 400, balls at most 1.6e-10 on any entry or partial (recip_crude). "
            "Not kernel-checked; the producer run had no negative control of the reciprocal-space code (the independent AI audit added one, AUDIT.md).",
            ["ZPD-L-0001"], arg("C-ball", "tails and recip_crude fields of the run JSONs", runs, "python-flint 0.6.0 (Arb); data/code/m1_certify.py")),
        rec("ZPD-C-0003", "C", "argument",
            "E(0) enclosures contain the Tier X E_zp (N2 tierx scan, N = 32 Gauss-Legendre, rc 100): Riesz 3 [4.244723,4.245148] contains 4.2449758; d=1/10 [4.209378,4.209801] contains 4.2096272; "
            "d=1/2 [3.528270,3.528669] contains 3.5284909; d/a 0.06 [4.229936,4.230360] contains 4.2301863; 0.09 [4.211652,4.212075] contains 4.2119010; 0.1 [4.203939,4.204361] contains 4.2041875; "
            "0.5 [3.441988,3.442382] contains 3.4422047 (midpoints within 4e-5). U_lin''(0) (B2 majorant) enclosures [17.1055,17.1565], [16.6205,16.6720], [9.2313,9.2797] contain Tier X 17.131, 16.646, 9.256.",
            ["ZPD-C-0001"], arg("C-ball", "E0 and U_lin_pp0_B2_majorant fields of the run JSONs; data/data/tierx_extra_rc100.txt", runs + [d / "tierx_extra_rc100.txt"],
                                "python-flint 0.6.0; Tier X values from N2's n2_explore.py")),
        rec("ZPD-C-0004", "C", "argument",
            "Positive controls through the new certifier (certifier hash identical in all runs): Gaussian a=1 M in [-8.23325,-7.15778], Gaussian a=2 and Yukawa kappa=2 bit-identical rationals to N2; "
            "Yukawa kappa=1 (single run, same 59867 cells) [-4.16485,-2.03702] contains N2's [-4.16483,-2.03704] and is NOT bit-identical (endpoints differ by <= 3e-5; "
            "N2 merged two part runs, so the ball summation order differs). These run with the reciprocal part switched off: they validate the refactor, not the Ewald split.",
            ["ZPD-L-0001"], arg("C-ball", "ctl_gauss1/ctl_yukawa1/ctl_yukawa2/negctl_gauss2 run JSONs", [d / "ctl_gauss1.json", d / "ctl_yukawa1.json", d / "ctl_yukawa2.json", d / "negctl_gauss2.json"],
                                "python-flint 0.6.0; data/code/m1_compare_n2.py")),
        rec("ZPD-C-0005", "C", "argument",
            "Negative controls in the certifier: Gaussian a=2 gives M in [+3.44960,+4.46308] (M_lo > 0), not certified, bit-identical to N2. r^-3 without the split (riesz3direct, Qmax 300): "
            "the power-law Voronoi tail lemma returns +inf for every s-, t'-, ss-, st-, tt-partial (exponent >= -2) and B-tails 226 / 1885 / 24127 (k = 0,1,2) against lambda_min(B) >= 6.5 in the certified run; refused, no integration attempted.",
            ["ZPD-L-0001"], arg("C-ball", "negctl_gauss2.json, negctl_riesz3direct.json", [d / "negctl_gauss2.json", d / "negctl_riesz3direct.json"], "python-flint 0.6.0; data/code/m1_certify.py")),
        rec("ZPD-C-0006", "C", "argument",
            "Written glue, none machine-checked. Inherited from N2: E <= U2 after integration over kappa, U2''(0) = E''(0), differentiation under the integral sign, mirror symmetry E(-t) = E(t), "
            "tau(t) = rho + sqrt3 t + O(t^2), the cell rule remainder. New: the Gaussian-mixture representations and the split at alpha; Poisson summation for the long part on L_t including the non-analytic -2 pi |k| term; "
            "complete monotonicity and majorants of the short part; the Voronoi integral lemmas; the Cauchy-estimate argument with its numerically asserted monotonicity conditions; Cramer's Hermite bound for the dipole remainder. "
            "Read only by the producer.",
            ["ZPD-L-0001"], arg("C-human", "Sections 3 and 6 of the paper", [DATA / "RESULT.md"], "none (reading)")),
        rec("ZPD-C-0007", "C", "argument",
            "HEADLINE. For each of seven potentials (Riesz r^-3; dipole d = 1/10, 1/2; dipole d/a = 0.06, 0.09, 0.1, 0.5) E(t) < E(0) for 0 < |t| <= 1e-5 along P_t L_rho, so the triangular lattice is NOT a local minimum "
            "of the model's harmonic zero-point energy over lattice shapes (harmonic approximation, 2D Bravais, one path, local window, model units). The sign is negative for all seven: the hoped-for first certified positive "
            "(local minimum) statement for an r^-3 potential did NOT happen. Filed C because it combines Tier A logic with Tier C-ball enclosures and Tier C-human glue. "
            "NOT claimed: real excitons, devices, melting, a structural transition, instability of the crystal, any global statement.",
            ["ZPD-A-0001", "ZPD-A-0002", "ZPD-A-0003", "ZPD-C-0001", "ZPD-C-0002", "ZPD-C-0006"],
            arg("C-assembly", "Assembly of the rows above as in Sections 2 to 4 of the paper.", [res, DATA / "RESULT.md"], "none")),
        # ------------------------------------------------------------------ X
        rec("ZPD-X-0001", "X", "numeric",
            "Ewald-specific point checks (not a certificate): B from the Ewald balls agrees with an independent direct real-space float sum (Qmax 300, continuum tail) to <= 1e-6 at 6 points on both triangles; "
            "B1 and B2 differ from h = 1e-3 finite differences by up to 8e-3 and converge to the ball values as h -> 0; alpha = 1/10 and 1/6 give the same B to 6 decimals; "
            "the series path equals the closed form for Riesz 3.",
            [], num([d / "selfcheck_riesz3.json", d / "selfcheck_dipolar_d0.1.json", d / "selfcheck_dipolar_half.json", d / "selfcheck_riesz3series.json"], "data/code/m1_selfcheck.py, m1_fdcheck.py")),
        rec("ZPD-X-0002", "X", "numeric",
            "Lindemann ratios in model units (hbar = m = 1, amplitude 1, harmonic, T = 0, N 48, rc 100): eta / eta_m = 0.534 / 0.661 (Riesz 3), 0.535 / 0.662 (d/a 0.06), 0.536 / 0.664 (0.09), 0.537 / 0.664 (0.1), 0.598 / 0.740 (0.5). "
            "Model units only: no melting or transition claim.",
            [], num([d / "m1x_lindemann.txt"], "data/code/m1x_lindemann.py")),
        rec("ZPD-X-0003", "X", "numeric",
            "Repository guards were run and FAIL for reasons in files this lane did not touch: antigravity_guard.py rc 1 (hallucinated-import findings in pre-existing anse/, scripts/, tests/, papers/), "
            "test_rigor_guard.py rc 1 (hollow tests in pre-existing test files), pytest tests/ rc 1 (73 failed, 1674 passed, 50 skipped, 19 errors). Recorded so the state is explicit; none of these outputs supports a claim.",
            [], num([DATA / "logs" / "guard_antigravity.txt", DATA / "logs" / "guard_test_rigor.txt", DATA / "logs" / "pytest_tests.txt"], "verbatim guard outputs of the M1 lane")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
