#!/usr/bin/env python3
"""make_result.py -- assemble EG-CB68 result.json from the run logs (no numbers typed by hand) and record the sha256
of every file under EG-CB68/ (except result.json itself)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEYS = ["states", "attempted", "structural", "c8", "c16", "completions"]


def load(rel: str) -> dict:
    p = ROOT / rel
    return json.loads(p.read_text()) if p.exists() else {}


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    res: dict[str, object] = {"item": "EG-CB68", "proposal": 5, "lane": "W1-c", "producer": "Claude (Opus), unaudited"}
    res["written_utc"] = __import__("datetime").datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    res["preregistration_sha256"] = sha(ROOT.parent / "preregistration.json")
    res["item_prereg_sha256"] = {n: sha(ROOT / n) for n in ("PREREG_ITEM.md", "PREREG_ADDENDUM_1.md", "PREREG_ADDENDUM_2.md")}
    res["outcome"] = "KEEP"
    res["outcome_class"] = "(d) independent certified re-check, not a new bound"
    res["statement_checked"] = ("Every simple cubic bipartite graph on at most 68 vertices contains a cycle of length 4, 8 or 16 "
                                "(no connected linear v_3-configuration with v <= 34 avoids Berge 4- and 8-cycles)")
    res["novelty"] = "killed"
    res["prior_claims"] = [
        {"source": "A. V. Ripatti, BAIKAL/MOTOR 2017 abstract, https://isem.irk.ru/conferences/mopt2017/Abstracts/BAIKAL_2017_paper_138.pdf",
         "claim": "smallest cubic graphs without 4,8,16 cycles have 78 vertices (covers all cubic graphs <= 76 vertices)",
         "certified": False, "note": "abstract only, probabilistic node checks, read in session 2026-10-31"},
        {"source": "Ducoffe-Dumitru arXiv 2609.28594 v1", "claim": "bipartite graphs of order <= 66 (min degree 3) contain a power-of-two cycle",
         "forbidden_lengths": "4, 8, 16, 32 (and 64 at orders 64-66); minimality reductions used", "certified": False,
         "note": "SAT without proof log"},
        {"source": "Tranquilli arXiv 2608.02675 v1", "claim": "cubic bipartite <= 58 vertices contain C4, C8 or C16", "certified": True},
    ]
    res["tiers"] = {"configuration_statement_v_le_34": "C (exhaustive search + same-author witness checkers; audit pending)",
                    "graph_statement_le_60_route1": "C (+ Moore lemma)",
                    "graph_statement_62_68_route1": "C conditional on Tier L n(3,10)=70 (O'Keefe-Wong 1980, read via Exoo-Jajcay DS16)",
                    "graph_statement_le_68_route2": "C (arbitrary root, no premise; cb_check_fast accepted cap-34 stream)"}
    res["extension_caps_ge_35"] = "not carried out: stopped by producer after the prior-claim finding (no result used)"
    res["producer_ne_verifier"] = "pending (checkers are same-author code paths)"
    paper = {1: [1405, 106964, 7184, 63526, 34850, 0], 2: [20088, 1655404, 113012, 1208473, 313832, 0]}
    p1 = {}
    for o in (1, 2):
        a, b, c = (load(f"logs/controls/P1_cap29_o{o}_{s}.json") for s in ("A", "B", "check"))
        p1[o] = {"ours": [a.get(k) for k in KEYS], "paper_table2": paper[o],
                 "match": [a.get(k) for k in KEYS] == paper[o], "oracleB_same_hash": a.get("transcript_hash") == b.get("transcript_hash"),
                 "checker_accepted": c.get("accepted")}
    res["P1_cap29"] = p1
    res["P2_counts_triangle"] = load("logs/controls/P2_canon_triangle.json")
    res["P2_counts_arbitrary"] = load("logs/controls/P2_canon_arbitrary.json")
    res["P2b_genbg_set_equality"] = load("logs/controls/P2b_set_equality.json")
    res["P2c_genbg_cycle_filter"] = {v: load(f"logs/controls/P2c_v{v}.json") for v in range(7, 17)}
    res["P3_C16off_cap19_triangle"] = load("logs/controls/P3_canon.json")
    res["P3b_C16off_cap19_arbitrary"] = load("logs/controls/P3b_canon.json")
    res["P3_v19_cycles"] = load("logs/controls/P3_v19_cycles.json")
    res["N1_C8off_cap13_triangle"] = load("logs/controls/N1_canon.json")
    res["N2_cap8"] = {o: {"c8on_completions": load(f"logs/controls/N2_cap8_o{o}_c8on.json").get("completions"),
                          "c8off_canon": load(f"logs/controls/N2_cap8_o{o}_c8off_canon.json"),
                          "c8off_checker": load(f"logs/controls/N2_cap8_o{o}_c8off_check.json").get("accepted")} for o in (0, 1, 2)}
    res["N2_heawood"] = {k: v for k, v in load("logs/controls/N2_heawood.json").items() if k != "fano_blocks"}
    res["N3_tamper_python"] = load("logs/controls/N3_tamper.json").get("all_tampered_rejected")
    res["N3_tamper_fast"] = load("logs/controls/N3_tamper_fast.json").get("all_tampered_rejected")
    tri = {}
    for cap in range(30, 36):
        for o in (1, 2):
            a, b, c = (load(f"data/main/T_cap{cap}_o{o}_{s}.json") for s in ("A", "B", "check"))
            if a:
                tri[f"cap{cap}_o{o}"] = {**{k: a.get(k) for k in KEYS}, "cpu_s_A": a.get("cpu_seconds"),
                                         "oracleB_same_hash": a.get("transcript_hash") == b.get("transcript_hash"),
                                         "python_checker_accepted": c.get("accepted")}
    res["triangle_rooted"] = tri
    arb = {}
    for cap in range(29, 45):
        a, b = load(f"data/main/R_cap{cap}_A.json"), load(f"data/main/R_cap{cap}_B.json")
        fast, py, cr = load(f"data/main/R_cap{cap}_checkfast.json"), load(f"data/main/R_cap{cap}_check_py.json"), load(f"data/main/R_cap{cap}_A_certrun.json")
        if a or cr:
            src = a or cr
            hashes = {"A": a.get("transcript_hash"), "A_certrun": cr.get("transcript_hash"), "B": b.get("transcript_hash")}
            present = {k: v for k, v in hashes.items() if v}
            arb[f"cap{cap}"] = {**{k: src.get(k) for k in KEYS}, "cpu_s_A": a.get("cpu_seconds"),
                                "cpu_s_A_certrun": cr.get("cpu_seconds"), "cpu_s_B": b.get("cpu_seconds"),
                                "transcript_hashes": present,
                                "all_present_hashes_equal": len(set(present.values())) == 1 if len(present) > 1 else None,
                                "fast_checker_accepted": fast.get("accepted") if fast else None,
                                "python_checker_accepted": py.get("accepted") if py else None}
    res["arbitrary_root"] = arb
    st = {}
    for name in ("R_cap34_stream_sha256.txt", "R_cap34_stream_py_sha256.txt"):
        q = ROOT / "logs/main" / name
        st[name] = q.read_text().split()[0] if q.exists() else None
    res["R34_stream_sha256"] = st
    res["R34_streams_identical"] = (st["R_cap34_stream_sha256.txt"] == st["R_cap34_stream_py_sha256.txt"]) if all(st.values()) else None
    ext = Path("/home/callensxavier_gmail_com/EG-CB68_scratch/certs")
    res["external_certificates_sha256_file"] = "logs/main/cert_sha256.txt (gzip files kept outside the repository: " + str(ext) + ")"
    files = {}
    for p in sorted(ROOT.rglob("*")):
        if p.is_file() and p.name != "result.json" and "__pycache__" not in p.parts:
            files[str(p.relative_to(ROOT))] = sha(p)
    res["sha256"] = files
    (ROOT / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "sha256"}, indent=1)[:6000])


if __name__ == "__main__":
    main()
