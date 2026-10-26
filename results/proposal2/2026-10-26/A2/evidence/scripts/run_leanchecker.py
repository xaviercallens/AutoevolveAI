"""Run the toolchain's `leanchecker` (kernel replay of each module's declarations into its
imported environment) over every corpus module of a closure, with N workers.

usage: run_leanchecker.py <closure_json> <out_jsonl> <workers> [<module> ...]
Appends one JSON line per module (resumable: modules already in out_jsonl with rc==0 are skipped).
Must be run with LEAN_PATH set (e.g. under `lake env`).
"""
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

LC = "/home/callensxavier_gmail_com/.elan/toolchains/leanprover--lean4---v4.34.0-rc2/bin/leanchecker"
closure = json.loads(Path(sys.argv[1]).read_text())
out = Path(sys.argv[2])
workers = int(sys.argv[3])
mods = sys.argv[4:] or closure["topo_order"]
done: set[str] = set()
if out.exists():
    for line in out.read_text().splitlines():
        r = json.loads(line)
        if r["rc"] == 0:
            done.add(r["module"])
todo = [m for m in mods if m not in done]
print(f"modules={len(mods)} already_ok={len(done)} todo={len(todo)}", flush=True)


def check(m: str) -> dict:
    t0 = time.time()
    try:
        p = subprocess.run([LC, m], capture_output=True, text=True, timeout=3600)
        rc, err = p.returncode, (p.stdout + p.stderr)[-2000:]
    except subprocess.TimeoutExpired:
        rc, err = -999, "TIMEOUT"
    r = {"module": m, "rc": rc, "secs": round(time.time() - t0, 1), "output": err}
    with out.open("a") as f:
        f.write(json.dumps(r) + "\n")
    if rc != 0:
        print(f"FAIL {m} rc={rc} {err[:300]}", flush=True)
    return r


with ThreadPoolExecutor(max_workers=workers) as ex:
    results = list(ex.map(check, todo))
bad = [r for r in results if r["rc"] != 0]
print(f"DONE checked={len(results)} failures={len(bad)}", flush=True)
