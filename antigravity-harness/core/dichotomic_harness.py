"""
CLI and execution harness for Dichotomic Task Decomposition.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Optional

from anse.orchestration.dichotomic_decomposer import (
    DichotomyEngine,
    DichotomicTaskNode,
    TaskStatus,
)


def run_dichotomy_cli(
    goal: str,
    total_budget: int = 16000,
    max_depth: int = 2,
    output_json: Optional[Path] = None,
    execute: bool = False,
) -> int:
    """
    Decomposes a goal into a dichotomic binary tree, outputs the Lines of Thought,
    and optionally executes and verifies every leaf task.
    """
    print("=" * 80)
    print("🌳 ANSE DICHOTOMIC TASK DECOMPOSITION & ZERO-STUB VERIFIER")
    print("=" * 80)
    print(f"Goal: {goal}")
    print(f"Total Token Budget: {total_budget} tokens | Max Depth: {max_depth}")
    print("-" * 80)

    engine = DichotomyEngine()
    root = engine.decompose(
        goal=goal,
        total_budget=total_budget,
        max_depth=max_depth,
    )

    nodes = root.get_all_nodes()
    leaves = root.get_all_leaves()
    print(f"Generated {len(nodes)} nodes ({len(leaves)} Atomic Verifiable Primitives / Leaves):")
    print()

    for n in nodes:
        indent = "  " * n.depth
        role = "🌿 [LEAF / AVP]" if n.is_leaf else "🔀 [BRANCH]"
        print(f"{indent}{role} ID: {n.task_id} (Budget: {n.token_budget} tokens)")
        print(f"{indent}   Goal: {n.goal}")
        print(f"{indent}   Axis: {n.dichotomy_axis.value}")
        print(f"{indent}   Line of Thought: {n.line_of_thought}")
        if n.is_leaf:
            print(f"{indent}   Acceptance Command: {n.acceptance_command}")
        print()

    if execute:
        print("=" * 80)
        print("⚡ EXECUTING LEAF TASKS & COMPOSING PROOFS (ZERO-STUB ENFORCEMENT)")
        print("=" * 80)

        for event_node in engine.run_pipeline(root):
            status_icon = "✅" if event_node.status == TaskStatus.VERIFIED else "❌"
            node_type = "Leaf" if event_node.is_leaf else "Synthesized Parent"
            print(f"{status_icon} [{node_type}] {event_node.task_id}: {event_node.status.value}")
            if event_node.proof_token:
                print(f"   Proof Token: {event_node.proof_token[:16]}... (Energy: {event_node.energy_score:.4f})")
            if event_node.status != TaskStatus.VERIFIED:
                print(f"   Receipt Error: {event_node.verification_receipt.get('error', 'Execution Failed')}")

    if output_json:
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(root.to_dict(), indent=2), encoding="utf-8")
        print(f"\n💾 Saved full dichotomic tree to {output_json}")

    return 0 if root.status == TaskStatus.VERIFIED or not execute else 1
