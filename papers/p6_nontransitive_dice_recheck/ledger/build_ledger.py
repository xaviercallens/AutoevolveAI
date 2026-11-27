"""Build the Elenchus claim ledger for the DICE-6 paper (papers/p6_nontransitive_dice_recheck).

Modelled on papers/p6_gale_conjecture_recheck/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not be filed above
anything in its depends_on; the kind caps the tier (citation L, argument C, numeric X). No Lean, so no Tier A row. An AI audit exists
(AUDIT.md, ACCEPT_WITH_CORRECTIONS), not a person. This is a recheck of a claim by others (Easlick, arXiv:2610.40321); no novelty claim.
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
SRC_COMMIT = "7c2b106"  # commit holding the lane records (PREREG_ITEM.md and results in the same commit); this paper is an uncommitted working-tree file


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
    S = D / "summaries"
    c = [
        rec("DICE-L-0001", "L", "citation",
            "Easlick, arXiv:2610.40321 v1 (29 Oct 2026, 'Computer-Assisted Results for n-Sided Non-Transitive Dice Taking Face Values in [n]', unrefereed): Defs. 1-2, eqs. 1, 3, 4 (dice = multisets of n faces in [n], strict beating, minimal winning probability 1/2+1/n^2 for even n and 1/2+1/(2n^2) for odd n), Theorem 1 (n=6), Conjecture 1, Sec. 3 and Appendices B-J (graph statistics n=3..10, printed cycles). "
            "'Maximum length n' is not formally defined in the paper; read here through the proof of Theorem 1 as 'an n-cycle exists and no longer cycle exists'. Taken as stated; the paper text is third-party and not shipped (data/result.json lists its external hash).",
            [], cite("arXiv:2610.40321v1", "Definitions 1, 2; eqs. 1, 3, 4; Theorem 1; Conjecture 1; Section 3; Appendices B-J",
                     "Read by the producer and the independent AI auditor; the text was removed from the repository", "taken as stated; full text kept outside the repo")),
        rec("DICE-L-0002", "L", "citation",
            "Related literature (alphaXiv and web search 2026-11-01, limited): Conrey-Gabbard-Grant-Liu-Morrison, 'Intransitive Dice', arXiv:1311.6511 (closest setting: proper dice, faces in [n], face sum n(n+1)/2; not cited by Easlick); Angel-Davis arXiv:1610.08595; Hur-Kim arXiv:2006.12866; Schaefer-Schweig arXiv:1602.00969 and 1706.08986; Rooney arXiv:2505.21950. None treats n-cycles in this graph; no earlier statement of the n=6 theorem was found, but the search was limited. Only arXiv:2610.40321 and arXiv:1311.6511 were verified on arxiv.org by the paper's author and listed as related identifiers.",
            [], cite("AUDIT.md section 7", "literature note", "auditor's search", "not an exhaustive prior-art search")),
        rec("DICE-C-0001", "C", "argument",
            "Graph statistics of G_n for n=3..10 by two independent implementations (producer numpy/scipy for n<=9, exact integers, brute-force double-sum cross-check n<=6; auditor C, histogram/cumulative encoding, iterative Tarjan, n<=10, 200000 random pairs per n cross-checked, 0 mismatches). "
            "dice/edges/SCCs/nontrivial SCC: n=3 10/3/10/none; n=4 35/67/35/none; n=5 126/620/126/none; n=6 462/5491/450/two of 7 vertices, 10 edges; n=7 1716/89153/636/one 1081 v, 53389 e; n=8 6435/956307/2115/one 4321 v, 674108 e; n=9 24310/12528131/3860/one 20451 v, 10933011 e; "
            "n=10 (auditor only) 92378/157244770/10588/one 81791 v, 147620052 e. All equal the paper's numbers (Sec. 3, App. B-J). Vertex lists of the n>=7 SCCs were not compared.",
            ["DICE-L-0001"],
            arg("C-exact-integer", "data/summaries/graph_*.json, data/code/dice_graph.py, data/audit/code/dg.c.txt, data/audit/logs/n9.log.txt, n10.log.txt",
                [S / "graph_3.json", S / "graph_4.json", S / "graph_5.json", S / "graph_6.json", S / "graph_7.json", S / "graph_8.json", S / "graph_9.json", D / "code" / "dice_graph.py",
                 D / "audit" / "code" / "dg.c.txt", D / "audit" / "logs" / "n9.log.txt", D / "audit" / "logs" / "n10.log.txt"],
                "dice_graph.py (producer, numpy); dg.c (auditor, C)")),
        rec("DICE-C-0002", "C", "argument",
            "The map f_n(x)=(n+1-x_n,...,n+1-x_1) is an involution on dice and sends every edge a->b to f(b)->f(a), checked on all edges for n=3..10 by the auditor (0 violations; fixed points 70 at n=9, 126 at n=10) and for n<=6 by the producer. "
            "n=3,4,5: all SCCs trivial, so G_n has no directed cycle and no n-cycle.",
            ["DICE-C-0001"],
            arg("C-exact-integer", "data/audit/logs/n9.log.txt, n10.log.txt, data/summaries/verify_results.json, data/code/verify.py",
                [D / "audit" / "logs" / "n9.log.txt", D / "audit" / "logs" / "n10.log.txt", S / "verify_results.json", D / "code" / "verify.py"], "verify.py (producer); dg.c (auditor)")),
        rec("DICE-C-0003", "C", "argument",
            "n=6 (Theorem 1 part): exhaustive simple-cycle enumeration (producer; auditor's own DFS) in the two 7-vertex SCCs gives per SCC exactly three 3-cycles and one 6-cycle, none of length 4, 5, 7; over G_6 six 3-cycles and exactly two 6-cycles. Every edge of each 6-cycle is exactly 19/36 (Fractions). "
            "f swaps the two 6-cycles (f of one, reversed, is a rotation of the other). SCC vertex labels (1-based lexicographic) {88,89,151,207,217,277,291} and {118,119,160,235,286,385,391} equal the paper's Appendix E. With n=3,4,5 cycle-free, n=6 is the smallest n>=3 with an n-cycle and its longest cycle has length 6.",
            ["DICE-C-0001", "DICE-C-0002"],
            arg("C-exact-integer", "data/audit/logs/cyc.log.txt, data/audit/code/cyc.py, data/summaries/verify_results.json, data/code/verify.py",
                [D / "audit" / "logs" / "cyc.log.txt", D / "audit" / "code" / "cyc.py", S / "verify_results.json", D / "code" / "verify.py"], "verify.py (producer); cyc.py (auditor)")),
        rec("DICE-C-0004", "C", "argument",
            "The paper's printed cycles for n=7 (14 dice), n=8 (29), n=9 (10) and n=10 (110) were parsed from the text and checked in print order with exact Fractions: all dice distinct, every edge at the minimal probability (25/49, 33/64, 41/81, 51/100). The n=10 check is the auditor's only. "
            "Consequence under the proof's reading of 'maximum length n': one exact-checked cycle longer than n shows the property fails, so it fails at n=7,8,9,10 (the n=10 case needs only the 110-cycle, not the 157M-edge graph). Conjecture 1 (n=6 is the largest n with a uniform minimal cycle of maximum length n) is therefore open only for n>=11 under this reading; under the alternative reading 'an n-cycle exists' it is false at n=7 (exact-checked 7-cycle). No proof of Conjecture 1 is claimed.",
            ["DICE-C-0001"],
            arg("C-exact-integer", "data/audit/logs/cyc.log.txt, data/summaries/verify_results.json",
                [D / "audit" / "logs" / "cyc.log.txt", S / "verify_results.json", S / "extra_results.json"], "verify.py (producer, n<=9); cyc.py (auditor, n<=10)")),
        rec("DICE-X-0001", "X", "numeric",
            "Searches and context controls (Tier X): randomized walk search in G_7 found exact-checked cycles (the check is exact, the search is not exhaustive) of every length 3..28, including 7, 8 and 14. "
            "Maximin context controls (orthogonal to the claim, not recomputed by the auditor): best 3-cycle winning probability for m-sided dice in [m] is 3/5 (m=5), 7/12 (m=6), 29/49 (m=7), all below (sqrt5-1)/2; m=4 has no 3-cycle. Controls recomputed by the auditor: Efron 2/3, Moon-Moser 5/9, 62/62 single-face perturbations break the 6-cycle, near-miss pairs W=20 and W=18 rejected by the predicate.",
            [], num([S / "extra_results.json", D / "logs" / "extra.log.txt", D / "audit" / "logs" / "cyc.log.txt"], "random-walk search and context controls, claim_licence false")),
        rec("DICE-X-0002", "X", "numeric",
            "NOT done / not verified: n>=11 and any proof of Conjecture 1; full vertex lists of the n>=7 SCCs in the paper's appendices (only sizes and counts); an exhaustive prior-art search; Lean or any proof-assistant check; a human audit. "
            "Provenance caveats: PREREG_ITEM.md was committed in the same commit as the results (7c2b106), so version control cannot show it was written first (self-attested; sha256 recorded); the preregistered W=20 near-miss control was actually run on a W=36 pair (key ctrl_predicate_rejects_W20 is mislabelled; the auditor ran W=20 and W=18).",
            [], num([D / "RESULT.md", D / "PREREG_ITEM.md"], "producer text and preregistration; recorded absences and caveats")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
