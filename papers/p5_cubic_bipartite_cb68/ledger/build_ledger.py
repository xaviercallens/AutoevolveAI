"""Build the Elenchus claim ledger for the EG-CB68 paper (papers/p5_cubic_bipartite_cb68).

Modelled on papers/p5_lonely_runner_ind/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not be filed above
anything in its depends_on, and the kind caps the tier (lean_axioms A, citation L, argument C, numeric X). There is NO Lean in this paper,
so there is no Tier A row. An independent AI audit exists (AUDIT.md, ACCEPT_WITH_CORRECTIONS, not a person).
Run:  /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I build_ledger.py   (any python3 -I works)
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
SRC_COMMIT = "abe4718ed552e3c77b7207cadb8095d998e02602"  # producer commit of the lane records (the paper itself is uncommitted)


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
    d = DATA
    aud = d / "audit" / "out"
    c = [
        # ------------------------------------------------------------------ L
        rec("EGC-L-0001", "L", "citation",
            "Tranquilli, arXiv 2608.02675 v1 (the method source; NOT 2609.04686, which is Garcia): Prop. 3 and Lemmas 5-6 (a simple cubic bipartite graph without 4-cycles is the Levi graph of a "
            "linear v_3-configuration; Levi 8- and 16-cycles are Berge 4- and 8-cycles); Prop. 10 (the triangle-rooted, least-unfinished-point, lexicographic growth search is complete for "
            "connected configurations with a Berge triangle); Lemma 8 (Moore bound for girth 10); Lemma 9 (triangle roots, two orbits); Table 2 (cap-29 counters per orbit); Table 4 (leaf counts). "
            "Certified result of that paper: no counterexample up to 58 vertices.",
            [], cite("arXiv:2608.02675v1", "Prop. 3, Lemmas 5-9, Prop. 10, Tables 2 and 4, Sec. 3.1 and 4",
                     "Read by the producer (method only; the repository of that paper was not opened) and re-read by the independent AI auditor",
                     "taken as stated; Prop. 10 was independently re-derived by the producer and by the auditor (EGC-C-0001); Table 4 leaf counts do not match either implementation (unexplained, see paper)")),
        rec("EGC-L-0002", "L", "citation",
            "Premise of route 1 only, orders 62-68: n(3,10) = 70, i.e. a cubic graph of girth at least 10 has at least 70 vertices (O'Keefe-Wong, JCTB 29 (1980) 91-105, computer assisted; completeness "
            "Wong 1983, McKay et al. 2000), read by the producer ONLY through the Exoo-Jajcay Dynamic Cage Survey (EJC DS16 v3, p. 7 Table 1, p. 10 Sec. 2.1.6). The original was not read by anyone. "
            "Together with the Moore bounds (girth 10: at least 62 vertices; girth 12: at least 126) it makes the triangle-rooted search sufficient for bipartite graphs of order at most 68. "
            "Route 2 (arbitrary root) does not use this premise.",
            ["EGC-L-0001"], cite("O'Keefe-Wong JCTB 29 (1980) 91-105 via Exoo-Jajcay EJC DS16 v3", "Table 1 p. 7; Sec. 2.1.6 p. 10",
                                 "The proof for girth 10 was computer assisted",
                                 "taken as stated through the survey; only the 62-68 part of route 1 depends on it")),
        rec("EGC-L-0003", "L", "citation",
            "Prior and parallel claims, as read: (a) A. V. Ripatti, BAIKAL/MOTOR 2017 one-page abstract (isem.irk.ru/conferences/mopt2017/Abstracts/BAIKAL_2017_paper_138.pdf): the smallest cubic graphs without "
            "4-, 8- and 16-cycles have 78 vertices, found with canonical augmentation and 'probabilistic checking of every node'; no certificate, no full paper found; covers every cubic graph on at most 76 vertices. "
            "(b) Ducoffe-Dumitru, arXiv 2609.28594 v1: bipartite graphs of minimum degree 3 and order at most 66 by SAT modulo symmetries, forbidding 4, 8, 16, 32 (and 64 at orders 64-66), no proof log. "
            "(c) Garcia, arXiv 2609.04686: cites 'Exoo gave 54 <= f(4) <= 78'. None of (Tranquilli, Ducoffe-Dumitru, Garcia) cites Ripatti.",
            [], cite("Ripatti BAIKAL 2017 abstract; arXiv:2609.28594v1; arXiv:2609.04686", "abstract; Sec. encoding E3 and results; introduction",
                     "Ripatti abstract fetched and text-extracted by the auditor (the PDF is not shipped); Ducoffe-Dumitru and Garcia read",
                     "taken as stated; Ripatti's claim is uncertified and only an abstract was available, so this paper cannot assess it beyond its statement")),
        # ------------------------------------------------------------------ C
        rec("EGC-C-0001", "C", "argument",
            "Coverage lemma (Tranquilli Prop. 10 for both root modes): with root {0,1,2} (arbitrary-root mode) or the triangle roots plus orbit 1 or 2, every connected linear v_3-configuration with v <= cap and "
            "no Berge 4- or 8-cycle appears as a completion of the growth tree, because the schedule is the lexicographic least-unfinished-point schedule with first-occurrence labels and the structural, "
            "C8 and C16 tests are monotone under sub-configurations. Re-derived independently by the producer and by the auditor (AUDIT.md section 1); NOT formalised. Empirical validation with both "
            "filters off: canonical class counts 1, 1, 3, 10, 31, 229, 2036 for v = 7..13 in both modes equal the nauty genbg -c sets exactly (set equality), and the auditor extended the check to v = 13 arbitrary root "
            "and v = 14 triangle roots (21,398 classes, set equal to genbg -c).",
            ["EGC-L-0001"],
            arg("C-argument", "result.json P2/P2b; auditor cov/p2_m0.json, cov/p2_tri_v14.canon.txt vs cov/genbg_c_v14.canon.txt (comm difference 0, identical sha256).",
                [d / "result.json", aud / "cov" / "p2_m0.json", aud / "cov" / "p2_m1_cap14.json", aud / "cov" / "p2_m2_cap14.json", aud / "cov" / "p2_tri_v14.canon.txt", aud / "cov" / "genbg_c_v14.canon.txt",
                 d / "audit" / "code" / "aud_search.c.txt"], "cb_search (P2), aud_search, nauty labelg and genbg")),
        rec("EGC-C-0002", "C", "argument",
            "Positive controls, run before any headline number: P1 cap 29 reproduces Tranquilli Table 2 exactly in both orbits (1,405 / 106,964 / 7,184 / 63,526 / 34,850 / 0 and 20,088 / 1,655,404 / 113,012 / 1,208,473 / 313,832 / 0), "
            "the auditor's independent search reproduces them and the producer's transcript hash; 19-block states 46 + 291 = 337; P2c genbg -d3:3 -D3:3 -Z1 with an independent DFS cycle filter finds no C4/C8/C16-free cubic bipartite graph for v = 7..16 (producer) "
            "and v = 7..15 (auditor: 1, 1, 3, 10, 31, 229, 2036, 21,399, 245,342 C4-free graphs, every one with a C8); P3 C16 filter off, cap 19: completions exist, one isomorphism class, C4/C8-free with a C16 "
            "(16 labelled leaves with triangle roots, 128 with the arbitrary root; the class is self-dual with a colour-preserving automorphism group of order 57, 114 as an uncoloured Levi graph, so 128 labelled copies of one configuration are consistent with the paper's '128 symmetric 19_3-configurations').",
            ["EGC-C-0001"],
            arg("C-exact-integer", "result.json P1/P2/P2b/P2c/P3/P3b; logs/controls/P1_*; auditor out/cov/p3_*.json, out/genbg/v*.out.txt, code/aut19.py.",
                [d / "result.json", d / "logs" / "controls" / "P1_cap29_o1_A.json", d / "logs" / "controls" / "P1_cap29_o2_A.json", aud / "cov" / "p3_m0.json", aud / "genbg" / "v15.out.txt", d / "audit" / "code" / "aut19.py"],
                "cb_search, cb_check, g6_cycles, nauty genbg/labelg, aud_search, aud_g6cyc")),
        rec("EGC-C-0003", "C", "argument",
            "Negative controls: N1 C8 filter off (C16 on), cap 13: completions appear, the Fano plane (v = 7) is the only class; N2 C8 filter on, cap 8: 0 completions in all three modes, with it off Fano (v = 7) and 8_3 (v = 8) appear "
            "and the checker accepts when completions are allowed; the Heawood graph (girth 6, 21 eight-cycles) is rejected by the C8 test on its last block; N3 tamper tests: truncated stream, flipped counter, corrupted C8 witness, "
            "wrong-length C16 witness, C16 relabelled as structural, deleted record, trailing data, inserted fake completion are all rejected by cb_check.py and cb_check_fast; the auditor's own tamper.py "
            "(11 further kinds: witness ending at an unintroduced point, non-simple walk, C16 witness cut to length 12, G re-tagged 8, deleted S, duplicated S, swapped records, false S, subtree replaced by S, header cap changed, header orbit changed) "
            "is rejected by all three checkers (cb_check.py, cb_check_fast, aud_check); verdicts as reported in AUDIT.md section 3 (the tampered streams are not shipped, 3.4 MB each; tamper.py regenerates them).",
            ["EGC-C-0002"],
            arg("C-exact-integer", "logs/controls/N1_*, N2_*, N3_tamper*.json; auditor code tamper.py and AUDIT.md section 3.",
                [d / "logs" / "controls" / "N1_canon.json", d / "logs" / "controls" / "N2_cap8_o0_c8on.json", d / "logs" / "controls" / "N2_heawood.json", d / "logs" / "controls" / "N3_tamper.json",
                 d / "logs" / "controls" / "N3_tamper_fast.json", d / "audit" / "code" / "tamper.py", PAPER / "AUDIT.md"], "cb_search, cb_check.py, cb_check_fast, heawood_c8.py, tamper_tests.py, tamper.py, aud_check")),
        rec("EGC-C-0004", "C", "argument",
            "Route 1 (triangle-rooted, Tranquilli's mode), caps 30..34 (orders 60..68) and also cap 35 (order 70, girth-6 part only): both orbits close with 0 completions; oracle A (DFS endpoint sets, cached) and oracle B (join of complete half-path lists, uncached) give identical "
            "counters and identical FNV-1a decision-transcript hashes at every cap and orbit; the 12 certificate streams (134,625,781 bytes gzip in all, kept outside the bundle, names/sizes/sha256 in table_certs.tex and data/certs_inventory.json) "
            "are accepted by the producer's Python and C checkers and by the auditor's independent C checker aud_check (expected cap and orbit hard-coded, flags empty, c6 = 0); the auditor's own search and the producer's rebuilt binary reproduce all counters and hashes.",
            ["EGC-C-0001", "EGC-C-0002", "EGC-C-0003"],
            arg("C-exact-integer", "table_route1.tex (generated by ledger/gen_tables.py from data/main and data/audit/out), certs_inventory.json, tables_check.json.",
                [d / "certs_inventory.json", HERE / "tables_check.json", d / "main" / "T_cap34_o2_A.json", d / "main" / "T_cap34_o2_B.json", d / "main" / "T_cap34_o2_check.json",
                 aud / "mine_T_cap34_o2.json", aud / "certs" / "T34_o2.aud.txt", d / "audit" / "code" / "aud_check.c.txt"], "cb_search A/B, cb_check.py, cb_check_fast, aud_search, aud_check")),
        rec("EGC-C-0005", "C", "argument",
            "Route 2 (arbitrary root {0,1,2}, no triangle assumed, no Moore or cage premise), caps 29..34 (orders 58..68): 0 completions at every cap, oracles A and B give identical counters and transcript hashes, and the auditor's independent search "
            "reproduces every counter and hash. Cap 34: 13,798,102 states, 1,899,509,410 proposals, hash 76e8805d44433718. The cap-34 certificate stream (tens of GB, never stored) was regenerated by the producer's binary and streamed through a FIFO into "
            "cb_check_fast (accepted, data/main/R_cap34_checkfast.json), and regenerated again by the AUDITOR from a rebuilt binary and streamed into aud_check: ACCEPT, all counters equal, same stream sha256 "
            "0112b8085b969bcfa75335fdb2aedc5d4b5b0e80c6dddf2d5d9ead8f5a18fad5. The Python check of this stream was stopped unfinished and is not used.",
            ["EGC-C-0001", "EGC-C-0002", "EGC-C-0003"],
            arg("C-exact-integer", "table_route2.tex; data/main/R_cap34_{A,B,checkfast}.json; logs/main/R_cap34_stream_sha256.txt; auditor out/r34_aud.out.txt, r34_stream.sha.txt, r34_certrun.json.",
                [d / "main" / "R_cap34_A.json", d / "main" / "R_cap34_B.json", d / "main" / "R_cap34_checkfast.json", d / "logs" / "main" / "R_cap34_stream_sha256.txt",
                 aud / "r34_aud.out.txt", aud / "r34_stream.sha.txt", aud / "r34_certrun.json", aud / "mine_R_cap34.json"], "cb_search A/B, cb_check_fast, aud_search, aud_check")),
        rec("EGC-C-0006", "C", "argument",
            "Independent re-computation by the auditor (separate AI agent instance, 2026-10-31; own code, independent code but the same Prop. 10 schedule and the same kind of endpoint-set path test, so not an independent method): "
            "own search aud_search.c, own checker aud_check.c, own cycle filter aud_g6cyc.c; full enumeration with nauty-genbg -d3:3 -D3:3 -Z1 (disconnected graphs included) for v = 7..15 finds no graph without a 4-, 8- or 16-cycle "
            "(orders up to 30; every one has a C8); filter sanity checks (Heawood, Tutte-Coxeter, Petersen give C8; the cube gives C4; C10 gives none; C16 gives C16); the producer's cb_search.c and cb_check_fast.c rebuild to the frozen sha256 values. "
            "NOT done: genbg at v = 16 (stopped for cost).",
            ["EGC-C-0004", "EGC-C-0005"],
            arg("C-audit-report", "AUDIT.md section 2; data/audit/ (sources as .c.txt, run scripts, outputs).",
                [PAPER / "AUDIT.md", d / "audit" / "code" / "aud_search.c.txt", d / "audit" / "code" / "aud_check.c.txt", d / "audit" / "code" / "aud_g6cyc.c.txt", d / "audit" / "runscripts" / "run_genbg.sh.txt"],
                "aud_search, aud_check, aud_g6cyc, nauty genbg")),
        rec("EGC-C-0007", "C", "argument",
            "HEADLINE (route 2, no premise). Every simple cubic bipartite graph on at most 68 vertices has a cycle of length 4, 8 or 16 (equivalently: no connected linear v_3-configuration with v <= 34 avoids Berge 4- and 8-cycles). "
            "Argument: a cubic bipartite graph has equal sides, so order <= 68 means v <= 34; a C4-free one is the Levi graph of a linear v_3-configuration, and a disconnected counterexample would contain a connected one of smaller order; "
            "the arbitrary-root search at cap 34 has no completion (EGC-C-0005); the coverage lemma (EGC-C-0001) is prose. This is a RE-CHECK, not a new bound: Ripatti 2017 (uncertified abstract) and Ducoffe-Dumitru 2026 "
            "(SAT, no proof log) cover these orders; we know of no earlier witness-checked computation. Filed C: exhaustive search plus witness checkers, no kernel check.",
            ["EGC-C-0005", "EGC-C-0006", "EGC-C-0001", "EGC-C-0003", "EGC-L-0003"],
            arg("C-assembly", "Assembly of the enumeration, the checkers, the audit and the literature as in Sections 3-6 of the paper.", [d / "result.json", d / "RESULT.md", PAPER / "AUDIT.md"], "none")),
        rec("EGC-C-0008", "C", "argument",
            "Route-1 reading of the graph statement: for order <= 60 the triangle-rooted search (EGC-C-0004) plus Tranquilli's Moore lemma suffices; for orders 62-68 it additionally needs n(3,10) = 70 (Tier L, read through a survey only), "
            "so the 62-68 part of route 1 is conditional; route 2 (EGC-C-0007) does not need it. The three (3,10)-cages (order 70) lie outside the triangle-rooted search; the route-1 cap-35 run is not a statement about order 70.",
            ["EGC-C-0004", "EGC-L-0002", "EGC-L-0001"],
            arg("C-assembly", "Reduction as in Section 3 of the paper (RESULT.md section 1).", [d / "RESULT.md"], "none")),
        # ------------------------------------------------------------------ X
        rec("EGC-X-0001", "X", "numeric",
            "Absence claim, not a licence: we know of no earlier witness-checked (certificate-producing) computation for cubic bipartite orders 60-68. Basis: alphaXiv and web searches on 2026-10-28 (before the first run) "
            "and 2026-10-31 (which found Ripatti 2017, missed on 10-28), plus the auditor's search of OEIS/House of Graphs (one query each, not browsed). Residual risk: a certified computation exists in a source we did not find "
            "(Ripatti's full method, unpublished code). Not a priority claim.",
            [], num([d / "logs" / "stopped_runs.txt", d / "PREREG_ITEM.md"], "records of the search dates; no claim about this paper rests on it")),
        rec("EGC-X-0002", "X", "numeric",
            "NOT run or not complete: Lean/kernel formalisation (none, Tier C is the ceiling); pytest tests/ (not run); the repository guards antigravity_guard.py and test_rigor_guard.py exit 1 on pre-existing files elsewhere in the repository "
            "and flag no EG-CB68 file (logs/guard_*.txt); the Python check of the route-2 cap-34 stream (started 2026-10-31 14:41 UTC, stopped 17:34 UTC after at least 17.5 GB without rejection, partial hash deleted); "
            "the exploratory extension to caps >= 35 in arbitrary-root mode (cap 35 started 17:06 UTC, stopped 17:34 UTC, no result used); the auditor's genbg run at v = 16; any reading of O'Keefe-Wong 1980 or the full text of Ripatti 2017; a human audit. "
            "Recorded so the absences are explicit.",
            [], num([d / "logs" / "guard_antigravity.txt", d / "logs" / "guard_test_rigor.txt", d / "logs" / "stopped_runs.txt"], "guard transcripts and the stop record; they contain no claim about this paper")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
