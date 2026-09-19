"""
ANSE Phase 1: Reality Engine (Neuro-Symbolic Grounding) CLI Entry Point.

Usage:
    python main.py --mock-llm --tasks tasks/phase1_benchmark.yaml
    python main.py --single-task "Write a function is_palindrome(s) and test with 'racecar'"
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

import yaml

from anse.config import ANSEConfig, get_config
from anse.core.agent_loop import AgentLoop, LoopSummary
from anse.core.encoder import HiddenStateExtractor
from anse.memory.harvester import Harvester
from anse.symbolic.evaluator import EnergyEvaluator
from anse.symbolic.sandbox import SandboxExecutor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("anse.main")


def load_tasks(tasks_path: Path) -> list[dict[str, Any]]:
    """Load benchmark tasks from a YAML file."""
    if not tasks_path.exists():
        logger.error("Tasks file not found: %s", tasks_path)
        return []

    with open(tasks_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "tasks" in data:
        return data["tasks"]
    return []


def run_benchmark(
    loop: AgentLoop,
    tasks: list[dict[str, Any]],
    max_retries: int = 3,
) -> tuple[list[LoopSummary], float]:
    """Execute all tasks and calculate the convergence rate."""
    summaries: list[LoopSummary] = []

    print("\n" + "=" * 70)
    print(f"ANSE Phase 1 Benchmark: Running {len(tasks)} tasks")
    print("=" * 70)

    for i, t in enumerate(tasks, 1):
        task_desc = t.get("task", "") or t.get("prompt", "")
        task_name = t.get("name", f"Task {i}")
        expected = t.get("expected_output")

        print(f"\n[{i}/{len(tasks)}] {task_name}: {task_desc[:60]}...")
        summary = loop.run(task=task_desc, expected_output=expected, max_retries=max_retries)
        summaries.append(summary)

        status_str = "CONVERGED" if summary.converged else "FAILED"
        print(
            f"   -> {status_str} in {summary.iterations} iteration(s) "
            f"| Final Energy: {summary.final_energy:.1f} ({summary.final_category})"
        )

    converged_count = sum(1 for s in summaries if s.converged)
    convergence_rate = (converged_count / len(tasks)) * 100.0 if tasks else 0.0

    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)
    print(f"Total tasks:       {len(tasks)}")
    print(f"Converged tasks:   {converged_count}")
    print(f"Convergence rate:  {convergence_rate:.1f}%")
    print(f"Target threshold:  70.0%")
    print("=" * 70 + "\n")

    return summaries, convergence_rate


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ANSE Phase 1: Neuro-Symbolic Reality Engine CLI"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="Qwen/Qwen2.5-Coder-7B-Instruct",
        help="HuggingFace model ID for LLM backbone",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        help="Device to run on ('auto', 'cuda', 'cpu', 'mps')",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retry attempts per task",
    )
    parser.add_argument(
        "--tasks",
        type=str,
        default="tasks/phase1_benchmark.yaml",
        help="Path to tasks YAML file",
    )
    parser.add_argument(
        "--single-task",
        type=str,
        default=None,
        help="Run a single task string directly",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to store interaction traces and chroma vectors",
    )
    parser.add_argument(
        "--mock-llm",
        action="store_true",
        help="Run using mock LLM extractor for testing without GPU/model weights",
    )
    parser.add_argument(
        "--no-chroma",
        action="store_true",
        help="Disable ChromaDB vector storage",
    )

    args = parser.parse_args()

    config = get_config()
    config.model.model_id = args.model
    config.model.device = args.device

    if args.output_dir:
        out_path = Path(args.output_dir)
        config.memory.persist_directory = out_path / "chroma"
        config.memory.interactions_log = out_path / "interactions.jsonl"

    extractor = HiddenStateExtractor(
        config=config.model,
        mock_mode=args.mock_llm,
    )
    sandbox = SandboxExecutor(config=config.sandbox)
    evaluator = EnergyEvaluator()
    harvester = Harvester(
        config=config.memory,
        enable_chroma=not args.no_chroma,
    )

    loop = AgentLoop(
        extractor=extractor,
        sandbox=sandbox,
        evaluator=evaluator,
        harvester=harvester,
        config=config,
        max_retries=args.max_retries,
    )

    if args.single_task:
        summary = loop.run(task=args.single_task, max_retries=args.max_retries)
        print(f"\nFinal Energy: {summary.final_energy:.1f} ({summary.final_category})")
        print(f"Iterations: {summary.iterations}")
        print(f"Converged: {summary.converged}")
        return 0 if summary.converged else 1

    tasks_path = Path(args.tasks)
    tasks = load_tasks(tasks_path)
    if not tasks:
        logger.error("No tasks found in %s", tasks_path)
        return 1

    _, rate = run_benchmark(loop, tasks, max_retries=args.max_retries)

    # Success criteria from Phase 1 Definition of Done: >= 70% convergence
    if rate >= 70.0:
        logger.info("Phase 1 benchmark PASSED with convergence rate: %.1f%%", rate)
        return 0
    else:
        logger.warning("Phase 1 benchmark FAILED (%.1f%% < 70.0%%)", rate)
        return 1


if __name__ == "__main__":
    sys.exit(main())
