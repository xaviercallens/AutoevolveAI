#!/usr/bin/env python3
"""Control (c): C scan vs pure-Python brute force on small boxes; and control (b): two witness lists give identical output on a mid box."""
import subprocess, os, json, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
code = os.path.join(root, "code")
cdir = os.path.join(root, "data", "controls")
res = {}
for n, N in [(4, 30), (5, 24), (6, 20), (7, 18), (8, 16)]:
    out4 = os.path.join(cdir, f"B_w4_n{n}_N{N}.txt")
    subprocess.run(["taskset", "-c", "7", os.path.join(code, "lrspec_scan_w4"), str(n), str(N), "40", "0", "0", "0", "1", out4], capture_output=True)
    r = subprocess.run(["taskset", "-c", "7", "python3", "-I", os.path.join(code, "brute.py"), str(n), str(N), out4], capture_output=True, text=True)
    res[f"n{n}_N{N}"] = r.stdout.strip()
for n, N in [(4, 200), (5, 100), (6, 110), (7, 60), (8, 45)]:
    a = os.path.join(cdir, f"W4_n{n}_N{N}.txt"); b = os.path.join(cdir, f"W9_n{n}_N{N}.txt")
    ra = subprocess.run(["taskset", "-c", "7", os.path.join(code, "lrspec_scan_w4"), str(n), str(N), "40", "0", "0", "0", "1", a], capture_output=True, text=True)
    rb = subprocess.run(["taskset", "-c", "7", os.path.join(code, "lrspec_scan_w9"), str(n), str(N), "60", "0", "0", "0", "1", b], capture_output=True, text=True)
    sa = open(a).read(); sb = open(b).read()
    res[f"twoW_n{n}_N{N}"] = {"identical": sa == sb, "lines": sa.count("\n"), "logW4": ra.stderr.strip(), "logW9": rb.stderr.strip()}
print(json.dumps(res, indent=1))
