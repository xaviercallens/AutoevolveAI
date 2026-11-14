#!/usr/bin/env python3
"""Negative controls N1 (strictness corrupted) and N2 (truncated candidates) vs the true scan, plus N3 tight family."""
import subprocess, sys, os, json
from fractions import Fraction

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scan = os.path.join(root, "code", "lrspec_scan_w4")
cdir = os.path.join(root, "data", "controls")
res = {}


def run(n, N, strict, mode, out):
    r = subprocess.run(["taskset", "-c", "7", scan, str(n), str(N), "40", str(strict), str(mode), "0", "1", out],
                       capture_output=True, text=True)
    line = r.stderr.strip()
    cnt = sum(1 for _ in open(out))
    return cnt, line


for n, N in [(4, 200), (6, 60), (7, 50), (8, 40)]:
    true_out = os.path.join(cdir, f"T_n{n}_N{N}.txt")
    c_true, l0 = run(n, N, 0, 0, true_out)
    c_str, l1 = run(n, N, 1, 0, os.path.join(cdir, f"N1_strict_n{n}_N{N}.txt"))
    c_trunc, l2 = run(n, N, 0, 1, os.path.join(cdir, f"N2_trunc_n{n}_N{N}.txt"))
    res[f"n{n}_N{N}"] = {"true_primitive_neartight": c_true, "N1_strictness_corrupted": c_str, "N2_truncated_candidates": c_trunc,
                         "N1_changed": c_str != c_true, "N2_changed": c_trunc != c_true,
                         "logs": [l0, l1, l2]}
print(json.dumps(res, indent=1))
