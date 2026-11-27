"""Compile one Lean file under the pinned Lean 4.34.1 + Mathlib d13f23b7 stack (same stack as A1's lean_pinned.py),
writing its olean into a caller-chosen directory (never A1's formal_cert/.olean_out, which is only read).

LEAN_PATH = pinned Mathlib packages + A1 oleans (read-only) + the given extra olean dirs (L1 core + dependencies) +
the output dir. The `lake env` LEAN_PATH is cached in a file. The compile runs under `taskset -c CORE` and
`/usr/bin/time -v` so that wall time and peak RSS are measured by the OS.

Usage: l1lean.py FILE MODULE OUTDIR [--core N] [--dep OLEANFILE ...] [--timeout S] [--json OUT]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

PINNED = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/openai_math_pinned/lean")
TOOLCHAIN_BIN = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/elan/toolchains/leanprover--lean4---v4.34.1/bin")
REPO = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
A1_OLEANS = REPO / "formal_cert" / ".olean_out"
CACHE = Path("/home/callensxavier_gmail_com/a1l1_oleans/lean_path_cache.txt")


def base_lean_path() -> str:
    if CACHE.exists() and CACHE.read_text().strip():
        return CACHE.read_text().strip()
    env = dict(os.environ, PATH=f"{TOOLCHAIN_BIN}:{os.environ.get('PATH', '')}")
    res = subprocess.run(["lake", "env", "printenv", "LEAN_PATH"], cwd=PINNED, env=env, capture_output=True, text=True, check=True)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(res.stdout.strip() + "\n")
    return res.stdout.strip()


def link(dst: Path, src: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_symlink() or dst.exists():
        if dst.is_symlink() and dst.resolve() == src.resolve():
            return
        dst.unlink()
    dst.symlink_to(src)


def compile_one(src: Path, module: str, outdir: Path, deps: list[Path], core: str | None, timeout: int) -> dict[str, object]:
    """Lean resolves a module through the FIRST search-path root that contains its top-level package directory
    (`Programmes`), so every chunk gets a self-contained root: OUTDIR/Programmes/SandierSerfaty is a symlink to A1's
    (read-only) oleans, and each dependency olean (`deps` = olean files in other chunk/core roots) is symlinked into
    OUTDIR at its module path. The chunk's own olean is a real file in OUTDIR."""
    outdir.mkdir(parents=True, exist_ok=True)
    link(outdir / "Programmes" / "SandierSerfaty", A1_OLEANS / "Programmes" / "SandierSerfaty")
    for d in deps:
        rel = d.as_posix().split("/Programmes/", 1)[1]
        for ext in (".olean", ".ilean"):
            link(outdir / "Programmes" / Path(rel).with_suffix(ext), d.with_suffix(ext))
    lp = ":".join([base_lean_path(), str(outdir)])
    env = dict(os.environ, LEAN_PATH=lp, PATH=f"{TOOLCHAIN_BIN}:{os.environ.get('PATH', '')}")
    olean = outdir / (module.replace(".", "/") + ".olean")
    olean.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["/usr/bin/time", "-v", str(TOOLCHAIN_BIN / "lean"), "-DautoImplicit=false", f"--root={REPO / 'formal_cert'}",
           "-o", str(olean), "-i", str(olean.with_suffix(".ilean")), str(src)]
    if core is not None:
        cmd = ["taskset", "-c", core] + cmd
    t0 = time.time()
    try:
        res = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=timeout)
        rc, out = res.returncode, res.stdout + res.stderr
    except subprocess.TimeoutExpired as e:
        rc = -9
        out = "TIMEOUT\n" + ((e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""))
    wall = round(time.time() - t0, 1)
    m = re.search(r"Maximum resident set size \(kbytes\): (\d+)", out)
    rss_kb = int(m.group(1)) if m else None
    m2 = re.search(r"Exit status: (\d+)", out)
    mu = re.search(r"User time \(seconds\): ([0-9.]+)", out)
    ms = re.search(r"System time \(seconds\): ([0-9.]+)", out)
    lean_out = out.split("\tCommand being timed:")[0]
    return {"file": str(src), "module": module, "rc": rc, "wall_s": wall, "peak_rss_kb": rss_kb,
            "user_s": float(mu.group(1)) if mu else None, "sys_s": float(ms.group(1)) if ms else None,
            "lean_exit": int(m2.group(1)) if m2 else None,
            "output": lean_out if len(lean_out) <= 40000 else lean_out[:20000] + "\n...[truncated]...\n" + lean_out[-20000:]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file", type=Path)
    ap.add_argument("module")
    ap.add_argument("outdir", type=Path)
    ap.add_argument("--core")
    ap.add_argument("--dep", action="append", default=[], type=Path)
    ap.add_argument("--timeout", type=int, default=86400)
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()
    r = compile_one(a.file.resolve(), a.module, a.outdir, a.dep, a.core, a.timeout)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=1) + "\n")
    print(json.dumps({k: r[k] for k in ("module", "rc", "wall_s", "user_s", "peak_rss_kb")}))
    print(str(r["output"])[-4000:])
    return 0 if r["rc"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
