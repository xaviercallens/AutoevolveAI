#!/usr/bin/env python3
"""Ladder 2 of PREREG_ADDENDUM_1: 8<=130, 7<=180, then 6<=150, 6<=200 (8<=150 not run; 7<=200 was run separately, logs/ext2_n7_N200.json)."""
import subprocess, os, json
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
code = os.path.join(root, "code")
steps = [(8, 130, "ext2"), (7, 180, "ext2"), (6, 150, "ext2"), (6, 200, "ext2")]
for n, N, lab in steps:
    r = subprocess.run(["python3", "-I", os.path.join(code, "run_box.py"), str(n), str(N), lab, "4"], capture_output=True, text=True)
    open(os.path.join(root, "logs", f"{lab}_n{n}_N{N}.json"), "w").write(r.stdout + r.stderr)
