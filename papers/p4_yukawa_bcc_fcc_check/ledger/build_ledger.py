"""Build the Elenchus claim ledger for the M3 paper (papers/p4_yukawa_bcc_fcc_check).

Modelled on papers/p4_amplifier_census/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not be filed
above anything in its depends_on, and the kind caps the tier (lean_axioms A, citation L, argument C, numeric X).
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
LOGS = DATA / "logs"
TOOLCHAIN = ("Lean 4.34.1 + Mathlib d13f23b7 through scripts/certified_numerics/lean_pinned.py (modules import "
             "Mathlib.Tactic and Mathlib.Algebra.BigOperators.Fin; no import Mathlib)")
ALLOW = ["propext", "Classical.choice", "Quot.sound"]
STATUS = ("producer-checked by the M3 lane; leanchecker replay rc 0 for Basic, Shells, Chains, LemmaA5, Lemma61 "
          "(data/logs/leanchecker.json, run by the producer); NO independent audit exists at writing (producer != "
          "verifier clean recompile pending); no human audit of statement adequacy; no statement lock")
SRC_COMMIT = "e5f38b289314c730ed4960104c91a2902b88f8ef"
ADEQ = "not audited by a human; no independent AI audit at writing"


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
            "axiom_output": axioms_from(LOGS / "lean_axioms.json", ["YukawaBccFcc." + n for n in names]),
            "allowlist": ALLOW, "compile_transcript": fref(LOGS / "lean_axioms.json"),
            "sources": [fref(LEAN / s) for s in srcs],
            "leanchecker_replay": fref(LOGS / "leanchecker.json"), "status": STATUS, "statement_adequacy": ADEQ}


def cite(source: str, where: str, text: str) -> dict:
    return {"kind": "citation", "source": source, "where": where, "text": text,
            "note": "taken as stated; not re-proved here; the paper was read in full by the producer via alphaXiv text extraction"}


def arg(subtier: str, text: str, files: list[Path], instrument: str) -> dict:
    return {"kind": "argument", "subtier": subtier, "text": text, "files": [fref(f) for f in files],
            "instrument": instrument, "source_commit": SRC_COMMIT}


def num(files: list[Path], note: str) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True, "note": note,
            "files": [fref(f) for f in files]}


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    d = DATA
    arb, extra, flt = d / "arb_results.json", d / "extra_results.json", d / "float_results.json"
    res = d / "result.json"
    c = [
        rec("YBC-A-0001", "A", "lean_axioms",
            "YukawaBccFcc.Nc_eq_ncard and Mc_eq_ncard: the box counts Nc n = #{m in [-5,5]^3 : |m|^2 = 2n} (2n < 36) and "
            "Mc l = #{m in [-6,6]^3 : |m|^2 = l, m1, m2, m3 of equal parity} (l < 49) equal Set.ncard of the same set over all of Z^3.",
            [], lean_ev(["Nc_eq_ncard", "Mc_eq_ncard"], ["Basic.lean"])),
        rec("YBC-A-0002", "A", "lean_axioms",
            "YukawaBccFcc.fcc_multiplicities: (Nc 1, ..., Nc 12) = (12,6,24,12,24,8,48,6,36,24,24,24). "
            "YukawaBccFcc.bcc_multiplicities: the nonzero Mc l for l <= 48 occur exactly at l in {3,4,8,11,12,16,19,20,24,27,32,35,36,40,43,44,48} "
            "with values (8,6,12,24,8,6,24,24,24,32,12,48,30,24,24,24,8) (17 values). Kernel enumeration (decide +kernel).",
            ["YBC-A-0001"], lean_ev(["fcc_multiplicities", "bcc_multiplicities"], ["Basic.lean", "Shells.lean"])),
        rec("YBC-A-0003", "A", "lean_axioms",
            "YukawaBccFcc.lemmaA5_A6: for every natural j < 1000, over the reals with Real.pi, Real.exp, a2 = 2^(1/3), b2 = 2^(-4/3): "
            "pi a2 sum_{n=1}^{12} n N_n e^{-pi a2 n (1+(j+1)/10^4)} - pi b2 sum_{l=1}^{48} l M_l e^{-pi b2 l (1+j/10^4)} - 10^-18 > 3/1000. "
            "Proof by 1000 kernel-checked rational cells and untrusted dyadic exp tables whose steps are kernel-checked against Taylor enclosures.",
            ["YBC-A-0002"], lean_ev(["lemmaA5_A6"], ["Basic.lean", "Chains.lean", "LemmaA5.lean"])),
        rec("YBC-A-0004", "A", "lean_axioms",
            "YukawaBccFcc.lemmaA5_A7: for every natural j < 2000: sum_{l=1}^{48} M_l e^{-pi b2 l (11/10+(j+1)/2000)} - "
            "sum_{n=1}^{12} N_n e^{-pi a2 n (11/10+j/2000)} - 10^-18 > 1/10000.",
            ["YBC-A-0002"], lean_ev(["lemmaA5_A7"], ["Basic.lean", "Chains.lean", "LemmaA5.lean"])),
        rec("YBC-A-0005", "A", "lean_axioms",
            "YukawaBccFcc.lemmaA5_A8: 8 e^{(pi a2 - 3 pi b2) 21/10} > 25/2.",
            [], lean_ev(["lemmaA5_A8"], ["Basic.lean", "Lemma61.lean"])),
        rec("YBC-A-0006", "A", "lean_axioms",
            "The finite constants used in the printed proof of Lemma 6.1: e^{-pi a2} < 1/49 (lemma61_exp_fcc), e^{-pi b2} < 3/10 "
            "(lemma61_exp_bcc), pi b2 < 5/4 (lemma61_pb_lt), a2 > 3 b2 (lemma61_a2_gt), e^{-pi a2 21/10} < 1/128 (lemma61_exp_fcc_21), "
            "12 + 30((1-x)^-2 - 1) < 25/2 for 0 <= x <= 1/128 (lemma61_prop41_bracket), and every partial sum of 30 sum_{n>=13} n 49^-n "
            "(lemma61_tail_fcc) and of (75/2) sum_{l>=49} l^2 (3/10)^l (lemma61_tail_bcc) is < 10^-18. The passage to the infinite sum "
            "is not written in Lean. These are inputs of Lemma 6.1, not Lemma 6.1.",
            [], lean_ev(["lemma61_exp_fcc", "lemma61_exp_bcc", "lemma61_pb_lt", "lemma61_a2_gt", "lemma61_exp_fcc_21",
                         "lemma61_prop41_bracket", "lemma61_tail_fcc", "lemma61_tail_bcc"], ["Basic.lean", "Lemma61.lean"])),
        rec("YBC-A-0007", "A", "lean_axioms",
            "YukawaBccFcc.lemmaA6_tail: the rational 60 (1/49)^13/(1-1/49) + 60 (3/10)^49/(1-3/10) is < 7e-21 (the tail printed in the "
            "proof of Lemma A.6; exact value 6.5267e-21), and YukawaBccFcc.lemmaA1_rational: 55995/10^6 < 7/125 (the rational step of Lemma A.1). "
            "Lemma A.6 itself is not in Lean.",
            [], lean_ev(["lemmaA6_tail", "lemmaA1_rational"], ["Lemma61.lean"])),
        rec("YBC-A-0008", "A", "lean_axioms",
            "Lean controls: RejectWitness.lean compiles with rc 0 and its theorems cellA7bad_0_false, bad_chain_false, N7_is_48 and N7_ne_46 are "
            "kernel-checked, so the kernel evaluates the tampered cell and tampered table checks to false and N7 to 48. RejectN7.lean (N7 = 46), "
            "RejectChain.lean (table entry C1[500] x 1.01) and RejectCell.lean (A.7 margin 1/1000) fail with rc 1. The planted ctl_sorry reports "
            "sorryAx and the planted ctl_axiom reports ctl_cheat in #print axioms although Controls.lean compiles with rc 0.",
            ["YBC-A-0002"],
            {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
             "axiom_output": ["'YukawaBccFcc.Controls.ctl_sorry' depends on axioms: [propext, sorryAx, Classical.choice, Quot.sound]",
                              "'YukawaBccFcc.Controls.ctl_axiom' depends on axioms: [propext, Classical.choice, Quot.sound, ctl_cheat]"],
             "allowlist": ALLOW, "compile_transcript": fref(LOGS / "lean_controls.log"),
             "rejections": [fref(LOGS / "lean_reject_witness.log")],
             "sources": [fref(LEAN / s) for s in ["Controls.lean", "RejectN7.lean", "RejectChain.lean", "RejectCell.lean", "RejectWitness.lean"]],
             "status": STATUS, "statement_adequacy": ADEQ,
             "note": "the two sentinel lines are the verbatim #print axioms output of Controls.lean; they show the gate CATCHES the planted sorry and axiom"}),
        # ------------------------------------------------------------------ L
        rec("YBC-L-0001", "L", "citation",
            "Luo and Wei, arXiv:2610.31456v1 [math.AP] 22 Oct 2026: Theorem 1.1 (for unit-covolume lattices, BCC is the unique minimiser of the "
            "Yukawa energy E_kappa below a unique threshold kappa* in (0, sqrt(pi)), FCC above, both at kappa*), the characterisation (1.4) of "
            "kappa* as the unique root of an integral involving D(t) = Theta(t,L_B) - Theta(t,L_F), Lemma 6.1 (D(1) = 0 and D(t) > 0 for t > 1), "
            "Lemma A.5 (A.6)-(A.8), Lemma A.6 (2(E(L_B) - E(L_F)) < -1e-19 at kappa = 1717921868469903/10^15 and > 1e-20 at ...904/10^15), "
            "Lemmas A.1-A.4, and the printed value kappa* = 1.7179218684699 (1.717921868469903 < kappa* < 1.717921868469904 in (A.9)).",
            [], cite("arXiv:2610.31456v1", "Thm 1.1, Lemma 6.1, Lemmas A.1-A.6, eq. (1.4), (A.9)",
                     "Statements pinned from the paper text; the credit for the result belongs to the authors")),
        rec("YBC-L-0002", "L", "citation",
            "Luo and Wei, Theorems 5.1 and 6.1 and the analytic reductions of Sections 2-5 (including the global comparison that Lemmas A.2-A.4 "
            "serve) are taken as stated; this paper did not check them.",
            ["YBC-L-0001"], cite("arXiv:2610.31456v1", "Sections 2-6", "Taken as stated; not re-proved here")),
        # ------------------------------------------------------------------ C
        rec("YBC-C-0001", "C", "argument",
            "kappa* reproduced three independent ways: (E) Ewald split in Arb at 320 bits: [1.717921868469903864250874 +/- 1.67e-25]; (D) direct "
            "real-space Arb sum over about 4000 shells with a rigorous integral tail: bracket "
            "[1.717921868469903864248480 +/- 2.6e-25, 1.717921868469903864252817 +/- 4.5e-25]; (Q) mpmath quadrature of the paper's integral equation (1.4) "
            "at 40 digits: 1.71792186846990386425087416661. Agreement to about 22 digits; the printed 1.71792186846990 and the (A.9) enclosure are reproduced. "
            "Ball arithmetic and quadrature are not kernel-checked.",
            ["YBC-L-0001"], arg("C-ball", "arb_results.json (kappa_star_bracket_ewald/direct), float_results.json (kappa_star_eq14_mpmath)",
                                [arb, flt], "python-flint 0.6.0 (Arb), mpmath; code/m3_arb.py, code/m3_float.py")),
        rec("YBC-C-0002", "C", "argument",
            "Lemma A.6 in Arb with full Ewald sums, G = 2(E_B - E_F): G(...903e-15) = -1.35363e-19 < -1e-19 and G(...904e-15) = +2.12616e-20 > 1e-20; "
            "controls G(...902e-15) = -2.91987e-19 and G(...905e-15) = +1.77886e-19; G(1) = -1.0745e-4, G(3) = +1.5771e-4; "
            "the direct sum agrees within its balls at every kappa; dG/dkappa at kappa* is 1.56624e-4. Not in Lean (the pinned Mathlib has no erfc).",
            ["YBC-C-0001"], arg("C-ball", "arb_results.json G_values", [arb], "python-flint 0.6.0; code/m3_arb.py")),
        rec("YBC-C-0003", "C", "argument",
            "Lemma A.6 under the paper's own truncation (FCC n <= 12, BCC l <= 48) plus the printed tail 7e-21: G_trunc(903) = -1.35362683e-19, "
            "G_trunc(904) = 2.12615782e-20; slacks 2.84e-20 (lower) and 4.26e-21 (upper); the actually omitted tail is 2.83e-26, far below the printed bound.",
            ["YBC-C-0002", "YBC-A-0007"], arg("C-ball", "extra_results.json A6_*", [extra], "python-flint 0.6.0; code/m3_extra.py")),
        rec("YBC-C-0004", "C", "argument",
            "Lemma A.5 re-run in Arb on all 1000 + 2000 cells and (A.8): no failure; minimum slacks 7.52e-4 ((A.6), j = 999), 7.65e-5 ((A.7), j = 0), "
            "(A.8) slack 0.143. The same inequalities are Tier A in YBC-A-0003..0005; the Arb run is a cross-check.",
            ["YBC-A-0003", "YBC-A-0004", "YBC-A-0005"], arg("C-ball", "arb_results.json lemmaA5", [arb], "python-flint 0.6.0; code/m3_arb.py")),
        rec("YBC-C-0005", "C", "argument",
            "Lemma A.1 in Arb: P(L_F,0) = 0.0558589... < 0.055995 < 7/125 = 0.056 < I(16/25,0) = 0.0561634...; Lemma A.3 (A.4) endpoints: "
            "e^{alpha1} = 0.44 - 2.05e-16 <= 11/25, e^{alpha2} = 0.147 - 1.37e-16 <= 147/1000, e^{beta} = 4/3 + 1.87e-16 >= 4/3; "
            "arithmetic: sum n_j = 84,043 and 1118 + 193 + 86 + 5828 = 7225.",
            ["YBC-L-0001", "YBC-A-0007"], arg("C-ball", "extra_results.json A3_*, A4_*", [extra], "python-flint 0.6.0; code/m3_extra.py")),
        rec("YBC-C-0006", "C", "argument",
            "Observation for a human reader, not a discrepancy: in Lemma A.3 (A.4) the three exponential bounds hold only by margins of about 2e-16 "
            "(the endpoints look like double-rounded logarithms, so the bounds hold or fail depending on rounding direction); the Arb check at 320 bits "
            "shows they hold. It is the tightest margin in the appendix that we could check.",
            ["YBC-C-0005"], arg("C-ball", "extra_results.json A4_e^alpha1 - 11/25 etc.", [extra], "python-flint 0.6.0; code/m3_extra.py")),
        rec("YBC-C-0007", "C", "argument",
            "Shell bounds N_n < 30n for n <= 2100 and M_l < 30 l (and M_l <= 18 l) for l <= 4200 hold on the enumerated range, by brute-force enumeration "
            "of r_3 cross-checked against the r_3 shortcut. For all n the bound is a paper argument (Prop. 4.1 / fixing two coordinates); it is not machine-checked.",
            [], arg("C-enumeration", "extra_results.json N_lt_30n_all_enumerated etc.; shells_k4200.json", [extra, d / "shells_k4200.json"],
                    "numpy enumeration; code/m3_shells.py")),
        rec("YBC-C-0008", "C", "argument",
            "Lemma 6.1 itself (D(1) = 0 and D(t) > 0 for t > 1) is NOT kernel-checked. Its finite inputs are Tier A (YBC-A-0005, YBC-A-0006); "
            "the assembly (theta functions as lattice sums over Z^3, Poisson summation for D(1) = 0 using L_B = L_F^*, the cell argument for D' and D, "
            "and N_n < 30n for all n) is the paper's argument, read and followed, not formalised. mpmath gives D(1) = -8.6e-42 numerically at 40 digits.",
            ["YBC-A-0006", "YBC-L-0001"], arg("C-paper-argument", "Paper proof of Lemma 6.1 against the Lean constants; float_results.json D(1)",
                                              [flt, LEAN / "Lemma61.lean"], "none (reading)")),
        rec("YBC-C-0009", "C", "argument",
            "HEADLINE. Every printed number and inequality of Luo and Wei that we checked holds, and no discrepancy was found: kappa* (three ways), "
            "the Lemma A.6 signs, Lemma A.5 (A.6)-(A.8), the shell multiplicities, the Lemma 6.1 constants and tails, Lemmas A.1 and A.3 endpoints. "
            "NOT checked: the Lemma 6.1 assembly, Lemma A.4 (5,828 rectangles; the partition data is not public, no ancillary files on arXiv), Lemma A.2, "
            "Lemma A.6 in Lean, and Sections 2-5. This is a partial independent check, not a verification of Theorem 1.1 and not a refutation. "
            "Filed C because the headline combines Tier C ball arithmetic with Tier A finite statements.",
            ["YBC-C-0001", "YBC-C-0002", "YBC-C-0004", "YBC-A-0002", "YBC-A-0006", "YBC-L-0002"],
            arg("C-assembly", "Assembly of the rows above as in Section 8 of the paper.", [res, d / "RESULT.md"], "none")),
        # ------------------------------------------------------------------ X
        rec("YBC-X-0001", "X", "numeric",
            "An IEEE-double direct sum reproduces kappa* to only 11 digits (1.7179218684625486) because of cancellation (dG/dkappa about 1.57e-4); "
            "double precision alone cannot reproduce the 13-digit printed value, so it is not used as a control.",
            [], num([flt], "kappa_star_double_direct; information only")),
        rec("YBC-X-0002", "X", "numeric",
            "Repository guards were run and FAIL for reasons in files this paper's lane did not touch: antigravity_guard.py rc 1 (103 findings in other "
            "lanes), test_rigor_guard.py rc 1, pytest tests/ rc 2 (28 collection errors, no test ran). Recorded so the state is explicit; none of these "
            "outputs supports a claim.",
            [], num([LOGS / "guard_antigravity.txt", LOGS / "guard_test_rigor.txt", LOGS / "pytest_tests.txt"],
                    "verbatim guard outputs of the M3 lane")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
