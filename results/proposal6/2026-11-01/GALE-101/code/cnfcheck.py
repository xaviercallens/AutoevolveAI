"""Proof without symmetry breaking + independent structural audit of the CNF files.
usage: python cnfcheck.py <data_dir> <work_dir> <out_json>"""
from __future__ import annotations

import hashlib
import json
import os
import sys

import satlib as S


def sha(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def audit_cnf(path: str, edges: set[tuple[int, int]], n: int, k: int, sym: bool) -> dict:
    """Independent parser: expected clause SET built from scratch from the edge list, compared with the file."""
    lines = open(path).read().splitlines()
    head = lines[0].split()
    clauses = []
    for l in lines[1:]:
        lits = tuple(sorted(int(x) for x in l.split()[:-1]))
        assert l.split()[-1] == "0"
        clauses.append(lits)
    exp: set[tuple[int, ...]] = set()
    x = lambda v, c: v * k + c + 1
    for v in range(n):
        exp.add(tuple(sorted(x(v, c) for c in range(k))))
        for a in range(k):
            for b in range(a + 1, k):
                exp.add(tuple(sorted((-x(v, a), -x(v, b)))))
    for (u, w) in edges:
        for c in range(k):
            exp.add(tuple(sorted((-x(u, c), -x(w, c)))))
    if sym:
        exp.add((x(0, 0),))
    return {
        "header": head,
        "n_clauses_file": len(clauses),
        "n_clauses_distinct": len(set(clauses)),
        "n_clauses_expected": len(exp),
        "file_equals_expected_set": set(clauses) == exp,
        "edge_conflict_clauses": 4 * len(edges),
    }


def main() -> None:
    data, work, outj = sys.argv[1:4]
    edges = {tuple(e) for e in json.load(open(os.path.join(data, "edges_088928.json")))}
    n, k = 101, 4
    res: dict = {}
    # sym = True file from headline.py
    res["with_sym_cnf_audit"] = audit_cnf(os.path.join(work, "gale101_k4.cnf"), edges, n, k, True)
    # sym = False
    cl = S.encode_a(n, sorted(edges), k, sym=False)
    cnf, prf = os.path.join(work, "gale101_k4_nosym.cnf"), os.path.join(work, "gale101_k4_nosym.drup")
    sat, _, dt = S.solve_glucose_proof(cl, prf, cnf)
    res["nosym_glucose_sat"] = sat
    res["nosym_seconds"] = dt
    res["nosym_cnf_audit"] = audit_cnf(cnf, edges, n, k, False)
    if not sat:
        ok, txt = S.drat_trim(cnf, prf)
        res["nosym_drat_trim_verified"] = ok
        res["nosym_drat_tail"] = txt.strip().splitlines()[-5:]
        res["nosym_cnf_sha256"], res["nosym_proof_sha256"] = sha(cnf), sha(prf)
        res["nosym_proof_bytes"] = os.path.getsize(prf)
    res["with_sym_cnf_sha256"] = sha(os.path.join(work, "gale101_k4.cnf"))
    res["with_sym_proof_sha256"] = sha(os.path.join(work, "gale101_k4.drup"))
    # drat-trim in forward mode as well, on the nosym pair
    import subprocess
    p = subprocess.run([S.DRAT_TRIM, cnf, prf, "-f"], capture_output=True, text=True)
    res["nosym_drat_trim_forward_verified"] = "s VERIFIED" in p.stdout
    json.dump(res, open(outj, "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
