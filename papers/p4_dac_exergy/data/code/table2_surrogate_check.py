"""Paper-side recount (reads K1 logs, writes data/table2_surrogate_check.json): surrogate-versus-full-model sign
agreement restricted to the 14 Table 2 rows, using exactly the rule of K1 code/surrogate_agreement.py (full model
'cold wins' iff best xi over coarse-grid points with T1_eff < T0 exceeds best over points with T1_eff >= T0).
Usage: python -I table2_surrogate_check.py <cert_sign.json> <scan_T1.json> <out.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    cert = json.loads(Path(sys.argv[1]).read_text())
    scan = json.loads(Path(sys.argv[2]).read_text())
    rows: dict[str, list[dict]] = {}
    for k, x in enumerate(scan.get("table2", [])):
        rows.setdefault(x["name"], []).append((k, x))
    out: dict[str, dict] = {}
    for c in cert["classification"]:
        if c["row"] != "table2":
            continue
        name = c["name"]
        T0, r = c["T0"], c["r"]
        key = f"T0={T0} r={r}"
        # table2 rows may share a material name (several paths); cert and scan are both ordered the same way
        out.setdefault(key, {"n": 0, "agree": 0, "undecided": 0, "disagree_names": []})
        lst = rows.get(name)
        if not lst:
            continue
        # cert_sign has one entry per (path, T0, r) in order; pick the matching path by occurrence count
        occ = out[key].setdefault("_occ", {})
        idx = occ.get(name, 0)
        occ[name] = idx + 1
        if idx >= len(lst):
            continue
        x = lst[idx][1]
        g = x["grid_coarse"]
        kk = f"xi_ex_{T0}_{r}"
        cold = [p[kk] for p in g if p.get(kk) is not None and p["T1_eff"] < T0]
        warm = [p[kk] for p in g if p.get(kk) is not None and p["T1_eff"] >= T0]
        if not cold or not warm:
            continue
        full = 1 if max(cold) > max(warm) else -1
        out[key]["n"] += 1
        if c["ex"]["sign"] == 0:
            out[key]["undecided"] += 1
        elif c["ex"]["sign"] == full:
            out[key]["agree"] += 1
        else:
            out[key]["disagree_names"].append(name)
    for v in out.values():
        v.pop("_occ", None)
    Path(sys.argv[3]).write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
