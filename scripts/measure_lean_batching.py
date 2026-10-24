#!/usr/bin/env python3
"""Does batching candidates into one Lean invocation actually pay?

`results/rung2_gate_cost.json` established that essentially the whole cost of a
rung-2 verification is a fixed `Mathlib.Tactic.Ring` load per process
invocation: a file containing only that import and one trivial theorem takes a
median 17.61 s, which was the SLOWEST of four conditions tested. That left
exactly one lever -- pay the load once for many candidates instead of once per
candidate -- which was recorded as predicted by the decomposition and NOT
demonstrated. This demonstrates or refutes it.

It also prices the lever's known downside, which follows from a fact measured
earlier: a Lean compile is ATOMIC. One candidate that fails to elaborate fails
the whole file, so a batch that contains a bad candidate yields no per-candidate
verdicts at all and the batch must be re-run individually to find out who
failed. Batching is therefore only cheap when candidates mostly pass, and the
break-even depends on the failure rate.

Three conditions, N candidates each:

  A  one invocation per candidate            N invocations
  B  all N in one file, all honest            1 invocation
  C  all N in one file, ONE of them false     1 invocation that fails,
                                              then N to isolate = N+1

Reported as wall-clock seconds with the spread on repeats, because the same-input
spread on this host reaches 2.60x and any claimed saving below that is
unmeasurable (LL.md 29.12).

    python scripts/measure_lean_batching.py --out results/lean_batching.json
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import time
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[1]
FORMAL = REPO / "formal"


def module(index: int, wrong: bool = False) -> str:
    """One self-contained candidate module plus its obligation.

    The constant differs per module so the candidates are textually distinct and
    nothing can be shared or cached between them by accident.
    """
    coeff = 3 if wrong else 2
    ns = f"Cand{index:02d}"
    return f"""
namespace {ns}

def candQ (h w q p : Rat) : Rat := q + h * p - (h ^ 2 * w ^ 2 / {coeff}) * q

theorem candQ_matches (h w q p : Rat) : candQ h w q p = ANSE.Verlet.qNext h w q p := by
  unfold candQ ANSE.Verlet.qNext; ring

end {ns}

#print axioms {ns}.candQ_matches

theorem defeqAudit_{ns} :
    ∀ h w q p : Rat, {ns}.candQ h w q p = ANSE.Verlet.qNext h w q p :=
  {ns}.candQ_matches

#print axioms defeqAudit_{ns}
"""


HEADER = "import Mathlib.Tactic.Ring\nimport ANSE.VerletSymplectic\n"


def write_file(path: Path, indices: List[int], wrong_index: int | None = None) -> None:
    body = "".join(module(i, wrong=(i == wrong_index)) for i in indices)
    path.write_text(HEADER + body, encoding="utf-8")


def run_lean(path: Path, timeout_s: float = 1800.0) -> tuple[float, int]:
    start = time.perf_counter()
    done = subprocess.run(
        ["lake", "env", "lean", str(path)],
        cwd=str(FORMAL), capture_output=True, text=True, timeout=timeout_s,
    )
    return time.perf_counter() - start, done.returncode


def summarise(xs: List[float]) -> Dict[str, object]:
    return {
        "n": len(xs),
        "median": round(statistics.median(xs), 2),
        "min": round(min(xs), 2),
        "max": round(max(xs), 2),
        "same_input_spread": round(max(xs) / max(min(xs), 1e-9), 2),
        "runs": [round(x, 2) for x in xs],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--candidates", type=int, default=8)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--work", type=Path,
                        default=Path("/home/xavkal/.claude/jobs/6eb13034/tmp/batching"))
    args = parser.parse_args()
    args.work.mkdir(parents=True, exist_ok=True)
    N, R = args.candidates, args.repeats
    indices = list(range(1, N + 1))

    # A: one invocation per candidate.
    per_candidate_totals: List[float] = []
    per_candidate_each: List[float] = []
    for _ in range(R):
        total = 0.0
        for i in indices:
            f = args.work / f"single_{i:02d}.lean"
            write_file(f, [i])
            dt, rc = run_lean(f)
            if rc != 0:
                raise RuntimeError(f"honest single candidate {i} failed to compile")
            total += dt
            per_candidate_each.append(dt)
        per_candidate_totals.append(total)
        print(f"  A: {N} separate invocations -> {total:.2f} s")

    # B: all N in one invocation, all honest.
    batch_totals: List[float] = []
    batch = args.work / "batch_all_honest.lean"
    write_file(batch, indices)
    for _ in range(R):
        dt, rc = run_lean(batch)
        if rc != 0:
            raise RuntimeError("the all-honest batch failed to compile")
        batch_totals.append(dt)
        print(f"  B: 1 batched invocation      -> {dt:.2f} s")

    # C: a batch containing one false candidate. It must fail, and then the
    # batch has to be re-run individually to find out which candidate was bad.
    poisoned = args.work / "batch_one_false.lean"
    write_file(poisoned, indices, wrong_index=indices[N // 2])
    poisoned_totals: List[float] = []
    for _ in range(R):
        dt, rc = run_lean(poisoned)
        if rc == 0:
            raise RuntimeError(
                "a batch containing a false obligation compiled successfully; "
                "the atomicity premise of this measurement is wrong"
            )
        poisoned_totals.append(dt)
        print(f"  C: 1 failing batch           -> {dt:.2f} s (rc={rc})")

    A, B, C = (summarise(per_candidate_totals), summarise(batch_totals),
               summarise(poisoned_totals))
    each = summarise(per_candidate_each)
    speedup = A["median"] / B["median"]
    # Isolation cost: the failed batch, then every candidate individually.
    isolate_median = C["median"] + A["median"]
    break_even_failure_rate = None
    if isolate_median > A["median"]:
        # Batching loses when p * (C + A) + (1-p) * B > A.
        denom = (C["median"] + A["median"]) - B["median"]
        if denom > 0:
            break_even_failure_rate = round(max(0.0, (A["median"] - B["median"]) / denom), 3)

    report = {
        "measurement": "does batching candidates into one Lean invocation pay?",
        "premise": (
            "results/rung2_gate_cost.json showed the whole cost is a fixed "
            "Mathlib.Tactic.Ring load per invocation (bare floor median 17.61 s, "
            "the slowest of four conditions). Batching pays that once for many "
            "candidates. This tests that prediction instead of asserting it."
        ),
        "candidates": N, "repeats": R,
        "conditions": {
            "A_one_invocation_per_candidate": A,
            "A_per_single_candidate": each,
            "B_all_in_one_invocation": B,
            "C_failing_batch": C,
        },
        "batched_speedup_median": round(speedup, 2),
        "isolation_cost_when_a_batch_fails_median_seconds": round(isolate_median, 2),
        "break_even_failure_rate": break_even_failure_rate,
        "atomicity": (
            "A batch containing one false obligation fails as a whole and yields "
            "no per-candidate verdict, so it must be re-run individually to "
            "isolate. That is the measured cost of the lever, not a caveat."
        ),
        "how_to_read_it": (
            "The same-input spread on this host reaches 2.60x, so a saving below "
            "that is unmeasurable (LL.md 29.12). Compare the speedup against the "
            "spreads reported per condition, not against zero."
        ),
        "not_established": [
            f"N={N}, R={R}. Small samples; medians with spreads, not distributions.",
            "A persistent Lean server was not built; this measures batching into one "
            "file, which is the cheap approximation of process reuse.",
            "The break-even failure rate assumes isolation re-runs every candidate; "
            "a bisection would be cheaper and is not measured.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"\n  A total  median {A['median']:>7.2f} s  (spread {A['same_input_spread']}x)")
    print(f"  per-one  median {each['median']:>7.2f} s  (spread {each['same_input_spread']}x)")
    print(f"  B batch  median {B['median']:>7.2f} s  (spread {B['same_input_spread']}x)")
    print(f"  C failed median {C['median']:>7.2f} s  (spread {C['same_input_spread']}x)")
    print(f"\n  batched speedup: {speedup:.2f}x over {N} candidates")
    print(f"  isolation cost when a batch fails: {isolate_median:.2f} s")
    if break_even_failure_rate is not None:
        print(f"  batching loses above a failure rate of ~{break_even_failure_rate:.1%}")
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
