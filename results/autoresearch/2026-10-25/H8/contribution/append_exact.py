"""Append the verbatim theorem headers and the audit result (from audit_formal.out) to FORMAL.md."""
import sys

d = sys.argv[1]
out = open(d + "/audit_formal.out").read()
head_part, audit_part = out.split("## audit", 1)
head_part = head_part.replace("## theorem headers (verbatim, 26)\n", "", 1).strip()
section = (
    "\n## Exact Lean statements (verbatim, extracted by `audit_formal.py` from the compiled file)\n"
    "```lean\n" + head_part + "\n```\n\n"
    "## Mechanical audit (`python -I audit_formal.py contribution/`, output in `audit_formal.out`)\n"
    "```\n" + audit_part.strip() + "\n```\n"
    "(The last line was produced before this section was appended; the axioms block above is unchanged.)\n"
    "\nKnown deviation: CLAUDE.md routes Lean verification through `anse/formal/lean_runner.py`. This lane followed the\n"
    "task's QuantumFluids rc2 recipe instead: direct `lean` with LEAN_PATH, the same recipe as round 1, whose\n"
    "independent verifier accepted it. The required checks (compile, `#print axioms` whitelist, `sorryAx` rejection,\n"
    "planted controls) are covered above.\n"
)
with open(d + "/FORMAL.md", "a") as fh:
    fh.write(section)
print("appended", len(section), "chars")
