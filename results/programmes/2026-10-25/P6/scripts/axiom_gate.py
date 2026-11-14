"""Axiom gate for the P6 Feynman-Bijl Lean files: reads lean_pinned.py compile JSONs.

PASS requires: main files rc 0, no `sorry` token in the sources, every `#print axioms` line within
{propext, Classical.choice, Quot.sound}, all declared theorems printed; controls file rc 0 with
ctl_sorry showing sorryAx and ctl_axiom showing ctl_cheat.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

WHITELIST = {"propext", "Classical.choice", "Quot.sound"}
LINE = re.compile(r"'([^']+)' depends on axioms: \[([^\]]*)\]")


def axioms(out: str) -> dict[str, set[str]]:
    return {m.group(1): {a.strip() for a in m.group(2).split(",") if a.strip()} for m in LINE.finditer(out)}


def declared(src: Path) -> list[str]:
    names = re.findall(r"^(?:theorem|lemma)\s+(\S+)", src.read_text(), flags=re.M)
    return ["ProgFeynmanBijl." + n for n in names]


def main() -> int:
    lean_dir, src_dir = Path(sys.argv[1]), Path(sys.argv[2])
    report: dict[str, object] = {}
    ok = True
    for stem, js in (("Basic", "compile_basic.json"), ("NegativeControls", "compile_negctl.json"),
                     ("PositiveControls", "compile_posctl.json")):
        res = json.loads((lean_dir / js).read_text())
        src = src_dir / f"{stem}.lean"
        ax = axioms(str(res["output"]))
        decl = declared(src)
        bad = {k: sorted(v - WHITELIST) for k, v in ax.items() if v - WHITELIST}
        missing = [d for d in decl if d not in ax]
        has_sorry = re.search(r"\bsorry\b", re.sub(r"/-.*?-/|--[^\n]*", "", src.read_text(), flags=re.S)) is not None
        passed = res["rc"] == 0 and not bad and not missing and not has_sorry
        ok &= passed
        report[stem] = {"rc": res["rc"], "printed": len(ax), "declared": len(decl), "non_whitelist": bad,
                        "not_printed": missing, "sorry_token": has_sorry, "PASS": passed}
    res = json.loads((lean_dir / "compile_controls.json").read_text())
    ax = axioms(str(res["output"]))
    caught_s = "sorryAx" in ax.get("ProgFeynmanBijl.ctl_sorry", set())
    caught_a = "ProgFeynmanBijl.ctl_cheat" in ax.get("ProgFeynmanBijl.ctl_axiom", set())
    report["Controls"] = {"rc": res["rc"], "ctl_sorry_caught": caught_s, "ctl_axiom_caught": caught_a,
                          "PASS": res["rc"] == 0 and caught_s and caught_a}
    ok &= bool(report["Controls"]["PASS"])  # type: ignore[index]
    report["GATE"] = "PASS" if ok else "FAIL"
    (lean_dir / "axiom_gate.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
