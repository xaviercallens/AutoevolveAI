#!/usr/bin/env python3
"""Live control for the first gate hole: `sorry` + `#exit` compiles rc 0 and
prints no axiom report. The pre-2026-09-27 parse read a missing report as
"no axioms" (clean); `build_ladder.verdict` must reject it and still accept a
genuine proof. Writes results/master_math_run2/exit_gate_control.json.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.hardness import build_ladder as bl  # noqa: E402

CASES = {
    "exit_after_sorry": "theorem exit_ctl (n : Nat) : n + 1 = n := by\n  sorry\n#exit\n#print axioms exit_ctl\n",
    "genuine": "theorem ok_ctl (n : Nat) : n + 0 = n := by\n  simp\n#print axioms ok_ctl\n",
}


def old_parse_clean(rc: int, out: str) -> bool:
    """The gate as it was: any axioms line, and a missing one meant none."""
    axioms: list[str] = []
    if "depends on axioms:" in out:
        part = out.split("depends on axioms:")[1].split("\n")[0]
        axioms = [a.strip() for a in part.strip(" []").split(",") if a.strip()]
    return rc == 0 and "sorryAx" not in out and set(axioms) <= bl.TRUSTED


def main() -> int:
    report = {}
    bl.TMP.mkdir(parents=True, exist_ok=True)
    for tag, src in CASES.items():
        f = bl.TMP / f"{tag}.lean"
        f.write_text(src)
        res = subprocess.run(["lake", "env", "lean", str(f)], cwd=str(bl.FORMAL), capture_output=True, text=True)
        out = res.stdout + res.stderr
        report[tag] = {"rc": res.returncode, "old_gate_clean": old_parse_clean(res.returncode, out),
                       "new_gate_clean": bl.verdict(src, res.returncode, out)["clean"]}
    (REPO / "results/master_math_run2/exit_gate_control.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))
    ok = report["exit_after_sorry"]["new_gate_clean"] is False and report["genuine"]["new_gate_clean"] is True
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
