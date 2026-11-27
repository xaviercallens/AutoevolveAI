"""N1: independent rendering of the certificate's sign claims by LeanFlow lean.certify (worktree
/home/callensxavier_gmail_com/LeanFlow-wt-p1, unmodified, tactic decide_kernel). For every certified record the
corner bound [qlo + cmin, qhi + cmax] is formed exactly (Python Fractions, the same formula as Lean's Rec.cmin /
Rec.cmax) and LeanFlow checks its sign; a copy with one planted false sign must be rejected.

usage: python -I n1_leanflow.py OUTDIR RUN1.json [RUN2.json ...]
"""

from __future__ import annotations

import json
import os
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, "/home/callensxavier_gmail_com/LeanFlow-wt-p1/src")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from leanflow_mcp.lean import LeanConfig, certify  # noqa: E402
from n1_make_cert import bounds  # noqa: E402

LEAN = "/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/elan/toolchains/leanprover--lean4---v4.34.1/bin/lean"


def main() -> int:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    runs: dict[tuple[Fraction, Fraction], dict] = {}
    for p in sys.argv[2:]:
        for r in json.load(open(p)):
            if r.get("engine") == "n1_certify2" and r["ok"]:
                runs[(Fraction(r["a_lo"]), Fraction(r["a_hi"]))] = r
    encl, asr = {}, []
    for i, k in enumerate(sorted(runs)):
        lo, hi = bounds(runs[k])
        if lo > 0:
            asr.append({"label": f"F > 0 on a in [{k[0]}, {k[1]}]", "endpoint": f"F{i}.lo", "op": ">", "rhs": "0"})
        elif hi < 0:
            asr.append({"label": f"F < 0 on a in [{k[0]}, {k[1]}]", "endpoint": f"F{i}.hi", "op": "<", "rhs": "0"})
        else:
            continue
        encl[f"F{i}"] = [str(lo), str(hi)]
    cfg = LeanConfig(lean_cmd=(LEAN,), timeout_s=900)
    planted = [dict(a) for a in asr]
    planted[0] = dict(planted[0], label="PLANTED " + planted[0]["label"], op="<" if planted[0]["op"] == ">" else ">")
    rc = 0
    for tag, assertions in (("exact", asr), ("planted", planted)):
        claim = {"name": f"n1_{tag}", "tactic": "decide_kernel", "enclosures": encl, "assertions": assertions}
        (out / f"leanflow_claim_{tag}.json").write_text(json.dumps(claim, indent=1) + "\n")
        res = certify(claim, cfg)
        (out / f"leanflow_result_{tag}.json").write_text(res.to_json() + "\n")
        print(tag, res.status, res.code, res.tier, "n_assertions", len(assertions), "failed:", list(res.failed),
              "seconds:", res.seconds)
        if tag == "exact" and not res.verified:
            rc = 1
        if tag == "planted" and not (res.status == "rejected" and list(res.failed) == ["cert_0"]):
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
