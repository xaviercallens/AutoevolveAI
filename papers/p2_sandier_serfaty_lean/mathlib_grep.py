"""Scan the pinned Mathlib (d13f23b7) for the four facts the paper states about what Mathlib has; write data/mathlib_grep.json."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ML = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/openai_math_pinned/lean/.lake/packages/mathlib/Mathlib")


def files_containing(root: Path, needle: str) -> list[str]:
    out = []
    for p in sorted(root.rglob("*.lean")):
        try:
            if needle in p.read_text(errors="replace").lower():
                out.append(str(p.relative_to(ML)))
        except OSError:
            pass
    return out


def main() -> int:
    res = {
        "mathlib_root": str(ML),
        "trapezoidal_rule_file": (ML / "MeasureTheory/Integral/IntervalIntegral/TrapezoidalRule.lean").is_file(),
        "weierstrass_file": (ML / "Analysis/SpecialFunctions/Elliptic/Weierstrass.lean").is_file(),
        "files_in_MeasureTheory_Integral_mentioning_midpoint": files_containing(ML / "MeasureTheory/Integral", "midpoint"),
        "files_in_Mathlib_mentioning_voronoi": files_containing(ML, "voronoi"),
        "files_in_Mathlib_mentioning_torus_green": files_containing(ML, "green's function") + files_containing(ML, "greens function"),
    }
    (HERE / "data/mathlib_grep.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
