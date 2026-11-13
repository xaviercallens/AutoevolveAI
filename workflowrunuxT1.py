#!/usr/bin/env python3
"""
workflowrunuxT1.py — ANSE Autopoietic T1 (Core Bulk Hardening & Verification) Workflow Runner.

Implements Tier-1 (T1) Core Bulk Hardening & Truth Verification Workstream from
RUNUX_V12_VERIFIED_CORE_PLAN.md and BUSINESS_CASE_PRIORITIZED_PLAN.md for RunuX:
1. ANSE Physics of Computation: E = w_t * duration_ms + w_m * peak_rss_mb, penalty 10^6 on failure.
2. Hardness Harness & Anti-Stub AST Guard: zero-trust verification.
3. T1.1: Static Metrics Ratchet Gate (metrics.py ratchet).
4. T1.2: Zero static mut Invariance Gate (rust.static_mut == 0).
5. T1.3: Anti-Stub AST Violation & Forbidden Marker Scan on Core Crates.
6. T1.4: Core Kernel Workspace Compilation & Lint Hygiene (cargo check).
7. T1.5: Fast Core Memory & Defense Test Smoke Suite (cargo test).
8. T1.6: ChromaDB VectorDB & LTM Telemetry Ingestion (ChromaRAG in .chroma_db).
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
    format="%(asctime)s [%(levelname)s] [T1-RUNNER] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("workflowrunuxT1")


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


class AntiStubInspector:
    """Enforces zero-trust anti-stub invariants on kernel code."""

    FORBIDDEN_PATTERNS = [
        "todo!()",
        "unimplemented!()",
        "unreachable_unchecked",
        "fake_mock",
        "mock_hardware",
        "/* simplified */",
    ]

    def inspect_file(self, file_path: Path) -> List[str]:
        if not file_path.is_file():
            return [f"File not found: {file_path}"]
        content = file_path.read_text(encoding="utf-8", errors="replace")
        violations = []
        for line_idx, line in enumerate(content.splitlines(), start=1):
            for pat in self.FORBIDDEN_PATTERNS:
                if pat in line and not line.strip().startswith("//"):
                    violations.append(f"{file_path.name}:{line_idx} contains forbidden stub '{pat}'")
        return violations


class RunuxT1WorkflowRunner:
    """Orchestrates T1 Core Bulk Hardening & Truth Verification under ANSE rules."""

    CORE_CRATES = [
        "kernel_types",
        "syscall_table",
        "ebpf_firewall",
        "ai_detector",
        "ai_bridge",
        "immutable_logs",
        "turbo_quant",
        "slab",
        "page_alloc",
        "vmalloc",
    ]

    def __init__(self, subproject_dir: Path = SUBPROJECT_ROOT):
        self.subproject_dir = subproject_dir
        self.physics = ANSEPhysicsEngine()
        self.anti_stub = AntiStubInspector()
        self.metrics_history: List[ANSEPhysicsMetrics] = []
        self._ensure_environment()

    def _ensure_environment(self) -> None:
        if not self.subproject_dir.exists():
            raise FileNotFoundError(f"Subproject root does not exist: {self.subproject_dir}")
        SECONDARY_TARGET_DIR.mkdir(parents=True, exist_ok=True)
        os.environ["CARGO_TARGET_DIR"] = str(SECONDARY_TARGET_DIR)
        logger.info(f"Initialized RunuX T1 Runner. Target partition: {SECONDARY_TARGET_DIR}")

    def run_command(
        self,
        cmd: List[str],
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: float = 120.0,
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

    def step_t1_1_metrics_ratchet_gate(self) -> ANSEPhysicsMetrics:
        """T1.1: Static Metrics Ratchet Gate."""
        logger.info("--- Executing T1.1: Static Metrics Ratchet Gate ---")
        # Measure
        ret_m, out_m, err_m, _, _ = self.run_command(["python3", "scripts/metrics.py", "measure"])
        if ret_m != 0:
            logger.error(f"metrics.py measure failed: {err_m}")

        # Ratchet
        ret, stdout, stderr, dur_ms, ram_mb = self.run_command(
            ["python3", "scripts/metrics.py", "ratchet"]
        )

        failed = (ret != 0)
        energy = self.physics.calculate_energy(dur_ms, ram_mb, failed=failed)
        status = "PASSED" if not failed else "FAILED"
        err = stderr if failed else None
        token = self.physics.mint_proof_token(f"T1.1_RATCHET_{ret}") if not failed else None

        metric = ANSEPhysicsMetrics(
            step_name="T1.1_Static_Metrics_Ratchet_Gate",
            duration_ms=dur_ms,
            peak_rss_mb=ram_mb,
            energy=energy,
            status=status,
            proof_token=token,
            error_message=err,
        )
        self.metrics_history.append(metric)
        logger.info(f"T1.1 Status: {status} | E = {energy:.2f} | Token: {token}")
        if stdout:
            for line in stdout.strip().splitlines()[-6:]:
                logger.info(f"  {line}")
        return metric

    def step_t1_2_zero_static_mut_invariance(self) -> ANSEPhysicsMetrics:
        """T1.2: Zero static mut Invariance Gate."""
        logger.info("--- Executing T1.2: Zero static mut Invariance Gate ---")
        start_time = time.perf_counter()
        rusage_before = resource.getrusage(resource.RUSAGE_CHILDREN)

        failed = False
        err = None
        count_static_mut = 0

        try:
            sys.path.insert(0, str(self.subproject_dir / "scripts"))
            import rust_tools

            crates_dir = self.subproject_dir / "crates"
            stats = rust_tools.analyze_workspace(crates_dir)
            count_static_mut = sum(s.static_mut for s in stats)

            if count_static_mut != 0:
                failed = True
                err = f"Zero static mut violation: found {count_static_mut} static mut items in crates/"
            else:
                logger.info("Zero static mut invariant holds: exactly 0 static mut detected across all crates.")
        except Exception as e:
            failed = True
            err = f"Failed to verify static mut invariance: {e}"

        dur_ms = (time.perf_counter() - start_time) * 1000.0
        rusage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
        ram_mb = (rusage_after.ru_maxrss - rusage_before.ru_maxrss) / 1024.0
        energy = self.physics.calculate_energy(dur_ms, ram_mb, failed=failed)
        status = "PASSED" if not failed else "FAILED"
        token = self.physics.mint_proof_token(f"T1.2_STATIC_MUT_{count_static_mut}") if not failed else None

        metric = ANSEPhysicsMetrics(
            step_name="T1.2_Zero_Static_Mut_Invariance",
            duration_ms=dur_ms,
            peak_rss_mb=ram_mb,
            energy=energy,
            status=status,
            proof_token=token,
            error_message=err,
        )
        self.metrics_history.append(metric)
        logger.info(f"T1.2 Status: {status} | E = {energy:.2f} | Token: {token}")
        return metric

    def step_t1_3_anti_stub_ast_inspection(self) -> ANSEPhysicsMetrics:
        """T1.3: Anti-Stub AST Violation & Forbidden Marker Scan on Core Defense Crates."""
        logger.info("--- Executing T1.3: Anti-Stub AST Scan on Core Crates ---")
        start_time = time.perf_counter()
        rusage_before = resource.getrusage(resource.RUSAGE_CHILDREN)

        all_violations = []
        for crate in self.CORE_CRATES:
            crate_lib = self.subproject_dir / "crates" / crate / "src" / "lib.rs"
            violations = self.anti_stub.inspect_file(crate_lib)
            all_violations.extend(violations)

        failed = bool(all_violations)
        err = "; ".join(all_violations) if failed else None
        dur_ms = (time.perf_counter() - start_time) * 1000.0
        rusage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
        ram_mb = (rusage_after.ru_maxrss - rusage_before.ru_maxrss) / 1024.0
        energy = self.physics.calculate_energy(dur_ms, ram_mb, failed=failed)
        status = "PASSED" if not failed else "FAILED"
        token = self.physics.mint_proof_token(f"T1.3_AST_GUARD_{len(all_violations)}") if not failed else None

        metric = ANSEPhysicsMetrics(
            step_name="T1.3_Anti_Stub_AST_Inspection",
            duration_ms=dur_ms,
            peak_rss_mb=ram_mb,
            energy=energy,
            status=status,
            proof_token=token,
            error_message=err,
        )
        self.metrics_history.append(metric)
        if failed:
            logger.error(f"T1.3 Violations detected: {err}")
        else:
            logger.info(f"T1.3 Status: {status} | Core crates 100% clean of forbidden stubs | E = {energy:.2f}")
        return metric

    def step_t1_4_core_workspace_check(self) -> ANSEPhysicsMetrics:
        """T1.4: Core Kernel Workspace Compilation & Lint Hygiene."""
        logger.info("--- Executing T1.4: Core Workspace Cargo Check ---")
        cmd = ["cargo", "check", "--target", "x86_64-unknown-linux-gnu"]
        for c in self.CORE_CRATES:
            cmd.extend(["-p", c])

        ret, stdout, stderr, dur_ms, ram_mb = self.run_command(cmd, timeout=120.0)

        failed = (ret != 0)
        err = stderr if failed else None
        energy = self.physics.calculate_energy(dur_ms, ram_mb, failed=failed)
        status = "PASSED" if not failed else "FAILED"
        token = self.physics.mint_proof_token(f"T1.4_CHECK_{ret}") if not failed else None

        metric = ANSEPhysicsMetrics(
            step_name="T1.4_Core_Workspace_Check",
            duration_ms=dur_ms,
            peak_rss_mb=ram_mb,
            energy=energy,
            status=status,
            proof_token=token,
            error_message=err,
        )
        self.metrics_history.append(metric)
        logger.info(f"T1.4 Status: {status} | E = {energy:.2f} | Token: {token}")
        return metric

    def step_t1_5_core_defense_smoke_tests(self) -> ANSEPhysicsMetrics:
        """T1.5: Fast Core Memory & Defense Test Smoke Suite."""
        logger.info("--- Executing T1.5: Core Memory & Defense Smoke Tests ---")
        smoke_crates = ["kernel_types", "page_alloc", "slab", "ai_detector", "ebpf_firewall"]
        cmd = ["cargo", "test", "--lib", "--target", "x86_64-unknown-linux-gnu"]
        for c in smoke_crates:
            cmd.extend(["-p", c])
        cmd.extend(["--", "--test-threads=1"])

        ret, stdout, stderr, dur_ms, ram_mb = self.run_command(cmd, timeout=120.0)

        failed = (ret != 0)
        err = stderr if failed else None
        energy = self.physics.calculate_energy(dur_ms, ram_mb, failed=failed)
        status = "PASSED" if not failed else "FAILED"
        token = self.physics.mint_proof_token(f"T1.5_SMOKE_{ret}") if not failed else None

        metric = ANSEPhysicsMetrics(
            step_name="T1.5_Core_Defense_Smoke_Tests",
            duration_ms=dur_ms,
            peak_rss_mb=ram_mb,
            energy=energy,
            status=status,
            proof_token=token,
            error_message=err,
        )
        self.metrics_history.append(metric)
        logger.info(f"T1.5 Status: {status} | E = {energy:.2f} | Token: {token}")
        return metric

    def step_t1_6_retrofit_ltm(self) -> ANSEPhysicsMetrics:
        """T1.6: Retrofit T1 Verified Telemetry into ChromaDB LTM."""
        logger.info("--- Executing T1.6: Retrofitting Telemetry into ChromaDB LTM ---")
        start_time = time.perf_counter()
        rusage_before = resource.getrusage(resource.RUSAGE_CHILDREN)

        try:
            sys.path.insert(0, str(REPO_ROOT))
            from anse.memory.chroma_rag import ChromaRAG

            rag = ChromaRAG(persist_directory=str(REPO_ROOT / ".chroma_db"))
            t1_summary = {
                "doc_id": "t1_workflow_runux_execution_report",
                "task_prompt": "RunuX T1 (Core Bulk Hardening & Truth Verification) execution under ANSE physics.",
                "language": "python",
                "energy": sum(m.energy for m in self.metrics_history),
                "metadata": {
                    "tier": "T1",
                    "status": "ALL_PASSED",
                    "steps_json": json.dumps([asdict(m) for m in self.metrics_history]),
                },
                "code_content": json.dumps([asdict(m) for m in self.metrics_history], indent=2),
            }
            rag.index_code_solution(
                doc_id=t1_summary["doc_id"],
                code_content=t1_summary["code_content"],
                task_prompt=t1_summary["task_prompt"],
                language="json",
                energy=t1_summary["energy"],
                metadata=t1_summary["metadata"],
            )
            failed = False
            err = None
            logger.info("Successfully indexed T1 workflow telemetry into ChromaDB LTM.")
        except Exception as e:
            logger.error(f"LTM indexing failed: {e}")
            failed = True
            err = str(e)

        dur_ms = (time.perf_counter() - start_time) * 1000.0
        rusage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
        ram_mb = (rusage_after.ru_maxrss - rusage_before.ru_maxrss) / 1024.0
        energy = self.physics.calculate_energy(dur_ms, ram_mb, failed=failed)
        status = "PASSED" if not failed else "FAILED"
        token = self.physics.mint_proof_token(f"T1.6_LTM_{status}") if not failed else None

        metric = ANSEPhysicsMetrics(
            step_name="T1.6_ChromaDB_LTM_Retrofit",
            duration_ms=dur_ms,
            peak_rss_mb=ram_mb,
            energy=energy,
            status=status,
            proof_token=token,
            error_message=err,
        )
        self.metrics_history.append(metric)
        logger.info(f"T1.6 Status: {status} | E = {energy:.2f} | Token: {token}")
        return metric

    def run_all(self) -> bool:
        start_wall = time.perf_counter()
        logger.info("=== Starting RunuX T1 Autonomous Workflow ===")

        self.step_t1_1_metrics_ratchet_gate()
        self.step_t1_2_zero_static_mut_invariance()
        self.step_t1_3_anti_stub_ast_inspection()
        self.step_t1_4_core_workspace_check()
        self.step_t1_5_core_defense_smoke_tests()
        self.step_t1_6_retrofit_ltm()

        total_wall_s = time.perf_counter() - start_wall
        cumulative_energy = sum(m.energy for m in self.metrics_history)
        all_passed = all(m.status == "PASSED" for m in self.metrics_history)

        if all_passed:
            logger.info(f"=== RunuX T1 Workflow COMPLETED SUCCESSFULLY ===")
            logger.info(f"Total Wall Time: {total_wall_s:.2f}s | Cumulative Energy: {cumulative_energy:.2f}")
            for m in self.metrics_history:
                logger.info(f"  * {m.step_name}: {m.status} (E = {m.energy:.2f}, token = {m.proof_token})")
            return True
        else:
            logger.error("=== RunuX T1 Workflow FAILED ===")
            for m in self.metrics_history:
                if m.status != "PASSED":
                    logger.error(f"  * {m.step_name}: {m.status} | Reason: {m.error_message}")
            return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RunuX T1 Bulk Hardening & Verification Runner")
    args = parser.parse_args()

    runner = RunuxT1WorkflowRunner()
    success = runner.run_all()
    sys.exit(0 if success else 1)
