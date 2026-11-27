"""Certify a (v, s) float state file produced by cover_ls_fast (lines 'v s'), optionally after a
chain-LP polish (search2.descend).  Usage:
  certify_file.py state.txt n search_radius_num search_radius_den out_cert.json meta.json [--polish]
Appends one JSON line to logs/certify_file.log."""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"

import json
import random
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cover_ls import certify  # noqa: E402
from search2 import Arcs, descend, gap  # noqa: E402


def main() -> None:
    st, n, rn, rd, out, meta = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], json.load(open(sys.argv[6]))
    polish = "--polish" in sys.argv
    t0 = time.process_time()
    rows = [ln.split() for ln in open(st).read().splitlines() if ln.strip()]
    v = [int(r[0]) for r in rows]
    s = np.array([float(r[1]) for r in rows])
    assert len(v) == n
    A = Arcs(np.array(v, dtype=float))
    g0 = gap(A, s)
    rec = {"state": os.path.basename(st), "n": n, "gap_before": g0, "E_before": 1 / g0 - (n + 1)}
    d_star = rn / rd
    if polish:
        s, g1 = descend(A, s, random.Random(1), patience=30, d=g0)
        rec.update({"gap_after_polish": g1, "E_after": 1 / g1 - (n + 1)})
        d_star = g1
    ok = False
    if d_star < 1.0 / (n + 1):
        meta = dict(meta, source_state=os.path.basename(st), polished=polish)
        ok, info = certify(v, list(s), 1, n + 1, out, d_star, meta)
        rec.update({"certified": ok, "D": info.get("D"), "msg": info.get("checker2", info.get("reason"))})
    else:
        rec["certified"] = False
    rec["cpu_s"] = time.process_time() - t0
    with open(os.path.join(os.path.dirname(HERE), "logs", "certify_file.log"), "a") as fh:
        fh.write(json.dumps(rec) + "\n")
    print(json.dumps(rec))


if __name__ == "__main__":
    main()
