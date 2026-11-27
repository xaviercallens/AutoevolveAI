import json, time, collections
from pathlib import Path
R = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
FC = R/"formal_cert"; OUT = FC/".olean_out"
now = time.time()
rows = []
for sub in ["Triangular","Autoresearch","Programmes"]:
    for p in sorted((FC/sub).rglob("*.lean")):
        n = p.name
        if "Controls" in n or "Reject" in n: continue
        mod = ".".join(p.relative_to(FC).with_suffix("").parts)
        ol = OUT/(mod.replace(".","/")+".olean")
        age = (now-p.stat().st_mtime)/60
        r = {"module":mod,"src":str(p.relative_to(R)),"src_age_min":round(age,1)}
        r["recent"] = age < 30
        r["olean_exists"] = ol.exists()
        r["fresh"] = ol.exists() and ol.stat().st_mtime >= p.stat().st_mtime
        rows.append(r)
(R/"results/kernel_replay_2026-10-26/plan.json").write_text(json.dumps(rows,indent=1))
c = collections.Counter((r["recent"], r["olean_exists"], r["fresh"]) for r in rows)
print(c)
for r in rows:
    if not r["recent"] and not r["fresh"]: print("STALE/MISSING", r["module"], r["olean_exists"])
    if r["recent"] and "L1" not in r["module"]: print("RECENT", r["module"])
