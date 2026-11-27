"""Build the Elenchus claim ledger for the M2 paper (papers/p4_born_stability_jarvis).

Modelled on papers/p5_lonely_runner_ind/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not
be filed above anything in its depends_on, and the kind caps the tier (lean_axioms A, citation L, argument C, numeric X).
An independent AI audit exists (AUDIT.md, ACCEPT_WITH_CORRECTIONS, not a person): Tier A rows carry an ai_audit field and the gate field audit stays null,
so LEDGER_UNAUDITED_TIER_A remains open (exit 1 is the honest state).
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
SUMM = DATA / "summaries"
TOOLCHAIN = ("Lean 4.34.1 + Mathlib d13f23b7 through scripts/certified_numerics/lean_pinned.py (module imports "
             "Mathlib.Tactic; no import Mathlib)")
ALLOW = ["propext", "Classical.choice", "Quot.sound"]
STATUS = ("kernel-checked by the producer; independently recompiled (byte-identical copies) and replayed with leanchecker by a different AI agent instance "
          "(AUDIT.md section 7); NOT run through anse/formal/lean_runner.py, NO statement-lock entry, NO human audit of statement adequacy")
AI_AUDIT = {"auditor": "independent AI audit agent (separate instance, producer != verifier), 2026-10-31", "human": False,
            "report": "papers/p4_born_stability_jarvis/AUDIT.md", "verdict": "ACCEPT_WITH_CORRECTIONS",
            "scope": "own recompile of byte-identical copies under /tmp, #print axioms, leanchecker replay (Probe and Witnesses rc 0, negative control rc 1), escape-hatch grep, "
                     "parsing of all 18 matrices and 12 witnesses and comparison with its own symmetrised literal tensors by jid",
            "not_scope": "the anse/formal/lean_runner.py gate and a statement lock were not run; statement adequacy (that the Lean statements mean what their gloss says) not certified by a person; "
                         "pd_k proves the LDL^T identity and positive pivots, positive definiteness then follows from unit lower-triangularity outside Lean",
            "note": "AI audit, not a person: the gate field audit is left null so LEDGER_UNAUDITED_TIER_A stays open; no statement lock"}
SRC_COMMIT = "abe4718ed552e3c77b7207cadb8095d998e02602"


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


def axiom_lines(path: Path) -> list[str]:
    out = json.loads(path.read_text())["output"]
    lines = [" ".join(ln.split()) for ln in out.splitlines() if "depends on axioms" in ln]
    if not lines:
        raise SystemExit(f"no axiom lines in {path}")
    return lines


def cite(source: str, where: str, text: str, note: str) -> dict:
    return {"kind": "citation", "source": source, "where": where, "text": text, "note": note}


def arg(subtier: str, text: str, files: list[Path], instrument: str) -> dict:
    return {"kind": "argument", "subtier": subtier, "text": text, "files": [fref(f) for f in files],
            "instrument": instrument, "source_commit": SRC_COMMIT}


def num(files: list[Path], note: str) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True, "note": note,
            "files": [fref(f) for f in files]}


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    wit_ax = axiom_lines(LOGS / "lean_witnesses_after_c9.json")
    probe_ax = axiom_lines(LOGS / "lean_Probe.json")
    assert len(wit_ax) == 24 and len(probe_ax) == 2
    c = [
        rec("BM-A-0001", "A", "lean_axioms",
            "BornM2W (Witnesses.lean): 12 theorems notpd_0..notpd_11 of the form exists x, x != 0 and quad S x <= 0 for 12 explicit rational 6x6 matrices S (symmetrised stored decimals of 12 JARVIS-DFT "
            "entries, jid in each comment; 4 of them pass the incorrect linear orthorhombic criterion), and 6 pairs pd_k / pd_k_pivots for 6 further matrices: the LDL^T identity "
            "x^T S x = sum_k d_k (l_k . x)^2 with explicit rational d_k and unit lower-triangular L, and 0 < d_k for every k. quad C x = sum_i sum_j x_i C_ij x_j. "
            "The file now begins with a CC BY 4.0 attribution comment (correction C9) and was recompiled after that edit: rc 0, 24 axiom lines, each within the whitelist. "
            "These are statements about 18 explicit matrices; the step from the pd_k identity to positive definiteness (L unit lower-triangular) is not a Lean theorem. "
            "That the matrices equal the dataset's symmetrised tensors is a Python and hash step (Tier C), checked by the auditor by jid.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output": wit_ax, "allowlist": ALLOW,
                 "compile_transcript": fref(LOGS / "lean_witnesses_after_c9.json"), "axiom_transcript": fref(LOGS / "lean_witnesses_after_c9.json"),
                 "sources": [fref(LEAN / "Witnesses.lean")], "earlier_compile_before_attribution_comment": fref(LOGS / "lean_witnesses.json"),
                 "status": STATUS,
                 "statement_adequacy": "not audited by a person; the statements are about explicit matrices whose match to the dataset the AI auditor checked by jid (18 of 18 identical)"}),
        rec("BM-A-0002", "A", "lean_axioms",
            "BornM2 (Probe.lean): foot_witness, a witness x != 0 with x^T C x <= 0 for the Mouhat-Coudert footnote-26 tensor (C11 = 1/2, C22 = C33 = 1, C12 = -1, C13 = C23 = 0; shear constants not given in the footnote, "
            "set to 1 here), and dia_pd, 578 * sum x_i^2 <= x^T C x for a diamond-type tensor (this does imply positive definiteness in Lean terms). "
            "Controls: Tamper1.lean (wrong witness), Tamper2.lean (lower bound 600 > 578) and Tamper3.lean (altered pivot) are rejected by the kernel (rc 1, errors: unsolved goal 2 <= 0, linarith failure, ring failure); "
            "the auditor's leanchecker negative control on a missing module gives rc 1.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output": probe_ax, "allowlist": ALLOW,
                 "compile_transcript": fref(LOGS / "lean_Probe.json"),
                 "rejections": [fref(LOGS / "lean_Tamper1.json"), fref(LOGS / "lean_Tamper2.json"), fref(LOGS / "lean_Tamper3.json")],
                 "sources": [fref(LEAN / "Probe.lean"), fref(LEAN / "Tamper1.lean"), fref(LEAN / "Tamper2.lean"), fref(LEAN / "Tamper3.lean")],
                 "status": STATUS, "statement_adequacy": "not audited by a person"}),
        # ------------------------------------------------------------------ L
        rec("BM-L-0001", "L", "citation",
            "Mouhat and Coudert, Phys. Rev. B 90, 224104 (2014), arXiv:1410.0065: an unstressed crystal is elastically stable iff the quadratic form E = (1/2) V0 sum C_ij e_i e_j is positive for all e != 0, i.e. the 6x6 stiffness matrix C is positive definite "
            "(all eigenvalues > 0, equivalently all leading principal minors > 0); under load the relevant matrix is B, not C (Eq. 20); the closed-form class conditions (Eqs. 6, 9, 11, 13, 15, 18); Eq. 19 is the linear orthorhombic criterion of Wu et al., "
            "PRB 76, 054115 (2007), which they call incorrect; footnote 26 gives the counterexample C11 = 1/2, C22 = C33 = 1, C12 = -1, C13 = C23 = 0.",
            [], cite("Mouhat, Coudert, PRB 90, 224104 (2014), arXiv:1410.0065; Wu et al., PRB 76, 054115 (2007)", "criterion paragraph; Eqs. 6, 9, 11, 13, 15, 18, 19, 20; footnote 26",
                     "Read by the producer; re-read by the independent AI auditor from the arXiv text on disk, including the footnote-26 values and Eq. 19's attribution",
                     "taken as stated; Wu et al. was not read")),
        rec("BM-L-0002", "L", "citation",
            "Dataset and licence. JARVIS-DFT 3D dataset (figshare article 6815699, DOI 10.6084/m9.figshare.6815699; version 11 is 10.6084/m9.figshare.6815699.v11), file jdft_3d-9-24-2025.json.zip; "
            "the unzipped json has sha256 9dacb55ac8371c7c2bf0332933b55c98e9cca6201e92eb9d6fcd03aab0975907 and the zip's md5 c3179161ef0d029cf1fa70da463aac6e equals the figshare API's computed_md5. "
            "Licence CC BY 4.0 (figshare API, read by the producer before download and again by the auditor). Attribution: Choudhary et al., npj Comput. Mater. 6, 173 (2020), arXiv:2007.01831; "
            "elastic-tensor workflow: Choudhary et al., Phys. Rev. B 98, 014107 (2018), arXiv:1804.01033. Stored units are GPa (the auditor matched five published values of Table S3 to the printed digits). "
            "The dataset is not redistributed here; at most 22 of its tensors appear in the shipped Lean and json files, with an attribution line.",
            [], cite("figshare API record 6815699; Choudhary et al. npj Comput. Mater. 6, 173 (2020), arXiv:2007.01831; arXiv:1804.01033",
                     "figshare metadata (license, computed_md5); Table S3 of arXiv:1804.01033",
                     "Licence and hash read from the figshare API by the producer (2026-10-31, before download) and by the auditor",
                     "the dataset file itself is not shipped; hashes are the only link")),
        rec("BM-L-0003", "L", "citation",
            "Born and Huang, Dynamical Theory of Crystal Lattices (Oxford, 1954), as the source that Mouhat and Coudert cite for the positive-definiteness criterion. Not read by the producer or the auditor; the criterion is taken from Mouhat-Coudert 2014.",
            ["BM-L-0001"], cite("Born, Huang, Dynamical Theory of Crystal Lattices (1954)", "as cited in Mouhat-Coudert 2014", "second-hand only",
                                "not read; listed as an open verification item")),
        # ------------------------------------------------------------------ C
        rec("BM-C-0001", "C", "argument",
            "Headline counts. Of 93,902 records, 59,400 have elastic_tensor = 'na', 34,502 carry a 6x6 list, 179 of these hold NaN or infinity and are excluded: N = 34,323. Reading each stored float as the exact rational of its shortest decimal "
            "and testing S = (C + C^T)/2: 22,842 are positive definite and 11,481 (33.45 %) are not, each of the latter with an exact rational witness x != 0, x^T S x <= 0 (204 of them on the boundary: first non-positive pivot exactly 0). "
            "Three exact methods agree on every one of the 34,323 entries: the producer's LDL^T and Bareiss elimination over Fractions, and the auditor's strict sign alternation of the exact characteristic polynomial (own code). "
            "The auditor re-checked all 11,481 witnesses on its own S (x != 0, x^T S x <= 0, equal to the stored value) and found 0 mismatches over 34,323 entries and 10 fields. sympy leading minors on a 14,615-entry subset agree (0 mismatches). "
            "The auditor's code and per-entry output are not shipped.",
            [], arg("C-exact-rational", "summaries/summary.json (counts), summaries/final_summary.json, logs/run_dataset.log.txt; auditor's reproduction described in AUDIT.md sections 3 and 4.",
                    [SUMM / "summary.json", SUMM / "final_summary.json", LOGS / "run_dataset.log.txt", DATA / "code" / "born_exact.py", DATA / "code" / "run_dataset.py", DATA / "result.json"],
                    "born_exact.py, run_dataset.py (producer, Fractions); auditor's charpoly classification (not shipped)")),
        rec("BM-C-0002", "C", "argument",
            "Null tensors. 234 stored tensors are numerically zero (max |entry| < 1e-6; the largest below the cut is 6.8e-12 and the smallest above is 0.333), all NOT PD. Excluding them, 11,247 of 34,089 (32.99 %) are not PD "
            "(robustly not PD 11,225). 12 tensors have a literal zero row.",
            ["BM-C-0001"], arg("C-exact-rational", "summaries/final_summary.json fields numerically_null_tensors_max_abs_lt_1e-6, exact_NOT_PD_excluding_null; AUDIT.md section 3 (null threshold gap).",
                               [SUMM / "final_summary.json", SUMM / "analysis2.json"], "final_summary.py (producer); auditor's gap check")),
        rec("BM-C-0003", "C", "argument",
            "Rounding robustness (correction C1). Each printed value may vary within +-1/2 unit of its last printed place. Producer (Frobenius sufficient test): ROBUST_PD 22,708; ROBUST_NOT_PD 11,244; undecided 371. "
            "Auditor, exact Rohn (1994) vertex test over the 32 matrices S - T_z D T_z (z_1 = 1): ROBUST_PD 22,809; ROBUST_NOT_PD 11,244; certified truly ambiguous 55 (33 nominally PD, 22 nominally NOT PD); undecided 215, of which 210 are null tensors. "
            "With the half-width floored at 0.05: 22,809 / 11,216 / ambiguous 286 (33 PD + 253 NOT PD) / undecided 12. 33,399 tensors print every entry at 1 decimal; 874 tensors have an entry printed with more than 6 places.",
            ["BM-C-0001"], arg("C-exact-rational", "summaries/summary.json, summaries/analysis2.json (producer, Frobenius); AUDIT.md section 4 table (auditor, Rohn).",
                               [SUMM / "summary.json", SUMM / "analysis2.json", PAPER / "AUDIT.md"], "born_exact.py interval rule (producer); Rohn vertex test (auditor, not shipped)")),
        rec("BM-C-0004", "C", "argument",
            "The incorrect linear orthorhombic criterion (Mouhat-Coudert Eq. 19, applied to all entries regardless of class): 23,184 tensors pass it; 342 (1.00 % of N) pass it yet are exactly NOT PD (328 robustly); "
            "0 fail it while PD (consistent with necessity). Class conditions: on the 30,203 entries to which a closed-form class condition applies, 555 disagree with exact PD of the full tensor (544 class-stable but not PD, 11 class-unstable but PD). "
            "Auditor's split of the 544 by block (correction C3): 184 have a Voigt diagonal entry <= 0, 299 a non-PD normal 3x3 block, 55 a non-PD shear block, 6 fail only through normal-shear couplings; 483 come from stored tensors that violate "
            "the class equalities the formulae assume, 61 from off-diagonal couplings. The VASP-to-Voigt permutation [0,1,2,4,5,3] was confirmed by the auditor (identity map would give 1,046 disagreements).",
            ["BM-C-0001", "BM-L-0001"], arg("C-exact-rational", "summaries/summary.json, summaries/final_summary.json; AUDIT.md sections 2 and 6.",
                                            [SUMM / "summary.json", SUMM / "analysis2.json", PAPER / "AUDIT.md"], "born_exact.py class conditions (producer); block decomposition (auditor, not shipped)")),
        rec("BM-C-0005", "C", "argument",
            "Controls, run and logged before any dataset number: positive (Cu, Si, diamond PD in exact, Bareiss and float; the footnote-26 tensor passes the incorrect linear criterion, fails exact PD, rational witness found; three known-unstable cubic tensors NOT PD); "
            "negative (sign flips of C11 and C44 flip the verdict; symmetry breaking detected; a singular tensor C11 = C12 is NOT PD and rounding-undecided; a tensor 0.1 GPa from the boundary is PD but undecided); "
            "random cross-check LDL^T vs Bareiss on 6,000 random rational matrices, sympy on 400. The producer log has 24 lines, every check PASS and ALL_CONTROLS_PASS True (logs/controls.json is the tracked record; the .log files are untracked and shipped as .log.txt copies, correction C8). "
            "The auditor ran 14 controls of its own (all PASS); it did not re-run the producer's controls.py.",
            [], arg("C-exact-rational", "logs/controls.json, logs/controls.log.txt, AUDIT.md section 3.", [LOGS / "controls.json", LOGS / "controls.log.txt", DATA / "code" / "controls.py"],
                    "controls.py (producer); controls_test.py (auditor, not shipped)")),
        rec("BM-C-0006", "C", "argument",
            "Dataset observations, neutral (the owner has not forwarded these to the dataset authors): 59,400 records with elastic_tensor = 'na'; 179 tensors with NaN or infinity; 234 numerically zero tensors; 12 with a literal zero row; "
            "922 not exactly symmetric (232 of them null tensors; 598 have max |C_ij - C_ji| > 1 GPa, median 19.5 GPa; for 7 the verdict depends on which triangle is mirrored); 874 with an entry printed with more than 6 places; "
            "18 with an entry above 1e4 GPa, smallest float eigenvalue -6.3e5. Read-sanity (a positive control for reading the dataset): Voigt K and G recomputed from the tensor match the stored bulk_modulus_kv / shear_modulus_gv within 1 % for 97.9 % / 98.1 % of entries (median relative error 3e-5).",
            ["BM-C-0001"], arg("C-exact-rational", "summaries/analysis2.json, summaries/final_summary.json, summaries/f1_inspect.json; AUDIT.md sections 3 and 9 (C5).",
                               [SUMM / "analysis2.json", SUMM / "final_summary.json", SUMM / "f1_inspect.json"], "analysis2.py, final_summary.py, inspect_f1.py (producer); asymmetry sizes (auditor)")),
        rec("BM-C-0007", "C", "argument",
            "Provenance of the preregistration (correction C7): prereg_M2.json (sha256 2c3127f9...5d0fb) records written_utc 16:30Z, which is wrong; its file mtime is 16:22:52Z, before the dataset download (16:23:00Z) and all runs (16:24 to 16:37). "
            "The file was committed together with the results (051f87d), so git does not show the order; only the mtimes do. Outcome by the preregistered rule: KEEP. Deviations are logged in RESULT.md (sympy on a subset; post hoc additions; Lean limited to controls plus an 18-entry sample).",
            [], arg("C-audit-report", "AUDIT.md section 1; data/prereg_M2.json; data/RESULT.md deviations.", [DATA / "prereg_M2.json", DATA / "prereg_M2.sha256", PAPER / "AUDIT.md"], "mtime comparison by the auditor")),
        rec("BM-C-0008", "C", "argument",
            "HEADLINE. Under the stated reading (every stored float taken as the exact rational of its shortest decimal; verdict for S = (C + C^T)/2; zero-stress Born criterion), 11,481 of the 34,323 finite 6x6 elastic tensors "
            "of JARVIS-DFT dft_3d (33.45 %; 32.99 % without the 234 null tensors) are not positive definite, each with an exact rational witness, by three exact methods and an independent AI audit. "
            "This is a statement about stored DFT tensors, not about materials: many entries are raw DFT outputs including hypothetical, unrelaxed and dynamically unstable structures, so a substantial fraction is expected; "
            "it does NOT say JARVIS-DFT is wrong and says nothing about any material being unstable in a laboratory. Finite-difference noise, residual stress, magnetism and convergence remain possible reasons for individual entries. "
            "Novelty: to our knowledge no exact-rational Born audit of the whole JARVIS elastic dataset has been published (not an exhaustive search). Filed C because the enumeration is not kernel-checked; Lean covers 18 explicit matrices only.",
            ["BM-C-0001", "BM-C-0002", "BM-C-0003", "BM-C-0005", "BM-A-0001", "BM-A-0002", "BM-L-0001", "BM-L-0002"],
            arg("C-assembly", "Assembly of the exact counts (C), the Lean sample (A) and the literature criterion (L) as in Sections 3 to 5 of the paper.", [DATA / "result.json", DATA / "RESULT.md"], "none")),
        # ------------------------------------------------------------------ X
        rec("BM-X-0001", "X", "numeric",
            "Float pipelines versus the exact verdict: numpy eigvalsh(S).min() > 0 disagrees with the exact verdict on 0 of 34,323 tensors; with absolute tolerance -1e-8 on 236 (all call a not-PD tensor stable; 234 are the null tensors); "
            "with relative tolerance -1e-6 * lambda_max on 3 (2 not null). Reproduced by the auditor with its own numpy call. Float verdicts are not evidence of anything about the exact verdict.",
            [], num([SUMM / "summary.json", SUMM / "analysis2.json"], "float eigenvalue runs; the exact classification does not depend on them")),
        rec("BM-X-0002", "X", "numeric",
            "Context only, no association claimed: among entries with min_ir_mode a negative lowest IR mode is stored for 40 of 480 NOT-PD tensors (8.3 %) versus 221 of 2,959 PD tensors (7.5 %) (2 null tensors among the 480); "
            "NOT-PD fraction is 11.3 % (1,048 of 9,258) for entries with an ICSD id versus 41.1 % (10,199 of 24,831) without. The meaning of min_ir_mode was not verified. "
            "The ehull bins of the producer's RESULT.md (30.3 % vs 33.0 %) are WITHDRAWN (correction C2): the field was not verified to be an energy above hull (median 1.55, ICSD-linked median 1.46); the producer's JSON files still contain those bins.",
            [], num([SUMM / "analysis2.json", SUMM / "final_summary.json"], "context counts; ehull deliberately not used")),
        rec("BM-X-0003", "X", "numeric",
            "NOT done or not verified: the binding anse/formal/lean_runner.py gate and a statement-lock entry for the Lean statements; the auditor did not re-run the producer's controls.py (it ran its own); Born-Huang 1954 not read; "
            "the physical meaning of the JARVIS fields ehull and min_ir_mode and the convergence state of individual calculations; Lean certificates for the other 11,469 unstable entries and for a larger stable sample (verified in Python only); "
            "repository guards antigravity_guard.py, test_rigor_guard.py and pytest tests/ were not run for this paper; no human audit. Recorded so the absences are explicit.",
            [], num([PAPER / "AUDIT.md"], "list of open items from AUDIT.md section 10; no run is claimed")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
