"""Auditor Lean recompile of CarbonK3 into a private olean dir (does not touch producer oleans)."""
import json, os, subprocess, sys, time
from pathlib import Path
REPO = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(REPO / "scripts/certified_numerics"))
import lean_pinned as L
MY = Path("/tmp/k3audit/olean")
(MY / "Programmes/CarbonK3").mkdir(parents=True, exist_ok=True)
LP = str(MY) + ":" + L.lean_path()
env = dict(os.environ, LEAN_PATH=LP, PATH=f"{L.TOOLCHAIN_BIN}:{os.environ.get('PATH', '')}")
lean = str(L.TOOLCHAIN_BIN / "lean")
res = {}
def run(name, cmd):
    t0 = time.time()
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=5000)
    res[name] = {"rc": r.returncode, "s": round(time.time() - t0, 1), "out": (r.stdout + r.stderr)}
    print(name, "rc", r.returncode, "s", res[name]["s"]); print((r.stdout + r.stderr)[-4000:])
core = REPO / "formal_cert/Programmes/CarbonK3/Core.lean"
ctl = REPO / "formal_cert/Programmes/CarbonK3/Controls.lean"
ol = MY / "Programmes/CarbonK3/Core.olean"
run("core", [lean, "-DautoImplicit=false", f"--root={REPO / 'formal_cert'}", "-o", str(ol), "-i", str(ol.with_suffix('.ilean')), str(core)])
run("controls", [lean, "-DautoImplicit=false", f"--root={REPO / 'formal_cert'}", str(ctl)])
run("leanchecker", [str(L.TOOLCHAIN_BIN / "leanchecker"), "Programmes.CarbonK3.Core"])
json.dump(res, open("/tmp/k3audit/lean_audit.json", "w"), indent=1)
