import json, os, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/scripts/certified_numerics")
import lean_pinned as L
L.OUT = Path("/tmp/e3audit/olean")
D = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/formal_cert/Programmes/LowDissE3")
steps = [("Core","Programmes.LowDissE3.Core"),("Instances","Programmes.LowDissE3.Instances"),("Engine","Programmes.LowDissE3.Engine"),("Axioms",None),("Controls",None)]
for name, mod in steps:
    r = L.compile_file(D/(name+".lean"), mod, 3000)
    print(name, r["rc"], r["seconds"], flush=True)
    Path(f"/tmp/e3audit/logs/{name}.txt").write_text(r["output"])
env = dict(os.environ, LEAN_PATH=L.lean_path(), PATH=f"{L.TOOLCHAIN_BIN}:{os.environ.get('PATH','')}")
print("LEAN_PATH tail", env["LEAN_PATH"][-200:], flush=True)
for mod in ["Programmes.LowDissE3.Core","Programmes.LowDissE3.Instances","Programmes.LowDissE3.Engine","Programmes.LowDissE3.DoesNotExist"]:
    t0=time.time()
    r = subprocess.run([str(L.TOOLCHAIN_BIN/"leanchecker"), mod], env=env, capture_output=True, text=True, timeout=3000)
    print("leanchecker", mod, r.returncode, round(time.time()-t0,1), r.stdout[-300:], r.stderr[-300:], flush=True)
