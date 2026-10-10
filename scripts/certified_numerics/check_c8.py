#!/usr/bin/env python3
"""C8 (P3): the kernel-evaluated r_d bracket at one point vs the float Aubourg formula of scripts/bao_bbn_h0/common.py."""

from __future__ import annotations

import json
import re
import sys
from fractions import Fraction

sys.set_int_max_str_digits(0)
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
R = REPO / "results" / "certified_numerics" / "P3_h0"
sys.path.insert(0, "/home/callensxavier_gmail_com/AutoevolveAI/scripts/bao_bbn_h0")
from common import rd_aubourg16  # noqa: E402

out = "".join(json.loads((R / "compile_Axioms.json").read_text())["output"].split())
m = re.search(r"\(\"(\d+)/(\d+)\",\"(\d+)/(\d+)\"\)", out)
lo, hi = Fraction(int(m.group(1)), int(m.group(2))), Fraction(int(m.group(3)), int(m.group(4)))
wcb = 0.3 * 0.73**2 - 0.0107 * 0.06
ref = float(rd_aubourg16(wcb, 0.02218))
res = {"point": {"omega_cb": wcb, "omega_b": 0.02218}, "certified_lo": float(lo), "certified_hi": float(hi),
       "rel_width": float((hi - lo) / lo), "common_rd_aubourg16": ref,
       "inside": float(lo) <= ref <= float(hi), "rel_diff_to_mid": abs(ref - float((lo + hi) / 2)) / ref}
res["pass"] = bool(res["inside"] and res["rel_diff_to_mid"] < 1e-10)
(R / "c8.json").write_text(json.dumps(res, indent=1) + "\n")
print(json.dumps(res, indent=1))
