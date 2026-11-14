"""Assemble a Lean audit file: imports + DumpCore + commands.

usage: make_dump_file.py <out.lean> <imports comma-separated> <roots comma-separated> <stmt_out> <sound_out|-> [extra_lean_file]
"""
import sys
from pathlib import Path

out, imports, roots, stmt_out, sound_out = sys.argv[1:6]
extra = Path(sys.argv[6]).read_text(encoding="utf-8") if len(sys.argv) > 6 else ""
core = Path("/home/callensxavier_gmail_com/proposal2/A2/lean_scripts/DumpCore.lean.txt").read_text(encoding="utf-8")
lines = ["import Lean"] + [f"import {m}" for m in imports.split(",") if m]
lines.append(core)
lines.append(extra)
root_arr = "#[" + ", ".join(f"`{r}" for r in roots.split(",") if r) + "]"
lines.append(f'run_cmd A2Audit.dumpStatement {root_arr} "{stmt_out}"')
if sound_out != "-":
    lines.append(f'run_cmd A2Audit.soundnessScan {root_arr} "{sound_out}"')
for r in roots.split(","):
    if r:
        lines.append(f"#print axioms {r}")
Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", out)
