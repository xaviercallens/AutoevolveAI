"""Build the Elenchus claim ledger for the LR-SPEC paper (papers/p5_near_tight_speed_tuples).

Modelled on papers/p5_graffiti_20_21_census/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not be filed above
anything in its depends_on; the kind caps the tier (citation L, argument C, numeric X). No Lean, so no Tier A row. An AI audit exists
(AUDIT.md, ACCEPT_WITH_CORRECTIONS), not a person.
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
    dd = D / "data"
    rs = D / "audit" / "rs"
    box_files = [dd / "summary.json", dd / "primary" / "n7_N80_W4.txt", dd / "primary" / "n8_N60_W4.txt",
                 dd / "ext2" / "n7_N200_W4.txt", dd / "ext2" / "n8_N130_W4.txt", dd / "ext2" / "n6_N200_W4.txt",
                 D / "code" / "lrspec_scan.c.txt", D / "code" / "verify.py"]
    c = [
        rec("LRS-L-0001", "L", "citation",
            "Fan and Sun, Amending the Lonely Runner Spectrum Conjecture, arXiv:2306.10417 v2 (EJC 33(1) (2026) P1.38): Conjecture 1.3 (ML = s/(ns+k) with k <= n, or ML >= 1/n), "
            "Conjecture 6.1 (k <= n/2), Table 1 (their search: 7 speeds up to 70 with k in {1,2}; 8 speeds up to 60 with k = 1; no published counts or tuples; code unpublished).",
            [], cite("arXiv:2306.10417v2", "Conjectures 1.3, 6.1; Table 1", "Read by producer (arXiv v2 and EJC PDF; Table 1 the same in both) and by the AI auditor; third-party PDFs not shipped",
                     "taken as stated")),
        rec("LRS-L-0002", "L", "citation",
            "Cordella, Odd denominators in the Lonely Runner spectrum for six speeds, arXiv:2609.03444 v2: near-tight definition (S2.1), Lemma 2.2 (witness times m/(v_i - e v_j), e = +-1), searches 7 speeds <= 50, 8 <= 40, 6 <= 110, "
            "Theorem 5.3 (v_max < 3q on the U_C family); code survey.c v1.0.2 (MIT, Zenodo 10.5281/zenodo.22345079).",
            [], cite("arXiv:2609.03444v2", "S2.1; Lemma 2.2; Thm 5.3; searches", "Read by producer and auditor; arXiv abstract page re-checked 2026-11-01 (title, author, dates)", "taken as stated")),
        rec("LRS-L-0003", "L", "citation",
            "Lonely runner conjecture proved for at most 8 runners (classical for <= 7, Rosenfeld arXiv:2509.14111 for 8); Hu-Jing arXiv:2610.23790 (uniform gap) is not about the spectrum.",
            [], cite("arXiv:2509.14111; arXiv:2610.23790", "titles/authors checked on arxiv.org 2026-11-01", "Rosenfeld: 'The lonely runner conjecture holds for eight runners'; Hu-Jing: 'Near optimal gap in the Lonely Runner Conjecture'",
                     "taken as stated; not re-read")),
        rec("LRS-C-0001", "C", "argument",
            "Equivalence and completeness. (a) With ML = p/q lowest terms and k' = q - np, Fan-Sun Conj 1.3 is exactly 1 <= k' <= n (k = g k'); Conj 6.1 is k' <= n/2. "
            "(b) For positive speeds the sum times m/(v_i+v_j), 1 <= m <= (v_i+v_j)/2, suffice: at a maximiser one active runner rises on the left and one falls on the right; if they differ t0 is a sum time, "
            "if equal then f(t0) = 1/2 and t0 is a sum time with m = D/2. Cordella's Lemma 2.2 uses sums and differences.",
            ["LRS-L-0001", "LRS-L-0002"],
            arg("C-argument", "AUDIT.md section 1 (read from the sources); paper Sections 1 and 2.", [PAPER / "AUDIT.md", D / "PREREG_ITEM.md"], "paper-and-pencil argument")),
        rec("LRS-C-0002", "C", "argument",
            "Scope: distinct speeds suffice (a repeated speed leaves at most n-1 <= 7 distinct speeds, and ML >= 1/n by the lonely runner conjecture for at most 8 runners); primitive tuples suffice (ML invariant under a common factor).",
            ["LRS-L-0003"], arg("C-argument", "AUDIT.md section 1 (Scope).", [PAPER / "AUDIT.md"], "paper-and-pencil argument")),
        rec("LRS-C-0003", "C", "argument",
            "Null boxes: exhaustive enumeration with exact integer witnesses and Fraction-recomputed ML for every reported tuple gives primitive near-tight counts 7<=80: 37 (k1:33,k2:4); 8<=60: 36 (k1:36); 7<=200: 55 (k1:51,k2:4); "
            "8<=130: 65 (k1:65); 6<=200: 1085 (k1:971,k3:114); controls 4<=200: 4125, 6<=110: 348, 7<=50: 29, 8<=40: 29 (other boxes in summary.json). No tuple has k > n or k > n/2. 7<=70 and 8<=60 recompute Fan-Sun Table 1; "
            "new relative to the literature are only 7 speeds in (70,200] and 8 speeds in (60,130], as null boxes. Conj 1.3 is neither proved nor refuted.",
            ["LRS-C-0001", "LRS-C-0002"],
            arg("C-exact-integer", "data/data/summary.json and tuple files; producer C scan plus Fraction verifier.", box_files, "lrspec_scan.c, verify.py")),
        rec("LRS-C-0004", "C", "argument",
            "Independent AI audit: a Rust screen with the complete witness set (every reduced a/b <= 1/2, b <= 2N; sums, differences, peaks) reproduces every tuple set with p, q, k identically on all boxes including 8<=130 and 7<=200 "
            "(prefilter mode matched full mode on four boxes); Cordella's survey.c (reviewed, then run) matches the controls for 4<=200, 6<=110, 7<=50, 8<=40 and finds (2,7,9,11,13,20,54) ML 9/65 at 7<=56. "
            "Fraction check of all rows of 7<=80, 8<=60 and 40 random rows of 7<=200, 8<=130, 6<=200: 0 mismatches. NOT a human audit; producer N2/N3 and the float-grid check not re-implemented.",
            ["LRS-C-0003"],
            arg("C-audit-report", "AUDIT.md sections 2-4; data/audit/.", [PAPER / "AUDIT.md", rs / "main.rs", rs / "r_n7_N200_x_pre.txt", rs / "r_n8_N130_x_pre.txt", D / "audit" / "fracverify.json",
                                                                       D / "audit" / "cmp.py", D / "audit" / "survey" / "s_n7_N56.txt"], "Rust screen; survey.c; fracverify.py")),
        rec("LRS-C-0005", "C", "argument",
            "The four k=2 septuples (1,2,3,4,5,7,18), (1,3,4,5,7,13,18) ML 3/23, (1,3,4,5,7,11,30) ML 5/37, (2,7,9,11,13,20,54) ML 9/65 are re-verified exactly over the complete set; they are the same four in every box from <= 54 to 200. "
            "(2,7,9,11,13,20,54) is printed in neither paper, lies outside Cordella's 7-speed box (54 > 50), is found by his survey.c at 7<=56, and lies inside Fan-Sun's searched range (<= 70): NOT a new finding. "
            "That Fan-Sun saw it is an inference (their code is unpublished).",
            ["LRS-C-0004"], arg("C-exact-integer", "data/audit/fracverify.json; AUDIT.md section 4.", [D / "audit" / "fracverify.json", D / "audit" / "fracverify.py", PAPER / "AUDIT.md"], "fracverify.py")),
        rec("LRS-C-0006", "C", "argument",
            "Secondary, descriptive: all 1085 sextuples <= 200 have ML = (P-1)/(6P), P = +-1 mod 6, with odd q; max v_max/q = 195/73 at (6,61,67,128,189,195) (a member of a family for which Cordella's Thm 5.3 already proves v_max < 3q: no new evidence); "
            "13/5 at (1,4,5,6,7,11,39) for 7 speeds and 21/17 at (1,5,6,7,8,11,13,21) for 8 speeds.",
            ["LRS-C-0004"], arg("C-audit-report", "AUDIT.md section 5 (secondary claims recomputed from the auditor's outputs).", [PAPER / "AUDIT.md", dd / "ext2" / "n6_N200_W4.txt"], "auditor recount")),
        rec("LRS-X-0001", "X", "numeric",
            "NOT done: Lean or any proof-assistant check; the box 8<=150 (about 26,000 core-s, skipped by choice); the producer's W9 run on 8<=130 and 7<=200 (superseded by the auditor's complete screen); "
            "re-implementation of producer controls N2, N3 and the float-grid check; any search outside the boxes; a human audit. Recorded so the absences are explicit.",
            [], num([D / "RESULT.md", D / "PREREG_ITEM.md", D / "PREREG_ADDENDUM_1.md"], "producer text and preregistration; they contain no claim about this paper beyond the recorded absences")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
