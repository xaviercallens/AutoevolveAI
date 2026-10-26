"""Copy A2 evidence into the results directory (large files gzipped)."""
import gzip
import shutil
from pathlib import Path

SRC = Path("/home/callensxavier_gmail_com/proposal2/A2")
DST = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal2/2026-10-26/A2")
BIG = 2_000_000
groups = {
    "logs": [SRC / "logs"],
    "audit": [SRC / "audit"],
    "controls": [SRC / "controls"],
    "scripts": [SRC / "scripts", SRC / "lean_scripts"],
    "inputs": [SRC / "closure_ns.json", SRC / "closure_euler.json", SRC / "closure_all.json",
               SRC / "scan_closure.json", SRC / "scan_closure.txt", SRC / "scan_allfiles.json",
               SRC / "clay_navierstokes.txt"],
}
n = 0
for g, paths in groups.items():
    for p in paths:
        files = [p] if p.is_file() else [f for f in p.rglob("*") if f.is_file()]
        for f in files:
            if f.suffix in (".olean", ".ilean"):
                continue
            rel = f.relative_to(SRC)
            out = DST / rel if g == "logs" else DST / "evidence" / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            if f.stat().st_size > BIG:
                with f.open("rb") as i, gzip.open(str(out) + ".gz", "wb") as o:
                    shutil.copyfileobj(i, o)
            else:
                shutil.copy2(f, out)
            n += 1
print("exported", n, "files")
