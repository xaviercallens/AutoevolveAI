"""Headline: non-4-colourability of the exact distance graph, three routes. usage: python headline.py <data_dir> <work_dir> <out_json>"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

import satlib as S


def sha(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main() -> None:
    data, work, outj = sys.argv[1:4]
    edges = [tuple(e) for e in json.load(open(os.path.join(data, "edges_088928.json")))]
    n = 101
    res: dict = {"n": n, "m": len(edges)}
    # (a) Glucose4 + DRUP + drat-trim
    cl = S.encode_a(n, edges, 4, sym=True)
    cnf, prf = os.path.join(work, "gale101_k4.cnf"), os.path.join(work, "gale101_k4.drup")
    sat, model, dt = S.solve_glucose_proof(cl, prf, cnf)
    res["a_glucose4_sat"] = sat
    res["a_glucose4_seconds"] = dt
    print("a: glucose sat =", sat, dt, flush=True)
    if not sat:
        res["a_cnf_sha256"], res["a_proof_sha256"] = sha(cnf), sha(prf)
        res["a_proof_bytes"] = os.path.getsize(prf)
        t = time.time()
        ok, txt = S.drat_trim(cnf, prf)
        res["a_drat_trim_verified"] = ok
        res["a_drat_trim_seconds"] = time.time() - t
        res["a_drat_trim_tail"] = txt.strip().splitlines()[-6:]
        print("a: drat-trim verified =", ok, flush=True)
    else:
        res["a_colouring_valid"] = S.valid_colouring(S.decode_a(model, n, 4), edges, 4)
    # (b) CaDiCaL 1.9.5, encoding B, no symmetry breaking
    cb = S.encode_b(n, edges, 4)
    sb, mb, dtb = S.solve_plain(cb, "cadical195")
    res["b_cadical195_encB_sat"] = sb
    res["b_seconds"] = dtb
    print("b:", sb, dtb, flush=True)
    sb2, _, dtb2 = S.solve_plain(cl, "cadical195")
    res["b2_cadical195_encA_sat"] = sb2
    res["b2_seconds"] = dtb2
    print("b2:", sb2, dtb2, flush=True)
    # 5-colourability, validated exactly
    c5 = S.encode_a(n, edges, 5, sym=True)
    s5, m5, d5 = S.solve_plain(c5, "cadical195")
    res["five_colourable"] = s5
    if s5:
        res["five_colouring_valid"] = S.valid_colouring(S.decode_a(m5, n, 5), edges, 5)
        res["five_colouring"] = S.decode_a(m5, n, 5)
    print("5-col:", s5, flush=True)
    json.dump(res, open(outj, "w"), indent=1)
    # (c) exhaustive DSATUR
    t = time.time()
    d, col, nodes = S.dsatur_colourable(n, edges, 4, node_limit=int(os.environ.get("NODE_LIMIT", "200000000")))
    res["c_dsatur_colourable"] = d
    res["c_nodes"] = nodes
    res["c_seconds"] = time.time() - t
    print("c:", d, nodes, res["c_seconds"], flush=True)
    json.dump(res, open(outj, "w"), indent=1)


if __name__ == "__main__":
    main()
