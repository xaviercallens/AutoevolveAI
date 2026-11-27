"""Build the Elenchus claim ledger for the P1 preprint (papers/prog_sandier_serfaty_audit).

Modelled on papers/ar_dipolar_exciton/ledger/build_ledger.py. Every claim gets a content-addressed evidence blob
(evidence/<sha256>.json): verbatim #print axioms lines plus source hashes (Tier A), verbatim primary-source excerpts
(Tier L, from sources/excerpts.json), the argument text file and its hash (Tier C), result files with claim_licence false
(Tier X). Dependency edges respect the gate's no-inversion rule: A and L rows depend on nothing; C rows depend only on A, L
or C rows; X rows may depend on anything (the audit row never rests on an X row).
Gate: python3 <elenchus>/tools/ledger.py ledger.json --evidence-dir evidence
Run:  /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I build_ledger.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
W = PAPER.parents[1]
EV = HERE / "evidence"
DATA = PAPER / "data"
RERUN = PAPER / "rerun"
EXC = json.loads((HERE / "sources/excerpts.json").read_text())
TOOLCHAIN = ("Lean 4.34.1, Mathlib d13f23b723b8a846827a245b89c10fc7d3f11612, pinned openai/math stack "
             "(scripts/certified_numerics/lean_pinned.py)")
LEAN_MAIN = W / "formal_cert/Programmes/SandierSerfatyStatement.lean"
LEAN_CTL = W / "formal_cert/Programmes/SandierSerfatyStatementControls.lean"
ALLOW = ["propext", "Classical.choice", "Quot.sound"]
PRODUCER = ("producer-checked at stage S3 and re-compiled at the paper stage by a second agent instance of the same AI pipeline "
            "(not an independent verifier); no human audit")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def blob(obj: dict) -> str:
    raw = json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False).encode()
    d = sha(raw)
    EV.mkdir(parents=True, exist_ok=True)
    (EV / f"{d}.json").write_bytes(raw)
    return f"sha256:{d}"


def file_ref(p: Path) -> dict:
    rel = str(p.relative_to(W)) if str(p).startswith(str(W)) else str(p)
    return {"path": rel, "sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}


def axiom_lines(output: str, names: list[str]) -> list[str]:
    out = output.replace("\n ", " ")
    lines = [ln.strip() for ln in out.split("\n") if any(f"'{n}'" in ln for n in names)]
    if len(lines) != len(names):
        raise SystemExit(f"axiom lines missing for {names}: {lines}")
    return lines


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict) -> dict:
    return {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
            "depends_on": depends, "evidence": blob(ev), "audit": None}


def lean_ev(names: list[str], status: str) -> dict:
    rs = json.loads((RERUN / "compile_statement.json").read_text())
    s3 = json.loads((DATA / "s3/compile_statement.json").read_text())
    lines = axiom_lines(rs["output"], ["ProgSandierSerfaty." + n for n in names])
    s3_lines = axiom_lines(s3["output"], ["ProgSandierSerfaty." + n for n in names])
    assert lines == s3_lines, "paper-stage rerun differs from the S3 transcript"
    return {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output": lines, "allowlist": ALLOW,
            "compile_transcripts": [file_ref(RERUN / "compile_statement.json"), file_ref(DATA / "s3/compile_statement.json")],
            "sources": [file_ref(LEAN_MAIN)], "status": status,
            "statement_adequacy": "not audited by a human; the gloss of each statement is a Tier C claim (SSA-C-0001)"}


CC = DATA / "citation_check"
CC_COVERED = {"ss_thm1": "ss_thm1_3_4", "ss_conj": "ss_thm2 (Theorem 2 only; Conjecture 1 is outside the tool's KINDS)", "ss_prop31": "ss_prop31",
              "ss_prop49": "ss_prop49", "bs_thm15": "bs_thm15"}


def cite(keys: list[str], **kw: object) -> dict:
    """Excerpts are rejoined ASCII transcriptions of alphaXiv extractions. At the REVISE stage citation_check.py was run on
    pdftotext primary text for the theorem-type passages listed in CC_COVERED (verbatim passages ACCEPTED; the rejoined
    excerpts themselves REFUSED as non-verbatim). citation_check_run is True only if every excerpt of the row is covered."""
    covered = {k: CC_COVERED[k] for k in keys if k in CC_COVERED}
    not_checked = [k for k in keys if k not in CC_COVERED]
    return {"kind": "citation", "excerpts": {k: EXC[k] for k in keys}, "excerpt_file": file_ref(HERE / "sources/excerpts.json"),
            "citation_check_run": bool(covered) and not not_checked,
            "citation_check": {"tool": "tools/citation_check.py on pdftotext output of the arXiv PDFs (primary text)",
                               "verbatim_passages_accepted_for": covered, "not_checked_by_the_tool": not_checked,
                               "ledger_excerpts_are_verbatim": False,
                               "note": "ACCEPTED means the quoted passage is present verbatim in the primary text; statement_match is the agent's judgment. The ledger excerpts themselves are rejoined transcriptions (REFUSED as non-verbatim by the same tool).",
                               "files": [file_ref(CC / "cite_results.json"), file_ref(CC / "run_cite.py"), file_ref(CC / "ss2012_full.txt"), file_ref(CC / "bs2018_full.txt"), file_ref(CC / "pdf_sha256.txt")]},
            **kw}


def num(files: list[Path], instrument: str, **kw: object) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True, "instrument": instrument,
            "files": [file_ref(p) for p in files], **kw}


def arg(files: list[Path], text: str) -> dict:
    return {"kind": "argument", "text": text, "text_files": [file_ref(p) for p in files]}


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    S3 = "stage S3 (Lean statement)"
    ctl = json.loads((RERUN / "compile_controls.json").read_text())
    ctl_s3 = json.loads((DATA / "s3/compile_controls.json").read_text())
    ctl_names = ["ProgSandierSerfaty.ctl_sorry", "ProgSandierSerfaty.ctl_axiom"]
    ctl_lines = axiom_lines(ctl["output"], ctl_names)
    assert ctl_lines == axiom_lines(ctl_s3["output"], ctl_names)
    lf = json.loads((DATA / "lean_data_certificates/result_positive_run.json").read_text())
    lf_names = [f"cert_{i}" for i in range(13)]
    lf_lines = axiom_lines(lf["output_excerpt"], lf_names)
    lf_neg = json.loads((DATA / "lean_data_certificates/result_negctl_run.json").read_text())

    claims = [
        # ------------------------------------------------------------------ Tier A
        rec("SSA-A-0001", "A", "lean_axioms",
            "ProgSandierSerfaty.negPi_admissibleBg_iff and negPi_admissible: with no charges (Lambda = empty), the field E(x) = -pi x satisfies the weak equations div E = 2 pi nu - b, curl E = 0 (against all smooth compactly supported test functions) iff b = 2 pi; hence the Lean class Admissible (b = 2 pi) is non-empty. Non-degeneracy of the definitions only; says nothing about the conjecture.",
            [], lean_ev(["negPi_admissibleBg_iff", "negPi_admissible"], S3 + "; " + PRODUCER)),
        rec("SSA-A-0002", "A", "lean_axioms",
            "Negative controls negPi_not_admissible_noBackground (b = 0) and negPi_not_admissible_wrongSign (b = -2 pi): the same field is NOT admissible for a missing or wrong-sign neutralizing background, so the background constant of the Lean statement is load-bearing.",
            [], lean_ev(["negPi_not_admissible_noBackground", "negPi_not_admissible_wrongSign"], S3 + "; " + PRODUCER)),
        rec("SSA-A-0003", "A", "lean_axioms",
            "negPi_hasLocalEnergy and competitor_nonvacuous: the puncture-limit relation HasLocalEnergy is satisfiable (Lambda = empty), and for every manuscript square cutoff family some competitor meets every hypothesis of the for-all clause of SandierSerfatyStatement, i.e. the competitor hypotheses are satisfiable. The witness has W = +infinity (Tier C, Gauss's law: a charge-free admissible field has local energy growing like R^4), so the inequality holds for it trivially; nothing is claimed about the conclusion constraining a competitor (gloss corrected at the revision stage after the audit, N3). The renormalization term pi log(eta) sum chi(p) is not exercised (no charges).",
            [], lean_ev(["negPi_hasLocalEnergy", "competitor_nonvacuous"], S3 + "; " + PRODUCER)),
        rec("SSA-A-0004", "A", "lean_axioms",
            "exists_squareCutoffFamily and exists_ballCutoffFamily: both cutoff classes of the statements (the manuscript's square class, a smooth version of the SS2012 ball class) are non-empty, with gradient bound uniform in R, so the for-all-chi quantifiers are not vacuous.",
            [], lean_ev(["exists_squareCutoffFamily", "exists_ballCutoffFamily"], S3 + "; " + PRODUCER)),
        rec("SSA-A-0005", "A", "lean_axioms",
            "triBasis_covolume and ssBasis_covolume: the basis of Lambda_tri in the Lean statement has covolume 1, and the SS2012 basis Lambda_m has covolume 2 pi / m (algebra on the Lean transcription of the lattices only).",
            [], lean_ev(["triBasis_covolume", "ssBasis_covolume"], S3 + "; " + PRODUCER)),
        rec("SSA-A-0006", "A", "lean_axioms",
            "Planted controls (separate file SandierSerfatyStatementControls.lean, importing the built module): ctl_sorry 'proves' SandierSerfatyStatement with sorry and depends on sorryAx; ctl_axiom depends on the planted axiom ctl_cheat; the file compiles with rc 0, so the exit status is not the gate and #print axioms catches both. Control row: both are OUTSIDE the allowlist.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output": ctl_lines, "raw_output": ctl["output"], "rc": ctl["rc"],
                 "allowlist": ALLOW, "expected": "both controls OUTSIDE the allowlist",
                 "compile_transcripts": [file_ref(RERUN / "compile_controls.json"), file_ref(DATA / "s3/compile_controls.json")],
                 "sources": [file_ref(LEAN_CTL)], "statement_adequacy": "control row; not audited by a human"}),
        rec("SSA-A-0007", "A", "lean_axioms",
            "LeanFlow data certificate of the positive run's printed pairs: 13 integer assertions (e.g. lambda in (-6.731,-6.729), K < 0, f(l) > 0, slope > 0, gmin-factor >= 1.20e-5, drneg+er_drop+K <= -4.585e-4, g_dd >= 1.0529222, g_xx >= 0.0128335, det Hess >= 0.0086252) are each accepted by core Lean 4.34.1 'decide'; every theorem 'does not depend on any axioms'. Tier A covers the arithmetic about these stated outward-rounded 1e-7 integers only, not that the C++ run computed them.",
            [], {"kind": "lean_axioms", "toolchain": "core Lean 4.34.1 (decide); LeanFlow commit 84e0c2899830fba671022eefcd408af9ecd565c8 (after the audit fix, which is commit 2c168be2de8104dddc48daecee1423c8d8f076b7 plus a docstring/documentation follow-up; the run was repeated with identical outcomes, data/lean_data_certificates_after_fix/), branch feat/lean-data-certificates-2026-10-25, local, not pushed",
                 "axiom_output": lf_lines, "allowlist": ALLOW, "n_assertions": len(lf["assertions"]), "tier_scope": lf["tier_scope"],
                 "claim_sha256": lf["claim_sha256"], "statement_sha256": lf["statement_sha256"],
                 "compile_transcripts": [file_ref(DATA / "lean_data_certificates/result_positive_run.json"), file_ref(DATA / "lean_data_certificates/claim_positive_run.json"), file_ref(DATA / "lean_data_certificates_after_fix/result_positive_run.json")],
                 "sources": [file_ref(DATA / "scripts/certify_run_outputs.py")],
                 "status": "producer run at stage S1/S4, repeated at REVISE with the fixed checker (same outcomes); the generator path is fail-closed (names regex-checked, labels single-line comments; audit probe_certify_inject) and the checker for arbitrary sources is hardened with a sentinel (88 tests) but is not a sandbox; no independent verifier of the Lean semantics beyond the audit agent; no human audit",
                 "statement_adequacy": "not audited by a human"}),
        # ------------------------------------------------------------------ Tier L
        rec("SSA-L-0001", "L", "citation",
            "Sandier-Serfaty 2012 (arXiv:1011.4617v2): the triangular lattice is the unique minimizer among lattices (Theorem 2) and its minimality among all configurations is Conjecture 1 (p.5); 'Its minimization in general remains open' (abstract, p.1). Theorem 1(3),(4) (p.5): the minimum of W over A_1 is achieved, finite and independent of U, and there is a minimizing sequence of fields periodic w.r.t. a square lattice of side sqrt(2 pi n).",
            [], cite(["ss_open", "ss_conj", "ss_thm1"])),
        rec("SSA-L-0002", "L", "citation",
            "Sandier-Serfaty 2012, Proposition 4.9 (p.41): a measure g >= -C(||m||^2+1) with |W(j,chi) - int chi dg| <= C n (log n + ||m||_inf) ||grad chi||_inf for every chi compactly supported in U; one g serves every chi. Statement read by the paper-stage agent; its proof is not re-checked.",
            [], cite(["ss_prop49"])),
        rec("SSA-L-0003", "L", "citation",
            "Sandier-Serfaty 2012: the definitions (1.7)-(1.8) of W(j,chi) and W_U(j) (p.3); the scaling (1.9) for j in A_m (p.3); Proposition 3.1 (p.26): a periodic admissible j differs from the mean-zero j_Lambda by a constant c, and W_U(j) >= W_U(j_Lambda) with equality iff j = j_Lambda.",
            [], cite(["ss_def", "ss_scaling", "ss_prop31"])),
        rec("SSA-L-0004", "L", "citation",
            "Betermin-Sandier 2018 (arXiv:1404.4485v5): Definition 2.1 and the scaling (2.4) (p.4); Theorem 1.5 (p.3): C = (1/pi) min_{A_1} W + (log pi)/2 + log 2, C <= C_BHS, equality iff min_{A_1} W is achieved by the density-one triangular lattice; W(Lambda_1) = pi log pi - (pi/2) log 3 - 3 pi log Gamma(1/3) + (3/2) pi log 2 ~ -4.1504128 and the equivalence of Conjectures 1.3 and 1.4 (p.26, Theorem 7.7).",
            [], cite(["bs_thm15", "bs_value", "bs_scaling"])),
        rec("SSA-L-0005", "L", "citation",
            "Brauchart-Hardin-Saff 2012 (arXiv:1202.4037v1), Conjecture 4 (p.13): C_log,2 = 2 log 2 + (1/2) log(2/3) + 3 log(sqrt(pi)/Gamma(1/3)) = -0.05560530494339251850...",
            [], cite(["bhs_conj4"])),
        # ------------------------------------------------------------------ Tier C
        rec("SSA-C-0001", "C", "argument",
            "Fidelity of the three Lean Props (SandierSerfatyStatement, SandierSerfatyValueStatement, SandierSerfatyOriginalStatement) to the openai/math manuscript's definitions (eqs cutoffs, admissible, local-energy, whole-energy, triangular-lattice, Theorem 1.1) and to SS2012 Defs 1.1-1.2 and Conjecture 1, read clause by clause by an AI agent (12-row comparison). Rows 1-4, 6a, 7, 8 and 10 match; stated deviations: row 5 (existence of the puncture limit is assumed, conditional: it enters the competitor class only), row 6b (SS ball cutoffs are restricted to smooth ones, harmless by SS Thm 1(1)), row 9 (E_tri is replaced by an existential Lambda_tri-periodic witness, equivalent by SS Prop. 3.1); rows 11-12 (the identification W(E_tri) = wTriClosedForm and the E-form vs j-form equivalence) are not formalized. The audit agent re-compared the definitions and found no misstatement beyond these. The statements are NOT proved. No human has certified the fidelity.",
            ["SSA-A-0001", "SSA-A-0002", "SSA-A-0003", "SSA-A-0004", "SSA-A-0005", "SSA-L-0003", "SSA-L-0004"],
            arg([DATA / "STATEMENT_FIDELITY.md", DATA / "STATEMENT_LOCK.json"],
                "Agent comparison of definitions; Tier A attaches to the non-degeneracy lemmas only. Statement-region sha256 38974cc16e90e77ac1553bedf6907ff2eb53f7689df00a9a82668d11574f0421 (locked, statement_lock.py check: match true).")),
        rec("SSA-C-0002", "C", "argument",
            "Adversarial agent audit of the reduction in the openai/math preprint 'Triangular minimality for planar Coulomb renormalized energy' (AI-generated, not peer reviewed), Sections 2-5: of 31 numbered steps (10 in Section 2, 7 in Section 3, 8 in Section 4, 6 in Section 5) plus 14 certificate-stage rows, none was classified GAP; all were CONFIRMED; one context citation (LRY2018 'Lemma 3 and Appendix A') is a numbering pin that does not match arXiv:1701.09064v3. The audit re-derived each step by hand and read the cited statements (SS2012 Thm 1, Lemma 4.7, Prop 4.9; BS2018 Thm 1.5) but not their proofs. Not exhaustive: see SSA-C-0004. This is not a proof and not peer review.",
            ["SSA-L-0001", "SSA-L-0002", "SSA-L-0003", "SSA-L-0004"],
            arg([DATA / "REDUCTION_AUDIT.md"],
                "Step tables R1-R10, G1-G7, K1-K8, T1-T6 and stage table in REDUCTION_AUDIT.md; the verdict column is the audit agent's.")),
        rec("SSA-C-0003", "C", "argument",
            "Scope gloss: this preprint reports an independent reproduction of the finite certificate of the manuscript, an adversarial audit of its reduction (no gap found at the stated depth) and a Lean statement of the conjecture. It does not prove, verify or refute the Sandier-Serfaty conjecture; every statement about the conjecture rests on the openai/math manuscript (AI-generated, not peer reviewed), on the cited literature (Tier L, statements read, proofs not re-checked) and on the certificate run. The conjecture was open in the human literature (SS2012, BS2018, BHS2012); we did not search for later resolutions.",
            ["SSA-C-0001", "SSA-C-0002", "SSA-L-0001", "SSA-L-0004", "SSA-L-0005"],
            arg([DATA / "WORK1.md"], "Scope statement; the corpus README says the wrapper does not read the manuscript and the finite checks rely on its analytic bounds.")),
        rec("SSA-C-0004", "C", "argument",
            "Limits of the audit (CANNOT_ASSESS): exhaustive code-to-formula equivalence (the spline pieces on [b,p) and (R_0,l], i.e. the inner S-cutoff, the P/Q extension and the tau blending, and the grid-stage values gmin, drneg, L_1-L_4 and the Hessian hulls rest on code reading only; jet pow/log/sqrt, cpol and hor were not read line by line); runtime trust (compiler, Boost, OpenMP, hardware); the internal proofs of SS2012 Thm 1, Lemma 4.7, Prop 4.9 and BS2018 Thm 1.5; no negative control has exercised inside_hess, calcLam or core_test; the strong minimum principle used in Lemma geo:separation has no verified reference; the calibration check 6K+lambda+2 pi mu is blind to errors in lambda and mu individually.",
            ["SSA-C-0002"], arg([DATA / "REDUCTION_AUDIT.md"], "Section 6 of REDUCTION_AUDIT.md.")),
        rec("SSA-C-0005", "C", "argument",
            "Tier scope of the LeanFlow certificate: SSA-A-0007 certifies arithmetic about the printed outward-rounded 1e-7 integers (floor/ceil of the exact 144-bit endpoints) of the positive run; it does not show that the C++ program computed those integers from the manuscript's formulas, nor that the formulas are the manuscript's inequalities. Scope of 'fail-closed': it is claimed only for sources rendered by the generator (certify()); the exported check_lean_source for arbitrary Lean sources was fail-open before the audit fix (a source with #exit and a forged axiom report returned ok for a false statement; found by the audit, fixed with a per-run sentinel and an #exit refusal) and is not a sandbox even after it.",
            ["SSA-A-0007"], arg([DATA / "leanflow_provenance.json"], "tier_scope field of the LeanFlow result: 'arithmetic statement about the stated numbers only; not the provenance of the numbers'.")),
        # ------------------------------------------------------------------ Tier X
        rec("SSA-X-0001", "X", "numeric",
            "Reproduction of the finite certificate (exact-integer interval arithmetic, not floating point; filed X because the toolchain is trusted): the unchanged corpus sources (sha256 of certificate.cpp, core.hpp, grids.hpp, run-certificate.py equal before and after and equal the record) compiled with g++ 11.4.0 / Boost 1_74 / Python 3.10.12 (the record: g++ 13.3.0 / Boost 1_83 / Python 3.12.13) and run on cores 0-3 with OMP_NUM_THREADS=32: wrapper exit 0, terminal OK, stage validation passed, wall time 490.35 s; all 22 printed pairs equal the saved rows of certificate-record.txt.",
            ["SSA-C-0003"], num([DATA / "s1_positive/run-receipt.json", DATA / "s1_positive/run.log", DATA / "scripts/certify_run_outputs.py", DATA / "lean_data_certificates/summary.json"],
                                 "g++ 11.4.0 -std=c++17 -O3 -fopenmp on certificate.cpp from the openai/math corpus; wrapper run-certificate.py",
                                 note="Depends on the manuscript's analytic bounds (audit SSA-C-0002), which this run does not test.")),
        rec("SSA-X-0002", "X", "numeric",
            "Negative control and dose-response on copies of the certificate (corpus untouched): S1-neg (midpoint remainder constant x24, one line of grids.hpp) is REJECTED (SIGABRT, wrapper exit -6, terminal_OK false, stage validation false; failing assertion (gmin-factor).u>0 && (drneg+er_drop+K).v<0; gmin-factor (-7,162) against (120,162)); variant A (x2) passes end to end (factor (0,20), gmin-factor (114,162)); variant B (er_drop Lipschitz allowance x2) is REJECTED with the same assertion (last row (-9944, 758)). Every pair printed before the edited line is identical to the positive run. A and B predictions were written (20:43:39 UTC) before they finished; the break-even multipliers (about 22.6 and 1.86) are fitted to coarsened printed pairs and the S1-neg numbers were known beforehand. Neither failing variant reached inside_hess.",
            ["SSA-X-0001"], num([DATA / "s1_neg/run-receipt.json", DATA / "s1_neg/run.log", DATA / "s1_neg/negctl.patch", DATA / "s1_neg/predictions_AB.txt",
                                 DATA / "s1_neg/A_midpoint_x2/run-receipt.json", DATA / "s1_neg/A_midpoint_x2/run.log", DATA / "s1_neg/A_midpoint_x2/grids.patch",
                                 DATA / "s1_neg/B_lipschitz_x2/run-receipt.json", DATA / "s1_neg/B_lipschitz_x2/run.log", DATA / "s1_neg/B_lipschitz_x2/grids.patch"],
                                 "same as SSA-X-0001 with OMP_NUM_THREADS=2 on cores 4-5 (S1-neg, A) and 6-7 (B)")),
        rec("SSA-X-0003", "X", "numeric",
            "Independent calibration check (exact Fractions for the interval, 50-digit mpmath for the values): the certificate's printed lambda, mu, K give 6K+lambda+2 pi mu in [-4.15042141551, -4.15040428896], which contains W(E_tri) = -4.1504128076789633794 from both the BS2018 closed form and an Ewald sum (difference 2.1e-50). Positive controls: SS-normalized Ewald values -0.20108945 (triangular) and -0.1957972 (square) match SS2012 Remark 1.5; C from BS Thm 1.5 equals C_BHS to 4.0e-51. Negative controls outside the interval: square lattice -4.11716061233, no 2 pi scaling -0.201089447612, 1/4 log 2pi shift dropped -1.26348226266. The combination is blind to errors in lambda and mu individually.",
            ["SSA-L-0004"], num([DATA / "s2_audit/calibration_check.py", DATA / "s2_audit/calibration_check.out.json"], "AutoevolveAI .venv python -I, mpmath 50 digits, fractions.Fraction (S2 audit stage)")),
        rec("SSA-X-0004", "X", "numeric",
            "Independent re-implementation of lambda, mu, K from the manuscript's TeX formulas only (mpmath, 45-digit Gauss-Legendre): lambda = -6.73002928856, mu = 0.413883384579, K = -0.00348158666, each inside the certificate's printed pair; G(p,x_0) = -1.008e-53 (a positive control: it is 0 by the definition of mu) and 6K+lambda+2 pi mu - W(E_tri) = -1.034e-25. Negative controls outside the printed pairs: no angular term e gives lambda -6.75295 and K -0.0039749; dropping mode m=1 gives lambda -6.76510 and K +0.000526. Independent B(l) = 1.04646435626 inside the printed pair (1.0464643, 1.0464644), |c_1| = 0.63469 < 1; controls: dropping m=1 gives 1.0827, a wrong lattice scale 1.0278. An earlier 25-digit tanh-sinh run cancelled catastrophically (our script's defect) and was replaced. Covers [p,R_0] only, not the spline pieces below p or above R_0.",
            ["SSA-X-0003"], num([DATA / "s2_audit/constants_reimpl.py", DATA / "s2_audit/constants_reimpl.out.json", DATA / "s2_audit/bl_check.py", DATA / "s2_audit/bl_check.out.json"], "AutoevolveAI .venv python -I, mpmath (S2 audit stage)")),
        rec("SSA-X-0005", "X", "numeric",
            "Exact-rational checks of the hand constants of Section 5, the Appendix rational propagation and the domain facts of Sections 6-7 (e.g. 25.4446 < 25.445; 19977 < 20000; T_0 = 1.5511e-21 < 1.56e-21; exact partial sum 1.6503e-21 < 2e-21; F(A,4A) = A(56264180+104A); 4 b^2 * 3.1416 = 0.9999684 < 1); the four tightened negative controls fail as designed.",
            [], num([DATA / "s2_audit/tail_constants.py", DATA / "s2_audit/tail_constants.out.json"], "AutoevolveAI .venv python -I, fractions.Fraction, sympy (S2 audit stage)")),
        rec("SSA-X-0006", "X", "numeric",
            "LeanFlow applied to the S1-neg run's printed pairs: the 10 assertions about them are 'rejected' (Lean's decide rejects 3 of them as false: the three that contain gmin-factor; a decide rejection is a tier X observation, not a kernel-checked negation); 7 are accepted. Control row; a failed decide is a rejection, not a kernel-checked negation of anything about the manuscript.",
            ["SSA-A-0007", "SSA-X-0002"], num([DATA / "lean_data_certificates/result_negctl_run.json", DATA / "lean_data_certificates/claim_negctl_run.json", DATA / "lean_data_certificates/summary.json"],
                                               "LeanFlow certify() with core Lean 4.34.1 decide", failed_assertions=lf_neg["failed"], status=lf_neg["status"])),
        rec("SSA-X-0007", "X", "numeric",
            "LeanFlow Lean data-certificate generator, fail-closed for generator-rendered sources (commit 84e0c2899830fba671022eefcd408af9ecd565c8 = sentinel fix 2c168be2de8104dddc48daecee1423c8d8f076b7 plus a docstring/documentation follow-up, on top of 542cea97aa78e30d8935ec81278aeb697a9f5dc7, branch feat/lean-data-certificates-2026-10-25, local, not pushed): AUDIT FINDING (B2) at the pre-fix commit: check_lean_source (exported library function, not the certify()/CLI path) returned status ok / verified true for the false statement (3:Int) < 2 when the source was a custom axiom, a forged #eval IO.println axiom report and #exit (#exit skips the appended #print axioms; its warning was not rejected); controls in the same probe: clean decide ok, cheat alone custom-axiom, cheat + forged report axiom-report-ambiguous, cheat + #exit axiom-report-missing. FIX: a per-run random sentinel is appended after the audit lines and must appear exactly once after the last report, and the #exit warning is refused (exit-command); the probe now returns error / exit-command and the four controls are unchanged; 6 new tests. certify() was not affected (names regex-checked, labels single-line comments; audit probe_certify_inject) and its 13/13 and 3/10 outcomes were re-run unchanged. pytest gave 82 passed at S4 and at the paper stage (pre-fix) and gives 88 passed after the fix (84 core-Lean/pure-Python incl. a 300-example Hypothesis rendering-vs-Fraction-oracle property, 4 pinned against Lean 4.34.1 + Mathlib); each listed failure mode (missing toolchain/workdir/build target, non-zero rc, signal, no axiom report, timeout, memory cap, sorry, sorryAx, custom axiom, native_decide, forged axiom report, invalid claim, internal exception, oracle disagreement) returns status != ok. Finding: on Lean 4.34.1 native_decide is reported as t._native.native_decide.ax_1_1, not Lean.ofReduceBool. A lying toolchain cannot be detected.",
            [], num([DATA / "leanflow_provenance.json", DATA / "leanflow_pinned_tests.log", RERUN / "leanflow_pytest.txt", RERUN / "leanflow_pytest_before_fix_commit542cea9.txt",
                 DATA / "leanflow_exit_probe/probe_exit_forge.py", DATA / "leanflow_exit_probe/probe_exit_forge.out.json", DATA / "leanflow_exit_probe/probe_exit_forge.after_fix.json",
                 DATA / "lean_data_certificates_after_fix/summary.json"], "pytest (AutoevolveAI .venv python, PYTHONPATH from pyproject) on the LeanFlow worktree; probe_exit_forge.py")),
        rec("SSA-X-0008", "X", "numeric",
            "Paper-stage reruns by the same AI pipeline (not producer != verifier): the Lean statement module recompiles with rc 0 (8.2 s) and its 10 axiom lines are identical to the S3 transcript; the controls file recompiles with rc 0 and #print axioms shows sorryAx and the planted axiom; the sha256 of both files equals the locked values and statement_lock.py check gives match true.",
            [], num([RERUN / "compile_statement.json", RERUN / "compile_controls.json", RERUN / "statement_lock_check.txt", DATA / "STATEMENT_LOCK.json"],
                    "lean_pinned.py compile on cores 4-7; statement_lock.py check")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": claims}, indent=1, ensure_ascii=False))
    tiers = {t: sum(1 for c in claims if c["tier"] == t) for t in "ALCX"}
    print(f"claims {len(claims)} {tiers}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
