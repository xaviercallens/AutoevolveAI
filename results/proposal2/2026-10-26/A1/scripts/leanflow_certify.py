"""Run the LeanFlow fail-closed data-certificate generator (worktree /home/callensxavier_gmail_com/LeanFlow-wt-p1,
commit 06084ef, tactic `decide_kernel`) on the certificate's assertions over the EXACT C++ endpoints, plus a copy with
one planted false assertion. Writes A1/leanflow/{claim,result}_{exact,planted}.json.
Usage: leanflow_certify.py DUMP_SCALARS COUNTED_RUN_ERR OUTDIR
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/callensxavier_gmail_com/LeanFlow-wt-p1/src")
from leanflow_mcp.lean import LeanConfig, certify  # noqa: E402

Q = 2**144
LEAN = "/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/elan/toolchains/leanprover--lean4---v4.34.1/bin/lean"


def main(scal: Path, runerr: Path, out: Path) -> int:
    v: dict[str, tuple[int, int]] = {}
    for line in scal.read_text().splitlines():
        p = line.split()
        if len(p) == 3:
            try:
                v[p[0]] = (int(p[1]), int(p[2]))
            except ValueError:
                pass
    for line in runerr.read_text().splitlines():
        if line.startswith("EXACT "):
            _, k, a, b = line.split()
            v[k] = (int(a), int(b))
    names = {"lam": "lambda", "K": "K", "fl": "fl", "slope": "slope", "gmf": "gmin_minus_factor", "neglhs": "neg_lhs",
             "gdd": "g_dd", "gxx": "g_xx", "det": "det", "co1": "co1"}
    encl = {n: [f"{v[k][0]}/{Q}", f"{v[k][1]}/{Q}"] for n, k in names.items()}
    asr = [
        {"label": "lambda > -6.731 (comp:tail-signs)", "endpoint": "lam.lo", "op": ">", "rhs": "-6731/1000"},
        {"label": "lambda < -6.729", "endpoint": "lam.hi", "op": "<", "rhs": "-6729/1000"},
        {"label": "K < 0", "endpoint": "K.hi", "op": "<", "rhs": "0"},
        {"label": "f(l) > 0", "endpoint": "fl.lo", "op": ">", "rhs": "0"},
        {"label": "slope -pi B(l) - lambda/2 > 0", "endpoint": "slope.lo", "op": ">", "rhs": "0"},
        {"label": "gmin - factor >= 1.20e-5 (comp:outer-assertion)", "endpoint": "gmf.lo", "op": ">=", "rhs": "12/1000000"},
        {"label": "drneg + er_drop + K <= -4.585e-4 (comp:negative-assertion)", "endpoint": "neglhs.hi", "op": "<=", "rhs": "-4585/10000000"},
        {"label": "g_dd > 0 (comp:hessian-assertions)", "endpoint": "gdd.lo", "op": ">", "rhs": "0"},
        {"label": "g_xx > 0", "endpoint": "gxx.lo", "op": ">", "rhs": "0"},
        {"label": "det Hess > 0", "endpoint": "det.lo", "op": ">", "rhs": "0"},
        {"label": "|c_1| < 1 (upper)", "endpoint": "co1.hi", "op": "<", "rhs": "1"},
        {"label": "|c_1| < 1 (lower)", "endpoint": "co1.lo", "op": ">", "rhs": "-1"},
    ]
    cfg = LeanConfig(lean_cmd=(LEAN,), timeout_s=600)
    out.mkdir(parents=True, exist_ok=True)
    rc = 0
    for tag, assertions in (("exact", asr), ("planted", asr[:5] + [dict(asr[5], label="PLANTED gmin - factor >= 1.21e-5", rhs="121/10000000")] + asr[6:])):
        claim = {"name": f"ss_cert_{tag}", "tactic": "decide_kernel", "enclosures": encl, "assertions": assertions}
        (out / f"claim_{tag}.json").write_text(json.dumps(claim, indent=1) + "\n")
        res = certify(claim, cfg)
        (out / f"result_{tag}.json").write_text(res.to_json() + "\n")
        print(tag, res.status, res.code, res.tier, "failed:", list(res.failed), "seconds:", res.seconds)
        if tag == "exact" and not res.verified:
            rc = 1
        if tag == "planted" and not (res.status == "rejected" and list(res.failed) == ["cert_5"]):
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])))
