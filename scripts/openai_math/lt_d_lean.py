#!/usr/bin/env python3
"""LT_D driver: kernel pilot of upstream's Lieb-Thirring closure under LeanMaster's toolchain.

Subcommands (all write only inside --lane; nothing is written into LeanMaster or upstream):
  deps       parse the import closure of OAI.Analysis.LiebThirring.Main, topo-sort, write closure.json
  challenge  elaborate ComparatorChallenges/LiebThirring.lean (Part 1a)
  closure    compile closure files one Lean process at a time, resumable (Part 1b)
  axioms     #print axioms of sharp_lieb_thirring via a scratch importer (Part 1c)
  elenchus   run Elenchus on the four challenge files under LeanMaster's environment (Part 2)
  lock       statement-lock hashes of the four challenge statements (Part 2)
  controls   positive/negative controls of this driver's own classifiers (no Mathlib)
  smoke      tiny-input self test
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

LM = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/SocrateAI-Scientific-Agora-LeanMaster")
UP = LM / "lean4basesource" / "openai-math" / "lean"
ELENCHUS_TOOLS = Path("/mnt/disks/disk-socrateai-local-1/SocrateAI-Scientific-Elenchus/tools")
ROOT_MODULE = "OAI.Analysis.LiebThirring.Main"
FINAL_THEOREM = "OAI.SharpLiebThirring.sharp_lieb_thirring"
CHALLENGES = ["TriangularEnergy", "AtomicGaussian", "PlanarPacking", "LiebThirring"]
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
IMPORT_RE = re.compile(r"^import\s+(\S+)", re.MULTILINE)


def mod_path(mod: str) -> Path:
    return UP / (mod.replace(".", "/") + ".lean")


def closure_order(root: str) -> list[str]:
    """Local (OAI.*) import closure of root, dependencies first. Raises on a cycle or missing file."""
    order: list[str] = []
    state: dict[str, int] = {}

    def visit(m: str) -> None:
        if state.get(m) == 2:
            return
        if state.get(m) == 1:
            raise ValueError(f"import cycle at {m}")
        state[m] = 1
        p = mod_path(m)
        if not p.is_file():
            raise FileNotFoundError(str(p))
        for dep in IMPORT_RE.findall(p.read_text(encoding="utf-8")):
            if dep.startswith("OAI"):
                visit(dep)
        state[m] = 2
        order.append(m)

    sys.setrecursionlimit(10000)
    visit(root)
    return order


def lean_path() -> str:
    """LEAN_PATH exactly as `lake env` gives it in LeanMaster (read-only query)."""
    r = subprocess.run(["lake", "env", "printenv", "LEAN_PATH"], cwd=LM, capture_output=True,
                       text=True, timeout=300)
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError(f"lake env failed rc={r.returncode}: {r.stderr[:500]}")
    return r.stdout.strip()


def run_lean(args: list[str], lp: str, timeout: int, cwd: Path = LM) -> dict[str, object]:
    env = dict(os.environ)
    env["LEAN_PATH"] = lp
    t0 = time.time()
    try:
        r = subprocess.run(["lean", *args], cwd=cwd, capture_output=True, text=True, env=env,
                           timeout=timeout)
        out = r.stdout + r.stderr
        rc = r.returncode
        timed_out = False
    except subprocess.TimeoutExpired as e:
        out = ((e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or "")) + "TIMEOUT"
        rc, timed_out = -1, True
    return {"rc": rc, "seconds": round(time.time() - t0, 1), "timed_out": timed_out,
            "output": out[-6000:], "has_error": bool(re.search(r"\berror\b", out)) or rc != 0 or timed_out}


def first_error(out: str) -> str:
    for line in out.splitlines():
        if re.search(r"\berror\b", line):
            return line[:400]
    return out.strip().splitlines()[-1][:400] if out.strip() else ""


def parse_axioms(out: str) -> dict[str, list[str]]:
    """Map declaration -> axiom list from '#print axioms' output."""
    res: dict[str, list[str]] = {}
    for m in re.finditer(r"'([^']+)' depends on axioms: \[([^\]]*)\]", out):
        res[m.group(1)] = [a.strip() for a in m.group(2).split(",") if a.strip()]
    for m in re.finditer(r"'([^']+)' does not depend on any axioms", out):
        res[m.group(1)] = []
    return res


def axiom_verdict(out: str, name: str) -> str:
    ax = parse_axioms(out)
    if name not in ax:
        return "NO_FOOTPRINT"
    if "sorryAx" in ax[name]:
        return "SORRY"
    if set(ax[name]) - ALLOWED_AXIOMS:
        return "BAD_AXIOM"
    return "OK"


def save(lane: Path, name: str, obj: object) -> None:
    (lane / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def cmd_deps(lane: Path) -> None:
    order = closure_order(ROOT_MODULE)
    save(lane, "closure.json", {"root": ROOT_MODULE, "n_files": len(order), "order": order,
                                "lines": sum(len(mod_path(m).read_text().splitlines()) for m in order)})
    print(len(order), "files")


def cmd_challenge(lane: Path) -> None:
    res = run_lean([str(UP / "ComparatorChallenges" / "LiebThirring.lean")], lean_path(), 3000)
    save(lane, "part1a_challenge.json", res)
    print({k: v for k, v in res.items() if k != "output"})


def cmd_closure(lane: Path, max_seconds: int) -> None:
    """Resumable: files whose record says compiled are skipped; dependents of a failure are blocked."""
    order = json.loads((lane / "closure.json").read_text())["order"]
    scratch = lane / "scratch_olean"
    scratch.mkdir(exist_ok=True)
    recp = lane / "part1b_closure.json"
    rec: dict[str, dict[str, object]] = json.loads(recp.read_text()) if recp.exists() else {}
    lp = lean_path() + ":" + str(scratch)
    t_start = time.time()
    for m in order:
        if m in rec and rec[m]["status"] in ("compiled", "failed", "blocked"):
            continue
        deps = [d for d in IMPORT_RE.findall(mod_path(m).read_text()) if d.startswith("OAI")]
        bad = [d for d in deps if rec.get(d, {}).get("status") != "compiled"]
        if bad:
            rec[m] = {"status": "blocked", "blocked_by": bad}
            save(lane, "part1b_closure.json", rec)
            continue
        if time.time() - t_start > max_seconds:
            print("time slice used; resume later")
            break
        out_o = scratch / (m.replace(".", "/") + ".olean")
        out_i = out_o.with_suffix(".ilean")
        out_o.parent.mkdir(parents=True, exist_ok=True)
        res = run_lean([f"--root={UP}", "-o", str(out_o), "-i", str(out_i), str(mod_path(m))], lp, 3000)
        ok = (not res["has_error"]) and out_o.exists()
        rec[m] = {"status": "compiled" if ok else "failed", "seconds": res["seconds"],
                  "first_error": "" if ok else first_error(str(res["output"])),
                  "timed_out": res["timed_out"]}
        save(lane, "part1b_closure.json", rec)
        print(m, rec[m]["status"], res["seconds"], flush=True)
    done = sum(1 for v in rec.values() if v["status"] == "compiled")
    print(f"compiled {done}/{len(order)}")


def cmd_axioms(lane: Path) -> None:
    scratch = lane / "scratch_olean"
    f = lane / "scratch_axioms.lean"
    f.write_text(f"import {ROOT_MODULE}\n#print axioms {FINAL_THEOREM}\n", encoding="utf-8")
    res = run_lean([str(f)], lean_path() + ":" + str(scratch), 3000)
    res["verdict"] = axiom_verdict(str(res["output"]), FINAL_THEOREM)
    res["axioms"] = parse_axioms(str(res["output"])).get(FINAL_THEOREM)
    save(lane, "part1c_axioms.json", res)
    print(res["verdict"], res["axioms"])


def cmd_elenchus(lane: Path, which: list[str]) -> None:
    """Run elenchus_check.main() in-process with REPO_ROOT pointed at LeanMaster so that its `lean`
    subprocess sees LeanMaster's toolchain pin; LEAN_PATH comes from `lake env`. Elenchus's code is unmodified."""
    sys.path.insert(0, str(ELENCHUS_TOOLS))
    import elenchus_check as E  # type: ignore[import-not-found]

    E.REPO_ROOT = str(LM)
    os.environ["LEAN_PATH"] = lean_path()
    outp = lane / "part2_elenchus.json"
    allres: dict[str, object] = json.loads(outp.read_text()) if outp.exists() else {}
    for name in which:
        if name in allres:
            continue
        path = name if name.endswith(".lean") and os.path.isabs(name) else str(UP / "ComparatorChallenges" / f"{name}.lean")
        buf_o, buf_e = io.StringIO(), io.StringIO()
        old_argv = sys.argv
        E.SKIP_REASONS.clear()
        sys.argv = ["elenchus_check.py", path]
        t0 = time.time()
        with redirect_stdout(buf_o), redirect_stderr(buf_e):
            rc = E.main()
        sys.argv = old_argv
        allres[name] = {"exit_code": rc, "stdout": buf_o.getvalue(), "stderr": buf_e.getvalue(),
                        "seconds": round(time.time() - t0, 1), "path": path}
        save(lane, "part2_elenchus.json", allres)
        print(name, "rc", rc, flush=True)


def cmd_lock(lane: Path) -> None:
    """Hash the four challenge statements with LeanMaster's statement_lock.py. LEAN_PROJECT_ROOT is a lane
    scratch root holding byte-identical copies, so LeanMaster's docs/statement_lock.json is untouched."""
    root = lane / "lock_root"
    (root / "docs").mkdir(parents=True, exist_ok=True)
    files = []
    for c in CHALLENGES:
        dst = root / "ComparatorChallenges" / f"{c}.lean"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(UP / "ComparatorChallenges" / f"{c}.lean", dst)
        files.append(str(dst))
    env = dict(os.environ, LEAN_PROJECT_ROOT=str(root))
    r = subprocess.run([sys.executable, str(LM / "tools" / "statement_lock.py"), "--update", *files],
                       env=env, capture_output=True, text=True, timeout=300)
    c = subprocess.run([sys.executable, str(LM / "tools" / "statement_lock.py"), "--check", *files],
                       env=env, capture_output=True, text=True, timeout=300)
    lock = json.loads((root / "docs" / "statement_lock.json").read_text())
    shas = {x: hashlib.sha256((UP / "ComparatorChallenges" / f"{x}.lean").read_bytes()).hexdigest()
            for x in CHALLENGES}
    identical = {x: (root / "ComparatorChallenges" / f"{x}.lean").read_bytes()
                 == (UP / "ComparatorChallenges" / f"{x}.lean").read_bytes() for x in CHALLENGES}
    save(lane, "part2_statement_lock.json", {
        "update_rc": r.returncode, "update_out": r.stdout, "check_rc": c.returncode, "check_out": c.stdout,
        "lock": lock, "file_sha256": shas, "copies_byte_identical": identical})
    print(r.stdout.strip(), "|", c.stdout.strip().splitlines()[-1] if c.stdout.strip() else "")


CTRL_FILES = {
    "pos_clean.lean": "theorem t_ok : 1 + 1 = 2 := rfl\n#print axioms t_ok\n",
    "neg_sorry.lean": "theorem t_bad : False := sorry\n#print axioms t_bad\n",
    "neg_axiom.lean": "axiom smuggled : False\ntheorem t_sm : False := smuggled\n#print axioms t_sm\n",
    "neg_syntax.lean": "theorem t_syn : 1 + 1 = 2 :=\n  by exact (rfl\n",
    "pos_classical.lean": "theorem t_cl (p : Prop) : p ∨ ¬ p := Classical.em p\n#print axioms t_cl\n",
}


def cmd_controls(lane: Path) -> dict[str, object]:
    d = lane / "controls"
    d.mkdir(exist_ok=True)
    lp = lean_path()
    out: dict[str, object] = {}
    exp = {"pos_clean.lean": ("t_ok", "OK", False), "neg_sorry.lean": ("t_bad", "SORRY", False),
           "neg_axiom.lean": ("t_sm", "BAD_AXIOM", False), "pos_classical.lean": ("t_cl", "OK", False),
           "neg_syntax.lean": ("t_syn", "NO_FOOTPRINT", True)}
    for fn, text in CTRL_FILES.items():
        (d / fn).write_text(text)
        res = run_lean([str(d / fn)], lp, 600)
        name, want, want_err = exp[fn]
        v = axiom_verdict(str(res["output"]), name)
        out[fn] = {"verdict": v, "expected": want, "has_error": res["has_error"],
                   "expected_error": want_err,
                   "pass": v == want and (res["has_error"] == want_err or fn in ("neg_sorry.lean",))}
    # the driver's compile classifier must call the syntax-error file an error and the clean file not one
    out["_all_pass"] = all(v["pass"] for k, v in out.items() if not k.startswith("_"))
    save(lane, "controls.json", out)
    print({k: (v["pass"] if isinstance(v, dict) else v) for k, v in out.items()})
    return out


def cmd_smoke(lane: Path) -> None:
    order = closure_order(ROOT_MODULE)
    pos = {m: i for i, m in enumerate(order)}
    for m in order:
        for dep in IMPORT_RE.findall(mod_path(m).read_text()):
            if dep.startswith("OAI"):
                assert pos[dep] < pos[m], (dep, m)
    assert order[-1] == ROOT_MODULE and len(order) > 10
    print("toposort ok", len(order))
    assert parse_axioms("'x' depends on axioms: [propext, sorryAx]") == {"x": ["propext", "sorryAx"]}
    assert axiom_verdict("'x' does not depend on any axioms", "x") == "OK"
    assert axiom_verdict("'x' depends on axioms: [foo]", "x") == "BAD_AXIOM"
    assert axiom_verdict("", "x") == "NO_FOOTPRINT"
    print("classifier ok")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["deps", "challenge", "closure", "axioms", "elenchus", "lock",
                                    "controls", "smoke"])
    ap.add_argument("--lane", required=True)
    ap.add_argument("--max-seconds", type=int, default=420)
    ap.add_argument("--only", nargs="*", default=CHALLENGES)
    a = ap.parse_args()
    lane = Path(a.lane)
    lane.mkdir(parents=True, exist_ok=True)
    if a.cmd == "deps":
        cmd_deps(lane)
    elif a.cmd == "challenge":
        cmd_challenge(lane)
    elif a.cmd == "closure":
        cmd_closure(lane, a.max_seconds)
    elif a.cmd == "axioms":
        cmd_axioms(lane)
    elif a.cmd == "elenchus":
        cmd_elenchus(lane, a.only)
    elif a.cmd == "lock":
        cmd_lock(lane)
    elif a.cmd == "controls":
        cmd_controls(lane)
    else:
        cmd_smoke(lane)
    return 0


if __name__ == "__main__":
    sys.exit(main())
