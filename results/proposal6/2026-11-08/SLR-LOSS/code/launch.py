"""Launch CP-SAT jobs pinned to cores, wait, print final status line of each.
usage: launch.py tlimit J pool g tag  core:N:rp:rq ...   (N = base size = n+g)"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = os.path.expanduser("~/.cache/slrvenv/bin/python")
tlimit, J, pool, g, tag = sys.argv[1:6]
procs = []
for spec in sys.argv[6:]:
    core, N, rp, rq = spec.split(":")
    n = int(N) - int(g)
    log = os.path.join(HERE, "..", "logs", f"{tag}_n{n}_g{g}.log")
    f = open(log, "w")
    cmd = ["taskset", "-c", core, PY, os.path.join(HERE, "cpsat2.py"), "--workers", os.environ.get("SLR_W", "1"), N, J, tlimit, f"{tag}_n{n}", "--pool", pool,
           "--g", g, "--rp", rp, "--rq", rq]
    procs.append((log, subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT)))
for log, p in procs:
    p.wait()
    last = open(log).read().strip().splitlines()[-1]
    print(log, p.returncode, last[:420], flush=True)
