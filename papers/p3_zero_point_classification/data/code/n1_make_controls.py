"""N1 Lean negative controls from REAL records (no invented numbers):

  RejectInside.lean   : asserts `allPos [r_in] = true` for the certified record at a = A_IN inside (a-, a+), whose
                        enclosure is negative. Must FAIL to compile (rc 1): the method cannot certify a local
                        minimum just inside the window.
  RejectTampered.lean : the record at A_POS (certified positive) with the sign of its qlo flipped; asserts
                        `allPos [r_t] = true`. Must FAIL (rc 1).
  Honest.lean         : the true statements `allPos [r_in] = false`, `allNeg [r_in] = true`,
                        `allPos [r_t] = false`; must compile (rc 0) with standard axioms only.

usage: python -I n1_make_controls.py OUTDIR A_IN A_POS RUN1.json [RUN2.json ...]
"""

from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from n1_make_cert import lean_q, rec_vals  # noqa: E402


def find(runs: list[dict], a: Fraction) -> dict:
    for r in runs:
        if Fraction(r["a_lo"]) == a == Fraction(r["a_hi"]) and r["ok"]:
            return r
    raise SystemExit(f"no certified thin record at a = {a}")


def main() -> None:
    outdir, a_in, a_pos = sys.argv[1], Fraction(sys.argv[2]), Fraction(sys.argv[3])
    runs = [r for p in sys.argv[4:] for r in json.load(open(p)) if r.get("engine") == "n1_certify2"]
    rin = rec_vals(find(runs, a_in))
    rp = list(rec_vals(find(runs, a_pos)))
    rt = rp.copy()
    rt[3] = -rt[3]
    rt[4] = rt[4] if rt[4] > -rt[3] else -rt[3]  # keep qlo <= qhi after the flip
    q = lambda v: "⟨" + ", ".join(lean_q(x) for x in v) + "⟩"  # noqa: E731
    head = "import Programmes.ZeroPointClass.Basic\n\nnamespace ProgZeroPointClass\n\n"
    files = {
        "RejectInside.lean": head + f"/-- MUST FAIL: the real record at a = {a_in} (inside the window) claimed positive. -/\n"
                             f"def rIn : Rec := {q(rin)}\n\ntheorem inside_claimed_pos : allPos [rIn] = true := by decide +kernel\n\n"
                             "end ProgZeroPointClass\n",
        "RejectTampered.lean": head + f"/-- MUST FAIL: the real positive record at a = {a_pos} with the sign of qlo flipped. -/\n"
                               f"def rT : Rec := {q(rt)}\n\ntheorem tampered_claimed_pos : allPos [rT] = true := by decide +kernel\n\n"
                               "end ProgZeroPointClass\n",
        "Honest.lean": head + f"def rInH : Rec := {q(rin)}\ndef rTH : Rec := {q(rt)}\ndef rPH : Rec := {q(rp)}\n\n"
                       "theorem inside_not_pos : allPos [rInH] = false := by decide +kernel\n"
                       "theorem inside_is_neg : allNeg [rInH] = true := by decide +kernel\n"
                       "theorem tampered_not_pos : allPos [rTH] = false := by decide +kernel\n"
                       "theorem untampered_pos : allPos [rPH] = true := by decide +kernel\n\n"
                       "end ProgZeroPointClass\n\n"
                       "#print axioms ProgZeroPointClass.inside_not_pos\n#print axioms ProgZeroPointClass.inside_is_neg\n"
                       "#print axioms ProgZeroPointClass.tampered_not_pos\n#print axioms ProgZeroPointClass.untampered_pos\n",
    }
    for name, src in files.items():
        with open(os.path.join(outdir, name), "w") as fh:
            fh.write(src)
        print("wrote", name)


if __name__ == "__main__":
    main()
