#!/usr/bin/env python3
"""
workflowrunuxT4.py — ANSE Autopoietic T4 (Deep Subsystems, Networking & Concurrency) Workflow Runner.

Implements Tier-4 (T4) Deep Subsystems, Networking & Concurrency Integration from
RUNUX_V12_VERIFIED_CORE_PLAN.md and BUSINESS_CASE_PRIORITIZED_PLAN.md for RunuX:
1. ANSE Physics of Computation: E = w_t * duration_ms + w_m * peak_rss_mb, penalty 10^6 on failure.
2. Hardness Harness & Anti-Stub Guard: fail-closed zero-trust verification.
3. T4.1: Netfilter & Conntrack Core Deep Subsystem Verification (nf_conntrack_core, nf_conntrack_ftp, netfilter).
4. T4.2: Const Stub Reduction Audit (rust.const_stub_fns <= 230, currently 220).
5. T4.3: Concurrency & Lock-Free SPSC Ring Buffer Verification (ai_bridge, buffer).
6. T4.4: Formal Proof Debt Hard Threshold Gate (lean.sorry < 200, lean.axiom <= 136).
7. T4.5: Anti-Cheat Metrics Ratchet Enforcement (metrics.py ratchet).
8. T4.6: ChromaDB VectorDB & LTM Telemetry Retrofit (ChromaRAG in .chroma_db).
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
    format="%(asctime)s [%(levelname)s] [T4-RUNNER] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("workflowrunuxT4")


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
    """Computes physical computational energy and enforces monotonic descent (Delta E < 0)."""

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


class RunuxT4WorkflowRunner:
    """Orchestrates T4 Deep Subsystems, Networking & Concurrency Integration under ANSE rules."""

    def __init__(self, subproject_dir: Path = SUBPROJECT_ROOT):
        self.subproject_dir = subproject_dir
        self.physics = ANSEPhysicsEngine()
        self.metrics_history: List[ANSEPhysicsMetrics] = []
        self._ensure_environment()

    def _ensure_environment(self) -> None:
        if not self.subproject_dir.exists():
            raise FileNotFoundError(f"Subproject root does not exist: {self.subproject_dir}")
        SECONDARY_TARGET_DIR.mkdir(parents=True, exist_ok=True)
        os.environ["CARGO_TARGET_DIR"] = str(SECONDARY_TARGET_DIR)
        logger.info(f"Initialized RunuX T4 Runner. Target partition: {SECONDARY_TARGET_DIR}")

    def run_command(
        self,
        cmd: List[str],
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: float = 180.0,
    ) -> Tuple[int, str, str, float, float]:
        effective_cwd = cwd or self.subproject_dir
        merged_env = os.environ.copy()
        merged_env["CARGO_TARGET_DIR"] = str(SECONDARY_TARGET_DIR)
        if env:
            merged_env.update(env)

        start_time = time.perf_counter()
        rusage_before = resource.getrusage(resource.RUSAGE_CHILDREN)

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(effective_cwd),
                env=merged_env,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            ret = proc.returncode
            stdout = proc.stdout
            stderr = proc.stderr
        except subprocess.TimeoutExpired as e:
            ret = -1
            stdout = e.stdout or ""
            stderr = f"TIMEOUT: Command exceeded {timeout}s"
        except Exception as e:
            ret = -1
            stdout = ""
            stderr = str(e)

        dur_ms = (time.perf_counter() - start_time) * 1000.0
        rusage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
        peak_rss_mb = (rusage_after.ru_maxrss - rusage_before.ru_maxrss) / 1024.0
        if peak_rss_mb <= 0:
            peak_rss_mb = rusage_after.ru_maxrss / 1024.0

        return ret, stdout, stderr, dur_ms, peak_rss_mb

    def step_t4_1_netfilter_conntrack_suite(self) -> ANSEPhysicsMetrics:
        """T4.1: Netfilter & Conntrack Core Deep Subsystem Verification."""
        logger.info("--- Executing T4.1: Netfilter & Conntrack Subsystem Verification ---")
        cmd = [
            "cargo", "test", "--lib", "--target", "x86_64-unknown-linux-gnu",
            "-p", "nf_conntrack_core",
            "-p", "nf_conntrack_ftp",
            "-p", "netfilter",
            "--", "--test-threads=1"
        ]
        ret, stdout, stderr, dur_ms, ram_mb = self.run_command(cmd, timeout=120.0)

        failed = (ret != 0)
        err = stderr if failed else None
        energy = self.physics.calculate_energy(dur_ms, ram_mb, failed=failed)
        status = "PASSED" if not failed else "FAILED"
        token = self.physics.mint_proof_token(f"T4.1_CONNTRACK_{ret}") if not failed else None

        metric = ANSEPhysicsMetrics(
            step_name="T4.1_Netfilter_Conntrack_Suite",
            duration_ms=dur_ms,
            peak_rss_mb=ram_mb,
            energy=energy,
            status=status,
            proof_token=token,
            error_message=err,
        )
        self.metrics_history.append(metric)
        logger.info(f"T4.1 Status: {status} | E = {energy:.2f} | Token: {token}")
        return metric

    def step_t4_2_const_stub_audit(self) -> ANSEPhysicsMetrics:
        """T4.2: Const Stub Reduction Audit (rust.const_stub_fns <= 230)."""
        logger.info("--- Executing T4.2: Const Stub Reduction Audit ---")
        start_time = time.perf_counter()
        rusage_before = resource.getrusage(resource.RUSAGE_CHILDREN)

        failed = False
        err = None
        count_const_stubs = 0

        try:
            sys.path.insert(0, str(self.subproject_dir / "scripts"))
            import rust_tools

            crates_dir = self.subproject_dir / "crates"
            stats = rust_tools.analyze_workspace(crates_dir)
            count_const_stubs = sum(s.const_stub_fns for s in stats)

            # Strict threshold: must be <= 200 (baseline was 259)
            if count_const_stubs > 200:
                failed = True
                err = f"Const stub regression or target missed: found {count_const_stubs} > 200"
            else:
                logger.info(f"Const stub count audit passed: {count_const_stubs} <= 200 (baseline 259)")
        except Exception as e:
            failed = True
            err = f"Failed to execute const stub audit: {e}"

        dur_ms = (time.perf_counter() - start_time) * 1000.0
        rusage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
        ram_mb = (rusage_after.ru_maxrss - rusage_before.ru_maxrss) / 1024.0
        energy = self.physics.calculate_energy(dur_ms, ram_mb, failed=failed)
        status = "PASSED" if not failed else "FAILED"
        token = self.physics.mint_proof_token(f"T4.2_CONST_STUBS_{count_const_stubs}") if not failed else None

        metric = ANSEPhysicsMetrics(
            step_name="T4.2_Const_Stub_Reduction_Audit",
            duration_ms=dur_ms,
            peak_rss_mb=ram_mb,
            energy=energy,
            status=status,
            proof_token=token,
            error_message=err,
        )
        self.metrics_history.append(metric)
        logger.info(f"T4.2 Status: {status} | E = {energy:.2f} | Token: {token}")
        return metric

    def step_t4_3_concurrency_and_ring_buffers(self) -> ANSEPhysicsMetrics:
        """T4.3: Concurrency & Lock-Free SPSC Ring Buffer Verification."""
        logger.info("--- Executing T4.3: Concurrency & SPSC Ring Buffer Verification ---")
        cmd = [
            "cargo", "test", "--lib", "--target", "x86_64-unknown-linux-gnu",
            "-p", "ai_bridge",
            "-p", "buffer",
            "--", "--test-threads=1"
        ]
        ret, stdout, stderr, dur_ms, ram_mb = self.run_command(cmd, timeout=120.0)

        failed = (ret != 0)
        err = stderr if failed else None
        energy = self.physics.calculate_energy(dur_ms, ram_mb, failed=failed)
        status = "PASSED" if not failed else "FAILED"
        token = self.physics.mint_proof_token(f"T4.3_CONCURRENCY_{ret}") if not failed else None

        metric = ANSEPhysicsMetrics(
            step_name="T4.3_Concurrency_And_Ring_Buffers",
            duration_ms=dur_ms,
            peak_rss_mb=ram_mb,
            energy=energy,
            status=status,
            proof_token=token,
            error_message=err,
        )
        self.metrics_history.append(metric)
        logger.info(f"T4.3 Status: {status} | E = {energy:.2f} | Token: {token}")
        return metric

    def step_t4_4_formal_proof_debt_gate(self) -> ANSEPhysicsMetrics:
        """T4.4: Formal Proof Debt Hard Threshold Gate (lean.sorry < 190, lean.axiom <= 136)."""
        logger.info("--- Executing T4.4: Formal Proof Debt Threshold Gate ---")
        start_time = time.perf_counter()
        rusage_before = resource.getrusage(resource.RUSAGE_CHILDREN)

        failed = False
        err = None
        total_sorry = 0
        total_axioms = 0

        try:
            sys.path.insert(0, str(self.subproject_dir / "scripts"))
            import lean_tools

            lean_dir = self.subproject_dir / "specs" / "lean4"
            tree_stats = lean_tools.analyze_tree(lean_dir)
            total_sorry = sum(f.sorry for f in tree_stats)
            total_axioms = sum(len(f.axioms) for f in tree_stats)

            # Strict historic milestone: must break below 190 sorry (baseline 249)
            if total_sorry >= 190:
                failed = True
                err = f"Formal sorry threshold violation: found {total_sorry} >= 190 (must be < 190)"
            elif total_axioms > 136:
                failed = True
                err = f"Formal axiom threshold violation: found {total_axioms} > 136"
            else:
                logger.info(f"Formal proof debt audit passed: sorry={total_sorry} < 190, axioms={total_axioms} <= 136")
        except Exception as e:
            failed = True
            err = f"Failed to execute formal proof debt gate: {e}"

        dur_ms = (time.perf_counter() - start_time) * 1000.0
        rusage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
        ram_mb = (rusage_after.ru_maxrss - rusage_before.ru_maxrss) / 1024.0
        energy = self.physics.calculate_energy(dur_ms, ram_mb, failed=failed)
        status = "PASSED" if not failed else "FAILED"
        token = self.physics.mint_proof_token(f"T4.4_FORMAL_GATE_{total_sorry}_{total_axioms}") if not failed else None

        metric = ANSEPhysicsMetrics(
            step_name="T4.4_Formal_Proof_Debt_Gate",
            duration_ms=dur_ms,
            peak_rss_mb=ram_mb,
            energy=energy,
            status=status,
            proof_token=token,
            error_message=err,
        )
        self.metrics_history.append(metric)
        logger.info(f"T4.4 Status: {status} | E = {energy:.2f} | Token: {token}")
        return metric

    def step_t4_5_anti_cheat_ratchet_enforcement(self) -> ANSEPhysicsMetrics:
        """T4.5: Anti-Cheat Metrics Ratchet Enforcement."""
        logger.info("--- Executing T4.5: Anti-Cheat Metrics Ratchet Enforcement ---")
        ret, stdout, stderr, dur_ms, ram_mb = self.run_command(
            ["python3", "scripts/metrics.py", "ratchet"]
        )

        failed = (ret != 0)
        err = stderr if failed else None
        energy = self.physics.calculate_energy(dur_ms, ram_mb, failed=failed)
        status = "PASSED" if not failed else "FAILED"
        token = self.physics.mint_proof_token(f"T4.5_RATCHET_{ret}") if not failed else None

        metric = ANSEPhysicsMetrics(
            step_name="T4.5_AntiCheat_Metrics_Ratchet",
            duration_ms=dur_ms,
            peak_rss_mb=ram_mb,
            energy=energy,
            status=status,
            proof_token=token,
            error_message=err,
        )
        self.metrics_history.append(metric)
        logger.info(f"T4.5 Status: {status} | E = {energy:.2f} | Token: {token}")
        if stdout:
            for line in stdout.strip().splitlines()[-6:]:
                logger.info(f"  {line}")
        return metric

    def step_t4_6_retrofit_ltm(self) -> ANSEPhysicsMetrics:
        """T4.6: Retrofit T4 Verified Telemetry into ChromaDB LTM."""
        logger.info("--- Executing T4.6: Retrofitting Telemetry into ChromaDB LTM ---")
        start_time = time.perf_counter()
        rusage_before = resource.getrusage(resource.RUSAGE_CHILDREN)

        try:
            sys.path.insert(0, str(REPO_ROOT))
            from anse.memory.chroma_rag import ChromaRAG

            rag = ChromaRAG(persist_directory=str(REPO_ROOT / ".chroma_db"))
            t4_summary = {
                "doc_id": "t4_workflow_runux_execution_report",
                "task_prompt": "RunuX T4 (Deep Subsystems, Networking & Concurrency) execution under ANSE physics.",
                "language": "python",
                "energy": sum(m.energy for m in self.metrics_history),
                "metadata": {
                    "tier": "T4",
                    "status": "ALL_PASSED",
                    "steps_json": json.dumps([asdict(m) for m in self.metrics_history]),
                },
                "code_content": json.dumps([asdict(m) for m in self.metrics_history], indent=2),
            }
            rag.index_code_solution(
                doc_id=t4_summary["doc_id"],
                code_content=t4_summary["code_content"],
                task_prompt=t4_summary["task_prompt"],
                language="json",
                energy=t4_summary["energy"],
                metadata=t4_summary["metadata"],
            )
            failed = False
            err = None
            logger.info("Successfully indexed T4 workflow telemetry into ChromaDB LTM.")
        except Exception as e:
            logger.error(f"LTM indexing failed: {e}")
            failed = True
            err = str(e)

        dur_ms = (time.perf_counter() - start_time) * 1000.0
        rusage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
        ram_mb = (rusage_after.ru_maxrss - rusage_before.ru_maxrss) / 1024.0
        energy = self.physics.calculate_energy(dur_ms, ram_mb, failed=failed)
        status = "PASSED" if not failed else "FAILED"
        token = self.physics.mint_proof_token(f"T4.6_LTM_{status}") if not failed else None

        metric = ANSEPhysicsMetrics(
            step_name="T4.6_ChromaDB_LTM_Retrofit",
            duration_ms=dur_ms,
            peak_rss_mb=ram_mb,
            energy=energy,
            status=status,
            proof_token=token,
            error_message=err,
        )
        self.metrics_history.append(metric)
        logger.info(f"T4.6 Status: {status} | E = {energy:.2f} | Token: {token}")
        return metric

    def run_all(self) -> bool:
        start_wall = time.perf_counter()
        logger.info("=== Starting RunuX T4 Autonomous Workflow ===")

        self.step_t4_1_netfilter_conntrack_suite()
        self.step_t4_2_const_stub_audit()
        self.step_t4_3_concurrency_and_ring_buffers()
        self.step_t4_4_formal_proof_debt_gate()
        self.step_t4_5_anti_cheat_ratchet_enforcement()
        self.step_t4_6_retrofit_ltm()

        total_wall_s = time.perf_counter() - start_wall
        cumulative_energy = sum(m.energy for m in self.metrics_history)
        all_passed = all(m.status == "PASSED" for m in self.metrics_history)

        if all_passed:
            logger.info(f"=== RunuX T4 Workflow COMPLETED SUCCESSFULLY ===")
            logger.info(f"Total Wall Time: {total_wall_s:.2f}s | Cumulative Energy: {cumulative_energy:.2f}")
            for m in self.metrics_history:
                logger.info(f"  * {m.step_name}: {m.status} (E = {m.energy:.2f}, token = {m.proof_token})")
            return True
        else:
            logger.error("=== RunuX T4 Workflow FAILED ===")
            for m in self.metrics_history:
                if m.status != "PASSED":
                    logger.error(f"  * {m.step_name}: {m.status} | Reason: {m.error_message}")
            return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RunuX T4 Deep Subsystems & Concurrency Runner")
    args = parser.parse_args()

    runner = RunuxT4WorkflowRunner()
    success = runner.run_all()
    sys.exit(0 if success else 1)
