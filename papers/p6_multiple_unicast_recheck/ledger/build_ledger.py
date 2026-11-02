"""Build the Elenchus claim ledger for the AIC-MUC9 paper (papers/p6_multiple_unicast_recheck).

Modelled on papers/p6_luo_counterexample_recheck/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not be filed above
anything in its depends_on; the kind caps the tier (citation L, argument C, numeric X). No Lean, so no Tier A row. An AI audit exists
(AUDIT.md, ACCEPT_WITH_CORRECTIONS), not a person. This is a recheck of a claim by others (Braverman and He, arXiv:2610.10108); no novelty claim.
Run:  python3 -I build_ledger.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
EV = HERE / "evidence"
D = PAPER / "data"
SRC_COMMIT = "a06dcfd"  # commit holding the producer lane record (PREREG_ITEM.md and RESULT.md in one commit); the audit and this paper are uncommitted


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
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True, "note": note,
            "files": [fref(f) for f in files]}


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    C = D / "code"
    DT = D / "data"
    LG = D / "logs"
    AC = D / "audit" / "code"
    AO = D / "audit" / "outputs"
    c = [
        rec("MUC-L-0001", "L", "citation",
            "Braverman and He, 'The Multiple Unicast Conjecture is False', arXiv:2610.10108 v1 (7 Oct 2026, unrefereed; title and authors checked on arxiv.org 2026-11-02): PG(2,9) incidence graph minus 175 edges (735 edges), 157 unicast sessions all at distance 5, a deterministic causal GF(9) code of common rate 1 (Section 4), versus routing/fractional flow at most 735/785 = 147/157; Section 3 gives a non-deterministic example (166 deleted edges, 744 edges, 744/830) that was not recomputed. Taken as stated. The third-party full text and its Appendix A lists are not shipped.",
            [], cite("arXiv:2610.10108v1", "Sections 1-4, Appendices A-B", "Read by the producer and the independent AI auditor", "taken as stated; full text and Appendix A lists not shipped")),
        rec("MUC-L-0002", "L", "citation",
            "Zhang, Li and Li, 'Network Coding Can Beat Routing in Undirected Multiple-Unicast Networks', arXiv:2610.09367 v1 (7 Oct 2026; title and authors checked on arxiv.org 2026-11-02). Abstract and introduction read by the auditor: an independent, very different counterexample (binary linear block code on a max-degree-3 network with leaf terminals, built from a reversible circuit, own tensor amplification); it states a Lean formalization, which was NOT checked here. Follow-ups 2610.20079, 2610.33655 and attempts 2608.06042, 2608.06070 were found but not read; the OpenAI 'Finite tensor savings and exact Fourier circuits' preprint was not found or opened; the kingy.ai and MathWorld statements cited in RESULT.md are unverified.",
            [], cite("arXiv:2610.09367v1", "abstract, introduction", "Read by the independent AI auditor", "Lean formalization not checked")),
        rec("MUC-L-0003", "L", "citation",
            "Not verified, taken from the literature: that the Section 2 model of 2610.10108 (edge split into two directed edges, H(X->)+H(X<-) <= c(e), causal computation, throughput r with H(m_i) >= r d_i c*) is the model of the Li-Li / Harvey-Kleinberg-Lehman (LL04, HKL04) conjecture; the Braverman-Garg-Schvartzman 2017 (BGS17) amplification and Corollary 1.2; Section 3's example (166/744/830). The authors' verifier and repository were not run.",
            [], cite("arXiv:2610.10108v1 Section 2, Corollary 1.2; LL04; HKL04; BGS17", "model and amplification", "background, not re-read by the producer or the auditor", "Tier L, unverified")),
        rec("MUC-C-0001", "C", "argument",
            "Graph facts (producer's own code; auditor's independent code): PG(2,9) incidence graph on 182 vertices, 10-regular, 910 edges, bipartite, girth 6; |R| = 175 distinct indices in [7,907], C and J disjoint 9-subsets of R, |B| = 157, pi a permutation of 0..181; G = H - R has 735 edges and is connected; on the full 910-edge orientation d-(v) = d+(v) = 5 and d+_C(v) = d-_J(v) at all 182 vertices; 157 sessions from 66 distinct sources, every BFS distance exactly 5, sum 785; 735 < 785 and 735/785 = 147/157 in Fraction arithmetic. The Appendix A lists were re-extracted by the auditor with pdftotext -layout and PyMuPDF word boxes (they agree element by element after dropping the page-number footer 13); their hashes equal the producer's transcription. The lists themselves are third-party and not shipped (hashes only, data/THIRDPARTY_FETCH.txt).",
            ["MUC-L-0001"],
            arg("C-exact-integer", "data/code/checks.py, muc9lib.py, main.py, data/data/main_results.json, data/logs/main.log, data/audit/code/extract.py, audit.py, data/audit/outputs/audit.log.txt",
                [C / "checks.py", C / "muc9lib.py", C / "main.py", DT / "main_results.json", LG / "main.log", AC / "extract.py", AC / "audit.py", AO / "audit.log.txt"], "main.py, checks.py (producer, numpy/python); audit.py, extract.py (auditor, Sage, pdftotext, PyMuPDF)")),
        rec("MUC-C-0002", "C", "argument",
            "GF(9) = GF(3)[i]/(i^2+1): the producer's hand-built tables satisfy the field axioms exactly (associativity, distributivity, commutativity, inverses, no zero divisors, cyclic multiplicative order 8, characteristic 3); the auditor used Sage GF(9, modulus=x^2+1) and a GF(3) 2x2-block cross-check (ring homomorphism checked on all of F9). All 182 local codes are 5-dimensional MDS: all 252 five-subsets of the 10 incident positions are independent, at every vertex (producer and auditor).",
            ["MUC-C-0001"],
            arg("C-exact-finite-field", "data/code/muc9lib.py, main.py, data/data/main_results.json, data/audit/code/audit.py, data/audit/outputs/audit.log.txt",
                [C / "muc9lib.py", C / "main.py", DT / "main_results.json", AC / "audit.py", AO / "audit.log.txt"], "muc9lib.py (producer); audit.py with Sage (auditor)")),
        rec("MUC-C-0003", "C", "argument",
            "Rank: the 910x910 parity matrix has rank 744 over F9 (producer's Gaussian elimination; auditor's Sage; the GF(3) 2x2-block version has rank 1488 = 2 x 744), so dim W = 166 exactly; dim W_C = 157; rank [P; e_C; e_B] = 910, so the restriction of W_C to the session edges B is injective and W_C is isomorphic to F9^157.",
            ["MUC-C-0002"],
            arg("C-exact-finite-field", "data/code/main.py, data/data/main_results.json, data/audit/code/audit.py, data/audit/outputs/audit.log.txt",
                [C / "main.py", DT / "main_results.json", AC / "audit.py", AO / "audit.log.txt"], "main.py (producer); audit.py (auditor, Sage)")),
        rec("MUC-C-0004", "C", "argument",
            "Appendix B (auditor): the 166 retained bidegree-(4,4) monomials (225 - 30 - 30 + 1 = 166) give assignments h(p^3, l) that are independent (rank 166) and satisfy every local code; all 225 monomials span only rank 166. So dim W = 166 exactly: the paper's lower bound is tight on this instance, and W equals the span of the Appendix B assignments here. The paper's analytic proof was not re-derived.",
            ["MUC-C-0003"],
            arg("C-exact-finite-field", "data/audit/code/appB.py, data/audit/outputs/audit.log.txt",
                [AC / "appB.py", AO / "audit.log.txt"], "appB.py (auditor, Sage)")),
        rec("MUC-C-0005", "C", "argument",
            "Causal pi-ordered interpolation (producer's and auditor's own implementations): at each vertex exactly 5 independent known values (incoming physical edges, own B-sources, C = 0); interpolate, emit, check consistency and agreement at both ends of J edges, decode at t_q. All 157 of 157 unit-vector inputs decode correctly; the map is F9-linear in the input, so the unit vectors cover every input exactly (the exact argument is Tier C; this is the audit's correction 3). The random-input trials (producer 1000/1000, auditor 200/200) are a redundant X check, see MUC-X-0001.",
            ["MUC-C-0003"],
            arg("C-exact-finite-field", "data/code/main.py, muc9lib.py, data/data/main_results.json, data/audit/code/audit.py, data/audit/outputs/audit.log.txt",
                [C / "main.py", C / "muc9lib.py", DT / "main_results.json", AC / "audit.py", AO / "audit.log.txt"], "main.py (producer); audit.py (auditor)")),
        rec("MUC-C-0006", "C", "argument",
            "Flow: the length function l_e = 1 gives the exact upper bound 735/785 = 147/157 on the undirected unit-capacity max concurrent flow. The auditor built an exact rational flow of value 147/157 on shortest paths with every edge saturated (66 source groups, 31,899 shortest-path-DAG arc variables, HiGHS support of 3,328 columns of full column rank, re-solved over Q in Sage, re-verified in Python Fraction: conservation with demand 147/157 for every session, every edge load = 1, all flows >= 0; run twice, same support and denominators; certificate lp_certificate.json, 3,328 arc flows, sha256 5f29f1accf037cf1c5b135c777d2eca62f7b6499842d717d4c9b00bd96a89ed3; the file itself is WITHHELD because its edge support determines the third-party deleted-edge set R; it is regenerated by data/audit/code/lp_exact.py from the locally extracted lists, see data/audit/outputs/lp_certificate_summary.json and data/THIRDPARTY_FETCH.txt). So the optimum is exactly 147/157. The producer's HiGHS value 0.9363057324840819 versus 147/157 = 0.9363057324840764 was only a floating-point agreement.",
            ["MUC-C-0001"],
            arg("C-exact-rational", "data/audit/code/lp_exact.py, data/audit/outputs/lp_exact.log.txt, lp_certificate_summary.json, data/code/lp.py, data/data/lp_result.json",
                [AC / "lp_exact.py", AO / "lp_exact.log.txt", AO / "lp_certificate_summary.json", C / "lp.py", DT / "lp_result.json"], "lp_exact.py (auditor, scipy HiGHS then Sage exact solve, Fraction check); lp.py (producer, HiGHS)")),
        rec("MUC-C-0007", "C", "argument",
            "Rate (auditor's argument, written down, not formalised): under the paper's own Section 2 definition with uniform x_q in F9, d_i = 1, c(e) = 1, c* = log 9, one execution already gives H(m_i) = log 9 >= r c* with r = 1, and each physical edge carries one symbol in one direction only, so H(X->)+H(X<-) <= log 9 = c(e) c*. Causality and correctness are what MUC-C-0005 checks. Pipelining is needed only for the time-slot wording of Section 4. That the Section 2 model is the LL04/HKL04 model is Tier L (MUC-L-0003).",
            ["MUC-L-0001", "MUC-C-0005"],
            arg("C-argument", "data/AUDIT.md section (1)", [D / "AUDIT.md"], "auditor's argument; AUDIT.md")),
        rec("MUC-C-0008", "C", "argument",
            "Controls (run before the headline). Positive: directed butterfly, GF(2) XOR code decodes all 4 inputs at rate 1 while the LP gives routing 0.5; undirected 4-cycle with two opposite sessions LP = 1.0, single edge 1.0, path with two sessions 0.5; the true field passes all field checks. Negative: wrong field relations (t^2 = 0 and t^2 = 1) fail; tampered R (restore edge 7, delete edge 0) violates d- = d+ = 5 at 2 vertices and 20/20 causal trials fail; renormalising (lambda, mu) at all neighbours of one vertex: 20/20 fail; adding 1 to one transmitted symbol: 20/20 fail; scaling one local-code row by theta: 17/20 fail in the producer's run (3 pass by chance), and the auditor's version (first-processed vertex row 0 scaled by theta) fails 16/20. An earlier, flawed renormalisation control touching one neighbour only was replaced; the final run is reported.",
            ["MUC-C-0005"],
            arg("C-exact-finite-field", "data/code/controls.py, data/data/controls.json, data/logs/controls.log, data/audit/outputs/audit.log.txt",
                [C / "controls.py", DT / "controls.json", LG / "controls.log", AO / "audit.log.txt"], "controls.py (producer); audit.py (auditor)")),
        rec("MUC-X-0001", "X", "numeric",
            "Random-input simulation: the producer's 1000/1000 random input tuples in F9^157 decode correctly through the pi-ordered interpolation, and the auditor's 200/200; redundant after the unit-vector argument of MUC-C-0005. The producer's HiGHS floating LP value 0.9363057324840819 (ratio to 147/157 = 1 + 5.8e-15) is likewise superseded by MUC-C-0006.",
            [], num([DT / "main_results.json", DT / "lp_result.json", LG / "main.log", LG / "lp.log", AO / "audit.log.txt"], "producer and auditor random-input and floating-LP readings; superseded by exact arguments")),
        rec("MUC-X-0002", "X", "numeric",
            "NOT done / not verified: Section 3's example (166/744/830); the Section 2 model equivalence, BGS17 amplification and Corollary 1.2; the authors' verifier and repository (not run); the OpenAI preprint (not found or opened); the Lean formalization claimed by 2610.09367 (not checked); the kingy.ai and MathWorld statements; follow-ups 2610.20079, 2610.33655 and attempts 2608.06042, 2608.06070 (not read); Lean or any proof assistant (no Tier A); a human audit. Provenance: PREREG_ITEM.md was committed in the same commit as RESULT.md (a06dcfd); that it came first is shown only by file timestamps (prereg 07:17, first code 07:18 on 2026-11-02).",
            [], num([D / "RESULT.md", D / "PREREG_ITEM.md", D / "AUDIT.md"], "producer text, preregistration, audit; recorded absences and caveats")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
