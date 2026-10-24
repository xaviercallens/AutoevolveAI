"""Does the rung-2 gate work at more than ONE obligation?

The stored controls (results/rung2_gate_controls.json) were all recorded at
`obligations_requested: 1`, so the multi-obligation path had never been
exercised -- guard G9 says validate at the real size, not a convenient one.

Two cases, and the second is the decisive one:

* m=2, both obligations honest  -> passed=True,  defeq_checked=2
* m=2, ONE obligation wrong     -> passed=False, defeq_checked=0

The second expectation was originally written as 1, on the theory that a counted
witness would report a partial tally and so prove itself measured rather than
derived. That prediction was WRONG and this test is what refuted it: a Lean
compile is atomic, so one obligation that fails to elaborate fails the whole
audit file, `verify_file` returns a single file-level failure row, and no
obligation rows exist to count. The value is therefore 0 or len(map) and nothing
between -- operationally the same range as the derived version it replaced.

The fix is still worth having, for a different reason: `verify_file` reads
`#print axioms` only for DECLARED theorems, and the previous anonymous
`example : P := thm` declared nothing, so an obligation could elaborate without
its axiom footprint ever being read. Naming the obligations puts each one under
the sorryAx and whitelist check. That, and the refusal of an empty obligation
map, are the real gains -- not a graduated witness.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "/home/xavkal/xdev/AutoevolveAI")
from anse.formal.lean_runner import LeanKernelVerifier  # noqa: E402

FORMAL = Path("/home/xavkal/xdev/AutoevolveAI/formal")
SPEC = FORMAL / "ANSE" / "VerletSymplectic.lean"


def candidate(ns: str, q_coeff: int, p_coeff: int) -> str:
    return f"""import Mathlib.Tactic.Ring
import ANSE.VerletSymplectic

namespace {ns}

def candQ (h w q p : Rat) : Rat := q + h * p - (h ^ 2 * w ^ 2 / {q_coeff}) * q

def candP (h w q p : Rat) : Rat :=
  p - h * w ^ 2 * q - (h ^ 2 * w ^ 2 / {p_coeff}) * p + (h ^ 3 * w ^ 4 / 4) * q

theorem candQ_matches (h w q p : Rat) : candQ h w q p = ANSE.Verlet.qNext h w q p := by
  unfold candQ ANSE.Verlet.qNext; ring

theorem candP_matches (h w q p : Rat) : candP h w q p = ANSE.Verlet.pNext h w q p := by
  unfold candP ANSE.Verlet.pNext; ring

end {ns}

#print axioms {ns}.candQ_matches
#print axioms {ns}.candP_matches
"""


def obligations(ns: str) -> dict[str, str]:
    return {
        f"{ns}.candQ_matches":
            f"∀ h w q p : Rat, {ns}.candQ h w q p = ANSE.Verlet.qNext h w q p",
        f"{ns}.candP_matches":
            f"∀ h w q p : Rat, {ns}.candP h w q p = ANSE.Verlet.pNext h w q p",
    }


CASES = [
    ("m=2 both obligations honest", candidate("TwoHonest", 2, 2), obligations("TwoHonest"), True, 2),
    ("m=2 one obligation wrong", candidate("OneWrong", 2, 3), obligations("OneWrong"), False, 0),
]


def main() -> int:
    v = LeanKernelVerifier(formal_dir=FORMAL)
    rows = []
    for label, src, mapping, expect_pass, expect_checked in CASES:
        with tempfile.TemporaryDirectory() as td:
            cand = Path(td) / "Candidate.lean"
            cand.write_text(src, encoding="utf-8")
            out = v.verify_against_spec(cand, SPEC, mapping, timeout_s=1200.0)
        got_pass = bool(out.get("passed"))
        got_checked = out.get("defeq_checked")
        ok = got_pass == expect_pass and got_checked == expect_checked
        rows.append({
            "case": label,
            "obligations_requested": out.get("obligations_requested"),
            "expected_pass": expect_pass, "passed": got_pass,
            "expected_defeq_checked": expect_checked, "defeq_checked": got_checked,
            "every_result_clean": out.get("every_result_clean"),
            "as_expected": ok,
        })
        print(f"{'OK ' if ok else '!! '}{label:<32} passed={got_pass!s:<5} "
              f"obligations={out.get('obligations_requested')} "
              f"defeq_checked={got_checked} (expected {expect_checked})")
    Path("/home/xavkal/.claude/jobs/6eb13034/tmp/rung2_multi_result.json").write_text(
        json.dumps(rows, indent=2) + "\n")
    agreed = sum(1 for r in rows if r["as_expected"])
    print(f"\n{agreed}/{len(rows)} as required")
    if agreed == len(rows):
        print("Multi-obligation path works at m=2. defeq_checked is 0 or len(map) "
              "and never partial, because a Lean compile is atomic -- so it is a "
              "binary witness, not a graduated one.")
    return 0 if agreed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
