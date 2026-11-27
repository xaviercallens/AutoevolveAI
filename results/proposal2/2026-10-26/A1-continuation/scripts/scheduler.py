"""Resumable scheduler for the A1 continuation (L1 kernel re-execution of the remaining certificate stages).

One process (guarded by an flock) that runs Lean compiles of generated chunk files, one per configured core.

* Work list: every `manifests/*.json` (one per stage, written by the generators); re-read on every loop, so a stage
  added later is picked up without a restart. Entries: core modules, chunks, planted false chunks, assembly files.
* Config: `pipeline_config.json` (re-read on every loop): `cores` (list of CPU ids; one Lean worker per core),
  `mem_budget_gb` (24), `min_mem_available_gb` (9), `default_peak_gb` (8, used for a stage until a chunk of it has
  been measured), `stage_order`, `paused`.
* Per-chunk status JSON in STATUS_DIR: queued / running / ok / fail (+ rc, wall time, peak RSS from /usr/bin/time -v,
  sha256 of the source, axiom report, classification). A chunk whose status is `ok` with the same source sha256 is
  skipped on restart; a `running` entry whose pid is gone (or belongs to a dead scheduler) is re-queued.
* Acceptance: genuine files must compile with rc 0, no `sorry` warning, and every `#print axioms` report within
  {propext, Classical.choice, Quot.sound}; a planted file is `ok` (= correctly rejected) only if Lean exits non-zero
  with a kernel refutation ("decide proved that the proposition ... is false" or "decide failed"), not on a timeout,
  an OOM kill or an import error.
* Memory guard: at most floor(mem_budget / measured peak RSS of the stage) concurrent workers, and no new worker while
  MemAvailable < min_mem_available_gb.
* After each finished chunk: STATUS.md and status_summary.json in the results directory are regenerated.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
CONT = REPO / "results" / "proposal2" / "2026-10-26" / "A1-continuation"
FORMAL = REPO / "formal_cert"
WORK = Path("/home/callensxavier_gmail_com/a1l1_oleans")
ROOTS = WORK / "roots"
STATUS_DIR = WORK / "status"
LOGS = WORK / "logs"
CONFIG = CONT / "pipeline_config.json"
PY = "/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python"
L1LEAN = CONT / "scripts" / "l1lean.py"
WHITELIST = {"propext", "Classical.choice", "Quot.sound"}

DEFAULT_CONFIG = {"cores": [0, 1, 2, 3], "mem_budget_gb": 24, "min_mem_available_gb": 9, "default_peak_gb": 8,
                  "stage_order": ["cs", "core_test", "bdsup", "inside_hess", "global_grid", "table"], "paused": False,
                  "timeout_s": 172800}


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def log(msg: str) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    with (LOGS / "scheduler.log").open("a") as fh:
        fh.write(f"{now()} {msg}\n")


def load_config() -> dict:
    cfg = dict(DEFAULT_CONFIG)
    try:
        cfg.update(json.loads(CONFIG.read_text()))
    except (OSError, json.JSONDecodeError) as e:
        log(f"config read failed ({e}); using defaults")
    return cfg


_SHA_CACHE: dict[tuple[str, int, int], str] = {}


def sha256(p: Path) -> str:
    """sha256 of a file, memoised on (path, mtime_ns, size)."""
    st = p.stat()
    key = (str(p), st.st_mtime_ns, st.st_size)
    if key not in _SHA_CACHE:
        _SHA_CACHE[key] = hashlib.sha256(p.read_bytes()).hexdigest()
    return _SHA_CACHE[key]


def safe(cid: str) -> str:
    return cid.replace("/", "__")


def write_json_atomic(p: Path, obj: object) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1) + "\n")
    os.replace(tmp, p)


def load_entries(cfg: dict) -> list[dict]:
    entries: list[dict] = []
    for mf in sorted((CONT / "manifests").glob("*.json")):
        try:
            m = json.loads(mf.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        stage = m["stage"]
        for c in m.get("core", []):
            entries.append({"id": f"{stage}/core/{c['module'].split('.')[-1]}", "stage": stage, "kind": "core",
                            "file": c["file"], "module": c["module"], "deps": c.get("deps", []), "order": -1})
        for c in m.get("chunks", []):
            entries.append(c)
    rank = {s: i for i, s in enumerate(cfg["stage_order"])}
    kind_rank = {"core": 0, "planted": 1, "chunk": 2, "assemble": 3}
    entries.sort(key=lambda e: (rank.get(e["stage"], 99), kind_rank.get(e["kind"], 9), e.get("order", 0), e["id"]))
    return entries


def status_path(cid: str) -> Path:
    return STATUS_DIR / (safe(cid) + ".json")


def read_status(cid: str) -> dict | None:
    try:
        return json.loads(status_path(cid).read_text())
    except (OSError, json.JSONDecodeError):
        return None


def olean_of(entry: dict) -> Path:
    return ROOTS / safe(entry["id"]) / (entry["module"].replace(".", "/") + ".olean")


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def mem_available_gb() -> float:
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) / 1024 / 1024
    return 0.0


AX_RE = re.compile(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[([^\]]*)\])")


FORBIDDEN = ("debug.skipKernelTC", "native_decide", "implemented_by", "@[extern", "unsafe ", "admit", "sorry",
             "ofReduceBool", "axiom ")


def forbidden_in(entry: dict) -> list[str]:
    try:
        src = (FORMAL / entry["file"]).read_text()
    except OSError:
        return ["<source unreadable>"]
    return [t for t in FORBIDDEN if t in src]


def classify(entry: dict, res: dict) -> tuple[str, dict]:
    out = str(res.get("output", ""))
    bad_src = forbidden_in(entry)
    if bad_src:
        return "fail", {"axioms": [], "non_whitelisted_axioms": [], "verdict": f"forbidden construct in source: {bad_src}"}
    axioms = []
    bad_ax = []
    for m in AX_RE.finditer(out):
        names = [a.strip() for a in (m.group(3) or "").split(",") if a.strip()]
        axioms.append({"decl": m.group(1), "axioms": names})
        bad_ax += [a for a in names if a not in WHITELIST]
    info = {"axioms": axioms, "non_whitelisted_axioms": sorted(set(bad_ax))}
    rc = res.get("rc")
    timeout = rc == -9 or "TIMEOUT" in out[:20]
    oom = (res.get("lean_exit") is None and rc not in (0, 1)) or "out of memory" in out.lower()
    if entry["kind"] == "planted":
        # a planted file holds an honest refutation `plant_refuted : ¬ claim` (must compile, axioms reported) and the
        # planted claim (must be the only error: the kernel evaluates `decide claim` to `false`, reported as a kernel
        # type mismatch, or the elaborator's "decide proved that the proposition ... is false")
        n_err = len(re.findall(r"error:", out))
        refut_ok = any(a["decl"].endswith("plant_refuted") for a in axioms) and not bad_ax
        kernel_rej = "(kernel) application type mismatch" in out or ("proved that the proposition" in out and "is false" in out)
        if rc != 0 and n_err == 1 and refut_ok and kernel_rej and not timeout:
            return "ok", dict(info, verdict="planted claim rejected by the kernel; honest refutation proved")
        return "fail", dict(info, verdict="planted claim NOT rejected by a kernel refutation" + (" (timeout)" if timeout else ""))
    if rc == 0 and "declaration uses 'sorry'" not in out and "sorryAx" not in out and not bad_ax:
        if entry["kind"] in ("chunk", "assemble") and not axioms:
            return "fail", dict(info, verdict="no #print axioms report found")
        return "ok", dict(info, verdict="compiled, axioms within whitelist")
    why = "timeout" if timeout else ("oom/killed" if oom else f"rc {rc}")
    return "fail", dict(info, verdict=f"compile failed ({why})")


def closure(entry: dict, by_mod: dict[str, dict]) -> list[dict]:
    seen: dict[str, dict] = {}
    stack = list(entry.get("deps", []))
    while stack:
        m = stack.pop()
        if m in seen or m not in by_mod:
            continue
        seen[m] = by_mod[m]
        stack += by_mod[m].get("deps", [])
    return list(seen.values())


_PEAKS: dict[str, tuple[float, dict[str, float], dict[str, float]]] = {}


def file_group(e: dict) -> str:
    return re.sub(r"\d+", "", e["file"])


def expected_peak(e: dict, entries: list[dict], cfg: dict) -> float:
    """Expected peak RSS (GB) of entry e, from measured peaks; recomputed at most every 60 s."""
    now_t = time.time()
    cached = _PEAKS.get("x")
    if cached is None or now_t - cached[0] > 60:
        by_group: dict[str, float] = {}
        by_stage: dict[str, float] = {}
        for x in entries:
            st = read_status(x["id"]) or {}
            if st.get("state") in ("ok", "fail") and st.get("peak_rss_kb"):
                gb = int(st["peak_rss_kb"]) / 1048576
                g = file_group(x)
                by_group[g] = max(by_group.get(g, 0.0), gb)
                by_stage[x["stage"]] = max(by_stage.get(x["stage"], 0.0), gb)
        cached = (now_t, by_group, by_stage)
        _PEAKS["x"] = cached
    _, by_group, by_stage = cached
    return by_group.get(file_group(e)) or by_stage.get(e["stage"]) or float(cfg["default_peak_gb"])


def probation(stage: str, entries: list[dict]) -> dict:
    """Probation entries of a stage: its cores, its planted chunks and its first (cheapest) genuine chunk."""
    st_entries = [e for e in entries if e["stage"] == stage]
    probes = [e for e in st_entries if e["kind"] in ("core", "planted")]
    genuine = [e for e in st_entries if e["kind"] == "chunk"]
    if genuine:
        probes.append(genuine[0])
    states = [(read_status(e["id"]) or {}).get("state", "queued") for e in probes]
    return {"probe_ids": {e["id"] for e in probes}, "passed": all(x == "ok" for x in states),
            "failed": any(x == "fail" for x in states)}


def render_status(entries: list[dict], cfg: dict) -> None:
    rows = []
    stages: dict[str, dict] = {}
    for e in entries:
        st = read_status(e["id"]) or {"state": "queued"}
        s = stages.setdefault(e["stage"], {"total": 0, "ok": 0, "fail": 0, "running": 0, "queued": 0, "wall_ok_s": 0.0,
                                           "ops_ok": 0, "ops_total": 0, "peak_rss_kb": 0, "planted_total": 0,
                                           "planted_rejected": 0})
        s["total"] += 1
        s[st["state"]] = s.get(st["state"], 0) + 1
        ops = int(e.get("ops_hint", 0) or 0)
        if e["kind"] == "chunk":
            s["ops_total"] += ops
        if e["kind"] == "planted":
            s["planted_total"] += 1
            if st["state"] == "ok":
                s["planted_rejected"] += 1
        if st["state"] == "ok":
            s["wall_ok_s"] += float(st.get("wall_s", 0) or 0)
            s["user_ok_s"] = s.get("user_ok_s", 0.0) + float(st.get("user_s") or 0)
            if e["kind"] == "chunk":
                s["ops_ok"] += ops
        if st.get("peak_rss_kb"):
            s["peak_rss_kb"] = max(s["peak_rss_kb"], int(st["peak_rss_kb"]))
        rows.append((e, st))
    ncores = max(1, len(cfg["cores"]))
    for s in stages.values():
        rate = s["wall_ok_s"] / s["ops_ok"] if s["ops_ok"] else None
        s["projected_remaining_core_h"] = round(rate * (s["ops_total"] - s["ops_ok"]) / 3600, 2) if rate else None
        s["projected_remaining_wall_h_at_cores"] = round(s["projected_remaining_core_h"] / ncores, 2) if rate else None
    summary = {"generated": now(), "cores": cfg["cores"], "stages": stages}
    write_json_atomic(CONT / "status_summary.json", summary)
    lines = ["# A1 continuation: L1 pipeline status", "",
             f"Generated {summary['generated']} by `scripts/scheduler.py` (regenerated after every finished chunk; do not edit).",
             f"Cores: {cfg['cores']}. Per-chunk status JSON: `{STATUS_DIR}`. Logs: `{LOGS}`.", "",
             "| stage | entries | ok | fail | running | queued | planted rejected | kernel wall s (ok) | peak RSS GB | projected remaining core-h | wall h at current cores |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name in cfg["stage_order"] + sorted(set(stages) - set(cfg["stage_order"])):
        if name not in stages:
            pend = (CONT / "manifests_pending" / f"{name}.json").exists()
            what = "generated, pending release (manifests_pending/)" if pend else "generator not yet written (BLOCKED)"
            lines.append(f"| {name} | 0 | - | - | - | - | - | - | - | {what} | - |")
            continue
        s = stages[name]
        lines.append(f"| {name} | {s['total']} | {s['ok']} | {s['fail']} | {s['running']} | {s['queued']} | "
                     f"{s['planted_rejected']}/{s['planted_total']} | {s['wall_ok_s']:.0f} | {s['peak_rss_kb']/1048576:.1f} | "
                     f"{s['projected_remaining_core_h'] if s['projected_remaining_core_h'] is not None else 'n/a'} | "
                     f"{s['projected_remaining_wall_h_at_cores'] if s['projected_remaining_wall_h_at_cores'] is not None else 'n/a'} |")
    lines += ["", "Probation: a stage's bulk chunks start only after its cores, planted controls and first genuine chunk are ok.",
              "The wall column sums process wall time (inflated by machine load); see projection.json / PIPELINE.md for the measured per-unit projection.", ""]
    for name in stages:
        pb = probation(name, entries)
        lines.append(f"* probation `{name}`: " + ("passed" if pb["passed"] else ("FAILED (stage halted)" if pb["failed"] else "in progress")))
    lines += ["", "## Failures and running entries", ""]
    for e, st in rows:
        if st["state"] in ("fail", "running"):
            lines.append(f"* `{e['id']}` ({e['kind']}): {st['state']} {st.get('verdict', '')} {st.get('wall_s', '')}")
    lines += ["", "## Finished entries (most recent 40)", ""]
    done = sorted([(st.get("finished", ""), e, st) for e, st in rows if st["state"] == "ok"], key=lambda x: x[0])[-40:]
    for fin, e, st in done:
        lines.append(f"* {fin} `{e['id']}` ({e['kind']}) {st.get('wall_s')} s, {int(st.get('peak_rss_kb') or 0)/1048576:.2f} GB, {st.get('verdict')}")
    tmp = CONT / "STATUS.md.tmp"
    tmp.write_text("\n".join(lines) + "\n")
    os.replace(tmp, CONT / "STATUS.md")


class Adopted:
    """A worker started by a previous scheduler instance, watched by pid (not our child)."""

    def __init__(self, pid: int) -> None:
        self.pid = pid
        self.returncode: int | None = None

    def poll(self) -> int | None:
        if pid_alive(self.pid):
            try:
                with open(f"/proc/{self.pid}/stat") as fh:
                    if fh.read().split()[2] == "Z":
                        self.returncode = 0
                        return 0
            except OSError:
                pass
            return None
        self.returncode = 0
        return 0


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    lockf = open(WORK / "scheduler.lock", "w")
    try:
        fcntl.flock(lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("another scheduler holds the lock", file=sys.stderr)
        return 1
    lockf.write(str(os.getpid()))
    lockf.flush()
    (WORK / "scheduler.pid").write_text(str(os.getpid()) + "\n")
    log(f"scheduler start pid {os.getpid()}")
    stop = {"flag": False}

    def on_term(signum: int, frame: object) -> None:
        stop["flag"] = True

    signal.signal(signal.SIGTERM, on_term)
    signal.signal(signal.SIGINT, on_term)
    running: dict[str, tuple[object, dict, int]] = {}
    # entries left 'running' by a previous scheduler: a worker that is still alive is ADOPTED (watched by pid until
    # it exits, then its result JSON is read); a dead one is re-queued
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    cfg0 = load_config()
    by_id0 = {e["id"]: e for e in load_entries(cfg0)}
    for sp in STATUS_DIR.glob("*.json"):
        try:
            st = json.loads(sp.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if st.get("state") == "running":
            pid = int(st.get("pid") or 0)
            if pid and pid_alive(pid) and st.get("id") in by_id0:
                running[st["id"]] = (Adopted(pid), by_id0[st["id"]], int(st.get("core", -1)))
                log(f"adopted running worker {st['id']} pid={pid}")
                continue
            st.update(state="queued", note=f"re-queued at restart {now()} (previous run interrupted)")
            write_json_atomic(sp, st)
    last_render = 0.0
    while True:
        cfg = load_config()
        entries = load_entries(cfg)
        by_id = {e["id"]: e for e in entries}
        by_mod = {e["module"]: e for e in entries}
        # reap finished workers
        changed = False
        for cid, (proc, entry, core) in list(running.items()):
            if proc.poll() is None:
                continue
            del running[cid]
            jf = LOGS / (safe(cid) + ".json")
            try:
                res = json.loads(jf.read_text())
            except (OSError, json.JSONDecodeError):
                res = {"rc": proc.returncode, "output": "no result json", "wall_s": None, "peak_rss_kb": None}
            state, info = classify(entry, res)
            st = read_status(cid) or {}
            st.update(state=state, rc=res.get("rc"), wall_s=res.get("wall_s"), user_s=res.get("user_s"),
                      peak_rss_kb=res.get("peak_rss_kb"), finished=now(), core=core, **info)
            write_json_atomic(status_path(cid), st)
            log(f"done {cid} state={state} wall={res.get('wall_s')} rss_kb={res.get('peak_rss_kb')} {info.get('verdict')}")
            changed = True
        if changed or time.time() - last_render > 300:
            render_status(entries, cfg)
            last_render = time.time()
        if stop["flag"]:
            for cid, (proc, entry, core) in running.items():
                try:
                    os.killpg(proc.pid, signal.SIGTERM)
                except OSError:
                    pass
                st = read_status(cid) or {}
                st.update(state="queued", note=f"stopped by SIGTERM {now()}")
                write_json_atomic(status_path(cid), st)
            log("scheduler stopped by signal")
            render_status(entries, cfg)
            return 0
        if not cfg.get("paused") and not (WORK / "PAUSE").exists():
            busy = {c for (_, _, c) in running.values()}
            free = [c for c in cfg["cores"] if c not in busy]
            for e in entries:
                if not free:
                    break
                if e["id"] in running:
                    continue
                src = FORMAL / e["file"]
                if not src.exists():
                    continue
                st = read_status(e["id"])
                cur_sha = sha256(src)
                if st and st.get("state") in ("ok", "fail") and st.get("sha256") == cur_sha:
                    continue
                deps = closure(e, by_mod)
                if any((read_status(d["id"]) or {}).get("state") != "ok" for d in deps):
                    continue
                # probation: a stage's bulk chunks wait until its cores, its planted controls and its first
                # genuine chunk (the probe) are ok; a failed probation entry halts the stage
                prob = probation(e["stage"], entries)
                if e["kind"] in ("chunk", "assemble") and e["id"] not in prob["probe_ids"] and not prob["passed"]:
                    continue
                if any(d["kind"] == "planted" for d in deps):
                    continue
                # memory guard: the expected peak of every running worker plus this one must fit in mem_budget_gb.
                # Expected peak of an entry = max measured peak RSS of finished entries of the same file group
                # (path with digits removed, e.g. Table/N.lean), else of its stage, else default_peak_gb.
                peak_gb = expected_peak(e, entries, cfg)
                in_use = sum(expected_peak(r[1], entries, cfg) for r in running.values())
                cap = int(cfg["mem_budget_gb"] // max(peak_gb, 0.5))
                if running and in_use + peak_gb > float(cfg["mem_budget_gb"]):
                    continue
                if mem_available_gb() < cfg["min_mem_available_gb"]:
                    log(f"MemAvailable {mem_available_gb():.1f} GB < {cfg['min_mem_available_gb']} GB: not starting {e['id']}")
                    break
                core = free.pop(0)
                root = ROOTS / safe(e["id"])
                jf = LOGS / (safe(e["id"]) + ".json")
                cmd = [PY, "-I", str(L1LEAN), str(src), e["module"], str(root), "--core", str(core),
                       "--timeout", str(cfg["timeout_s"]), "--json", str(jf)]
                for d in deps:
                    cmd += ["--dep", str(olean_of(d))]
                LOGS.mkdir(parents=True, exist_ok=True)
                outf = open(LOGS / (safe(e["id"]) + ".out"), "w")
                proc = subprocess.Popen(cmd, stdout=outf, stderr=subprocess.STDOUT, start_new_session=True)
                running[e["id"]] = (proc, e, core)
                write_json_atomic(status_path(e["id"]), {"id": e["id"], "stage": e["stage"], "kind": e["kind"],
                                                         "module": e["module"], "file": e["file"], "sha256": cur_sha,
                                                         "state": "running", "pid": proc.pid, "core": core,
                                                         "started": now(), "scheduler_pid": os.getpid()})
                log(f"start {e['id']} core={core} pid={proc.pid} cap={cap} peak_gb={peak_gb:.1f}")
                render_status(entries, cfg)
                last_render = time.time()
        time.sleep(10)


if __name__ == "__main__":
    sys.exit(main())
