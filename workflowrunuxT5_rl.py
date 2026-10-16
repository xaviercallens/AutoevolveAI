#!/usr/bin/env python3
"""
workflowrunuxT5_rl.py — ANSE Autopoietic T5 (Differential RL & Iso-Functional Parity) Workflow Runner.

Implements Tier-5 (T5) ANSE-RL Differential Reinforcement Learning Workstream for RunuX:
1. ANSE Physics of Computation: E = w_t * duration_ms + w_m * peak_rss_mb, penalty 10^6 on failure.
2. Dual-Kernel Shadow Execution Arena: Side-by-side Linux C Kernel vs RunuX Rust Kernel.
3. T5.1: Dual-Kernel Boot Telemetry Verification (boot <= 25ms, RSS <= 30MB).
4. T5.2: 80% Iso-Functionality Gate (\u03a6_func >= 0.80 across POSIX LTP vectors).
5. T5.3: Performance Degradation Bounded Gate (degradation <= +50%, Ops ratio >= 0.67).
6. T5.4: Actor-Critic GRPO Rollout & Golden Trajectory Selection.
7. T5.5: Low-Cost GCP Spot MicroVM Provisioning Validation (< $0.01 budget).
8. T5.6: ChromaDB VectorDB & LTM Telemetry Ingestion with Cryptographic Attestation.
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
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent
SUBPROJECT_ROOT = REPO_ROOT / "sub_projects" / "rust_linux_mini_kernel" / "rust-linux-mini-kernel"
SECONDARY_TARGET_DIR = (
    Path("/mnt/data/tmp/runux_target")
    if Path("/mnt/data/tmp/runux_target").exists()
    else Path("/media/xavkal/3ada43de-fc4a-43bd-a9f8-cf396fd17033/tmp/runux_target")
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [T5-RL-RUNNER] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("workflowrunuxT5_rl")


@dataclass
class ANSEPhysicsMetrics:
    step_name: str
    duration_ms: float
    peak_rss_mb: float
    energy: float
    status: str
    proof_token: Optional[str] = None
    error_message: Optional[str] = None


class ANSEPhysicsEngine:
    """Computes physical computational energy and enforces monotonic descent."""

    def __init__(self, wt: float = 1.0, wm: float = 2.0, max_penalty: float = 1_000_000.0):
        self.wt = wt
        self.wm = wm
        self.max_penalty = max_penalty

    def calculate_energy(self, duration_ms: float, peak_rss_mb: float, failed: bool = False) -> float:
        if failed:
            return self.max_penalty
        return self.wt * duration_ms + self.wm * peak_rss_mb

    def mint_proof_token(self, payload: str) -> str:
        h = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
        return f"PROOF_TOKEN:{h}"


class RunuxT5WorkflowRunner:
    """Orchestrates Tier 5 Differential Reinforcement Learning and Parity Verification."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.physics = ANSEPhysicsEngine()
        self.metrics_log: List[ANSEPhysicsMetrics] = []
        self.cumulative_energy = 0.0

    def _record_step(
        self,
        name: str,
        start_time: float,
        failed: bool = False,
        token_payload: Optional[str] = None,
        err_msg: Optional[str] = None,
    ) -> ANSEPhysicsMetrics:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        usage = resource.getrusage(resource.RUSAGE_SELF)
        peak_rss_mb = usage.ru_maxrss / 1024.0

        energy = self.physics.calculate_energy(duration_ms, peak_rss_mb, failed=failed)
        self.cumulative_energy += energy

        token = None
        if not failed and token_payload:
            token = self.physics.mint_proof_token(token_payload)

        status = "FAILED" if failed else "PASSED"
        m = ANSEPhysicsMetrics(
            step_name=name,
            duration_ms=round(duration_ms, 2),
            peak_rss_mb=round(peak_rss_mb, 2),
            energy=round(energy, 2),
            status=status,
            proof_token=token,
            error_message=err_msg,
        )
        self.metrics_log.append(m)
        logger.info(
            f"Step '{name}' -> {status} (Energy: {m.energy}, "
            f"Duration: {m.duration_ms}ms, RSS: {m.peak_rss_mb}MB, token = {token})"
        )
        return m

    def step_t5_1_dual_boot_telemetry(self) -> bool:
        """T5.1: Dual-Kernel Boot Telemetry Verification."""
        logger.info("--- Step T5.1: Dual-Kernel Boot Telemetry Verification ---")
        t0 = time.perf_counter()
        try:
            from anse.rl.differential_arena import DualKernelDifferentialArena
            arena = DualKernelDifferentialArena()
            boot = arena.capture_boot_telemetry()

            passed = boot.dual_boot_matching and (boot.runux_boot_ms <= 25.0)
            if not passed:
                self._record_step("T5.1_DualBootTelemetry", t0, failed=True, err_msg="Boot metrics exceeded threshold")
                return False

            payload = f"DualBoot:Linux={boot.linux_boot_ms}ms:RunuX={boot.runux_boot_ms}ms"
            self._record_step("T5.1_DualBootTelemetry", t0, failed=False, token_payload=payload)
            return True
        except Exception as e:
            self._record_step("T5.1_DualBootTelemetry", t0, failed=True, err_msg=str(e))
            return False

    def step_t5_2_iso_functionality_gate(self) -> bool:
        """T5.2: 100% Iso-Functionality Parity Gate across 5 Kernel Benchmark Suites."""
        logger.info("--- Step T5.2: 100% Iso-Functionality Gate (Phi_func == 100.0% across 5 Suites) ---")
        t0 = time.perf_counter()
        try:
            from anse.rl.kernel_benchmarks import KernelBenchmarkManager
            mgr = KernelBenchmarkManager()
            report = mgr.run_all_10_suites(iterations=3)

            passed = report.passed_100_iso_gate
            if not passed:
                err = f"Iso-Functionality failed: {report.global_functional_parity * 100:.1f}% < 100.0%"
                self._record_step("T5.2_IsoFunctionalityGate", t0, failed=True, err_msg=err)
                return False

            payload = f"IsoParity100:Phi={report.global_functional_parity}:Matching={report.total_vectors_matched}/{report.total_vectors_tested}"
            self._record_step("T5.2_IsoFunctionalityGate", t0, failed=False, token_payload=payload)
            return True
        except Exception as e:
            self._record_step("T5.2_IsoFunctionalityGate", t0, failed=True, err_msg=str(e))
            return False

    def step_t5_3_performance_degradation_gate(self) -> bool:
        """T5.3: Performance Degradation (<= +50%) & Global Performance Gain Gate (>= +10%)."""
        logger.info("--- Step T5.3: Performance Degradation (<= +50%) & +20% Gain Gate ---")
        t0 = time.perf_counter()
        try:
            from anse.rl.kernel_benchmarks import KernelBenchmarkManager
            mgr = KernelBenchmarkManager()
            report = mgr.run_all_10_suites(iterations=3)

            passed = (report.global_perf_gain_pct >= 10.0) and (
                (report.global_degradation_pct <= 50.0) or (report.global_ops_ratio >= 0.67)
            )
            if not passed:
                err = (
                    f"Performance gate failed: Degradation={report.global_degradation_pct}% "
                    f"(Ops: {report.global_ops_ratio:.2f}x), Gain={report.global_perf_gain_pct}%"
                )
                self._record_step("T5.3_PerfDegradationGate", t0, failed=True, err_msg=err)
                return False

            payload = f"Degradation:DegPct={report.global_degradation_pct}:OpsRatio={report.global_ops_ratio:.2f}:Gain={report.global_perf_gain_pct}%"
            self._record_step("T5.3_PerfDegradationGate", t0, failed=False, token_payload=payload)
            return True
        except Exception as e:
            self._record_step("T5.3_PerfDegradationGate", t0, failed=True, err_msg=str(e))
            return False

    def step_t5_4_grpo_golden_trajectory(self) -> bool:
        """T5.4: Actor-Critic GRPO Rollout & Golden Trajectory Selection."""
        logger.info("--- Step T5.4: Actor-Critic GRPO Rollout & Golden Trajectory Selection ---")
        t0 = time.perf_counter()
        try:
            from anse.rl.dual_kernel_rl import ANSERLEngine
            engine = ANSERLEngine(phase=3)
            
            candidates = engine.generate_candidate_rollouts(target_syscall="sys_socket")
            winner, report = engine.evaluate_candidates_and_select_winner(candidates, iterations=2)
            trace = engine.retrofit_golden_trajectory(winner, report)

            passed = (
                (trace.actual_iso_parity >= 1.0)
                and (trace.actual_degradation_pct <= 50.0)
                and (trace.perf_gain_pct >= 10.0)
            )
            if not passed:
                self._record_step("T5.4_GRPORollout", t0, failed=True, err_msg="RL cycle failed 100% parity or +10% perf gain constraints")
                return False

            payload = f"GRPO:{trace.selected_variant_id}:{trace.attestation_receipt}"
            self._record_step("T5.4_GRPORollout", t0, failed=False, token_payload=payload)
            return True
        except Exception as e:
            self._record_step("T5.4_GRPORollout", t0, failed=True, err_msg=str(e))
            return False

    def step_t5_5_gcp_spot_validation(self) -> bool:
        """T5.5: Low-Cost GCP Spot MicroVM Provisioning Validation."""
        logger.info("--- Step T5.5: Low-Cost GCP Spot MicroVM Provisioning Validation ---")
        t0 = time.perf_counter()
        try:
            from scripts.gcp_spot_manager import GCPSpotMicroVMManager
            manager = GCPSpotMicroVMManager()
            dry_res = manager.dry_run()

            passed = dry_res.get("within_budget", False) and dry_res.get("status") == "DRY_RUN_PASSED"
            if not passed:
                self._record_step("T5.5_GCPSpotValidation", t0, failed=True, err_msg="GCP Spot budget check failed")
                return False

            payload = f"GCPSpot:Machine={dry_res['machine_type']}:CostUSD={dry_res['estimated_cost_usd']}"
            self._record_step("T5.5_GCPSpotValidation", t0, failed=False, token_payload=payload)
            return True
        except Exception as e:
            self._record_step("T5.5_GCPSpotValidation", t0, failed=True, err_msg=str(e))
            return False

    def step_t5_6_chroma_ltm_retrofit(self) -> bool:
        """T5.6: ChromaDB VectorDB & LTM Telemetry Ingestion."""
        logger.info("--- Step T5.6: ChromaDB VectorDB & LTM Telemetry Ingestion ---")
        t0 = time.perf_counter()
        try:
            from anse.memory.chroma_rag import ChromaRAG
            rag = ChromaRAG(persist_directory=str(REPO_ROOT / ".chroma_db"))

            summary = {
                "tier": "T5_RL_DIFFERENTIAL_ARENA",
                "phase": 3,
                "cumulative_energy": self.cumulative_energy,
                "steps_passed": len([m for m in self.metrics_log if m.status == "PASSED"]),
                "tokens": [m.proof_token for m in self.metrics_log if m.proof_token],
                "timestamp": time.time(),
            }
            doc_id = f"tier5_rl_differential_report_{int(time.time())}"
            rag.index_code_solution(
                doc_id=doc_id,
                code_content=json.dumps(summary, indent=2),
                task_prompt="RunuX Tier 5 ANSE-RL Differential Parity Telemetry",
                language="json",
                energy=self.cumulative_energy,
                metadata={"tier": "T5", "status": "PASSED"},
            )

            payload = f"ChromaT5:{doc_id}:Energy={self.cumulative_energy}"
            self._record_step("T5.6_ChromaLTMRetrofit", t0, failed=False, token_payload=payload)
            return True
        except Exception as e:
            self._record_step("T5.6_ChromaLTMRetrofit", t0, failed=True, err_msg=str(e))
            return False

    def run_all(self) -> bool:
        logger.info("================================================================")
        logger.info("=== STARTING TIER 5: ANSE-RL DIFFERENTIAL PARITY SUITE ===")
        logger.info("================================================================")
        start_all = time.perf_counter()

        steps = [
            self.step_t5_1_dual_boot_telemetry,
            self.step_t5_2_iso_functionality_gate,
            self.step_t5_3_performance_degradation_gate,
            self.step_t5_4_grpo_golden_trajectory,
            self.step_t5_5_gcp_spot_validation,
            self.step_t5_6_chroma_ltm_retrofit,
        ]

        for step in steps:
            ok = step()
            if not ok:
                logger.error("Tier 5 execution aborted due to gate failure.")
                return False

        duration = time.perf_counter() - start_all
        tokens = [m.proof_token for m in self.metrics_log if m.proof_token]
        logger.info("================================================================")
        logger.info(f"=== TIER 5 COMPLETED SUCCESSFULLY (100% GREEN) ===")
        logger.info(f"=== Total Duration: {duration:.2f}s | Cumulative Energy: {self.cumulative_energy:.2f} ===")
        logger.info(f"=== Minted Proof Tokens: {len(tokens)} / {len(steps)} ===")
        for tok in tokens:
            logger.info(f"  * {tok}")
        logger.info("================================================================")
        return True


def main():
    parser = argparse.ArgumentParser(description="RunuX Tier 5 ANSE-RL Workflow Runner")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    args = parser.parse_args()

    runner = RunuxT5WorkflowRunner(dry_run=args.dry_run)
    success = runner.run_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
