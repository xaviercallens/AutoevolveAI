"""Build the Elenchus claim ledger for the MS-CENSUS paper (papers/p6_murty_simon_lemmas_census).

Modelled on papers/p6_nontransitive_dice_recheck/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not be filed above
anything in its depends_on; the kind caps the tier (citation L, argument C, numeric X). No Lean, so no Tier A row. An AI audit exists
(AUDIT.md, ACCEPT_WITH_CORRECTIONS), not a person. This is a recheck of a claim by others (Das-Fox, arXiv:2610.39032); no novelty claim.
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
SRC_COMMIT = "c981c12"  # commit holding the lane records (PREREG_ITEM.md and results in the same commit); this paper is an uncommitted working-tree file


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
    L = D / "data"
    A = D / "audit"
    lem = [L / f"lemmas_n{n}.json" for n in range(3, 12)]
    c = [
        rec("MS-L-0001", "L", "citation",
            "Das-Fox, 'A proof of the Murty--Simon conjecture on diameter-2-critical graphs', arXiv:2610.39032 v1 (28 Oct 2026, unrefereed). D2C = diameter 2 and deleting any edge destroys diameter 2. "
            "Lemma 1.2 (as read by the auditor from the full text): for every D2C graph G on n>=3 vertices and every maximal matching M (inclusion-maximal), |E(G) minus M| <= number of non-edges. "
            "Lemma 1.3: if equality holds for every maximal matching then G is triangle-free. Both are unconditional for-all statements. Theorem 1.1: a D2C graph on n vertices has at most floor(n^2/4) edges. "
            "AI statement of the paper: GPT-5.6 Sol found a proof of the floor(n^2/4) bound (Lemma 1.2) and an equality-case proof for even n only; the all-n equality proof (Lemma 1.3) is the authors' own work. Taken as stated; the paper text is third-party and not shipped.",
            [], cite("arXiv:2610.39032v1", "Lemmas 1.2, 1.3; Theorem 1.1; AI statement", "Read in full by the independent AI auditor (AUDIT.md section 1)", "taken as stated; full text kept outside the repo")),
        rec("MS-L-0002", "L", "citation",
            "Prior art: Dailly-Foucaud-Hansberg, 'Strengthening the Murty-Simon conjecture on diameter 2 critical graphs', arXiv:1812.08420 (Discrete Math 2019): computer search on all graphs of order <= 11, structural facts, no per-order counts; reports that Fan (1987) proved the Murty-Simon conjecture for n <= 24 and n = 26 (Fan not read here). "
            "OEIS A330333 'Number of diameter-2-critical graphs with n nodes': 1, 2, 3, 5, 10, 30, 103, 519, 3746 (offset 3), M. Zivkovic Dec 2019, a(11) added by S. A. Irvine 2026-09-05 (checked on oeis.org 2026-11-01). MacDougall-Eggleton (1997) list the D2C graphs up to n=7 (via the auditor; not read here).",
            [], cite("arXiv:1812.08420; oeis.org/A330333", "abstract, introduction, section 4; OEIS data", "auditor read DFH (abstract, intro, concluding section, keyword search of full text) and the raw OEIS entry", "no per-order counts in DFH; counts are in OEIS")),
        rec("MS-C-0001", "C", "argument",
            "Census of D2C graphs, 3<=n<=11, by two independent implementations. Producer: nauty-geng -c piped to a C filter (explicit criticality test). Auditor: fresh geng, Rust filter with a common-neighbour characterisation, cross-checked by explicit BFS edge deletion for n<=10 (0 disagreements on 11,989,762 connected graphs), and a full fresh enumeration of all 1,006,700,565 connected graphs at n=11. "
            "Connected graphs (= A001349): 2, 6, 21, 112, 853, 11117, 261080, 11716571, 1006700565. D2C graphs: 1, 2, 3, 5, 10, 30, 103, 519, 3746 (total 4419), equal to OEIS A330333; canonical D2C sets (nauty labelg) are equal for n=3..11, symmetric difference 0. Controls: positives C4, C5, Petersen, K23, K33, K45, K15 accepted; negatives K3, K4, K5, K4-e, C6, C7, P4 rejected (both implementations). This is a recomputation of published counts.",
            ["MS-L-0002"],
            arg("C-exact-integer", "data/code/d2c_filter.c.txt, audit/code/d2c_main.rs, data/data/controls.json, census and audit logs",
                [A / "code" / "d2c_main.rs", D / "code" / "d2c_filter.c.txt", D / "data" / "controls.json", D / "logs" / "census_n11_p0.log.txt", D / "logs" / "census_n10_p0.log.txt",
                 A / "out" / "n11_p0.log.txt", A / "out" / "n11_p1.log.txt", A / "out" / "n11_p2.log.txt", A / "out" / "n11_p3.log.txt", A / "code" / "cmp.sh.txt", A / "code" / "ctl.py"],
                "d2c_filter.c (producer); d2c_main.rs (auditor, Rust)")),
        rec("MS-C-0002", "C", "argument",
            "Per-graph test of Das-Fox Lemmas 1.2 and 1.3 and of Theorem 1.1 on all 4419 D2C graphs with 3<=n<=11: 776,217 maximal matchings tested (2, 5, 15, 39, 147, 788, 5142, 50991, 719088 for n=3..11), recomputed identically by the producer (Python) and the auditor (own enumerator, equal to brute force on the 51 D2C graphs with n<=8 plus 14 control graphs). "
            "0 violations of Lemma 1.2; 0 violations of Lemma 1.3; max edges = floor(n^2/4) at every n, attained uniquely by the balanced K_{ceil(n/2),floor(n/2)}. Exactly one graph per n is an equality case for ALL maximal matchings: the balanced K_{a,b}, triangle-free, so Lemma 1.3 is nearly vacuous in this range. "
            "Auditor finding: equality for even ONE maximal matching holds only at K_{a,b}; triangle-containing D2C graphs stay below the bound of Lemma 1.2 by at least 1 at n=6 and at least 10 at n=11 (D2C graphs with a triangle: 1, 4, 20, 87, 488, 3685 for n=6..11). Perturbed statements (strict <, bound minus 1, empty matching) fail as they must. "
            "Sanity check only: Theorem 1.1 was already reported proved for n<=24 and n=26 by Fan (1987, per DFH, not read).",
            ["MS-L-0001", "MS-C-0001"],
            arg("C-exact-integer", "data/code/lemmas.py, audit/code/lem.py, data/data/lemmas_n*.json, audit/out/lem_out.json",
                [D / "code" / "lemmas.py", A / "code" / "lem.py", A / "code" / "bf.py", A / "out" / "lem_out.json"] + lem,
                "lemmas.py (producer, Python); lem.py (auditor, Python)")),
        rec("MS-C-0003", "C", "argument",
            "Auditor reproduction of the structural facts of Dailly-Foucaud-Hansberg on the D2C list: 13 non-bipartite D2C graphs at floor((n-1)^2/4)+1 edges outside the C5+ family (n=7: 3, n=8: 8, n=9: 2; none at n=10, 11), 3 of them without a dominating edge; 10 graphs at that bound with a dominating edge, all with n<=9; only H5 (n=6, 8 edges) above that bound; maximum degree n-1 only in stars (0 exceptions).",
            ["MS-C-0001", "MS-L-0002"],
            arg("C-exact-integer", "audit/code/dfh.py",
                [A / "code" / "dfh.py", A / "out" / "d2c_n9.g6.txt", A / "out" / "d2c_n11_p0.g6.txt"], "dfh.py (auditor, Python)")),
        rec("MS-X-0001", "X", "numeric",
            "Intermediate lemmas of Das-Fox (2.4, 2.5, 2.13, 3.1, 3.2): 0 violations on all 4419 graphs by the producer's own implementation of the paper's definitions (critical non-edge, I, I', C_l). The auditor did NOT recompute these; a misreading of those definitions would not affect the checks of Lemmas 1.2, 1.3 and Theorem 1.1. Tier X (unaudited producer numbers).",
            [], num([D / "code" / "lemmas.py", D / "result.json"] + lem, "producer-only intermediate lemma checks, claim_licence false")),
        rec("MS-X-0002", "X", "numeric",
            "NOT done / not verified: the Das-Fox proof logic; anything for n>=12 (n=12 has about 1.65e11 connected graphs, about 16 wall-hours on 4 cores, not run); Fan (1987); the producer's reconstructed Figure 1 graph; Lean or any proof-assistant check; a human audit. "
            "Provenance caveats: PREREG_ITEM.md (sha256 b731521c...) and RESULT.md were committed together in c981c12, so the claim that it was written before any computation is self-attested and not verifiable from git; the producer ran 4 geng|filter pipelines = 8 processes on cores 2-5 (not <=4 processes as written in RESULT.md).",
            [], num([D / "RESULT.md", D / "PREREG_ITEM.md", D / "AUDIT.md"], "producer text, preregistration and audit; recorded absences and caveats")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
