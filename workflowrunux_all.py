#!/usr/bin/env python3
"""
workflowrunux_all.py — ANSE Master Multi-Tier Workflow Orchestrator for RunuX.

Orchestrates all verified RunuX Tiers (T1, T2, T3, T4) under ANSE Thermodynamic Physics:
- Tier 1: Bulk Hardening & Ground Truth Verification (workflowrunuxT1.py)
- Tier 2: Design, Research & Architecture Verification (workflowrunuxT2.py)
- Tier 3: Formal Proof Discharge & Axiom Soundness Verification (workflowrunuxT3.py)
- Tier 4: Deep Subsystems, Networking & Concurrency Integration (workflowrunuxT4.py)
- Tier 5: ANSE-RL Differential Shadow Execution & Parity Gate (workflowrunuxT5_rl.py)

Enforces:
1. Physical Energy Minimization: E = w_t * duration_ms + w_m * peak_rss_mb (Penalty 10^6 on failure).
2. Monotonic Ratchet Descent: Zero regressions allowed across any metric.
3. Anti-Cheat & Anti-Stub AST Invariance: Zero-trust attestation with proof tokens.
4. ChromaDB LTM Unified Telemetry Retrofitting.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import resource
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup root paths
REPO_ROOT = Path(__file__).resolve().parent
SUBPROJECT_ROOT = REPO_ROOT / "sub_projects" / "rust_linux_mini_kernel" / "rust-linux-mini-kernel"
SECONDARY_TARGET_DIR = (
    Path("/mnt/data/tmp/runux_target")
    if Path("/mnt/data/tmp/runux_target").exists()
    else Path("/media/xavkal/3ada43de-fc4a-43bd-a9f8-cf396fd17033/tmp/runux_target")
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [MASTER-TIER] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("workflowrunux_all")


@dataclass
class TierExecutionResult:
    tier: str
    status: str
    wall_time_s: float
    total_energy: float
    steps_count: int
    proof_tokens: List[str]
    error_message: Optional[str] = None


class RunuxMasterTierOrchestrator:
    """Coordinates execution across all RunuX Tiers under ANSE thermodynamic laws."""

    def __init__(self, tiers: Optional[List[str]] = None):
        self.tiers_to_run = tiers or ["T1", "T2", "T3", "T4", "T5"]
        self.results: List[TierExecutionResult] = []
        SECONDARY_TARGET_DIR.mkdir(parents=True, exist_ok=True)
        os.environ["CARGO_TARGET_DIR"] = str(SECONDARY_TARGET_DIR)

    def run_tier_script(self, script_name: str, tier_name: str) -> TierExecutionResult:
        logger.info(f"============================================================")
        logger.info(f"=== LAUNCHING TIER {tier_name}: {script_name} ===")
        logger.info(f"============================================================")

        script_path = REPO_ROOT / script_name
        if not script_path.exists():
            return TierExecutionResult(
                tier=tier_name,
                status="FAILED",
                wall_time_s=0.0,
                total_energy=1_000_000.0,
                steps_count=0,
                proof_tokens=[],
                error_message=f"Script not found: {script_path}",
            )

        start_time = time.perf_counter()
        proc = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        duration_s = time.perf_counter() - start_time

        # Print script output for user visibility
        if proc.stdout:
            for line in proc.stdout.strip().splitlines():
                logger.info(f"[{tier_name}] {line}")
        if proc.stderr:
            for line in proc.stderr.strip().splitlines():
                logger.warning(f"[{tier_name}-ERR] {line}")

        passed = (proc.returncode == 0)
        status = "PASSED" if passed else "FAILED"
        err = proc.stderr.strip() if not passed else None

        # Parse output for energy and proof tokens
        tokens = []
        total_energy = 0.0
        steps = 0
        combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
        for line in combined.splitlines():
            if "token = PROOF_TOKEN:" in line:
                part = line.split("token = ")[1].strip().rstrip(")")
                tokens.append(part)
                steps += 1
            if "Cumulative Energy:" in line:
                try:
                    total_energy = float(line.split("Cumulative Energy:")[1].strip().split()[0])
                except Exception:
                    pass

        if not passed and total_energy == 0.0:
            total_energy = 1_000_000.0

        res = TierExecutionResult(
            tier=tier_name,
            status=status,
            wall_time_s=duration_s,
            total_energy=total_energy,
            steps_count=steps,
            proof_tokens=tokens,
            error_message=err,
        )
        self.results.append(res)
        return res

    def retrofit_master_telemetry(self) -> None:
        """Retrofits unified multi-tier execution telemetry into ChromaDB LTM."""
        logger.info("--- Retrofitting Unified Master Multi-Tier Telemetry into ChromaDB LTM ---")
        try:
            sys.path.insert(0, str(REPO_ROOT))
            from anse.memory.chroma_rag import ChromaRAG

            rag = ChromaRAG(persist_directory=str(REPO_ROOT / ".chroma_db"))
            total_system_energy = sum(r.total_energy for r in self.results)
            all_passed = all(r.status == "PASSED" for r in self.results)

            summary = {
                "doc_id": f"master_multi_tier_runux_report_{int(time.time())}",
                "task_prompt": "RunuX Master Multi-Tier (T1, T2, T3, T4, T5) Full Execution & Hardening Suite.",
                "language": "python",
                "energy": total_system_energy,
                "metadata": {
                    "tiers_executed": ",".join(self.tiers_to_run),
                    "status": "ALL_PASSED" if all_passed else "FAILED",
                    "total_system_energy": total_system_energy,
                    "results_json": json.dumps([asdict(r) for r in self.results]),
                },
                "code_content": json.dumps([asdict(r) for r in self.results], indent=2),
            }
            rag.index_code_solution(
                doc_id=summary["doc_id"],
                code_content=summary["code_content"],
                task_prompt=summary["task_prompt"],
                language="json",
                energy=summary["energy"],
                metadata=summary["metadata"],
            )
            logger.info("Successfully indexed Master Multi-Tier Telemetry into ChromaDB LTM.")
        except Exception as e:
            logger.error(f"Failed to retrofit master telemetry: {e}")

    def run_all(self) -> bool:
        start_master = time.perf_counter()
        logger.info("================================================================")
        logger.info("=== STARTING RUNUX MASTER MULTI-TIER EXECUTION PIPELINE      ===")
        logger.info(f"=== Active Tiers: {', '.join(self.tiers_to_run)}                         ===")
        logger.info("================================================================")

        tier_script_map = {
            "T1": "workflowrunuxT1.py",
            "T2": "workflowrunuxT2.py",
            "T3": "workflowrunuxT3.py",
            "T4": "workflowrunuxT4.py",
            "T5": "workflowrunuxT5_rl.py",
        }

        all_success = True
        for tier in self.tiers_to_run:
            script = tier_script_map.get(tier)
            if not script:
                logger.error(f"Unknown tier: {tier}")
                all_success = False
                continue
            res = self.run_tier_script(script, tier)
            if res.status != "PASSED":
                all_success = False

        total_master_time = time.perf_counter() - start_master
        total_energy = sum(r.total_energy for r in self.results)

        self.retrofit_master_telemetry()

        logger.info("================================================================")
        if all_success:
            logger.info("=== ALL RUNUX TIERS COMPLETED SUCCESSFULLY (100% GREEN)      ===")
        else:
            logger.error("=== SOME RUNUX TIERS FAILED                                  ===")
        logger.info(f"=== Total Wall Time: {total_master_time:.2f}s | System Energy: {total_energy:.2f} ===")
        for r in self.results:
            logger.info(f"  * Tier {r.tier}: {r.status} (Energy: {r.total_energy:.2f}, Time: {r.wall_time_s:.2f}s, Tokens: {len(r.proof_tokens)})")
        logger.info("================================================================")

        return all_success


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RunuX Master Multi-Tier Workflow Orchestrator")
    parser.add_argument("--tiers", nargs="+", choices=["T1", "T2", "T3", "T4", "T5"], help="Specific tiers to run")
    args = parser.parse_args()

    orchestrator = RunuxMasterTierOrchestrator(tiers=args.tiers)
    success = orchestrator.run_all()
    sys.exit(0 if success else 1)
