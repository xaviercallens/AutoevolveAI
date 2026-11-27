"""Build the Elenchus claim ledger for the BIO-BISTAB paper (papers/p6_bistable_networks_recheck).

Modelled on papers/p6_nontransitive_dice_recheck/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not be filed above
anything in its depends_on; the kind caps the tier (citation L, argument C, numeric X). No Lean, so no Tier A row. An AI audit exists
(AUDIT.md, ACCEPT_WITH_CORRECTIONS), not a person. This is a recheck of a claim by others (Peng, arXiv:2610.32739); no novelty claim.
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
SRC_COMMIT = "f86e0a2"  # HEAD when the lane records were written; the lane records and this paper are uncommitted working-tree files


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
    C = D / "code"
    A = D / "audit"
    c = [
        rec("BIST-L-0001", "L", "citation",
            "Peng, arXiv:2610.32739 v1 (23 Oct 2026, 'Bistability with equal and independent removal in small bimolecular networks', math.DS, unrefereed): network class (complexes X, Y, 2X, X+Y, 2Y; at most 3 directed edges), models E and F, bistability target (two positive equilibria with trace<0, det>0), 681 orbits, 27 bistable networks with Table 2 rational witnesses, exclusion by JAC 245, DIV 216, ROOT 179, FLUX 14, Lemma 3, Theorem 2. "
            "Taken as stated; the paper text is third-party and not shipped. The paper is internally inconsistent on the label count (1351 in Sec. 1, '1362 labels' in Sec. 5; 1362 = 1351 + 11).",
            [], cite("arXiv:2610.32739v1", "Sections 1-5, Tables 1-2, Lemma 3, Theorem 2", "Read by the producer and the independent AI auditor (auditor also viewed the page-7 image)", "taken as stated; full text kept outside the repo")),
        rec("BIST-L-0002", "L", "citation",
            "Related literature (alphaXiv and web search 2026-11-01, limited): Tang-Xu, 'Multistability of Small Reaction Networks', arXiv:2008.03846 (title and authors checked on arxiv.org 2026-11-02); Joshi-Shiu; Banaji-Boros-Hofbauer; arXiv:1909.11940, 2207.04971, 2608.01116, 2406.11586 (not verified here, not listed as identifiers). No earlier enumeration of this exact 681/27 class was found; the search was not exhaustive. No independent verification or critique of 2610.32739 was found.",
            [], cite("AUDIT.md section 7; PREREG_ITEM.md", "literature note", "auditor's and producer's searches", "not an exhaustive prior-art search")),
        rec("BIST-C-0001", "C", "argument",
            "Enumeration (producer and auditor, own code each): 1351 labelled edge sets, 11 fixed by species exchange, 681 orbits with sizes 1/10/100/570; first-appearance numbering in lexicographic order reproduces all 27 Table-1 identifiers; the 27 sets lie in 27 distinct orbits.",
            ["BIST-L-0001"],
            arg("C-exact-integer", "data/code/p1_enum.py, p1b_ids.py, data/summaries/p1_enum.json, data/audit/code/a1_enum.py",
                [C / "p1_enum.py", C / "p1b_ids.py", S / "p1_enum.json", A / "code" / "a1_enum.py"], "p1_enum.py (producer); a1_enum.py (auditor)")),
        rec("BIST-C-0002", "C", "argument",
            "The 27 Table-2 rational witnesses (rho = 1): producer by Groebner elimination, square-free resultant, Sturm count and rational interval signs; auditor by certified Arb root isolation (python-flint, 400 bits). Each has exactly 3 positive equilibria = 2 sinks (tr<0, det>0) + 1 saddle (det<0), 0 undecided signs. Rows N0514, N0524, N0548, N0554 (k1=17; k2=100/9, 100/9, 100/159, 100/159; k3=2600/2809, 650/729, 2600/2809, 2600/2809) confirmed against the PDF image by the auditor; the author's catalogue was not used.",
            ["BIST-C-0001"],
            arg("C-exact-rational", "data/summaries/p2_witnesses.json, p2b_alt_parse.json, data/audit/outputs/a2_witness.json, data/audit/code/a2_witness.py",
                [S / "p2_witnesses.json", S / "p2b_alt_parse.json", A / "outputs" / "a2_witness.json", A / "code" / "a2_witness.py", C / "p2_witnesses.py"], "p2_witnesses.py (producer, sympy/Sturm); a2_witness.py (auditor, flint Arb)")),
        rec("BIST-C-0003", "C", "argument",
            "Exclusion certificates, conditional on the paper's Lemma 3 (and its Sard step) and the JAC midpoint identity, which are pen-and-paper and not machine-checked: JAC excludes 245 and DIV a further 216 (producer and auditor agree; split by network size 0 edges 1/0, 1 edge 8/2, 2 edges 54/33, 3 edges 182/181 equals the paper's table); 0 of the 27 positives excluded. "
            "ROOT: the auditor, taking the Sylvester resultant at the actual degree of each polynomial in the eliminated variable, passes 179 of the remaining 193 negatives (13 with 2 edges, 166 with 3 edges), 0 positives, 0 FLUX networks; the producer's fixed degree-2 (4x4) reading passes only 105, so the gap of 88 comes from the producer's reading of 'nominal degree'. "
            "FLUX 14/14 reproduced by the auditor (cone rays plus copositivity: 11 entrywise nonnegative; N0391 and N0646 positive definite; N0610 copositive, not PSD). Total 245+216+179+14 = 654.",
            ["BIST-L-0001", "BIST-C-0001"],
            arg("C-symbolic", "data/summaries/p4_jac_div.json, p5_root.json, data/audit/outputs/a3_rules.json, data/audit/code/a3_rules.py, a4_flux.py",
                [S / "p4_jac_div.json", S / "p5_root.json", A / "outputs" / "a3_rules.json", A / "code" / "a3_rules.py", A / "code" / "a4_flux.py", C / "p4_jac_div.py", C / "p5_root.py"], "p4_jac_div.py, p5_root.py (producer); a3_rules.py, a4_flux.py (auditor, sympy)")),
        rec("BIST-C-0004", "C", "argument",
            "Controls (exact): Sec. 4 baseline (Y->2X, 2X->X+Y, X+Y->Y; a = 4/99, b = 1/90) has equilibria x = 1/10, 1/5, 3/5 with det 25/9, -20/9, 100/9 and the fold at a ~ 0.04610; negatives (empty, X->Y, X<->Y, X+Y<->2X) give exactly 1 positive equilibrium; N0056 gives exactly 1 at the producer's tested parameters and 0 at a=1/3, b=2/7, k=3/2, h=5/4, rho=1 (consistent with the paper's bound of at most 2); scaling the inflow a by 2, 5, 20, 100, 1000 destroys bistability in all 27 witnesses.",
            ["BIST-C-0002"],
            arg("C-exact-rational", "data/summaries/p3_controls.json, data/audit/code/a6_controls.py, data/code/p3_controls.py",
                [S / "p3_controls.json", A / "code" / "a6_controls.py", C / "p3_controls.py"], "p3_controls.py (producer); a6_controls.py (auditor)")),
        rec("BIST-X-0001", "X", "numeric",
            "Random search (Tier X, evidence only): producer 125,000 log-uniform samples per network over all 681 (85.1M); all 27 positives re-found with an exact-verified two-sink point; 654 negatives with 0 candidates (depends on the producer's pipeline). Auditor 20,000 samples per network on the 27 positives and 193 ROOT/FLUX negatives (4.4M): all 27 re-found (lowest hit rate 0.39%); the float pipeline flagged 247 samples on 10 negative networks, all rejected by exact Arb re-check (0 with >= 2 sinks, 0 undecided). 0 bistable negatives.",
            [], num([S / "p7_search_summary.json", A / "outputs" / "a5_search_20000.json", A / "outputs" / "a5_search_2000.json", A / "code" / "a5_search.py", C / "p6_search.py"], "random search, claim_licence false")),
        rec("BIST-X-0002", "X", "numeric",
            "NOT done / not verified: Lemma 3 and its Sard step, the JAC midpoint identity (read, not machine-checked); Theorem 2 (deletion-minimality, inheritance) and B_E = B_F beyond counts; the author's supplementary certificates and code (not used); Lean or any proof-assistant check; an exhaustive prior-art search; a human audit. "
            "Provenance: PREREG_ITEM.md is self-attested (sha256 recorded, written before computation per the producer, no independent timestamp).",
            [], num([D / "RESULT.md", D / "PREREG_ITEM.md", D / "AUDIT.md"], "producer text, preregistration, audit; recorded absences and caveats")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
