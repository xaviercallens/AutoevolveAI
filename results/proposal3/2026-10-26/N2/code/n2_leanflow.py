"""N2: LeanFlow lean.certify (decide_kernel, unmodified LeanFlow at /home/callensxavier_gmail_com/LeanFlow-wt-p1) on the
rational endpoints of an n2_certify.py run: M.hi < 0 and the three positivity margins > 0.

usage: python -I n2_leanflow.py RUN.json NAME OUT_CLAIM.json OUT_CERT.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/callensxavier_gmail_com/LeanFlow-wt-p1/src")
from leanflow_mcp.lean.certify import certify  # noqa: E402
from leanflow_mcp.lean.config import LeanConfig  # noqa: E402

LEAN = "/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/elan/toolchains/leanprover--lean4---v4.34.1/bin/lean"


def main() -> None:
    run = json.load(open(sys.argv[1]))
    name, out_claim, out_cert = sys.argv[2], sys.argv[3], sys.argv[4]
    cr = run["cert_rationals"]
    claim = {
        "name": name,
        "tactic": "decide",
        "enclosures": {
            "M": [cr["M_lo"], cr["M_hi"]],
            "lmin": [cr["lmin_lo"], cr["lmin_lo"]],
            "lminu": [cr["lminu_lo"], cr["lminu_lo"]],
            "qpd": [cr["qpd_lo"], cr["qpd_lo"]],
        },
        "assertions": [
            {"label": "window curvature bound M.hi < 0", "terms": [["1", "M.hi"]], "op": "<", "rhs": "0"},
            {"label": "stability of L_0: lambda_min(B_0) lower bound > 0", "terms": [["1", "lmin.lo"]], "op": ">", "rhs": "0"},
            {"label": "stability on the window: lambda_min(B_u) lower bound > 0", "terms": [["1", "lminu.lo"]], "op": ">", "rhs": "0"},
            {"label": "X_u positive definite on the window", "terms": [["1", "qpd.lo"]], "op": ">", "rhs": "0"},
        ],
    }
    Path(out_claim).write_text(json.dumps(claim, indent=1) + "\n")
    cfg = LeanConfig(lean_cmd=(LEAN,), timeout_s=300.0)
    res = certify(claim, cfg)
    Path(out_cert).write_text(res.to_json() + "\n")
    print(json.dumps({"name": name, "status": res.status, "code": res.code, "tier": res.tier, "verified": res.verified,
                      "failed": list(res.failed), "message": res.message}, indent=1))


if __name__ == "__main__":
    main()
