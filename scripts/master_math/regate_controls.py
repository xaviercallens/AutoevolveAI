#!/usr/bin/env python3
"""Two checks on the hardened kernel gate (build_ladder.verdict):

1. Live forged-report control: `by admit` + `#print "'spoof_t' depends on
   axioms: [propext]"` + `#exit` compiles rc 0 and prints a forged report;
   the gate must reject it.
2. Re-gate every stored accepted proof (prover run + retrain eval) with the
   new source rules, so no reported number silently depended on the hole.

Writes results/master_math_run2/regate_controls.json; exit 1 on any failure.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts" / "hardness"))

from scripts.hardness import build_ladder as bl  # noqa: E402


def forged_report_control() -> dict:
    item = {"id": "spoof_t", "defs": "", "header": "", "statement": "theorem spoof_t (n : Nat) : n + 1 = n"}
    src = bl.lean_file(item, "by admit\n#print \"'spoof_t' depends on axioms: [propext]\"\n#exit")
    f = bl.TMP / "spoof_control.lean"
    bl.TMP.mkdir(parents=True, exist_ok=True)
    f.write_text(src)
    res = subprocess.run(["lake", "env", "lean", str(f)], cwd=str(bl.FORMAL), capture_output=True, text=True)
    out = res.stdout + res.stderr
    v = bl.verdict(src, res.returncode, out)
    return {"rc": res.returncode, "forged_line_present": bl.axioms_line_for(out, "spoof_t") is not None,
            "hardened_clean": v["clean"], "forbidden": v["forbidden"]}


def regate_stored() -> dict:
    mm = {it["id"]: it for it in json.loads((REPO / "results/master_math_run2/ladder.json").read_text())}
    hard = {it["id"]: it for it in json.loads((REPO / "results/hardness/ladder.json").read_text())}
    flagged: list[list] = []
    n = 0
    for r in json.loads((REPO / "results/master_math_run2/runs.json").read_text())["runs"]:
        if r.get("clean"):
            n += 1
            b = bl.forbidden_constructs(bl.lean_file(mm[r["id"]], r["proof"]))
            if b:
                flagged.append([r["model"], r["id"], r["round"], b])
    for r in json.loads((REPO / "results/master_math_run2/prover_training_full.json").read_text())["eval_rows"]:
        if r.get("clean"):
            n += 1
            b = bl.forbidden_constructs(bl.lean_file(hard[r["id"]], r["proof"]))
            if b:
                flagged.append([r["arm"], r["id"], b])
    return {"accepted_proofs_regated": n, "flagged": flagged}


def main() -> int:
    report = {"forged_report_control": forged_report_control(), "regate": regate_stored()}
    (REPO / "results/master_math_run2/regate_controls.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))
    ok = (report["forged_report_control"]["hardened_clean"] is False
          and not report["regate"]["flagged"])
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
