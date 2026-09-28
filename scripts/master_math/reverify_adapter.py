#!/usr/bin/env python3
"""Re-verify every proof the prover adapter got accepted, outside the eval
pipeline that produced it (producer != verifier): rebuild each Lean file from
the saved proof text and the frozen ladder, compile it fresh, read the axiom
report, and scan for suspicious constructs.

Writes results/master_math_run2/prover_adapter_reverify.json.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts" / "hardness"))

from scripts.hardness import build_ladder as bl  # noqa: E402

SUSPICIOUS = ("#exit", "axiom ", "set_option", "sorry", "admit", "native_decide", "implemented_by", "@[extern")


def main() -> int:
    run = json.loads((REPO / "results/master_math_run2/prover_training_full.json").read_text())
    ladder = {it["id"]: it for it in json.loads((REPO / "results/hardness/ladder.json").read_text())}
    out: list[dict] = []
    for r in run["eval_rows"]:
        if not (r["arm"] == "adapter" and r["clean"]):
            continue
        it = ladder[r["id"]]
        src = bl.HEADER + "\n" + it["defs"] + "\n\n" + it["statement"] + " := " + r["proof"] \
            + f"\n\n#print axioms {it['id']}\n"
        f = bl.TMP / f"reverify_{it['id']}.lean"
        bl.TMP.mkdir(parents=True, exist_ok=True)
        f.write_text(src)
        res = subprocess.run(["lake", "env", "lean", str(f)], cwd=str(bl.FORMAL),
                             capture_output=True, text=True, timeout=900)
        o = res.stdout + res.stderr
        m = re.search(r"'" + re.escape(it["id"]) + r"' depends on axioms: \[([^\]]*)\]", o)
        out.append({"id": it["id"], "tier": it["tier"], "truth": it["truth"], "rc": res.returncode,
                    "axioms": m.group(1) if m else None, "sorryAx": "sorryAx" in o,
                    "suspicious": [w for w in SUSPICIOUS if w in r["proof"]]})
        print(json.dumps(out[-1]), flush=True)
    (REPO / "results/master_math_run2/prover_adapter_reverify.json").write_text(json.dumps(out, indent=1))
    bad = [x for x in out if x["rc"] != 0 or x["sorryAx"] or x["suspicious"] or x["axioms"] is None]
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
