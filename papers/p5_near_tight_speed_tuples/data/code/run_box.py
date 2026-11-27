#!/usr/bin/env python3
"""Run one box with the correct scan on cores 6 and 7 (two interleaved parts) and merge.
usage: run_box.py n N [label] [W=4|9]"""
import subprocess, sys, os, time, json
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
code = os.path.join(root, "code")
n, N = int(sys.argv[1]), int(sys.argv[2])
label = sys.argv[3] if len(sys.argv) > 3 else "box"
W = sys.argv[4] if len(sys.argv) > 4 else "4"
bw = "40" if W == "4" else "60"
d = os.path.join(root, "data", label)
os.makedirs(d, exist_ok=True)
t0 = time.time()
procs = []
for part, core in [(0, "6"), (1, "7")]:
    out = os.path.join(d, f"n{n}_N{N}_W{W}_part{part}.txt")
    procs.append((part, out, subprocess.Popen(["taskset", "-c", core, os.path.join(code, f"lrspec_scan_w{W}"), str(n), str(N), bw, "0", "0", str(part), "2", out],
                                              stderr=subprocess.PIPE, text=True)))
logs = []
for part, out, p in procs:
    _, err = p.communicate()
    logs.append(err.strip())
wall = time.time() - t0
lines = []
for part, out, p in procs:
    lines += [l for l in open(out).read().splitlines() if l.strip()]
lines.sort(key=lambda s: list(map(int, s.split())))
merged = os.path.join(d, f"n{n}_N{N}_W{W}.txt")
open(merged, "w").write("\n".join(lines) + ("\n" if lines else ""))
for part, out, p in procs:
    os.remove(out)
print(json.dumps({"n": n, "N": N, "W": W, "wall_s": round(wall, 1), "core_s_approx": round(2 * wall, 1), "primitive_neartight": len(lines), "logs": logs}))
