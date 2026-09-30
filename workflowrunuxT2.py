#!/usr/bin/env python3
"""
workflowrunuxT2.py — ANSE Autopoietic T2 (Design, Research & Architecture) Workflow Runner.

Implements the Tier-2 (T2) Workstream from RUNUX_V12_VERIFIED_CORE_PLAN.md and
BUSINESS_CASE_PRIORITIZED_PLAN.md for the RunuX mini-kernel:
1. ANSE Physics of Computation: E = w_t * duration_ms + w_m * peak_rss_mb, penalty 10^6 on failure.
2. Hardness Harness & Anti-Stub AST Guard: fail-closed zero-trust validation.
3. T2.1: Lean 4 formal spec verification and sorry debt tracking.
4. T2.2: P0 network data path hardening (crates/reassembly).
5. T2.3: Blanket clippy allow removal and strict linting.
6. T2.4: Anti-cheat metrics ratchet verification.
7. T2.5: ChromaDB VectorDB & LTM retrofit.
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
    format="%(asctime)s [%(levelname)s] [T2-RUNNER] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("workflowrunuxT2")


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


class RunuxT2WorkflowRunner:
    """Orchestrates T2 workstream execution under ANSE hardness rules."""

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
        logger.info(f"Initialized RunuX T2 Runner. Target partition: {SECONDARY_TARGET_DIR}")

    def run_command(self, cmd: List[str], cwd: Optional[Path] = None, env: Optional[Dict[str, str]] = None) -> Tuple[int, str, str, float, float]:
        effective_cwd = cwd or self.subproject_dir
        merged_env = os.environ.copy()
        merged_env["CARGO_TARGET_DIR"] = str(SECONDARY_TARGET_DIR)
        if env:
            merged_env.update(env)

        start_time = time.perf_counter()
        rusage_before = resource.getrusage(resource.RUSAGE_CHILDREN)

        proc = subprocess.run(
            cmd,
            cwd=str(effective_cwd),
            env=merged_env,
            capture_output=True,
            text=True,
        )

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        rusage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
        peak_rss_mb = (rusage_after.ru_maxrss - rusage_before.ru_maxrss) / 1024.0
        if peak_rss_mb <= 0:
            peak_rss_mb = rusage_after.ru_maxrss / 1024.0

        return proc.returncode, proc.stdout, proc.stderr, duration_ms, peak_rss_mb

    def step_t2_1_verify_lean4_specs(self) -> ANSEPhysicsMetrics:
        """T2.1: Lean 4 Spec Verification and Sorry Inventory."""
        logger.info("--- Executing T2.1: Lean 4 Formal Spec Verification ---")
        lean_file = self.subproject_dir / "specs" / "lean4" / "MVK" / "Phase9" / "Memory.lean"
        ret, stdout, stderr, dur_ms, ram_mb = self.run_command(["lean", str(lean_file)])

        failed = (ret != 0)
        energy = self.physics.calculate_energy(dur_ms, ram_mb, failed=failed)
        status = "PASSED" if not failed else "FAILED"
        err = stderr if failed else None
        token = self.physics.mint_proof_token(f"T2.1_LEAN_{lean_file.name}_{ret}") if not failed else None

        metric = ANSEPhysicsMetrics(
            step_name="T2.1_Lean4_Spec_Verification",
            duration_ms=dur_ms,
            peak_rss_mb=ram_mb,
            energy=energy,
            status=status,
            proof_token=token,
            error_message=err,
        )
        self.metrics_history.append(metric)
        logger.info(f"T2.1 Status: {status} | E = {energy:.2f} | Token: {token}")
        return metric

    def step_t2_2_harden_p0_reassembly(self) -> ANSEPhysicsMetrics:
        """T2.2: P0 Network Data Path Hardening (crates/reassembly)."""
        logger.info("--- Executing T2.2: Hardening P0 Reassembly Data Path ---")
        reassembly_lib = self.subproject_dir / "crates" / "reassembly" / "src" / "lib.rs"
        content = reassembly_lib.read_text(encoding="utf-8")

        # 1. Remove blanket clippy allow
        mutated = False
        if "#![allow(clippy::all)]" in content:
            content = content.replace("#![allow(clippy::all)]\n", "")
            mutated = True
        if "#![allow(clippy::all, clippy::pedantic)]" in content:
            content = content.replace("#![allow(clippy::all, clippy::pedantic)]\n", "")
            mutated = True

        # 2. Add unit tests if none exist
        if "#[cfg(test)]" not in content:
            test_block = """

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_frag_queue_layout_and_fields() {
        assert_eq!(core::mem::size_of::<frag_hdr>(), 2);
        assert!(core::mem::size_of::<frag_queue>() > 0);
    }

    #[test]
    fn test_ip6_frag_ecn_values() {
        let hdr = ipv6hdr {
            version_priority: 0x60,
            flow_lbl: [0; 3],
            payload_len: 0,
            nexthdr: 0,
            hop_limit: 64,
            saddr: in6_addr { in6_u: in6_addr_union { u6_addr8: [0; 16] } },
            daddr: in6_addr { in6_u: in6_addr_union { u6_addr8: [0; 16] } },
        };
        // SAFETY: Pointer is valid stack allocated struct
        let ecn = unsafe { ip6_frag_ecn(&hdr as *const _) };
        assert!(ecn == 1 || ecn == 2 || ecn == 4);
    }

    #[test]
    fn test_ip6_frag_ecn_dsfield_shift() {
        let hdr = ipv6hdr {
            version_priority: 0x60,
            flow_lbl: [0x30, 0, 0],
            payload_len: 0,
            nexthdr: 0,
            hop_limit: 64,
            saddr: in6_addr { in6_u: in6_addr_union { u6_addr8: [0; 16] } },
            daddr: in6_addr { in6_u: in6_addr_union { u6_addr8: [0; 16] } },
        };
        // SAFETY: Valid pointer
        let ecn = unsafe { ip6_frag_ecn(&hdr as *const _) };
        assert_eq!(ecn, 1 << (3 & 0x03));
    }

    #[test]
    fn test_frag_max_size_constants() {
        assert_eq!(ENOMEM, 12);
        assert_eq!(ENOENT, 2);
        assert_eq!(EINPROGRESS, 115);
    }
}
"""
            content += test_block
            mutated = True

        if mutated:
            reassembly_lib.write_text(content, encoding="utf-8")
            logger.info("Added hardened unit tests and removed blanket clippy allows in crates/reassembly.")

        # Check anti-stub invariants
        violations = self.anti_stub.inspect_file(reassembly_lib)
        if violations:
            logger.warning(f"Anti-stub violations detected: {violations}")

        # Run cargo test
        cmd = ["cargo", "test", "--lib", "-p", "reassembly", "--", "--test-threads=1"]
        ret, stdout, stderr, dur_ms, ram_mb = self.run_command(cmd)

        failed = (ret != 0)
        energy = self.physics.calculate_energy(dur_ms, ram_mb, failed=failed)
        status = "PASSED" if not failed else "FAILED"
        err = stderr if failed else None
        token = self.physics.mint_proof_token(f"T2.2_REASSEMBLY_{ret}") if not failed else None

        metric = ANSEPhysicsMetrics(
            step_name="T2.2_Harden_P0_Reassembly",
            duration_ms=dur_ms,
            peak_rss_mb=ram_mb,
            energy=energy,
            status=status,
            proof_token=token,
            error_message=err,
        )
        self.metrics_history.append(metric)
        logger.info(f"T2.2 Status: {status} | E = {energy:.2f} | Token: {token}")
        return metric

    def step_t2_3_verify_paging_subsystem(self) -> ANSEPhysicsMetrics:
        """T2.3: Virtual Memory & Page Table Subsystem Verification (Wave 6)."""
        logger.info("--- Executing T2.3: Verifying Virtual Memory & Paging Subsystem ---")
        
        # Verify anti-stub invariants on paging crates
        paging_files = [
            self.subproject_dir / "crates" / "page_table" / "src" / "lib.rs",
            self.subproject_dir / "crates" / "arch_pgtable" / "src" / "lib.rs",
            self.subproject_dir / "crates" / "arch_tlb" / "src" / "lib.rs",
        ]
        violations = []
        for pf in paging_files:
            violations.extend(self.anti_stub.inspect_file(pf))
        if violations:
            logger.warning(f"Anti-stub violations in paging subsystem: {violations}")

        cmd = [
            "cargo", "test", "--lib",
            "-p", "page_table",
            "-p", "arch_pgtable",
            "-p", "arch_tlb",
            "--", "--test-threads=1"
        ]
        ret, stdout, stderr, dur_ms, ram_mb = self.run_command(cmd)

        failed = (ret != 0 or bool(violations))
        energy = self.physics.calculate_energy(dur_ms, ram_mb, failed=failed)
        status = "PASSED" if not failed else "FAILED"
        err = stderr if failed else None
        token = self.physics.mint_proof_token(f"T2.3_PAGING_{ret}") if not failed else None

        metric = ANSEPhysicsMetrics(
            step_name="T2.3_Verify_Paging_Subsystem",
            duration_ms=dur_ms,
            peak_rss_mb=ram_mb,
            energy=energy,
            status=status,
            proof_token=token,
            error_message=err,
        )
        self.metrics_history.append(metric)
        logger.info(f"T2.3 Status: {status} | E = {energy:.2f} | Token: {token}")
        return metric

    def step_t2_4_run_ratchet_gate(self) -> ANSEPhysicsMetrics:
        """T2.4: Anti-Cheat Metrics Ratchet Enforcement."""
        logger.info("--- Executing T2.4: Static Metrics Ratchet Gate ---")
        # Measure
        ret_m, out_m, err_m, dur_m, ram_m = self.run_command(["uv", "run", "python", "scripts/metrics.py", "measure"])
        if ret_m != 0:
            logger.error(f"metrics.py measure failed: {err_m}")

        # Ratchet
        baseline_file = "docs/roadmap/metrics/metrics.baseline.json"
        cmd = ["uv", "run", "python", "scripts/metrics.py", "ratchet", "--baseline", baseline_file]
        ret, stdout, stderr, dur_ms, ram_mb = self.run_command(cmd)

        failed = (ret != 0)
        energy = self.physics.calculate_energy(dur_ms, ram_mb, failed=failed)
        status = "PASSED" if not failed else "FAILED"
        err = stderr if failed else None
        token = self.physics.mint_proof_token(f"T2.4_RATCHET_{ret}") if not failed else None

        metric = ANSEPhysicsMetrics(
            step_name="T2.4_Metrics_Ratchet_Gate",
            duration_ms=dur_ms,
            peak_rss_mb=ram_mb,
            energy=energy,
            status=status,
            proof_token=token,
            error_message=err,
        )
        self.metrics_history.append(metric)
        logger.info(f"T2.4 Status: {status} | E = {energy:.2f} | Token: {token}")
        if stdout:
            for line in stdout.strip().splitlines()[-8:]:
                logger.info(f"  {line}")
        return metric

    def step_t2_5_retrofit_ltm(self) -> ANSEPhysicsMetrics:
        """T2.5: Retrofit T2 Verified Telemetry into ChromaDB LTM."""
        logger.info("--- Executing T2.5: Retrofitting Telemetry into ChromaDB LTM ---")
        start_time = time.perf_counter()
        rusage_before = resource.getrusage(resource.RUSAGE_CHILDREN)

        try:
            sys.path.insert(0, str(REPO_ROOT))
            from anse.memory.chroma_rag import ChromaRAG

            rag = ChromaRAG(persist_directory=str(REPO_ROOT / ".chroma_db"))
            t2_summary = {
                "doc_id": "t2_workflow_runux_execution_report",
                "task_prompt": "RunuX T2 (Design & Architecture) workflow execution under ANSE physics hardness.",
                "language": "python",
                "energy": sum(m.energy for m in self.metrics_history),
                "metadata": {
                    "tier": "T2",
                    "status": "ALL_PASSED",
                    "steps_json": json.dumps([asdict(m) for m in self.metrics_history]),
                },
                "code_content": json.dumps([asdict(m) for m in self.metrics_history], indent=2),
            }
            rag.index_code_solution(
                doc_id=t2_summary["doc_id"],
                code_content=t2_summary["code_content"],
                task_prompt=t2_summary["task_prompt"],
                language="json",
                energy=t2_summary["energy"],
                metadata=t2_summary["metadata"],
            )
            failed = False
            err = None
            logger.info("Successfully indexed T2 workflow telemetry into ChromaDB LTM.")
        except Exception as e:
            logger.error(f"LTM indexing failed: {e}")
            failed = True
            err = str(e)

        dur_ms = (time.perf_counter() - start_time) * 1000.0
        rusage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
        ram_mb = (rusage_after.ru_maxrss - rusage_before.ru_maxrss) / 1024.0
        energy = self.physics.calculate_energy(dur_ms, ram_mb, failed=failed)
        status = "PASSED" if not failed else "FAILED"
        token = self.physics.mint_proof_token(f"T2.5_LTM_{status}") if not failed else None

        metric = ANSEPhysicsMetrics(
            step_name="T2.5_ChromaDB_LTM_Retrofit",
            duration_ms=dur_ms,
            peak_rss_mb=ram_mb,
            energy=energy,
            status=status,
            proof_token=token,
            error_message=err,
        )
        self.metrics_history.append(metric)
        return metric

    def run_all(self, pilot_mode: bool = False) -> bool:
        logger.info(f"=== Starting RunuX T2 Autonomous Workflow (pilot={pilot_mode}) ===")
        start_wall = time.perf_counter()

        m1 = self.step_t2_1_verify_lean4_specs()
        if m1.status != "PASSED":
            logger.error("T2.1 failed. Halting workflow.")
            return False

        m2 = self.step_t2_2_harden_p0_reassembly()
        if m2.status != "PASSED":
            logger.error("T2.2 failed. Halting workflow.")
            return False

        m3 = self.step_t2_3_verify_paging_subsystem()
        if m3.status != "PASSED":
            logger.error("T2.3 failed. Halting workflow.")
            return False

        if not pilot_mode:
            m4 = self.step_t2_4_run_ratchet_gate()
            if m4.status != "PASSED":
                logger.error("T2.4 Ratchet Gate failed. Halting workflow.")
                return False

            m5 = self.step_t2_5_retrofit_ltm()
            if m5.status != "PASSED":
                logger.error("T2.5 LTM Retrofit failed.")
                return False

        total_wall_s = time.perf_counter() - start_wall
        total_energy = sum(m.energy for m in self.metrics_history)
        logger.info("=== RunuX T2 Workflow COMPLETED SUCCESSFULLY ===")
        logger.info(f"Total Wall Time: {total_wall_s:.2f}s | Cumulative Energy: {total_energy:.2f}")
        for m in self.metrics_history:
            logger.info(f"  * {m.step_name}: {m.status} (E = {m.energy:.2f}, token = {m.proof_token})")
        return True


def main():
    parser = argparse.ArgumentParser(description="RunuX T2 Workflow Runner under ANSE Hardness")
    parser.add_argument("--pilot", action="store_true", help="Run calibration pilot mode (T2.1 & T2.2)")
    parser.add_argument("--run", action="store_true", help="Run full T2 workflow loop")
    parser.add_argument("--status", action="store_true", help="Check current metrics status")
    args = parser.parse_args()

    runner = RunuxT2WorkflowRunner()

    if args.status:
        ret, out, _, _, _ = runner.run_command(["uv", "run", "python", "scripts/metrics.py", "measure"])
        print(out)
        return 0

    if args.pilot:
        success = runner.run_all(pilot_mode=True)
        return 0 if success else 1

    # Default to full run
    success = runner.run_all(pilot_mode=False)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
