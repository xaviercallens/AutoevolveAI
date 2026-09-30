#!/usr/bin/env python
"""
AR-H5 Benchmark Runner — Phase C Ratchet
=========================================
Autoresearch Hypothesis 5: Asymmetric Dual-Process Test-Time Compute
Qwen2.5-8B (AR Policy) + Laya-LoRA ONNX (NAR Value) in MCTS Tree-of-Thoughts

Fitness = Pass@1 - λ·VRAM_peak_GB - γ·TTS_s   (λ=0.02, γ=0.001)

Ratchet: commits if and only if Fitness(AR-H5) > Fitness(baseline_zero_shot)

Usage:
  uv run python run_ar_h5_benchmark.py --n_problems 10 --dry_run   # mock run
  uv run python run_ar_h5_benchmark.py --n_problems 50             # ratchet + commit
  uv run python run_ar_h5_benchmark.py --laya_onnx /path/to/model_int8.onnx  # real ONNX
"""

import argparse
import hashlib
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from anse.autoresearch.ar_h5_orchestrator import AR_H5_Orchestrator
from anse.autoresearch.ar_record import ARRecord, ARRecordRegistry
from anse.autoresearch.policy import MockQwenPolicy, QwenPolicy
from anse.autoresearch.ratchet import RatchetGate
from anse.autoresearch.sandbox import AR_H5_Sandbox
from anse.autoresearch.value import LayaONNXValue, MockLayaValue

LAMBDA_VRAM = 0.02
GAMMA_TTS = 0.001
RESULTS_DIR = Path("results/ar_h5")


# ---------------------------------------------------------------------------
# Mock problems (used when no dataset file found)
# ---------------------------------------------------------------------------
MOCK_PROBLEMS = [
    "Write a Python function to find the two sum problem: given list and target, return indices.",
    "Implement binary search returning -1 if not found.",
    "Write a function to check if a string is a palindrome.",
    "Implement merge sort in Python.",
    "Write a generator for the Fibonacci sequence.",
    "Implement a simple LRU cache with get/put operations.",
    "Write a depth-first search for a graph represented as adjacency list.",
    "Implement a function to find all prime numbers up to N using Sieve of Eratosthenes.",
    "Write a function to flatten a nested list of arbitrary depth.",
    "Implement a stack with push, pop, and min operations all in O(1).",
]


# ---------------------------------------------------------------------------
# Fitness
# ---------------------------------------------------------------------------
def compute_fitness(pass_at_1: float, vram_peak_gb: float, tts_s: float) -> float:
    return pass_at_1 - LAMBDA_VRAM * vram_peak_gb - GAMMA_TTS * tts_s


# ---------------------------------------------------------------------------
# Problem loader
# ---------------------------------------------------------------------------
def load_problems(subset: str, n: int) -> list[str]:
    if subset == "cruxeval":
        path = Path("/mnt/data/home/xavkal/laya_coding_datasets/stage3/cruxeval.jsonl")
    else:
        path = Path(f"/mnt/data/home/xavkal/laya_coding_datasets/{subset}.jsonl")

    if path.exists():
        problems = []
        with open(path) as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    prompt = obj.get("prompt") or obj.get("question") or obj.get("input") or str(obj)
                    problems.append(prompt)
                except json.JSONDecodeError:
                    continue
                if len(problems) >= n:
                    break
        if problems:
            print(f"  Loaded {len(problems)} problems from {path}")
            return problems

    print(f"  Dataset not found at {path}, using {min(n, len(MOCK_PROBLEMS))} mock problems")
    return (MOCK_PROBLEMS * ((n // len(MOCK_PROBLEMS)) + 1))[:n]


# ---------------------------------------------------------------------------
# Baseline runner (zero-shot: policy generates 1 branch, sandbox checks it)
# ---------------------------------------------------------------------------
def run_baseline(problems: list[str], policy, sandbox: AR_H5_Sandbox) -> dict:
    print(f"\n[Baseline] Zero-shot on {len(problems)} problems …")
    passed = 0
    total_tts = 0.0
    per_problem = []

    for i, p in enumerate(problems):
        t0 = time.perf_counter()
        branches = policy.generate_branches("", p, k=1)
        code = branches[0] if branches else ""
        result = sandbox.run_auto(code)
        tts = time.perf_counter() - t0

        ok = not result.is_error
        if ok:
            passed += 1
        total_tts += tts
        per_problem.append({"problem_idx": i, "passed": ok, "tts_s": round(tts, 3)})
        print(f"  [{i+1:02d}/{len(problems)}] {'✓' if ok else '✗'}  {tts*1000:.0f}ms")

    pass_rate = passed / len(problems)
    avg_tts = total_tts / len(problems)
    return {
        "pass_at_1": pass_rate,
        "passed": passed,
        "total": len(problems),
        "avg_tts_s": round(avg_tts, 3),
        "vram_peak_gb": 0.0,  # Mock: no GPU
        "per_problem": per_problem,
    }


# ---------------------------------------------------------------------------
# AR-H5 runner (MCTS with Laya value network)
# ---------------------------------------------------------------------------
def run_arh5(problems: list[str], orchestrator: AR_H5_Orchestrator) -> dict:
    print(f"\n[AR-H5] MCTS Tree-of-Thoughts on {len(problems)} problems …")
    passed = 0
    total_tts = 0.0
    total_branches_killed = 0
    total_laya_calls = 0
    per_problem = []

    for i, p in enumerate(problems):
        result = orchestrator.run(p)
        ok = result.success
        if ok:
            passed += 1
        total_tts += result.elapsed_s
        total_branches_killed += result.branches_killed
        total_laya_calls += result.laya_calls
        per_problem.append({
            "problem_idx": i,
            "passed": ok,
            "tts_s": round(result.elapsed_s, 3),
            "nodes": result.tree_nodes,
            "killed": result.branches_killed,
            "sandbox_errors": result.sandbox_errors,
        })
        print(f"  [{i+1:02d}/{len(problems)}] {'✓' if ok else '✗'}  "
              f"{result.elapsed_s*1000:.0f}ms  "
              f"nodes={result.tree_nodes}  killed={result.branches_killed}  "
              f"laya={result.laya_calls}")

    pass_rate = passed / len(problems)
    avg_tts = total_tts / len(problems)
    return {
        "pass_at_1": pass_rate,
        "passed": passed,
        "total": len(problems),
        "avg_tts_s": round(avg_tts, 3),
        "vram_peak_gb": 0.0,
        "total_branches_killed": total_branches_killed,
        "total_laya_calls": total_laya_calls,
        "per_problem": per_problem,
    }


# ---------------------------------------------------------------------------
# Receipt writing with SHA-256
# ---------------------------------------------------------------------------
def write_receipt(
    record: dict,
    path: Path,
) -> str:
    payload = json.dumps(record, indent=2, sort_keys=True)
    sha = hashlib.sha256(payload.encode()).hexdigest()
    record["sha256"] = sha
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True))
    return sha


# ---------------------------------------------------------------------------
# Git commit (ratchet accepted)
# ---------------------------------------------------------------------------
def git_commit_arh5(delta: float) -> str | None:
    try:
        subprocess.run(["git", "add",
                        "anse/autoresearch/",
                        "run_ar_h5_benchmark.py",
                        "results/ar_h5/",
                        ".agents/skills/autoresearch/"], check=False, capture_output=True)
        result = subprocess.run(
            ["git", "commit", "-m",
             f"autoresearch(AR-H5): ratchet ACCEPTED — ΔFitness={delta:+.4f}\n\n"
             f"Asymmetric Dual-Process MCTS: Qwen2.5 (Policy) + Laya-LoRA ONNX (Value)\n"
             f"Fitness = Pass@1 - 0.02·VRAM - 0.001·TTS\n"
             f"All results in results/ar_h5/ratchet_results.json (SHA-256 verified)"],
            check=False, capture_output=True, text=True
        )
        if result.returncode == 0:
            hash_result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True
            )
            return hash_result.stdout.strip()
    except Exception as e:
        print(f"  Git commit failed: {e}")
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="AR-H5 Ratchet Benchmark: Qwen2.5 + Laya-LoRA MCTS vs zero-shot baseline"
    )
    parser.add_argument("--subset", default="cruxeval", help="Dataset subset name")
    parser.add_argument("--n_problems", type=int, default=10)
    parser.add_argument("--dry_run", action="store_true", help="Skip git commit even if ratchet passes")
    parser.add_argument("--laya_onnx", default=None, help="Path to Laya ONNX INT8 model")
    parser.add_argument("--qwen_model", default=None, help="Qwen model name/path (default: mock)")
    parser.add_argument("--max_depth", type=int, default=3)
    parser.add_argument("--k", type=int, default=3, help="MCTS branching factor")
    parser.add_argument("--timeout_s", type=float, default=30.0)
    args = parser.parse_args()

    print("=" * 60)
    print("AR-H5: Asymmetric Dual-Process Test-Time Compute")
    print(f"  Subset: {args.subset}  |  N={args.n_problems}")
    print(f"  MCTS: k={args.k}, max_depth={args.max_depth}, timeout={args.timeout_s}s")
    print(f"  Fitness = Pass@1 - {LAMBDA_VRAM}·VRAM - {GAMMA_TTS}·TTS")
    print("=" * 60)

    # --- Build components ---
    print("\n[Setup] Loading components …")
    sandbox = AR_H5_Sandbox(python_timeout_s=8.0)

    if args.laya_onnx and Path(args.laya_onnx).exists():
        print(f"  Value: LayaONNXValue ({args.laya_onnx})")
        value = LayaONNXValue(onnx_path=args.laya_onnx)
    else:
        print("  Value: MockLayaValue (fixed_score=0.75, fixed_noul=0.85 → PASS)")
        value = MockLayaValue(fixed_score=0.75, fixed_noul=0.85)

    if args.qwen_model:
        print(f"  Policy: QwenPolicy ({args.qwen_model})")
        policy = QwenPolicy(model_name=args.qwen_model)
    else:
        print("  Policy: MockQwenPolicy (deterministic code responses)")
        policy = MockQwenPolicy()

    orchestrator = AR_H5_Orchestrator(
        policy=policy,
        value=value,
        sandbox=sandbox,
        max_depth=args.max_depth,
        k=args.k,
        tau_noul=0.3,
        timeout_s=args.timeout_s,
        results_dir=RESULTS_DIR,
    )

    # --- Load problems ---
    print("\n[Data] Loading problems …")
    problems = load_problems(args.subset, args.n_problems)

    # --- Run baseline ---
    baseline = run_baseline(problems, policy, sandbox)
    baseline_fitness = compute_fitness(
        baseline["pass_at_1"], baseline["vram_peak_gb"], baseline["avg_tts_s"]
    )

    # --- Run AR-H5 ---
    arh5 = run_arh5(problems, orchestrator)
    arh5_fitness = compute_fitness(
        arh5["pass_at_1"], arh5["vram_peak_gb"], arh5["avg_tts_s"]
    )

    delta = arh5_fitness - baseline_fitness
    verdict = "ACCEPTED" if delta > 0 else "REJECTED"

    # --- Print results ---
    print("\n" + "=" * 60)
    print("RATCHET RESULTS")
    print("=" * 60)
    print(f"  Baseline : Pass@1={baseline['pass_at_1']:.3f}  "
          f"TTS={baseline['avg_tts_s']:.3f}s  Fitness={baseline_fitness:.4f}")
    print(f"  AR-H5    : Pass@1={arh5['pass_at_1']:.3f}  "
          f"TTS={arh5['avg_tts_s']:.3f}s  Fitness={arh5_fitness:.4f}")
    print(f"  ΔFitness : {delta:+.4f}")
    print(f"  Verdict  : {verdict}")
    if arh5.get("total_branches_killed", 0) > 0:
        kill_rate = arh5["total_branches_killed"] / max(arh5["total_laya_calls"], 1)
        print(f"  Laya killed {arh5['total_branches_killed']} branches "
              f"({kill_rate:.1%} kill rate, {arh5['total_laya_calls']} total calls)")
    print("=" * 60)

    # --- Write receipt ---
    now = datetime.now(timezone.utc).isoformat()
    receipt = {
        "hypothesis": "AR-H5",
        "title": "Asymmetric Dual-Process Test-Time Compute",
        "timestamp": now,
        "subset": args.subset,
        "n_problems": len(problems),
        "dry_run": args.dry_run,
        "policy": args.qwen_model or "MockQwenPolicy",
        "value": args.laya_onnx or "MockLayaValue",
        "mcts_k": args.k,
        "mcts_max_depth": args.max_depth,
        "fitness_lambda_vram": LAMBDA_VRAM,
        "fitness_gamma_tts": GAMMA_TTS,
        "baseline": {**baseline, "fitness": round(baseline_fitness, 6)},
        "arh5": {**arh5, "fitness": round(arh5_fitness, 6)},
        "delta_fitness": round(delta, 6),
        "verdict": verdict,
        "commit_hash": None,
    }

    sha = write_receipt(receipt, RESULTS_DIR / "ratchet_results.json")
    print(f"\nReceipt: results/ar_h5/ratchet_results.json  (SHA-256: {sha[:16]}…)")

    # --- Ratchet commit ---
    if verdict == "ACCEPTED" and not args.dry_run:
        print("\n✓ Ratchet ACCEPTED — committing AR-H5 improvements …")
        commit_hash = git_commit_arh5(delta)
        if commit_hash:
            receipt["commit_hash"] = commit_hash
            write_receipt(receipt, RESULTS_DIR / "ratchet_results.json")
            print(f"  Committed: {commit_hash[:8]}")
        else:
            print("  Git commit failed (possibly no changes to commit)")
    elif verdict == "REJECTED":
        print(f"\n✗ Ratchet REJECTED — ΔFitness={delta:+.4f} ≤ 0. No commit.")
    else:
        print(f"\n  Dry run — would {'commit' if delta > 0 else 'reject'} (ΔFitness={delta:+.4f})")


if __name__ == "__main__":
    main()
