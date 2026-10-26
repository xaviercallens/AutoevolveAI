"""Kernel replay driver. usage: kr_run.py build|replay|forged"""
import json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

R = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
FC = R / "formal_cert"
OUT = FC / ".olean_out"
PRIV = OUT
TC = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/elan/toolchains/leanprover--lean4---v4.34.1/bin")
KR = R / "results/kernel_replay_2026-10-26"
LOGS = KR / "logs"
BASE_LP = Path("/tmp/leanpath.txt").read_text().strip()  # pinned build + Mathlib + OUT


def lp() -> str:
    return BASE_LP


plan = json.loads((KR / "plan.json").read_text())
# scope: not recent, not SandierSerfatyL1 (work in progress by another job, no oleans built, untracked)
scope = [r for r in plan if not r["recent"] and ".SandierSerfatyL1." not in r["module"]]
SKIP_EXTRA = set(sys.argv[2:])


def src_of(m: str) -> Path:
    return FC / (m.replace(".", "/") + ".lean")


def build(r: dict) -> dict:
    m = r["module"]
    ol = PRIV / (m.replace(".", "/") + ".olean")
    ol.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, LEAN_PATH=lp(), PATH=f"{TC}:{os.environ['PATH']}")
    cmd = ["nice", "-n", "10", str(TC / "lean"), "-DautoImplicit=false", f"--root={FC}", "-o", str(ol),
           "-i", str(ol.with_suffix(".ilean")), str(src_of(m))]
    t0 = time.time()
    p = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=3000, cwd="/tmp")
    (LOGS / f"build_{m}.log").write_text(p.stdout + p.stderr)
    return {"module": m, "build_rc": p.returncode, "build_s": round(time.time() - t0, 1)}


def replay(r: dict) -> dict:
    m = r["module"]
    env = dict(os.environ, LEAN_PATH=lp(), PATH=f"{TC}:{os.environ['PATH']}")
    t0 = time.time()
    try:
        p = subprocess.run(["nice", "-n", "10", str(TC / "leanchecker"), m], env=env, capture_output=True,
                           text=True, timeout=3600, cwd="/tmp")
        rc, out = p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        rc, out = -999, "TIMEOUT"
    s = round(time.time() - t0, 1)
    (LOGS / f"{m}.log").write_text(f"rc={rc}\n{out}")
    rec = {"module": m, "rc": rc, "seconds": s, "tail": out[-500:]}
    with (KR / "replay.jsonl").open("a") as f:
        f.write(json.dumps(rec) + "\n")
    print(m, rc, s, flush=True)
    return rec


mode = sys.argv[1]
if mode == "build":
    todo = [r for r in scope if not r["fresh"] and r["module"] not in SKIP_EXTRA]
    print("to build:", [r["module"] for r in todo], flush=True)
    res = []
    pending = todo
    for rnd in range(3):  # retry rounds to resolve inter-dependencies among these
        nxt = []
        for r in pending:
            x = build(r)
            print(x, flush=True)
            if x["build_rc"] == 0:
                res.append(x)
            else:
                nxt.append(r)
        pending = nxt
        if not pending:
            break
    (KR / "build.json").write_text(json.dumps({"built": res, "failed": [r["module"] for r in pending]}, indent=1))
elif mode == "replay":
    done = set()
    jl = KR / "replay.jsonl"
    if jl.exists():
        done = {json.loads(l)["module"] for l in jl.read_text().splitlines() if json.loads(l)["rc"] == 0}
    built = {x["module"] for x in json.loads((KR / "build.json").read_text())["built"]} if (KR / "build.json").exists() else set()
    todo = [r for r in scope if (r["fresh"] or r["module"] in built) and r["module"] not in done and r["module"] not in SKIP_EXTRA]
    print("to replay:", len(todo), flush=True)
    with ThreadPoolExecutor(3) as ex:
        list(ex.map(replay, todo))
