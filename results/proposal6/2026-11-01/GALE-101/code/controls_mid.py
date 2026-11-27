"""N5 planted-colourable graph at claimed size; corrupted-proof control for drat-trim. usage: python controls_mid.py <work_dir> <out_json>"""
from __future__ import annotations

import json
import os
import random
import sys

import satlib as S
from controls_small import complete


def main() -> None:
    work, outj = sys.argv[1:3]
    res: dict = {}
    # N5: planted 4-colourable graph, 101 vertices, 2030 edges
    for seed in range(3):
        rng = random.Random(seed)
        part = [rng.randrange(4) for _ in range(101)]
        pairs = [(i, j) for i in range(101) for j in range(i + 1, 101) if part[i] != part[j]]
        edges = rng.sample(pairs, 2030)
        cl = S.encode_a(101, edges, 4, sym=False)
        ok1, m1, _ = S.solve_plain(cl, "cadical195")
        ok2, m2, _ = S.solve_plain(S.encode_b(101, edges, 4), "cadical195")
        d, col, nodes = S.dsatur_colourable(101, edges, 4, node_limit=5_000_000)
        res[f"N5_seed{seed}"] = {
            "encA_sat": ok1, "encA_valid": S.valid_colouring(S.decode_a(m1, 101, 4), edges, 4) if ok1 else None,
            "encB_sat": ok2, "encB_valid": S.valid_colouring(S.decode_b(m2, 101, 4), edges, 4) if ok2 else None,
            "dsatur": d, "dsatur_valid": S.valid_colouring(col, edges, 4) if d else None, "dsatur_nodes": nodes,
        }
    # corrupted proof must be rejected: K5, k=4 without the symmetry unit so proof is non-trivial; use pigeonhole-like Grotzsch k=3
    from controls_small import grotzsch
    n, e = grotzsch()
    cl = S.encode_a(n, e, 3, sym=False)
    cnf, prf = os.path.join(work, "corrupt.cnf"), os.path.join(work, "corrupt.drup")
    sat, _, _ = S.solve_glucose_proof(cl, prf, cnf)
    ok_good, _ = S.drat_trim(cnf, prf)
    lines = open(prf).read().splitlines()
    # replace the proof by a single bogus lemma that is not RUP and no empty clause
    bogus = os.path.join(work, "bogus.drup")
    with open(bogus, "w") as f:
        f.write("1 2 3 0\n")
    ok_bogus, txt = S.drat_trim(cnf, bogus)
    # empty proof on a non-trivially UNSAT formula
    empty = os.path.join(work, "empty.drup")
    open(empty, "w").write("")
    ok_empty, txt2 = S.drat_trim(cnf, empty)
    res["corrupt_proof"] = {"sat": sat, "good_verified": ok_good, "bogus_verified": ok_bogus, "empty_verified": ok_empty,
                            "proof_lines": len(lines)}
    res["PASS"] = bool(all(v["encA_sat"] and v["encB_sat"] and v["dsatur"] and v["encA_valid"] and v["encB_valid"] and v["dsatur_valid"]
                           for k, v in res.items() if k.startswith("N5")) and ok_good and not ok_bogus)
    print(json.dumps(res, indent=1))
    json.dump(res, open(outj, "w"), indent=1)


if __name__ == "__main__":
    main()
