"""Build the Elenchus claim ledger for the GALE-101 paper (papers/p6_gale_conjecture_recheck).

Modelled on papers/p5_graffiti_20_21_census/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not be filed above
anything in its depends_on; the kind caps the tier (citation L, argument C, numeric X). No Lean, so no Tier A row. An AI audit exists
(AUDIT.md, ACCEPT_WITH_CORRECTIONS), not a person. This is a recheck of a claim by others (Voronov, arXiv:2610.28828); no novelty claim.
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
SRC_COMMIT = "97164dd"  # HEAD of the working branch when written; the lane records and this paper are uncommitted working-tree files


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
    c = [
        rec("GALE-L-0001", "L", "citation",
            "Voronov, arXiv:2610.28828 v1 (20 Oct 2026, 'A counterexample to Gale's conjecture in R^3', by its own statement not independently reviewed and not formalised in Lean): "
            "Gale's 1953 conjecture, as quoted there, is beta_{n,n+1} = beta_{n+1}(B^n) for every n >= 2; Theorem 2 claims that the 101-point set V in R^3 of Appendix A satisfies beta_4(V) > 0.88928 > beta_4(S^2). "
            "Taken as stated; Gale 1953 was not read.",
            [], cite("arXiv:2610.28828v1", "abstract; Definitions 1, 2; Conjecture 1; Theorem 2; Appendix A (Table 2); footnote 1",
                     "Read by the producer and the independent AI auditor; the third-party text and coordinates are not shipped (data/third_party_hashes.json)",
                     "taken as stated; Appendix A coordinates are not stored in this repository")),
        rec("GALE-L-0002", "L", "citation",
            "Upper bound for the ball: beta_4(B^3) <= sigma_3 = sqrt((3+sqrt3)/6) = 0.8880738340 (explicit cone partition over a regular tetrahedron); optimality beta_4(B^3) = sigma_3 is cited to Kalai's survey in Voronov's paper and is not needed for the refutation. "
            "The reduction to the diameter of one spherical triangle T is rigorous (each cone lies in conv({0} u T), diameter max(diam T, 1/2) = diam T); diam T >= sigma_3 is analytic (vertex to opposite midpoint chord); "
            "diam T = sigma_3 is asserted by the paper and only sampled here (GALE-X-0001). Tier stays L.",
            [], cite("arXiv:2610.28828v1; Kalai survey as cited there", "the paper's statement of the sigma_3 bound and of Kalai's optimality result",
                     "AUDIT.md section 4; data/audit/code/sigma3.py", "taken as stated; not re-derived")),
        rec("GALE-C-0001", "C", "argument",
            "Exact geometry of the rounded Appendix A set (rational arithmetic and Python integers, two extraction tools: PyMuPDF word boxes and pdfminer.six agree; producer's pdftotext route agrees): 303 numbers give 101 distinct points; "
            "D^2 = 100000021020030 in units 1e-14 (D = 1.0000001051), attained only by the pair (19,56); exactly 2030 pairs with dist > (88928/100000) D, none on the threshold; weakest included ratio 0.8892809651305 "
            "(ratio^2 margin 1.7165e-6, ratio margin 9.65e-7), strongest excluded ratio 0.8892597950 (gap 2.02e-5); degrees 28..52, 4-core all 101 vertices, maximum clique 4. "
            "Rounding robustness: any coordinate set within 5e-8 of the rounded one changes any ratio by at most about 3.3e-7 and so gives the same 2030-edge graph; the author's 17-figure repository points give the identical edge set (symmetric difference 0), "
            "diameter pair (12,37), weakest ratio 0.8892811623939.",
            ["GALE-L-0001"],
            arg("C-exact-integer", "data/derived/geometry_summary.json, data/derived/edges_088928.json, data/audit/out/geom_derived.json (summary and index lists only, no coordinates), data/code/geom.py, data/audit/code/geom_audit.py",
                [D / "derived" / "geometry_summary.json", D / "derived" / "edges_088928.json", D / "audit" / "out" / "geom_derived.json", D / "code" / "geom.py", D / "audit" / "code" / "geom_audit.py"],
                "geom.py (producer), geom_audit.py (auditor, fractions.Fraction)")),
        rec("GALE-C-0002", "C", "argument",
            "The 2030-edge distance graph is not 4-colourable (UNSAT, certificates checked): producer, Glucose4 DRUP proofs verified by drat-trim with and without a symmetry unit, CaDiCaL 1.9.5 on a ladder encoding, own exhaustive DSATUR (745 nodes); "
            "auditor, own 2-bit encoding with no symmetry breaking (202 variables, 8120 clauses), PicoSAT and CaDiCaL 3.0.1 UNSAT, DRAT proof verified by drat-trim, LRAT proof verified by lrat-check.c and by the auditor's own Python LRAT checker (6246 lemmas); "
            "a proof with one hint removed is rejected by both LRAT checkers; the producer's CNF files equal the clause set rebuilt from the edge list. Controls (K4, K5, K6, Groetzsch, Moser spindle, Petersen; corrupted proof; planted 4-colourable 101-vertex graphs) all pass. "
            "The graph is 5-colourable (chromatic number 5).",
            ["GALE-C-0001"],
            arg("C-sat-certificate", "data/derived/headline.json, cnfcheck.json, controls_small.json, controls_mid.json, data/sat (CNF and proofs, .txt suffix), data/audit/out/sat.json, aud_log.*.txt, data/audit/code/sat_audit*.py",
                [D / "derived" / "headline.json", D / "derived" / "cnfcheck.json", D / "derived" / "controls_small.json", D / "derived" / "controls_mid.json", D / "sat" / "gale101_k4_nosym.cnf.txt",
                 D / "sat" / "gale101_k4_nosym.drup.txt", D / "audit" / "out" / "sat.json", D / "audit" / "out" / "aud_log.lrat.txt", D / "audit" / "code" / "sat_audit.py", D / "audit" / "code" / "sat_audit_lrat.py"],
                "Glucose4 + drat-trim; CaDiCaL 3.0.1 + drat-trim + lrat-check.c + own Python LRAT checker; PicoSAT; DSATUR")),
        rec("GALE-C-0003", "C", "argument",
            "Value and structure: beta_4(V) = sqrt(39541040058709/50000010510015) = 0.88928096513... exactly for this rounded set (the 2029 longest pairs form a 4-colourable graph, decoded colouring checked edge by edge, its longest monochromatic pair is pair number 2030); "
            "threshold sweep: not 4-colourable at t = 0.888, 0.888073 (2054 edges), 0.889 (2039), 0.88928 (2030), 4-colourable at 0.889281 (2025 edges) and above; a minimal (edge-critical) non-4-colourable subgraph with 425 edges on all 101 vertices "
            "(all 425 single-edge deletions are 4-colourable, exhaustive); deleting any one vertex leaves a 4-colourable graph; moving one coordinate by 1e-3 makes all 20 trials 4-colourable; 50 random 60-vertex induced subgraphs are 4-colourable. "
            "The set is a finely tuned object, not a robust one.",
            ["GALE-C-0001", "GALE-C-0002"],
            arg("C-sat-certificate", "data/derived/analysis.json, data/audit/out/sat.json, data/audit/code/prefix_check.py",
                [D / "derived" / "analysis.json", D / "audit" / "out" / "sat.json", D / "audit" / "code" / "prefix_check.py", D / "code" / "analysis.py"], "analysis.py (producer); prefix_check.py (auditor, PicoSAT)")),
        rec("GALE-C-0004", "C", "argument",
            "Logic chain, argued and not formalised: V finite so beta_4(V) is a minimum over 4-partitions; a 4-partition is a 4-colouring; since the distance graph at threshold t D is not 4-colourable, some part contains a pair with distance > t D, so beta_4(V) > t relative to D = 1.0000001051 "
            "(the threshold multiplies D, as applied). With t = 0.88928 and sigma_3 = 0.8880738340, 0.88928 > sigma_3 holds exactly ((6t^2-3)^2 > 3 with 6t^2-3 > 0). "
            "Hence, given the upper bound GALE-L-0002, beta_4(V) exceeds the ball bound sigma_3 >= beta_4(B^3); this is the refutation claimed by Voronov, not ours.",
            ["GALE-C-0002", "GALE-L-0002"],
            arg("C-argument", "AUDIT.md section 4; data/derived/geometry_summary.json; data/audit/code/sigma3.py", [PAPER / "AUDIT.md", D / "derived" / "geometry_summary.json"], "paper-and-pencil; exact inequality by squaring")),
        rec("GALE-X-0001", "X", "numeric",
            "diam T = sigma_3 for the tetrahedral spherical triangle T (radius 1/2) is supported only by floating-point dense sampling (6000 boundary and 4000 interior points: maximum 0.888073833977, equal to sigma_3 to 2e-16); producer sanity check likewise. Not a proof.",
            [], num([D / "audit" / "code" / "sigma3.py", D / "derived" / "analysis.json"], "floating-point sampling, claim_licence false")),
        rec("GALE-X-0002", "X", "numeric",
            "NOT done: Lean or any proof-assistant check (Tier A not reached); a proof that diam T = sigma_3 or of the optimality of sigma_3 for the ball; Gale 1953 not read; kissat run (build refused by the permission classifier); a formally verified checker (cake_lpr); "
            "dimensions 4 to 6 and the author's search code; contacting the author; a human audit. No independent verification, refutation or comment was found in the literature on 2026-11-01. Recorded so the absences are explicit.",
            [], num([D / "RESULT.md", D / "PREREG_ITEM.md"], "producer text and preregistration; they contain no claim about this paper beyond the recorded absences")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
