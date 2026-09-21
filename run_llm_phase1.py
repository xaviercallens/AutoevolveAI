#!/usr/bin/env python3
"""Phase 1 use case on real hardware: local quantised Qwen3-8B closes the energy loop.

Runs the 20-task benchmark through :class:`AgentLoop` with generation served by Ollama
on the T4, measuring the convergence rate that the Definition of Done claims (>= 70%).
Every trace is harvested with a 1024-d latent so Phase 2 can train on real data.

Usage::

    python run_llm_phase1.py --out .scratchpad/llm_phase1
"""

from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from pathlib import Path

from anse.config import MemoryConfig
from anse.core.agent_loop import AgentLoop
from anse.core.ollama_extractor import OllamaConfig, OllamaExtractor
from anse.memory.harvester import Harvester
from main import load_tasks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks", default="tasks/phase1_benchmark.yaml")
    parser.add_argument("--out", default=".scratchpad/llm_phase1")
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--model", default="qwen3:8b")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    extractor = OllamaExtractor(OllamaConfig(gen_model=args.model))
    harvester = Harvester(
        config=MemoryConfig(
            persist_directory=out_dir / "chroma",
            interactions_log=out_dir / "interactions.jsonl",
        ),
        enable_chroma=False,
    )
    loop = AgentLoop(extractor=extractor, harvester=harvester, max_retries=args.max_retries)

    tasks = load_tasks(Path(args.tasks))
    print(f"[phase1-llm] model={args.model} tasks={len(tasks)} max_retries={args.max_retries}")

    rows: list[dict] = []
    by_tier: dict[str, list[bool]] = defaultdict(list)
    wall_start = time.time()

    for i, task in enumerate(tasks, 1):
        name = task.get("name", f"task_{i}")
        tier = task.get("tier", "unknown")
        started = time.time()
        summary = loop.run(
            task=task["task"],
            expected_output=task.get("expected_output"),
            max_retries=args.max_retries,
        )
        row = {
            "name": name,
            "tier": tier,
            "converged": summary.converged,
            "iterations": summary.iterations,
            "final_energy": round(summary.final_energy, 2),
            "final_category": summary.final_category,
            "wall_s": round(time.time() - started, 1),
        }
        rows.append(row)
        by_tier[tier].append(summary.converged)
        print(
            f"[{i:2d}/{len(tasks)}] {tier:12s} {name:24s} "
            f"E={row['final_energy']:>10.2f} iters={row['iterations']} "
            f"converged={summary.converged} ({row['wall_s']}s)",
            flush=True,
        )

    converged = sum(r["converged"] for r in rows)
    rate = 100.0 * converged / max(len(rows), 1)
    report = {
        "model": args.model,
        "tasks": len(rows),
        "converged": converged,
        "convergence_rate_pct": round(rate, 1),
        "definition_of_done_pct": 70.0,
        "passed_dod": rate >= 70.0,
        "wall_s": round(time.time() - wall_start, 1),
        "llm_calls": extractor.calls,
        "generated_tokens": extractor.total_eval_tokens,
        "by_tier": {
            tier: {
                "converged": sum(v),
                "total": len(v),
                "rate_pct": round(100.0 * sum(v) / len(v), 1),
            }
            for tier, v in sorted(by_tier.items())
        },
        "rows": rows,
    }
    (out_dir / "phase1_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\n=== PHASE 1 (real LLM) ===")
    print(f"convergence {converged}/{len(rows)} = {rate:.1f}%  (DoD >= 70% -> {report['passed_dod']})")
    for tier, stats in report["by_tier"].items():
        print(f"  {tier:12s} {stats['converged']}/{stats['total']} = {stats['rate_pct']}%")
    print(f"traces -> {harvester.log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
