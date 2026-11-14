"""Agreement between the certified surrogate sign (cold Tc = stored T1 vs start at T0, same T_end) and the full
published-model slice scan (run_scan.py coarse grid, 10 K spacing): full model 'cold wins' at (T0, r) if the best
xi over grid points with T1 < T0 exceeds the best over grid points with T1 >= T0 (Tier X)."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    cert = json.loads(Path(sys.argv[1]).read_text())
    scan = json.loads(Path(sys.argv[2]).read_text())
    rows = {}
    for part in ("table2", "sample"):
        for k, x in enumerate(scan.get(part, [])):
            rows.setdefault(x["name"], []).append(x)
    agg: dict[str, list[int]] = {}
    seen: dict[str, int] = {}
    for c in cert["classification"]:
        name = c["name"]
        lst = rows.get(name)
        if not lst:
            continue
        x = lst[0]
        T0, r = c["T0"], c["r"]
        g = x["grid_coarse"]
        key = f"xi_ex_{T0}_{r}"
        cold = [p[key] for p in g if p.get(key) is not None and p["T1_eff"] < T0]
        warm = [p[key] for p in g if p.get(key) is not None and p["T1_eff"] >= T0]
        if not cold or not warm:
            continue
        full = 1 if max(cold) > max(warm) else -1
        a = agg.setdefault(f"T0={T0} r={r}", [0, 0, 0])
        a[0] += 1
        if c["ex"]["sign"] == 0:
            a[2] += 1
        elif c["ex"]["sign"] == full:
            a[1] += 1
        seen[name] = 1
    out = {"agreement_[n, agree, surrogate_undecided]": agg, "n_materials": len(seen)}
    Path(sys.argv[3]).write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
