"""C1b full N = 11 census driver: resumable, detached, per-part logs.

Usage:
  run_census.py start <census_fast binary> [mod] [workers]   daemonises itself (double fork + setsid), writes logs/driver.pid
  run_census.py foreground <census_fast binary> [mod] [workers]
Resume: run the same `start` command again; parts whose data/parts/part_<res>of<mod>.json exists and passes the count check are
skipped, stale *.tmp files are discarded. Stop: kill the PID in logs/driver.pid (its pipelines die with their process group).

Each part runs `nauty-geng -c 11 res/mod | census_fast 11 tmp.json`, both pinned with `taskset -c 2,3`. geng is NOT run with -q,
so its stderr count line ">Z <k> graphs generated" is kept in logs/parts/part_<res>of<mod>.log and must equal the number of
graphs census_fast decided (and bad_lines must be 0). No graph6 data is written to disk.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PARTS = ROOT / "data" / "parts"
PLOGS = ROOT / "logs" / "parts"
DRIVER_LOG = ROOT / "logs" / "driver.log"
PIDFILE = ROOT / "logs" / "driver.pid"
CORES = "2,3"
N = 11
GENG_RE = re.compile(r">Z\s+(\d+)\s+graphs generated in\s+([\d.]+)\s+sec")


def log(msg: str) -> None:
    with open(DRIVER_LOG, "a") as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%S") + " " + msg + "\n")


def part_ok(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        d = json.load(open(path))
    except (OSError, ValueError):
        return False
    return bool(d.get("count_check_ok"))


def launch(binary: str, res: int, mod: int) -> dict:
    tag = f"part_{res:04d}of{mod}"
    tmp = PARTS / (tag + ".json.tmp")
    plog = PLOGS / (tag + ".log")
    lf = open(plog, "w")
    lf.write(f"start {time.strftime('%Y-%m-%dT%H:%M:%S')} geng -c {N} {res}/{mod}\n")
    lf.flush()
    geng = subprocess.Popen(["taskset", "-c", CORES, "nauty-geng", "-c", str(N), f"{res}/{mod}"], stdout=subprocess.PIPE, stderr=lf)
    cen = subprocess.Popen(["taskset", "-c", CORES, binary, str(N), str(tmp)], stdin=geng.stdout, stderr=lf)
    assert geng.stdout is not None
    geng.stdout.close()
    return {"res": res, "tag": tag, "tmp": tmp, "plog": plog, "lf": lf, "geng": geng, "cen": cen, "t0": time.time()}


def finish(job: dict, mod: int) -> bool:
    gr = job["geng"].wait()
    cr = job["cen"].wait()
    job["lf"].write(f"end {time.strftime('%Y-%m-%dT%H:%M:%S')} geng_rc {gr} census_rc {cr}\n")
    job["lf"].close()
    text = job["plog"].read_text()
    m = GENG_RE.search(text)
    if gr != 0 or cr != 0 or m is None or not job["tmp"].exists():
        log(f"{job['tag']} FAILED rc geng {gr} census {cr} geng_line {bool(m)}")
        return False
    d = json.load(open(job["tmp"]))
    geng_count = int(m.group(1))
    ok = d["graphs"] == geng_count and d["bad_lines"] == 0 and d["N"] == N and d["corrupt"] == "none"
    d.update({"res": job["res"], "mod": mod, "geng_count": geng_count, "geng_seconds": float(m.group(2)),
              "wall_seconds_part": round(time.time() - job["t0"], 1), "count_check_ok": ok})
    final = PARTS / (job["tag"] + ".json")
    with open(job["tmp"], "w") as f:
        json.dump(d, f, indent=0)
    os.replace(job["tmp"], final)
    log(f"{job['tag']} graphs {d['graphs']} geng {geng_count} ok {ok} excluded {d['excluded_certified']} cand {d['n_candidates']} "
        f"near {d['n_near']} wall {d['wall_seconds_part']}s")
    return ok


def run(binary: str, mod: int, workers: int) -> None:
    PARTS.mkdir(parents=True, exist_ok=True)
    PLOGS.mkdir(parents=True, exist_ok=True)
    for t in PARTS.glob("*.tmp"):
        t.unlink()
    todo = [r for r in range(mod) if not part_ok(PARTS / f"part_{r:04d}of{mod}.json")]
    log(f"driver pid {os.getpid()} mod {mod} workers {workers} todo {len(todo)} binary {binary}")
    running: list[dict] = []
    failed = False
    while (todo or running) and not failed:
        while todo and len(running) < workers and not failed:
            running.append(launch(binary, todo.pop(0), mod))
        time.sleep(2)
        still = []
        for job in running:
            if job["cen"].poll() is not None and job["geng"].poll() is not None:
                if not finish(job, mod):
                    failed = True
            else:
                still.append(job)
        running = still
    if failed:
        for job in running:
            job["geng"].kill()
            job["cen"].kill()
        log("STOPPED: a part failed its count/return-code check; fix and resume")
    else:
        log("ALL_PARTS_DONE")


def main() -> None:
    mode, binary = sys.argv[1], str(Path(sys.argv[2]).resolve())
    mod = int(sys.argv[3]) if len(sys.argv) > 3 else 256
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    if mode == "foreground":
        run(binary, mod, workers)
        return
    if mode != "start":
        raise SystemExit("mode must be start or foreground")
    if os.fork() > 0:
        print("detaching; see", PIDFILE, "and", DRIVER_LOG)
        return
    os.setsid()
    if os.fork() > 0:
        os._exit(0)
    devnull = os.open(os.devnull, os.O_RDWR)
    out = os.open(str(DRIVER_LOG), os.O_WRONLY | os.O_CREAT | os.O_APPEND)
    os.dup2(devnull, 0)
    os.dup2(out, 1)
    os.dup2(out, 2)
    PIDFILE.write_text(str(os.getpid()) + "\n")
    run(binary, mod, workers)


if __name__ == "__main__":
    main()
