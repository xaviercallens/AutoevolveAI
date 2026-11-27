"""Compare our constants (Dickson Guide formulas) against PyCO2SYS's own constants at a few (T, S) points."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import PyCO2SYS as pyco2
from mpmath import iv

sys.path.insert(0, str(Path(__file__).parent))
import k2lib as K  # noqa: E402

rows = []
for t, s in ((0.0, 30.0), (10.0, 33.0), (15.0, 35.0), (25.0, 35.0), (30.0, 38.0)):
    r = pyco2.sys(par1=2300.0, par1_type=1, par2=420.0, par2_type=5, salinity=s, temperature=t, opt_k_carbonic=10,
                  opt_pH_scale=1, total_sulfate=0, total_fluoride=0, opt_total_borate=1)
    c = K.constants(iv.mpf(t), iv.mpf(s))
    mine = {k: float(v.mid) for k, v in c.items()}
    theirs = {"K0": float(r["k_CO2"]), "K1": float(r["k_carbonic_1"]), "K2": float(r["k_carbonic_2"]),
              "KB": float(r["k_borate"]), "KW": float(r["k_water"]), "BT": float(r["total_borate"]) * 1e-6}
    rows.append({"T": t, "S": s, "relative_difference": {k: mine[k] / theirs[k] - 1 for k in mine}})
Path(sys.argv[1]).write_text(json.dumps(rows, indent=1))
print(json.dumps(rows[2], indent=1))
