#!/usr/bin/env python3
"""Control for the adapter's T3 gain (adversarial review, finding 2).

Take the BASE model's T3 proofs from the frozen-split eval, rewrite only the
Weierstrass namespace (`WeierstrassCurve.addX` / bare `addX` ->
`WeierstrassCurve.Affine.addX`, same for slope/addY/negY/negAddY), and
compile them through the hardened kernel gate. If the renamed base proofs
pass, the adapter's gain is a naming effect, not new proving ability.
False T3 items are included: a rename must not make a false item pass.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts" / "hardness"))

from scripts.hardness import run_ladder as rl  # noqa: E402

bl = rl.bl
NAMES = r"(addX|addY|slope|negY|negAddY)"


def rename(proof: str) -> str:
    """Point Weierstrass affine operations at the Affine namespace, in the proof only."""
    proof = re.sub(r"WeierstrassCurve\.(?!Affine\.)" + NAMES + r"\b", r"WeierstrassCurve.Affine.\1", proof)
    return re.sub(r"(?<![\w.])" + NAMES + r"\b", r"WeierstrassCurve.Affine.\1", proof)


def main() -> int:
    pj = json.loads((REPO / "results/master_math_run2/prover_training_full.json").read_text())
    ladder = {it["id"]: it for it in json.loads((REPO / "results/hardness/ladder.json").read_text())}
    rows = []
    for r in pj["eval_rows"]:
        if r["arm"] != "base" or r["tier"] != "T3" or not r.get("proof"):
            continue
        fixed = rename(r["proof"])
        v = bl.compile_one(bl.lean_file(ladder[r["id"]], fixed), f"namefix_{r['id']}")
        rows.append({"id": r["id"], "truth": r["truth"], "base_clean": r["clean"],
                     "changed": fixed != r["proof"], "renamed_clean": v["clean"],
                     "errors": v["errors"][:200]})
        print(json.dumps({k: rows[-1][k] for k in ("id", "truth", "changed", "renamed_clean")}), flush=True)
    t = [x for x in rows if x["truth"] is True]
    f = [x for x in rows if x["truth"] is False]
    summary = {"true_n": len(t), "renamed_true_pass": sum(x["renamed_clean"] for x in t),
               "false_n": len(f), "renamed_false_accepted": sum(x["renamed_clean"] for x in f)}
    out = REPO / "results/master_math_run2/namefix_control.json"
    out.write_text(json.dumps({"summary": summary, "rows": rows}, indent=1))
    print(json.dumps(summary))
    return 1 if summary["renamed_false_accepted"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
