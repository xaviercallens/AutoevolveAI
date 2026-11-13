#!/usr/bin/env python3
"""Put the Rust KGE solutions through the real Lean kernel gate.

`kge ladder --lean-out DIR` renders every solution it finds as a Lean candidate
and each rung's target as a `RungSpec`. This script is the half of the
architecture the Rust crate deliberately does not contain: acceptance. Lean
verification in this project goes through `anse/formal/lean_runner.py` only, so
the candidates are handed to `verify_batch_against_spec`, which compiles a batch
in ONE invocation and reads the kernel's per-declaration axiom report.

What it establishes, per rung:

* every candidate that reached fitness zero is proved equal to the specification
  (or named as a culprit if it is not -- an agreement at twelve sample points is
  not equality, and this is where that distinction is enforced);
* the batch cost one invocation regardless of how many candidates it held;
* and the control: a deliberately WRONG candidate is appended to one rung's
  batch and must be rejected, so a gate that accepted everything could not pass.

Usage:
    .venv/bin/python scripts/kge_gate_rust_solutions.py \
        --candidates results/kge_lean_candidates --per-rung 8 \
        --out results/kge_rust_gate.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from anse.formal.lean_runner import LeanKernelVerifier  # noqa: E402

FORMAL = REPO / "formal"
RUNGS = ("L1_base", "L2_minus_q", "L3_minus_wq", "L4_minus_hwq", "L5_minus_half_hwq", "L6_full")


def obligation(ns: str) -> dict[str, str]:
    return {f"{ns}.{ns}_m": f"∀ h w q p : Rat, {ns}.candQ h w q p = RungSpec.specQ h w q p"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--per-rung", type=int, default=8,
                        help="distinct candidates to gate per rung (one invocation each)")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--names", type=str, default="",
                        help="comma-separated candidate names to gate instead of the ladder rungs "
                             "(e.g. the --name values given to `kge solve`)")
    args = parser.parse_args()
    names = tuple(n for n in args.names.split(",") if n) or RUNGS

    verifier = LeanKernelVerifier(formal_dir=FORMAL)
    report: dict[str, object] = {
        "what_this_is": "Rust KGE solutions put through the Lean kernel gate, one invocation per rung",
        "gate": "anse/formal/lean_runner.py::verify_batch_against_spec",
        "rungs": {},
    }
    total_invocations = 0
    total_candidates = 0
    total_accepted = 0

    for rung in names:
        spec = args.candidates / f"RungSpec_{rung}.lean"
        if not spec.exists():
            report["rungs"][rung] = {"blocked": f"BLOCKED: no RungSpec for {rung}"}
            continue
        files = sorted(args.candidates.glob(f"{rung}_S*.lean"))
        # Distinct by rendered term, so the batch measures distinct solutions.
        seen: set[str] = set()
        batch: list[tuple[str, Path, dict[str, str]]] = []
        for path in files:
            text = path.read_text(encoding="utf-8")
            match = re.search(r"def candQ \(h w q p : Rat\) : Rat := (.+)", text)
            term = match.group(1).strip() if match else text
            if term in seen:
                continue
            seen.add(term)
            ns = path.stem
            batch.append((ns, path, obligation(ns)))
            if len(batch) >= args.per_rung:
                break
        if not batch:
            report["rungs"][rung] = {"candidates": 0, "note": "no solutions found by the search"}
            continue

        # The control: one candidate that is certainly wrong (the spec plus one)
        # rides along in the batch and must be REJECTED by name.
        wrong_ns = f"{rung}_WRONG"
        wrong_path = args.candidates / f"{wrong_ns}.lean"
        spec_term = re.search(r"def specQ \(h w q p : Rat\) : Rat := (.+)",
                              spec.read_text(encoding="utf-8")).group(1).strip()
        wrong_path.write_text(
            "import Mathlib.Tactic.Ring\n"
            f"namespace {wrong_ns}\n"
            f"def candQ (h w q p : Rat) : Rat := ({spec_term} + (1 : Rat))\n"
            f"theorem {wrong_ns}_m (h w q p : Rat) : candQ h w q p = RungSpec.specQ h w q p := by\n"
            "  unfold candQ RungSpec.specQ; ring\n"
            f"end {wrong_ns}\n",
            encoding="utf-8",
        )
        batch.append((wrong_ns, wrong_path, obligation(wrong_ns)))

        t0 = time.perf_counter()
        out = verifier.verify_batch_against_spec(batch, spec, timeout_s=1800.0)
        elapsed = time.perf_counter() - t0
        verdicts = out.get("verdicts", {})
        accepted = [k for k, v in verdicts.items() if v and k != wrong_ns]
        rejected = [k for k, v in verdicts.items() if not v and k != wrong_ns]
        control_rejected = verdicts.get(wrong_ns) is False
        total_invocations += int(out.get("invocations", 0))
        total_candidates += len(batch) - 1
        total_accepted += len(accepted)
        report["rungs"][rung] = {
            "distinct_candidates_gated": len(batch) - 1,
            "accepted_by_kernel": len(accepted),
            "rejected_by_kernel": rejected,
            "control_wrong_candidate_rejected": control_rejected,
            "invocations": out.get("invocations"),
            "wall_clock_s": round(elapsed, 2),
            "blocked": out.get("blocked"),
        }
        print(f"  {rung:<20} gated {len(batch)-1:>2} distinct  accepted {len(accepted):>2}  "
              f"rejected {len(rejected)}  control_rejected={control_rejected}  "
              f"invocations={out.get('invocations')}  {elapsed:6.1f}s")

    report["totals"] = {
        "distinct_candidates_gated": total_candidates,
        "accepted_by_kernel": total_accepted,
        "invocations": total_invocations,
        "all_controls_rejected": all(
            r.get("control_wrong_candidate_rejected", True)
            for r in report["rungs"].values() if isinstance(r, dict) and "invocations" in r
        ),
    }
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
