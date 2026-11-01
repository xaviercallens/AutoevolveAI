"""Build the Elenchus claim ledger for the GR-11 paper (papers/p5_graffiti_20_21_census).

Modelled on papers/p5_cubic_bipartite_cb68/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not be filed above
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
SRC_COMMIT = "b6dad99"  # HEAD of the working branch when written; the lane records and this paper are uncommitted working-tree files


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
    logs = sorted((D / "logs").glob("scan_n*.json"))
    c = [
        rec("GR11-L-0001", "L", "citation",
            "Kumar and Pragada, arXiv:2607.19817 v1 (22 Jul 2026, unrefereed; AI used for ideation): Theorem 1.2, E(G) >= 2(n - alpha(G)) (Fajtlowicz, Graffiti #543); with alpha <= min(n - n_+, n - n_-) it gives "
            "E >= 2 max(n_+, n_-), which they state resolves Aouchiche-Hansen 2010 Conjectures #20, #21 (Table 6). The proof was NOT checked by us.",
            [], cite("arXiv:2607.19817v1", "abstract; Thm 1.2; corollary after it (resolves [4, Conjectures #20, #21, Table 6])",
                     "Read by the independent AI auditor (third-party text is not shipped); abstract page re-checked 2026-11-01",
                     "taken as stated; unrefereed; proof unchecked")),
        rec("GR11-L-0002", "L", "citation",
            "Written on the Wall (July 2004 scan, sha256 d2c779d2...f7733, read by eye): p.19 conjecture 20 'The number of positive eigenvalues of a graph is not more than their sum', conjecture 21 'The number of negative eigenvalues "
            "of a graph is not more than the sum of its positive eigenvalues'; comment citing Fajtlowicz 1987 [F2], sum |eig| >= rank (partial solution to 21); p.23 conjecture 29 (Randic index <= number of negative distance eigenvalues; "
            "disproved by Alon, Saks, Seymour, Shearer, Winkler, July 88).",
            [], cite("Written on the Wall, July 2004", "pp. 19 and 23", "Pages rendered and read by eye (scanned bitmap, no text layer)",
                     "taken as read; the scan is third-party and is not shipped")),
        rec("GR11-L-0003", "L", "citation",
            "Zhang, arXiv:2409.15504, calls E >= 2 min(n_+, n_-) open; evidently a slip for max, so not evidence that conjectures 20 and 21 are open. Roucairol-Cazenave, arXiv:2409.18626, do not state conjectures 20 or 21.",
            [], cite("arXiv:2409.15504; arXiv:2409.18626", "as quoted in AUDIT.md section 0; producer read 2409.18626 in full",
                     "Abstract pages checked for title, authors and date on 2026-11-01", "taken as stated")),
        rec("GR11-C-0001", "C", "argument",
            "Frame: tr A = 0 gives S+ = E/2, so conjectures 20 (n_+ <= S+) and 21 (n_- <= S+) are together exactly E >= 2 max(n_+, n_-); the min-count version follows from E >= rank (Fajtlowicz 1987). "
            "Equality: K_n has spectrum {n-1, (-1)^(n-1)} so S+ = n-1 = n_- (tie in 21); K1, K2 tie in both, K3 in 21, P3 strict, so statements about the minimum margin 0.236 of conjecture 20 need n >= 4.",
            ["GR11-L-0001", "GR11-L-0002"],
            arg("C-argument", "AUDIT.md sections 0 and 5 (corrections 1, 4, 5); exact verdict for K_11 in data/summaries/n11_exact_check.jsonl.",
                [PAPER / "AUDIT.md", D / "summaries" / "n11_exact_check.jsonl"], "algebra; exact_check.py")),
        rec("GR11-C-0002", "C", "argument",
            "Certified smallest non-K_n margins of conjecture 21 (sympy real-root enclosures of width 1e-25 on the integer characteristic polynomial, exact inertia by Descartes' rule): n=5: 0.2143 (DQw); 6: 0.1463 (EQjO); "
            "7: 0.1249 (FQhVO); 8: 0.0941 (GQhTUg); 9: 0.0806 (HQhTQji); 10: 0.0645 (IQhTQiitO); 11: 0.0561 (JQhTQiiTVT?, part 39); n=4: 0.2361 (CU = P4). They shrink with n. These are the argmin graphs found by the float scan; "
            "that no other graph is smaller is the Tier X claim GR11-X-0001. Rerun for this paper (exact_margin_rerun_2026-11-01.txt).",
            ["GR11-C-0001"],
            arg("C-exact-integer", "data/audit/out/exact_margin_rerun_2026-11-01.txt; auditor out/n9.json, n10.json, n11_39.json.",
                [D / "audit" / "out" / "exact_margin_rerun_2026-11-01.txt", D / "audit" / "out" / "n9.json", D / "audit" / "out" / "n10.json", D / "audit" / "out" / "n11_39.json",
                 D / "audit" / "code" / "exact_margin.py"], "exact_margin.py (sympy)")),
        rec("GR11-C-0003", "C", "argument",
            "Rounding soundness: every nonzero adjacency eigenvalue of a graph with n <= 11 vertices has |lambda| >= 1/11^5 ~ 6.2e-6 (integer product of the nonzero eigenvalues, sum lambda^2 <= 2m <= 110, AM-GM), so the 1e-9 zero "
            "threshold gives exact n_+ and n_- given LAPACK backward stability (error ~1e-14), and the error of S+ (Weyl) is ~1e-12, below the 1e-6 flag band. Not interval-certified.",
            [], arg("C-argument", "AUDIT.md section 3; auditor out/*.json fields inertia_mismatch_float, min_abs_nonzero_ev, max_dSplus_geev_syevd.",
                    [PAPER / "AUDIT.md", D / "audit" / "out" / "n10.json", D / "audit" / "out" / "n11_5.json"], "paper-and-pencil bound; audit_scan.py")),
        rec("GR11-C-0004", "C", "argument",
            "Independent recomputation by a separate AI agent instance (own graph6 decoder, exact inertia via Faddeev-LeVerrier plus Descartes, S+ via dgeev cross-checked against dsyevd, BFS distances, certified enclosures for argmin graphs): "
            "all 11,989,760 graphs with n <= 10 match with 0 violations; n=11 parts 31, 39, 12, 5, 7 of 40 (122,811,341 graphs, 12.2%) match the producer's per-part logs; the producer's scan.py rerun on part 39 is identical except time. "
            "35 of the 40 n=11 parts are not recomputed independently. Control 29 firings (n=7: FEhf?, n=8: G?zTb_, ...) genuine under exact distance inertia. NOT a human audit.",
            ["GR11-C-0001", "GR11-C-0003"],
            arg("C-audit-report", "AUDIT.md sections 2-4; data/audit/.", [PAPER / "AUDIT.md", D / "audit" / "code" / "audit_scan.py", D / "audit" / "out" / "producer_rerun_n11_39.json",
                                                                        D / "audit" / "out" / "n11_31.json"], "audit_scan.py, exact_c29.py, exact_margin.py")),
        rec("GR11-X-0001", "X", "numeric",
            "Float scan (numpy eigvalsh, threshold 1e-9, violation < -1e-6): all 1,018,690,325 connected graphs with 4 <= n <= 11 (counts 6, 21, 112, 853, 11117, 261080, 11716571, 1006700565) give 0 violations of Graffiti 20 and 21; the only graph "
            "with margin below 1e-6 is K_n (n <= 10) and K_11 (n=11), decided exactly. Controls: Graffiti 29 first fires at n=7 (1862 firings at n=11), negative controls fire 0 times. This is a consistency check of a claimed theorem (GR11-L-0001), not a new result.",
            ["GR11-L-0001", "GR11-C-0001"],
            num([D / "result.json", D / "summaries" / "n11_aggregate.json", D / "summaries" / "n11_exact_check.jsonl", D / "code" / "scan.py", D / "code" / "exact_check.py"] + logs,
                "producer logs for every part; floats, not interval-certified")),
        rec("GR11-X-0002", "X", "numeric",
            "NOT done: Lean or any proof-assistant check; a check of the Kumar-Pragada proof; independent recomputation of 35 of 40 n=11 parts; conjectures 39, 40, 129, 143, 154, 195, 284, 698 (BLOCKED, definitions not pinned); "
            "third-party 'already resolved' claims for other conjectures; a human audit; n >= 12. Recorded so the absences are explicit.",
            [], num([D / "RESULT.md", D / "PREREG_ITEM.md", D / "PREREG_ITEM_addendum2.md"], "producer text and preregistration; they contain no claim about this paper beyond the recorded absences")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
