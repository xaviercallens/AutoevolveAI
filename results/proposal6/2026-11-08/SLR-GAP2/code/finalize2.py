"""Append the PHASE2 section to RESULT.md from logs/runs2.jsonl, refresh result.json and files.sha256.
Run from the worktree root:  python3 results/proposal6/2026-11-08/SLR-GAP2/code/finalize2.py [--partial]
"""
import collections
import hashlib
import json
import os
import sys

R = "results/proposal6/2026-11-08/SLR-GAP2"
rows = [json.loads(x) for x in open(f"{R}/logs/runs2.jsonl")]
start = [json.loads(x) for x in open(f"{R}/logs/runs2_start.log")]
done = {d["tag"] for d in rows}
killed = sum(s.get("killed_s", 0) * s["workers"] for s in start if s["tag"] not in done)
cpu = sum(d["wall_s"] * d["workers"] for d in rows) + killed
ctl = [d for d in rows if d["family"] == "ctl2_pos"]
main = [d for d in rows if d["family"] != "ctl2_pos"]
found = [d for d in main if d["status"] in ("OPTIMAL", "FEASIBLE")]
c = collections.Counter((d["family"], d["status"]) for d in main)
inprog = [s["tag"] for s in start if s["tag"] not in done]
outcome = "FOUND" if found else ("NEGATIVE_INCONCLUSIVE" if any(d["status"] == "UNKNOWN" for d in main) else "NEGATIVE")
partial = "--partial" in sys.argv
lines = ["", "## PHASE2 (2026-11-10): " + outcome + (" (PARTIAL: stopped before the 14 core-h budget)" if partial else ""),
         f"Amendment in PREREG_ITEM.md (hash refreshed; phase-1 hash in PREREG_ITEM.md.sha256.phase1). Driver code/run_phase2.py, log logs/runs2.jsonl (+ runs2_start.log). 6 workers, 600 s per (N, family), cores 1-6.",
         "Pruning (exact rational uncovered measure of the fixed runners <= slots*2/N) kept every N in 40..95 for all three families (ratios 0.29-0.4): it is a ranking, not a filter, here. Phase 1 INFEASIBLE pairs were not in these families.",
         ""]
for d in ctl:
    lines.append(f"Positive control (6 workers, 600 s cap): N=64 {d['status']} in {d.get('solve_s')} s solve, checkers {d.get('certify')} (certificates/ctl2 not written; cert in certificates/p2).")
lines += ["", "| tag | family | N | n | status | solve s | wall s | pool | slots | points |", "|---|---|---|---|---|---|---|---|---|---|"]
for d in main:
    lines.append(f"| {d['tag']} | {d['family']} | {d['N']} | {d['n']} | {d['status']} | {d.get('solve_s','')} | {d['wall_s']} | {d.get('pool','')} | {d.get('slots','')} | {d.get('points','')} |")
lines += ["", "Status counts: " + ", ".join(f"{k[0]}:{k[1]}={v}" for k, v in sorted(c.items())),
          f"FEASIBLE n: {[d['n'] for d in found]}",
          f"Runs killed before finishing (counted up to their kill time): {inprog}",
          f"CPU ledger phase 2: {cpu/3600:.2f} core-h (wall x 6, rows {sum(d['wall_s']*d['workers'] for d in rows)/3600:.2f} + killed {killed/3600:.2f}); phase 1 was about 3.5. INFEASIBLE/UNKNOWN verdicts concern the given pool and shift menu only, not the conjecture.", ""]
open(f"{R}/RESULT.md", "a").write("\n".join(lines))
js = json.load(open(f"{R}/result.json"))
js.update({"outcome": outcome, "found_n": [d["n"] for d in found], "phase2_core_hours": round(cpu / 3600, 2),
           "phase2_runs": len(main), "phase2_partial": partial})
files = ["RESULT.md", "PREREG_ITEM.md", "PREREG_ITEM.md.sha256.phase1", "logs/runs.jsonl", "logs/runs2.jsonl",
         "logs/runs2_start.log", "logs/summary.txt", "code/cpsat_gen.py", "code/run_phase2.py", "code/finalize2.py"]
sh = {f: hashlib.sha256(open(f"{R}/{f}", "rb").read()).hexdigest() for f in files if os.path.exists(f"{R}/{f}")}
for f in sorted(os.listdir(f"{R}/certificates/p2")) if os.path.isdir(f"{R}/certificates/p2") else []:
    sh["certificates/p2/" + f] = hashlib.sha256(open(f"{R}/certificates/p2/{f}", "rb").read()).hexdigest()
js["sha256"] = sh
json.dump(js, open(f"{R}/result.json", "w"), indent=1)
open(f"{R}/files.sha256", "w").write("".join(f"{h}  {f}\n" for f, h in sh.items()))
print(outcome, round(cpu / 3600, 2))
