"""Build the Elenchus claim ledger for the PH-2 validated Robertson enclosure paper (papers/ph2_validated_robertson).

Modelled on papers/ge2_three_species_bistability_census/ledger/build_ledger.py. Tier discipline: a claim may not be filed above anything in
its depends_on; the kind caps the tier (lean_axioms A, citation L, argument C, numeric X). No Tier A row: there is no Lean in this paper.
Tier X rows are standalone (a C claim never depends on an X claim). The gate field audit stays null.
Run:  python3 -I build_ledger.py     (standard library only; empty ledger/evidence/ first)
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
EV = HERE / "evidence"
DATA = PAPER / "data"
SRC_COMMIT = "(lane records of PH2, rusty-SUNDIALS af4886f2 for the Rust port; paper and data uncommitted at writing)"


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


def cite(source: str, where: str, text: str, note: str) -> dict:
    return {"kind": "citation", "source": source, "where": where, "text": text, "note": note}


def arg(subtier: str, text: str, files: list[Path], instrument: str) -> dict:
    return {"kind": "argument", "subtier": subtier, "text": text, "files": [fref(f) for f in files],
            "instrument": instrument, "source_commit": SRC_COMMIT}


def num(files: list[Path], note: str) -> dict:
    return {"kind": "numeric", "files": [fref(f) for f in files], "note": note, "source_commit": SRC_COMMIT}


def main() -> int:
    L, A, P = DATA / "logs", DATA / "code_auditor", DATA / "code_producer"
    c = [
        rec("PH2-L-0001", "L", "citation",
            "Validated stiff integration, taken as stated and at the depth read: Nedialkov-Jackson overview of validated interval-Taylor / Hermite-Obreschkoff methods (wrapping effect as a stability question; truncation-error formulae make validated stiff methods hard), "
            "read at snippet/abstract level; Neumaier's logarithmic-norm enclosures (arnold-neumaier.at/ms/ode.pdf, ivpBounds.pdf), secondary; Sandretto-Chapoutot DynIBEX validated Runge-Kutta incl. implicit Radau, arXiv:1804.04847, abstract read; "
            "arXiv:2604.19068 (Taylor tube method) listed by search, not read. VNODE-LP, CAPD, COSY, Ariadne, Flow*, VSPODE papers were not individually checked.",
            [], cite("Nedialkov-Jackson; Neumaier; arXiv:1804.04847; arXiv:2604.19068", "see statement", "see statement",
                     "PRIOR_ART.md and AUDIT.md section 6 (searches 2026-11-11 and 2026-11-14); full texts not read; entries written from the search record")),
        rec("PH2-L-0002", "L", "citation",
            "Textbook and documentation statement, taken as stated: BDF/CVODE error control is local, there is no global error guarantee, and the global error need not be proportional to the tolerance (Hairer-Wanner II Sec. IV.8; SUNDIALS documentation).",
            [], cite("Hairer-Wanner, Solving ODEs II, IV.8; SUNDIALS documentation", "see statement", "see statement",
                     "cited from the prior-art screen (PRIOR_ART.md); not re-read in this session; the Hairer-Wanner entry is from memory")),
        rec("PH2-L-0003", "L", "citation",
            "Reference solutions of the Bari stiff test set for Robertson were computed with RADAU in double precision at tight tolerance and are not validated (secondary reports).",
            [], cite("Mazzia-Magherini Test Set for IVP Solvers (archimede.uniba.it/~testset)", "ROBER entry, as reported secondarily", "see statement",
                     "SECONDARY in PRIOR_ART.md; the test set pages were not read")),
        rec("PH2-C-0001", "C", "argument",
            "Step theorem. For a quadratic planar field f, a polynomial reference q, an invertible P, defect bound dbar >= sup ||P^-1 (f(q)-q')||, a box U containing every segment [q(t), q(t)+Pw] with |w| <= rho, and nu >= sup_U lambda_max(sym(P^-1 J P)): "
            "if (eps0 + dbar h) exp(max(nu,0) h) < rho then the solution exists on [0,h] and ||z-q||_P <= eps0 e^{nu t} + dbar int_0^t e^{nu s} ds. Proof by the first-exit argument and f(z)-f(q) = J(q+e/2) e, exact because J is affine; the defect is an exact polynomial (no remainder). "
            "The code (ph2_enclose.py, lines 77-88, 98-113, 187-255) implements the obligations; the auditor read each obligation (defect, one-sided Lipschitz, bootstrap, jump and basis change, output, rounding, resume) and judged them discharged. The proof is in prose, not formalised.",
            [], arg("C-prose-proof", "Prose proof in Section 2 of the paper, audited line by line against the code (AUDIT.md section 2).",
                    [P / "ph2_enclose.py", DATA / "AUDIT.md", DATA / "PREREG_ITEM.md"], "Sage 9.5 Arb RealBallField(160); numpy only for the basis choice")),
        rec("PH2-C-0002", "C", "argument",
            "Controls. Positive: the stiff linear system (exact solution known in balls) and the logistic equation are contained at all tested times at p=24 and p=6. Negative: with the defect term dropped (p=6) containment is lost at every time for both systems. "
            "The (1+1e-6) shift is rejected for the linear y1 and both logistic components at p=24 but never for the linear y2 (relative width ~3e7): adjudicated as a test without power, not a soundness failure. "
            "controls.json was produced by an earlier code version; the auditor's rerun on the final code gives the same verdicts.",
            ["PH2-C-0001"],
            arg("C-controls", "Controls run with the producer's code (controls.py) and rerun by the auditor on the final ph2_enclose.py.",
                [L / "controls.json", L / "controls.log", A / "ctrl_rerun.json", A / "ctrl_rerun.log", P / "controls.py"], "same code as the enclosure")),
        rec("PH2-C-0003", "C", "argument",
            "Enclosure. Under the assumptions that Arb (Sage 9.5) ball arithmetic is correct and the step theorem holds, the solution of Robertson's problem (k=1/25, 1e4, 3e7; y(0)=(1,0,0)) lies in the exact-rational boxes of enclosures.json at t = 0.1, 0.4, 1, 4, 10, 40, 100, 400, 1000, 4000, "
            "with relative width <= 1e-6 required and <= 5.99e-10 reported (y2 at t=4000); 2,850,083 steps, 8.31 core-hours, stopped on the CPU cap (outcome PARTIAL; T=40000 not reached). "
            "Independently confirmed at t = 1, 10, 40 only (PH2-C-0004).",
            ["PH2-C-0001", "PH2-C-0002"],
            arg("C-validated", "Ball-arithmetic evaluation of every obligation of the step theorem, chained across steps with exact rational states; checkpoints resumable and valid at every restart.",
                [DATA / "enclosures.json", DATA / "RESULT.md", DATA / "result.json", L / "robertson_run.log", L / "enclosure_ckpt.json.SHA256.txt", L / "result_json_hash_check.txt"],
                "Sage 9.5 Arb; checkpoint file (13 MB) not shipped, hash stored")),
        rec("PH2-C-0004", "C", "argument",
            "Independent re-derivation at t = 1, 10, 40. The auditor's Lohner interval Taylor integrator (MPFI, 128 bits, order 18, no logarithmic norm, no producer step logic) produced boxes lying inside the producer's boxes on all three components at t=1, 10 and 40 "
            "(midpoints agree to about 1e-26 to 1e-30; auditor radii 1e3 to 1e8 times narrower; at t=10 y2 the producer's midpoint lies outside the auditor's narrower box, consistent with inclusion). No box was compared at t = 0.1, 0.4, 4.",
            ["PH2-C-0003"],
            arg("C-independent", "Exact-rational comparison script compare.py (the auditor's), rerun by the writer on the lane's enclosures.json; output saved.",
                [A / "aud_lohner.py", A / "compare.py", L / "auditor_aud_encl.json", L / "compare_py_output.txt", A / "aud_encl.log", DATA / "AUDIT.md"], "Sage 9.5 MPFI RealIntervalField(128); Python fractions")),
        rec("PH2-C-0005", "C", "argument",
            "True global error of the rusty-SUNDIALS cvode crate (a Rust port of CVODE, NOT C CVODE; HEAD af4886f2, BDF, Newton, dense LU, analytic Jacobian, scalar atol) against the enclosure: 120 error intervals (4 rtol x 10 output times x 3 components), "
            "by exact ball subtraction of the solver's doubles from the boxes. rtol 1e-4, 1e-6, 1e-8 use atol = 1e-3 rtol; rtol 1e-10 uses atol = 1e-10 (non-preregistered; the preregistered atol 1e-13 run failed with ErrTestFailure). "
            "Largest error over the ten times in units of rtol*|y| for (y1,y2,y3): 2.7, 4.1, 2.2 (1e-4); 8.1, 10.9, 8.2 (1e-6); 16.6, 20.3, 13.8 (1e-8); 136, 169, 486 (1e-10).",
            ["PH2-C-0003"],
            arg("C-comparison", "Interval error computation (finalise.py) and a writer recomputation from comparison.json and enclosures.json (analyse.py), output saved.",
                [DATA / "comparison.json", DATA / "cvode_runs.json", L / "cvode_raw.jsonl", P / "finalise.py", P / "rob_runner" / "src" / "main.rs", P / "rob_runner" / "Cargo.toml", L / "analyse_output.txt"],
                "Rust cvode crate output as printed shortest round-trip doubles; Sage balls")),
        rec("PH2-C-0006", "C", "argument",
            "For y2 the preregistered 'provably exceeds tolerance' flag is never raised only because the tolerance for y2 (<= 3.6e-5) is atol-dominated (largest error / atol = 0.16); against rtol*|y2| alone the port's error is up to 4.1x (1e-4), 11x (1e-6), 20x (1e-8), 169x (1e-10, t=4000) the relative tolerance. "
            "The flag compares a global error with a local-error tolerance scale; it documents the global error and is not a breach of the solver's contract. For this port, these settings and this problem only.",
            ["PH2-C-0005", "PH2-L-0002"],
            arg("C-atol-dominance", "Direct arithmetic on the error intervals; the audit reproduced the 169x/20x/11x/4.1x figures and the writer's analyse.py reproduces them.",
                [DATA / "comparison.json", L / "analyse_output.txt", DATA / "AUDIT.md", DATA / "RESULT.md"], "Python arithmetic on comparison.json")),
        rec("PH2-C-0007", "C", "argument",
            "HEADLINE. A validated enclosure of Robertson's problem at ten output times from 0.1 to 4000 (relative width <= 1e-6 required, <= 6e-10 reported), rigorous under the stated assumptions (Arb correct; log-norm step theorem proved in prose, not formalised), "
            "independently re-derived by a different method at t = 1, 10, 40 only; and the true error of a Rust port of CVODE (not C CVODE) for rtol 1e-4..1e-10 against it, including the atol-dominance finding for y2. "
            "Producer and one independent audit are AI agents; no human audit; the preregistration was first committed after the run started (mtimes and self-hash only); no Lean.",
            ["PH2-C-0001", "PH2-C-0002", "PH2-C-0003", "PH2-C-0004", "PH2-C-0005", "PH2-C-0006"],
            arg("C-assembly", "Assembly of the step theorem, controls, enclosure, independent check and comparison (all C) as in Sections 2 to 7.",
                [DATA / "RESULT.md", DATA / "result.json", DATA / "AUDIT.md"], "none")),
        rec("PH2-X-0001", "X", "numeric",
            "NOT independently confirmed: the enclosure for 40 < t <= 4000. The auditor's integrator reached t=40 only; the non-rigorous double-precision Radau cross-check at t=4000 agrees to ~1e-14 relative but lies OUTSIDE the producer's y1 and y3 boxes (offset ~8e-15 against radius ~5e-16, within the Radau runs' own spread) and cannot test the box. "
            "Single implementation plus code audit only.",
            [], num([A / "radau.json", A / "radau_check.py", DATA / "AUDIT.md"], "Radau output and AUDIT.md section 3")),
        rec("PH2-X-0002", "X", "numeric",
            "NOT established: the provenance of the Rust binary (Cargo path dependency; HEAD af4886f2 recorded, not pinned); the correctness of Arb/Sage 9.5 beyond the MPFI cross-check to t=40; the step theorem is not formalised (no Lean). "
            "'Formally verified' is NOT claimed. NOT a statement about LLNL C CVODE, general stiff problems, or t >= 1e4.",
            [], num([P / "rob_runner" / "Cargo.toml", DATA / "result.json", DATA / "AUDIT.md"], "AUDIT.md section 5 and 'Remaining unverified'")),
        rec("PH2-X-0003", "X", "numeric",
            "The cvRoberts_dns values (t = 0.4, 4, 40, five digits) in RESULT.md were recalled, not fetched, and are SOLVER OUTPUT at rtol=1e-4 with vector atol, not the true solution; no conclusion is drawn from them.",
            [], num([DATA / "RESULT.md", DATA / "AUDIT.md"], "RESULT.md secondary values section; AUDIT.md section 5")),
        rec("PH2-X-0004", "X", "numeric",
            "Novelty is NOT a certified fact: 'to our knowledge' no validated Robertson enclosure to t >= 4000 and no CVODE-versus-enclosure study was found, in a limited search (2 web + 2 alphaXiv queries at scouting, repeated at audit); VNODE-LP, CAPD, COSY, Ariadne papers not individually checked; authors not contacted; no priority claim. "
            "Also unverifiable from version control: the preregistration freeze (PREREG_ITEM.md first committed 2026-11-13, after the 2026-11-11 launch; mtimes and a self-hash only).",
            [], num([DATA / "PRIOR_ART.md", DATA / "AUDIT.md", DATA / "PREREG_ITEM.md", DATA / "PREREG_ITEM.md.sha256"], "PRIOR_ART.md; AUDIT.md sections 1 and 6")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
