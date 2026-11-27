"""Auditor recompile: Core -> olean in /tmp/k2audit/olean, Controls against that olean, leanchecker replay."""
import json, os, subprocess, sys, time, re
from pathlib import Path
REPO = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
sys.path.insert(0, str(REPO / "scripts/certified_numerics"))
import lean_pinned as L
OUT = Path("/tmp/k2audit/olean")
OUT.mkdir(parents=True, exist_ok=True)
lp = L.lean_path().replace(str(L.OUT), str(OUT))
env = dict(os.environ, LEAN_PATH=lp, PATH=f"{L.TOOLCHAIN_BIN}:{os.environ.get('PATH', '')}")
lean = str(L.TOOLCHAIN_BIN / "lean")
src = REPO / "formal_cert/Programmes/CarbonateK2"
res = {}
ol = OUT / "Programmes/CarbonateK2/Core.olean"
ol.parent.mkdir(parents=True, exist_ok=True)
t0 = time.time()
r = subprocess.run([lean, "-DautoImplicit=false", f"--root={REPO / 'formal_cert'}", "-o", str(ol), "-i", str(ol.with_suffix('.ilean')), str(src / "Core.lean")], env=env, capture_output=True, text=True, timeout=3000)
res["core"] = {"rc": r.returncode, "s": round(time.time()-t0, 1), "out": r.stdout + r.stderr}
t0 = time.time()
r = subprocess.run([lean, "-DautoImplicit=false", f"--root={REPO / 'formal_cert'}", str(src / "Controls.lean")], env=env, capture_output=True, text=True, timeout=3000)
res["controls"] = {"rc": r.returncode, "s": round(time.time()-t0, 1), "out": r.stdout + r.stderr}
t0 = time.time()
r = subprocess.run([str(L.TOOLCHAIN_BIN / "leanchecker"), "Programmes.CarbonateK2.Core"], env=env, capture_output=True, text=True, timeout=3000)
res["leanchecker"] = {"rc": r.returncode, "s": round(time.time()-t0, 1), "out": (r.stdout + r.stderr)[-1500:]}
print(json.dumps(res, indent=1))
