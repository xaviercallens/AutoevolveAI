"""Build the Elenchus claim ledger for the N1 paper (papers/p3_zero_point_classification).

Modelled on papers/p3_zero_point_physical/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not be filed above
anything in its depends_on. C-ball and C-human are both Tier C in the ledger; the evidence blob carries a "subtier" field.
No independent audit exists yet (pending at writing): the ledger's audit field is null and no ai_audit field is recorded.
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
TOOLCHAIN = ("Lean 4.34.1 + Mathlib through scripts/certified_numerics/lean_pinned.py (modules import Programmes.ZeroPointCert.Basic "
             "and Mathlib submodules; no import Mathlib)")
ALLOW = ["propext", "Classical.choice", "Quot.sound"]
STATUS = ("producer-checked by the N1 lane; no independent audit yet (an independent AI audit is pending at the time of writing); "
          "leanchecker replay rc 0 for Programmes.ZeroPointClass.Basic only (data/kernel_replay_2026-10-26_replay.jsonl), "
          "none recorded for Cert; no human audit of statement adequacy; no statement lock")
PFX = "ProgZeroPointClass."


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def blob(obj: dict) -> str:
    raw = json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False).encode()
    d = sha(raw)
    EV.mkdir(parents=True, exist_ok=True)
    (EV / f"{d}.json").write_bytes(raw)
    return f"sha256:{d}"


def fref(rel: str) -> dict:
    p = DATA / rel
    return {"path": f"data/{rel}", "sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict) -> dict:
    return {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
            "depends_on": depends, "evidence": blob(ev), "audit": None}


def axiom_lines(jfile: str, names: list[str]) -> list[str]:
    j = json.loads((DATA / jfile).read_text())
    lines = [l.strip() for l in j["output"].split("\n") if any(f"'{PFX}{n}' " in l for n in names)]
    if len(lines) != len(names):
        raise SystemExit(f"axiom lines missing for {names} in {jfile}: {lines}")
    return lines


def lean_ev(jfile: str, names: list[str], srcs: list[str]) -> dict:
    return {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output": axiom_lines(jfile, names), "allowlist": ALLOW,
            "compile_transcript": fref(jfile), "sources": [fref(f"lean/{s}") for s in srcs], "status": STATUS,
            "statement_adequacy": "not audited by a human"}


def ball(files: list[str], note: str) -> dict:
    return {"kind": "argument", "subtier": "C-ball", "note": note, "files": [fref(f) for f in files],
            "instrument": "data/code/n1_certify2.py (python-flint 0.6.0, Arb ball arithmetic, 96 bits, outward rounded); not kernel-checked"}


def human(text: str, sec: str) -> dict:
    return {"kind": "argument", "subtier": "C-human", "text": text, "source_note": fref("CLASSIFICATION.md"), "where": sec}


def num(files: list[str], note: str) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True, "note": note, "files": [fref(f) for f in files]}


SEG_NEG = ["runs/sweep_inside_ext.json", "runs/sweep_inside_ext2.json", "runs/sweep_inside_ext3.json", "runs/sweep_inside_ext4.json",
           "runs/sweep_inside_ext5.json", "runs/sweep_inside_mid.json", "runs/sweep_inside_hi.json", "runs/sweep_near_ap_inside.json",
           "runs/sweep_ap_tight.json", "runs/sweep_near_am_inside.json"]
SEG_POS = ["runs/sweep_near_ap_right.json", "runs/sweep_right_kept.json", "runs/sweep_right2.json"]
THIN = ["runs/sweep_left_pts.json", "runs/sweep_pts_extra.json", "runs/sweep_pts_extra2.json", "runs/sweep_am_tight.json",
        "runs/sweep_near_am_inside.json"]
CTL = ["runs/ctl_straddle.json", "runs/ctl_straddle_am.json"]


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    c = [
        rec("PZC-A-0001", "A", "lean_axioms",
            "ProgZeroPointClass.window_upper, window_lower, not_localMin_of_curv_neg, strict_gt_of_curv_pos: if E has derivative E' and E' has derivative F on [-t0, t0], F <= B there, then E t + E(-t) - 2 E 0 <= B t^2 (>= for F >= B, convex twin); with E(-t) = E(t) and B < 0, E is not locally minimal at 0 and E t < E 0 for 0 < t <= t0; with B > 0, E 0 < E t for 0 < |t| <= t0.",
            [], lean_ev("lean_basic.json", ["window_upper", "window_lower", "not_localMin_of_curv_neg", "strict_gt_of_curv_pos"], ["Basic.lean"])),
        rec("PZC-A-0002", "A", "lean_axioms",
            "ProgZeroPointClass.covers_of_chain, mul_le_corners, corners_le_mul, Encloses.left/right, allPos_left/right, allNeg_left/right, rec_upper, rec_lower, neg_on_of_chain, pos_on_of_chain, pos_of_mem, neg_of_mem: a chainFrom list of rational a-intervals covers [A, B]; from Encloses (the affine enclosure F - (a - ac) d in [qlo, qhi], d in [dlo, dhi]) and the sign of qhi + cmax (resp. qlo + cmin), F has that sign on every a of the covered interval and on every |t| <= t0. The enclosure is a hypothesis, not proved.",
            ["PZC-A-0001"], lean_ev("lean_basic.json", ["covers_of_chain", "mul_le_corners", "corners_le_mul", "Encloses.left", "Encloses.right", "allPos_left", "allPos_right", "allNeg_left", "allNeg_right", "rec_upper", "rec_lower", "neg_on_of_chain", "pos_on_of_chain", "pos_of_mem", "neg_of_mem"], ["Basic.lean"])),
        rec("PZC-A-0003", "A", "lean_axioms",
            "ProgZeroPointClass.sign_pos, sign_neg, brackets_ordered, chain_pos0, chain_neg0 (decide +kernel on the generated Cert.lean): all 113 positive records of Lpos have 0 < qlo + cmin, all 84 negative records of Lneg have qhi + cmax < 0, the bracket points 749/2000 < 379/1000 < 1579/1000 < 1583/1000 are thin records, Lposseg0 chains 198/125 to 4 (103 records) and Lnegseg0 chains 17/40 to 1579/1000 (71 records). Arithmetic about the stated rationals; that they enclose F is PZC-C-0001..0004.",
            ["PZC-A-0002"], lean_ev("lean_cert.json", ["sign_pos", "sign_neg", "brackets_ordered", "chain_pos0", "chain_neg0"], ["Cert.lean"])),
        rec("PZC-A-0004", "A", "lean_axioms",
            "ProgZeroPointClass.segment_neg0 and segment_pos0: (Encloses F t0 Lneg) implies F a t < 0 for all a in [17/40, 1579/1000], |t| <= t0 = 1e-8; (Encloses F t0 Lpos) implies 0 < F a t for all a in [198/125, 4], |t| <= t0. Conditional on the C-ball enclosures.",
            ["PZC-A-0003"], lean_ev("lean_cert.json", ["segment_neg0", "segment_pos0"], ["Cert.lean", "Basic.lean"])),
        rec("PZC-A-0005", "A", "lean_axioms",
            "ProgZeroPointClass.root_in_gap, root_in_gap' (Basic) and classification (Cert): F > 0 on every record of Lpos, F < 0 on every record of Lneg, and, if a -> F a 0 is continuous on [0.3745, 0.379] and on [1.579, 1.583], it has a zero in (0.3745, 0.379) and one in (1.579, 1.583) (intermediate value theorem between certified-sign thin points). Conditional on the enclosures and on continuity. Uniqueness is not claimed.",
            ["PZC-A-0003"], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                             "axiom_output": axiom_lines("lean_basic.json", ["root_in_gap"]) + axiom_lines("lean_cert.json", ["classification"]),
                             "allowlist": ALLOW, "compile_transcript": fref("lean_cert.json"), "other_transcripts": [fref("lean_basic.json")],
                             "sources": [fref("lean/Cert.lean"), fref("lean/Basic.lean")], "status": STATUS, "statement_adequacy": "not audited by a human"}),
        rec("PZC-A-0006", "A", "lean_axioms",
            "ProgZeroPointClass.along_path, segment_neg0_path, segment_pos0_path: under the hypotheses hE (E a has derivative E' a on [-t0, t0]), hE' (E' a has derivative F a) and hsym (E a (-t) = E a t), for every a of a negative record (in particular all of [17/40, 1579/1000]) E a is not locally minimal at 0 and E a t < E a 0 for 0 < t <= t0, and for every a of a positive record (all of [198/125, 4]) E a 0 < E a t for 0 < |t| <= t0. The hypotheses are the C-human inputs PZC-C-0009, PZC-C-0010.",
            ["PZC-A-0001", "PZC-A-0004"], lean_ev("lean_cert.json", ["along_path", "segment_neg0_path", "segment_pos0_path"], ["Cert.lean", "Basic.lean"])),
        rec("PZC-A-0007", "A", "lean_axioms",
            "LeanFlow lean.certify (unmodified, commit 06084ef, decide_kernel): the 197 exact corner-bound sign claims are verified (status ok, code verified, tier A for the arithmetic statement only, all axiom reports standard, claim sha256 497f465a...); a copy with the first sign planted false is rejected (false-statement, failed cert_0). Arithmetic about the stated numbers, not their provenance.",
            [], {"kind": "lean_axioms", "toolchain": "Lean 4.34.1 (LeanFlow lean.certify)", "axiom_output": ["leanflow_result_exact: message 'compiled with rc 0; all axiom reports STANDARD'"],
                 "allowlist": ALLOW, "compile_transcript": fref("leanflow/leanflow_result_exact.json"),
                 "other_transcripts": [fref("leanflow/leanflow_result_planted.json")],
                 "sources": [fref("leanflow/leanflow_claim_exact.json"), fref("leanflow/leanflow_claim_planted.json")],
                 "status": STATUS, "statement_adequacy": "not audited by a human"}),
        rec("PZC-A-0008", "A", "lean_axioms",
            "Controls are caught: ctl_sorry depends on sorryAx and ctl_axiom on the planted axiom ProgZeroPointClass.ctl_cheat although Controls.lean compiles with rc 0 (honest ctl_false standard); the kernel rejects (rc 1) the real a = 2/5 record claimed all-positive (RejectInside.lean) and a real a = 93/250 record with qlo sign flipped (RejectTampered.lean); Honest.lean proves inside_not_pos, inside_is_neg, tampered_not_pos, untampered_pos with standard axioms.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": [l.strip() for l in json.loads((DATA / "lean_controls.json").read_text())["output"].split("\n") if "'" in l and "axioms" in l]
                 + axiom_lines("lean_honest.json", ["inside_not_pos", "inside_is_neg", "tampered_not_pos", "untampered_pos"]),
                 "allowlist": ALLOW, "compile_transcript": fref("lean_controls.json"),
                 "other_transcripts": [fref("lean_honest.json")],
                 "rejections": [fref("lean_reject_inside.json"), fref("lean_reject_tampered.json")],
                 "sources": [fref("lean/Controls.lean"), fref("lean/Honest.lean"), fref("lean/RejectInside.lean"), fref("lean/RejectTampered.lean")],
                 "status": STATUS, "statement_adequacy": "not audited by a human"}),
        # ---------------------------------------------------------------- C-ball
        rec("PZC-C-0001", "C", "argument",
            "C-ball. Outside chain: 103 records of the affine enclosure F - (a - ac) d in Q + R, d in D, chaining 198/125 = 1.584 to 4, widths 0.003 to 0.0538, window |t| <= 1e-8, all with qlo + cmin > 0; the weakest enclosure is F >= 0.01558 on [1.584, 1.587].",
            [], ball(SEG_POS + ["cert_summary.json"], "run files and the summary of the Lean inputs")),
        rec("PZC-C-0002", "C", "argument",
            "C-ball. Inside chain: 71 records chaining 17/40 = 0.425 to 1579/1000, widths 0.001 to 0.02, all with qhi + cmax < 0; the weakest enclosure is F <= -0.01519 on [1.576, 1.579]. Plus the single interval [0.381, 0.383] with F <= -0.0549.",
            [], ball(SEG_NEG + ["cert_summary.json"], "run files and the summary of the Lean inputs")),
        rec("PZC-C-0003", "C", "argument",
            "C-ball. Root brackets (thin points, N = 64): F(0.3745, t) in [0.0177, 0.0949] > 0 and F(0.379, t) in [-0.0978, -0.0235] < 0; F(1.579, t) in [-0.0423, -0.0195] < 0 and F(1.583, t) in [0.0075, 0.0303] > 0, for |t| <= 1e-8.",
            [], ball(["runs/sweep_am_tight.json", "runs/sweep_pts_extra.json", "runs/sweep_ap_tight.json", "runs/sweep_near_ap_right.json", "cert_summary.json"], "thin-point records at the four bracket values")),
        rec("PZC-C-0004", "C", "argument",
            "C-ball. The other thin-point records: F > 0 at a = 0.33, 0.35, 0.36, 0.37, 0.372 and F < 0 at 0.381, 0.383, 0.39, 0.40, 0.42, 0.45, 0.5, 0.55, 1.57, 1.576; F > 0 at 1.584, 1.587, 1.593 (22 thin records with the bracket points).",
            [], ball(THIN + ["cert_summary.json"], "thin-point run files")),
        rec("PZC-C-0005", "C", "argument",
            "C-ball. Stability on every cell: det B > 0 and tr B > 0 certified on the whole cell ball x a-interval x t-window, so D_t = s^2 B_t is positive definite for kappa != 0 for every a of the interval and |t| <= 1e-8; 1,284,310 cells (232,178 refined) over the 203 ok records, 0 failed. The lattice tail is an explicit computed bound (ratio < 1) added to every jet component.",
            [], ball(SEG_NEG + SEG_POS + THIN, "stats fields of the run records")),
        rec("PZC-C-0006", "C", "argument",
            "C-ball. Straddling intervals certify neither sign: [0.3745, 0.379] F in [-0.1514, 0.1470] and [1.579, 1.583] F in [-0.0482, 0.0362], sign 'none'. 12 of the 210 run records carry no sign (7 with failed cells, 5 straddling).",
            [], ball(CTL + ["cert_summary.json"], "straddle control runs; cert_summary.json 'uncertified'")),
        # ---------------------------------------------------------------- C-human
        rec("PZC-C-0007", "C", "argument",
            "C-human. Exact second variation: for 2x2 positive semi-definite D, tr sqrt(D) = sqrt(tr D + 2 sqrt(det D)) (Cayley-Hamilton); with Duffy coordinates (D_t = s^2 B_t), F = int g, g = s^2 tau''/4, tau = sqrt(T + 2 delta), T = tr B_t, delta = sqrt(det B_t), delta'' = det''/(2 delta) - det'^2/(4 delta^3), tau'' = (T'' + 2 delta'')/(2 tau) - (T' + 2 delta')^2/(4 tau^3). Exact, no inequality; singular only where det B or tr B vanishes (excluded by PZC-C-0005).",
            ["PZC-C-0005"], human("Derivation of section 3 step 2 of the paper; prefactors and triangle bookkeeping as in B2 and N2.", "paper section 3, step 2")),
        rec("PZC-C-0008", "C", "argument",
            "C-human. B2's linear-response majorant cannot reach the roots: U'' - E'' = (1/2) int tr(X^{-1} Y^2) >= 0 (N2), so E'' = 0 forces U'' >= 0 at a root; Tier X values U'' = +2.79 at 0.3767 and +8.77 at 1.5815, U'' < 0 only at a = 0.5, 0.7, 1 of 17 grid values. Hence the exact F is enclosed instead.",
            [], human("Relaxation term of N2 step 3 plus the Tier X values of PZC-X-0002.", "paper section 3, step 1")),
        rec("PZC-C-0009", "C", "argument",
            "C-human. E(a, .) is C^2 on the window with second derivative F (differentiation under the Brillouin-zone integral: the Duffy integrand is jointly smooth and bounded on the compact domain because det B > 0 is certified on every cell); the Lean hypotheses hE, hE' at the window edges need a neighbourhood of the closed window, closed by continuity as the margins are strict (stated, not separately certified).",
            ["PZC-C-0005", "PZC-C-0007"], human("Dominated convergence on the Duffy cells.", "paper section 3, step 6")),
        rec("PZC-C-0010", "C", "argument",
            "C-human. Mirror symmetry E(a, -t) = E(a, t) for every radial V (diag(1, -1) maps L_rho to itself and conjugates P_t to P_{-t}); and tau(t) = rho + sqrt3 t + O(t^2), so E(a, t) < E(a, 0) for small t != 0 means rho is not a local minimum over lattice shapes.",
            [], human("As B2 sections 2.4 and 2.5.", "paper section 3, steps 6 and 7")),
        rec("PZC-C-0011", "C", "argument",
            "C-human. Continuity of a -> F(a, 0) on [0.3745, 0.379] and [1.579, 1.583] (analytic in a: a uniformly convergent lattice sum of smooth integrals); not formalised. Needed by the intermediate value theorem.",
            ["PZC-C-0005"], human("Uniform convergence on compact a-ranges.", "paper section 3, step 5")),
        rec("PZC-C-0012", "C", "argument",
            "HEADLINE inside (C): for every a in [0.425, 1.579] and |t| <= 1e-8, F(a, t) < 0, E(a, t) < E(a, 0) for 0 < |t| <= 1e-8 along the shear, and the triangular lattice is not a local minimum of the harmonic zero-point energy over lattice shapes (Gaussian exp(-pi a r^2), harmonic approximation, Bravais, 2D, local window). Tier A part: the logic and the rational signs (PZC-A-0001..0006); C-ball: PZC-C-0002, 0005; C-human: the glue.",
            ["PZC-A-0004", "PZC-A-0006", "PZC-C-0002", "PZC-C-0005", "PZC-C-0007", "PZC-C-0009", "PZC-C-0010"],
            human("Assembly of the A, C-ball and C-human pieces, steps 2 to 7 of the paper.", "paper sections 2-3")),
        rec("PZC-C-0013", "C", "argument",
            "HEADLINE outside and roots (C): for every a in [1.584, 4] and |t| <= 1e-8, F(a, t) > 0 and E(a, 0) < E(a, t) for 0 < |t| <= 1e-8 (strict minimum along the shear); a -> F(a, 0) has a zero in (0.3745, 0.379) and one in (1.579, 1.583) (uniqueness not certified); every zero of a -> F(a, t) in [0.425, 4] lies in (1.579, 1.584) minus {1.583}. The full iff for all a > 0 is NOT claimed.",
            ["PZC-A-0004", "PZC-A-0005", "PZC-A-0006", "PZC-C-0001", "PZC-C-0003", "PZC-C-0004", "PZC-C-0005", "PZC-C-0007", "PZC-C-0009", "PZC-C-0010", "PZC-C-0011"],
            human("Assembly of steps 2 to 6 of the paper.", "paper sections 2-3")),
        rec("PZC-C-0014", "C", "argument",
            "C-human, extra hypotheses (E_zp of class C^2 near rho in shape space, rho critical with isotropic Hessian from the order-3 stabiliser, F(a, 0) = 2 Lap E_zp(rho), 2D second-derivative test; none formalised): for a in [1.584, 4] the triangular lattice is a strict local minimum of E_zp over unit-covolume lattice shapes. Without these assumptions the proven statement is the strict minimum along the shear.",
            ["PZC-C-0013"], human("Stabiliser argument of P2 section 3.1 and B2 section 2.6; classical second-derivative test.", "paper section 6")),
        # ---------------------------------------------------------------- X
        rec("PZC-X-0001", "X", "numeric",
            "Tier X cross-check: every certified enclosure contains the independent floating-point value of F(a, 0) (closed form, Gauss-Legendre N = 32) at a_lo, a_c, a_hi of every run: 609 checks, 0 not contained. Consistency, not independence of the formula.",
            [], num(["crosscheck_tierX.json", "runs/crosscheck.log"], "output of code/n1_crosscheck.py")),
        rec("PZC-X-0002", "X", "numeric",
            "Tier X scan (N = 64) over 17 values of a in [0.15, 4]: closed-form F agrees with finite differences of E to <= 4.92e-4; c = F/8 reproduces P2's c(a); U''(0) of B2's majorant is < 0 only at a = 0.5, 0.7, 1 and equals +2.79 at 0.3767, +8.77 at 1.5815; F > 0 at a = 0.15, 0.2, 0.25, 0.3, 0.35 (no sign change seen there).",
            [], num(["runs/explore_tierX_N64.txt", "runs/fcheck.txt"], "verbatim scan output of code/n1_explore.py and the f-helper check")),
        rec("PZC-X-0003", "X", "numeric",
            "Not certified (reported, not hidden): thin points a = 0.25 (104 failed cells, depth 2) and a = 0.30 (9 failed cells); intervals of width 0.0025 to 0.005 on [0.3925, 0.41] have failed cells; [0.41, 0.425] enclosures straddle zero; nothing is claimed for a < 0.33 or in (0.383, 0.425) beyond the thin points 0.39, 0.40, 0.42, nor for a > 4.",
            [], num(["cert_summary.json"], "'uncertified' field of the summary")),
        rec("PZC-X-0004", "X", "numeric",
            "Repository guards at writing: antigravity_guard.py rc 1 and test_rigor_guard.py rc 1, both on pre-existing files; archived verbatim; neither output mentions an N1 file. pytest tests/ was not run for this paper.",
            [], num(["guard_antigravity.txt", "guard_test_rigor.txt"], "verbatim outputs")),
        rec("PZC-X-0005", "X", "numeric",
            "P2's sign change of the curvature near a ~ 0.123 (c(0.1) < 0) and the precision-flagged values at a = 6, 8 are cited from P2 (doi:10.5281/zenodo.23653833), not re-run here; they are the reason the full iff for all a > 0 is not claimed. This paper's own Tier X scan stops at a = 0.15.",
            [], num(["runs/explore_tierX_N64.txt"], "N1 scan covers a >= 0.15 only; the 0.123 value is P2's")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
