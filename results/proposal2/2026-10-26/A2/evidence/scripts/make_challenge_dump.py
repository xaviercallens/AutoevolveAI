"""Make a Lean file = verbatim challenge source + DumpCore + statement dump of the challenge theorems.

usage: make_challenge_dump.py <challenge.lean> <out.lean> <roots comma-separated> <stmt_out_abs>
"""
import sys
from pathlib import Path

src_p, out_p, roots, stmt_out = sys.argv[1:5]
src = Path(src_p).read_text(encoding="utf-8")
core = Path("/home/callensxavier_gmail_com/proposal2/A2/lean_scripts/DumpCore.lean.txt").read_text(encoding="utf-8")
assert "import Mathlib\n" in src
src = src.replace("import Mathlib\n", "import Mathlib\nimport Lean\n", 1)
root_arr = "#[" + ", ".join(f"`{r}" for r in roots.split(",")) + "]"
tail = f'\nrun_cmd A2Audit.dumpStatement {root_arr} "{stmt_out}"\n'
Path(out_p).write_text(src + "\n" + core + tail, encoding="utf-8")
print("wrote", out_p)
