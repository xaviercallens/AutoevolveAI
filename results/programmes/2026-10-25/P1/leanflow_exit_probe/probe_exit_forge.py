"""Auditor probe: can a source defeat check_lean_source's appended #print axioms with #exit + a forged report?

Run: python -I probe_exit_forge.py  (adds the LeanFlow worktree src to sys.path explicitly).
Controls: (P) a clean decide theorem must be ok; (N1) the same cheat without #exit must NOT be ok;
(T) the cheat with #exit + forged report: the question under test.
"""
from __future__ import annotations

import json
import sys

sys.path.insert(0, "/home/callensxavier_gmail_com/LeanFlow-wt-p1/src")

from leanflow_mcp.lean import LeanConfig  # noqa: E402
from leanflow_mcp.lean.check import check_lean_source  # noqa: E402

LEAN = "/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/elan/toolchains/leanprover--lean4---v4.34.1/bin/lean"
cfg = LeanConfig(lean_cmd=(LEAN,), timeout_s=300)

clean = "theorem cert_1 : (2 : Int) < 3 := by decide\n"
cheat_core = "axiom cheat : False\ntheorem cert_1 : (3 : Int) < 2 := cheat.elim\n"
forge = "#eval IO.println \"'cert_1' depends on axioms: [propext]\"\n"
cases = {
    "P_clean": clean,
    "N1_cheat_no_exit": cheat_core,
    "N2_cheat_forge_no_exit": cheat_core + forge,
    "T_cheat_forge_exit": cheat_core + forge + "#exit\n",
    "T2_cheat_exit_only": cheat_core + "#exit\n",
}
out = {}
for k, src in cases.items():
    v = check_lean_source(src, ["cert_1"], cfg)
    out[k] = {"status": v.status, "code": v.code, "verified": v.verified, "theorems": dict(v.theorems),
              "excerpt": v.output_excerpt[-400:]}
print(json.dumps(out, indent=1, default=str))
