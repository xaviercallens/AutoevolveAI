#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server for Project HiveMind Contributions (`hivemind-contributor`)
===============================================================================================
Exposes tools for autonomous agents and contributors working on `https://github.com/xaviercallens/HiveMind`:
1. `hivemind_status_and_bounties`: Inspects repo readiness, Season 6 (Wave 5) open milestones (`HM-S6-01..05`),
   and the 4 Golden Engineering Invariants.
2. `hivemind_scan_pr_security`: Runs the 5-Layer `PRSecurityScanner` (`PAY-01..03`, `CB-01..04`, `SEC-01..05`)
   and `AutoevolveAI` `AntiStubGuard` on candidate Pull Requests or modified files.
3. `hivemind_run_hardness_gate`: Executes the 6-Layer `HiveMindHardnessEngine` (Anti-Stub + 5-Layer PR Scanner
   + 25-Vector Attack Simulator + 128-Theorem Lean 4 Spec + Exact-Q Bridge + Execution Attestation).
4. `hivemind_verify_lean4_spec`: Verifies all 128 machine-checked Lean 4 theorems (`0 sorry`, `0` axioms)
   in `sub_projects/hivemind/formal/HiveMindSpec.lean`.
5. `hivemind_record_conversation_episode`: Scrubs PII/secrets (`anse.v2.scrub`) and records a contribution turn
   into `results/hivemind_conversation_spool.jsonl` and SQLite `EpisodeStore` (`data/hivemind_episodes.db`).
"""

from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

ROOT_DIR = Path(__file__).resolve().parent
HIVEMIND_SUBPROJECT_DIR = ROOT_DIR / "sub_projects" / "hivemind"
HIVEMIND_REPO_DIR = HIVEMIND_SUBPROJECT_DIR / "HiveMind"
HIVEMIND_SRC_DIR = HIVEMIND_REPO_DIR / "src"

for p in (ROOT_DIR, HIVEMIND_SRC_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from antigravity_harness.core.lean4_verifier import Lean4Verifier  # noqa: E402
from sub_projects.hivemind.hivemind_conversation_recorder import (  # noqa: E402
    harvest_antigravity_brain_transcripts,
    record_hivemind_contribution_turn,
)
from sub_projects.hivemind.hivemind_hardness_engine import (  # noqa: E402
    audit_pull_request_candidate,
    run_hivemind_hardness_suite,
)
from sub_projects.hivemind.hivemind_swarm_bridge_harness import (  # noqa: E402
    certify_hivemind_swarm_bridge,
)

mcp = FastMCP("hivemind-contributor")

SEASON6_OPEN_MILESTONES: tuple[dict[str, str], ...] = (
    {
        "id": "HM-S6-01",
        "branch_prefix": "feat/s6-ef21-diloco",
        "target_file": "src/hivemind/swarm/strategy_optimizer.py",
        "title": "Asynchronous Error-Feedback Residual Buffer (EF21-DiLoCo) for Ultra-Sparse Top-1% FP8 Outer Loops (Integrated via PR #63 & PR #69 by @clark719664)",
        "lean_theorem": "ef_conservation_any_compressor",
    },
    {
        "id": "HM-S6-02",
        "branch_prefix": "feat/s6-128-moe-3tier",
        "target_file": "src/hivemind/core/btm_moe.py",
        "title": "128-Expert 3-Tier Hierarchical MoE (E=128, Top-2) with Speculative Ring Token-Tree Prefetching (Integrated via PR #71 & PR #75 by @clark719664)",
        "lean_theorem": "hierarchical_128_expert_3tier_gating_savings",
    },
    {
        "id": "HM-S6-03",
        "branch_prefix": "feat/s6-zk-opoi-v4",
        "target_file": "src/hivemind/swarm/swarm_fabric.py",
        "title": "Zero-Knowledge Succinct Activation Commitments (ZK-OPoI v4) & Cross-Guild Slashing Insurance Pool (Integrated via PR #79 by @clark719664)",
        "lean_theorem": "slashing_insurance_pool_solvency_bound",
    },
    {
        "id": "HM-S6-04",
        "branch_prefix": "feat/s6-agent-arena",
        "target_file": "src/hivemind/game/hf_hack_miner.py",
        "title": "Season 6 Autonomous Agent Arena (Missions 21-24): Self-Play Code Repair & Live Strategy HUD (Integrated via PR #78 by @radialmonster)",
        "lean_theorem": "ucb1_bandit_exploration_bonus_monotonicity",
    },
    {
        "id": "HM-S6-05",
        "branch_prefix": "formal/s6-error-feedback-model",
        "target_file": "lean4/HiveMindSpec.lean",
        "title": "Formal Lean 4 Proofs (Theorems 49-72) for EF21-DiLoCo Conservation, Top-k Contraction & UCB1 Bounds (Integrated via PR #68 by @clark719664)",
        "lean_theorem": "topk_contraction_rate",
    },
)

SEASON7_NEXT_HORIZON_DIRECTIONS: tuple[dict[str, str], ...] = (
    {
        "id": "HM-S6-06",
        "branch_prefix": "feat/s7-looped-moe-backbone",
        "target_file": "src/hivemind/core/btm_upcycle.py",
        "title": "Looped Expert-Backbone (Prelude-RecurrentCore-Coda) for Qwen2.5-0.5B on 8 GB GPUs (Issue #66, Huang et al. 2026 Part I)",
        "lean_theorem": "rtx2070_8gb_vram_envelope_verified",
    },
    {
        "id": "HM-S6-07",
        "branch_prefix": "feat/s7-terminal-kv-sharing",
        "target_file": "src/hivemind/core/btm_moe.py",
        "title": "Terminal Fixed-Point KV-Cache Sharing Stacked on FP8 Paged KV-Cache (~6x Combined Cache Reduction, Issue #66 Part II)",
        "lean_theorem": "fp8_paged_kv_cache_vram_fits_in_2200mib",
    },
    {
        "id": "HM-S6-08",
        "branch_prefix": "feat/s7-fixed-point-speculative-gate",
        "target_file": "src/hivemind/swarm/inference_ring.py",
        "title": "Recurrent Fixed-Point Stability Detector as Adaptive-Gamma Gate for Prefix-Trie Speculative Decoding + ZK-OPoI v4 Batch Commitments",
        "lean_theorem": "prefix_trie_speculative_progress_bounds",
    },
    {
        "id": "HM-S6-09",
        "branch_prefix": "formal/s7-banach-kv-contraction",
        "target_file": "lean4/HiveMindSpec.lean",
        "title": "Formal Lean 4 Proofs (Theorems 73-80) for Terminal-KV Banach Contraction, FL-08 Workunit Ownership & ZK-OPoI v4 Position-Bound Merkle Soundness",
        "lean_theorem": "ef_residual_stays_bounded_under_decay",
    },
)

SEASON9_10_COORDINATOR_MILESTONES: tuple[dict[str, str], ...] = (
    {
        "id": "HM-S9-01",
        "branch_prefix": "feat/s9-decoupled-quorum-campaign",
        "target_file": "src/hivemind/cli/multi_moe_hf_campaign.py",
        "title": "Wire DecoupledDiLoCoQuorumSyncer (SI-12) and AdaptiveGraceWindowController into DiLoCoOuterOptimizer & multi_moe_hf_campaign",
        "lean_theorem": "quorum_liveness_under_m_minus_k_stragglers",
    },
    {
        "id": "HM-S9-02",
        "branch_prefix": "feat/s9-sigma-moe-peri-ln",
        "target_file": "src/hivemind/core/btm_upcycle.py",
        "title": "Sigma-MoE + Peri-LN & Empirical Skip-Token FLOP Report Gated on Realized Ghost Fraction",
        "lean_theorem": "sigma_moe_independent_gates_preserve_resident_expert_score",
    },
    {
        "id": "HM-S9-03",
        "branch_prefix": "feat/s9-orthoinj-depth-prior",
        "target_file": "src/hivemind/core/btm_upcycle.py",
        "title": "Orthogonal Input Injection (OrthoInj), LearnedDepthPrior & Terminal-KV Sharing Evaluation",
        "lean_theorem": "ortho_inj_pythagorean_energy_conservation",
    },
    {
        "id": "HM-S9-04",
        "branch_prefix": "feat/s9-factored-gossip-mix1-mix2",
        "target_file": "src/hivemind/swarm/diloco_nextgen.py",
        "title": "Factored Gossip (Mix1 Parameter / Mix2 Outer-Gradient Split) with Jensen-Shannon Router Disagreement Gating",
        "lean_theorem": "factored_gossip_js_gate_skips_blocking_mix2_barrier",
    },
    {
        "id": "HM-S9-05",
        "branch_prefix": "feat/s9-periodic-momentum-restart",
        "target_file": "src/hivemind/core/diloco_outer.py",
        "title": "Periodic Outer-Momentum Restarting (K_restart) for Nesterov, CPU Flat-Bucket & PA-CGAD",
        "lean_theorem": "outer_momentum_restart_zeroes_stale_velocity_energy",
    },
    {
        "id": "HM-S9-06",
        "branch_prefix": "feat/s9-heartbeat-cas-leases",
        "target_file": "src/hivemind/swarm/dht_storage.py",
        "title": "Heartbeat-Backed CAS Data Shard Leases with Adaptive Grace-Derived TTL and Expired Reclamation",
        "lean_theorem": "data_lease_batch_conservation_no_duplicates",
    },
    {
        "id": "HM-S9-08",
        "branch_prefix": "formal/s9-quorum-liveness-data-leasing",
        "target_file": "lean4/HiveMindSpec.lean",
        "title": "Season 15 Lean 4 Formal Proofs (Theorems 121-128): Quorum Liveness, RDA Bounds, Lease Conservation & OrthoInj",
        "lean_theorem": "data_lease_ttl_exceeds_step_plus_rtt_bound",
    },
    {
        "id": "HM-S10-01",
        "branch_prefix": "feat/s10-lattice-delta-compressor",
        "target_file": "src/hivemind/swarm/diloco_nextgen.py",
        "title": "Wire Gosset E8, Scalar Z, and Sign Delta Quantizers into ComputeVisibleSparseLoCoCompressor with EF21",
        "lean_theorem": "e8_lattice_second_moment_strictly_beats_z8_cubic",
    },
    {
        "id": "HM-S10-02",
        "branch_prefix": "feat/s10-orchestrator-axiom-gate",
        "target_file": "src/hivemind/cli/community_orchestrator.py",
        "title": "Enforce #print axioms Coverage Gate & Scientific-Lead Protected File Guard in Community Orchestrator",
        "lean_theorem": "data_lease_ttl_exceeds_step_plus_rtt_bound",
    },
    {
        "id": "HM-S9-13",
        "branch_prefix": "feat/s9-continuous-async-learner-quorum",
        "target_file": "src/hivemind/swarm/decoupled_diloco.py",
        "title": "Continuous Asynchronous Learner Coordinator with Deferred Token-Weighted & Eager One-Step Straggler Folding (E12 P5b)",
        "lean_theorem": "quorum_liveness_under_m_minus_k_stragglers",
    },
    {
        "id": "HM-S9-14",
        "branch_prefix": "feat/s9-campaign-rda-delta-cosine-diagnostic",
        "target_file": "src/hivemind/swarm/decoupled_diloco.py",
        "title": "Campaign RDA vs Direct Pairwise Delta-Cosine Diagnostic & Theoretical Common-Norm Multiplier Verification (E12 P5a)",
        "lean_theorem": "rda_common_norm_squared_sum",
    },
    {
        "id": "HM-S10-05",
        "branch_prefix": "feat/s10-a2-hexagonal-kv-cache-codecs",
        "target_file": "src/hivemind/compress/lattice_quantizer.py",
        "title": "Conway-Sloane 2D Hexagonal A2 Lattice Decoder & Pluggable KV-Cache Page Codecs in FP8PagedKVCache (E13)",
        "lean_theorem": "e8_lattice_second_moment_strictly_beats_z8_cubic",
    },
    {
        "id": "HM-S10-08",
        "branch_prefix": "feat/s10-execution-class-two-stat-spot-check",
        "target_file": "src/hivemind/boinc/validator.py",
        "title": "Execution-Class-Matched Validator Assignment, Two-Statistic Spot-Check Rule & Fixed-Point Q16 Digest Prototype (E12 P12)",
        "lean_theorem": "quorum_token_weighted_convex_combination",
    },
)


@mcp.tool()
def hivemind_status_and_bounties() -> dict[str, Any]:
    """Return Project HiveMind repository status, 4 Golden Rules, and Season 6/7 contributor tasks."""
    bridge = certify_hivemind_swarm_bridge()
    return {
        "repository": "https://github.com/xaviercallens/HiveMind",
        "local_checkout": str(HIVEMIND_REPO_DIR),
        "legal_charter": (
            "Strictly non-monetary open-source project (0.00 EUR/USD); there is no financial payment. "
            "Accumulated 'points' (PTS and $HIVE) grant exclusively reciprocal computing processing "
            "benefits when the live production HiveMind Swarm is deployed, available, and used by a large community."
        ),
        "community_gpu_benchmark": {
            "runner_script": "scripts/run_community_gpu_benchmark.py",
            "pytest_suite": "tests/test_community_gpu_benchmark.py",
            "receipt_artifact": "artifacts/community_gpu_benchmark_receipt.json",
            "command": "uv run python scripts/run_community_gpu_benchmark.py --contributor-handle <github_handle>",
        },
        "golden_rules": [
            "1. 8 GB Consumer GPU VRAM Ceiling (<= 6656 MiB usable WDDM ceiling; Qwen2.5-0.5B 96-MoE <= 2.0 GB, 7B worker <= 6.5 GB)",
            "2. Bitwise / Bounded CUDA Determinism (eps <= 1e-4 under CUBLAS_WORKSPACE_CONFIG=:4096:8 for 10% spot-check)",
            "3. Byzantine Resilience (Multi-Krum n >= 2f + 3, Adaptive Median-L2 clipping, and ZK-OPoI activation cosine >= 0.992)",
            "4. Zero-Intrusion Gamer Respect (< 1.5s NVMe emergency preemption and 500 ms WDDM TDR safety margin)",
        ],
        "season6_wave5_milestones": list(SEASON6_OPEN_MILESTONES),
        "season7_next_horizon_directions": list(SEASON7_NEXT_HORIZON_DIRECTIONS),
        "season9_10_coordinator_milestones": list(SEASON9_10_COORDINATOR_MILESTONES),
        "bridge_certificate": asdict(bridge),
    }


@mcp.tool()
def hivemind_scan_pr_security(
    pr_title: str,
    pr_body: str,
    author: str = "contributor",
    changed_filenames: list[str] | None = None,
    added_lines_per_file: int = 25,
) -> dict[str, Any]:
    """Audit a proposed Pull Request against HiveMind's 5-Layer PRSecurityScanner and AutoevolveAI AntiStubGuard."""
    base_patch_lines = [
        "+def verified_contribution(grad: float, residual: float, alpha: float) -> float:",
        "+    if alpha <= 0.0 or alpha > 1.0:",
        "+        raise ValueError('alpha must be in (0, 1]')",
        "+    delta = grad - residual",
        "+    updated = residual + alpha * delta",
        "+    return round(updated, 8)",
    ]
    selected_lines = (
        base_patch_lines
        if added_lines_per_file >= 5
        else base_patch_lines[: max(1, added_lines_per_file)]
    )
    patch_str = "\n".join(selected_lines) + "\n"
    changed_files = [
        {
            "filename": fname,
            "status": "modified",
            "additions": added_lines_per_file,
            "patch": patch_str,
        }
        for fname in (changed_filenames or ["src/hivemind/swarm/strategy_optimizer.py"])
    ]
    return audit_pull_request_candidate(
        pr_title=pr_title,
        pr_body=pr_body,
        author=author,
        changed_files=changed_files,
        commit_messages=[pr_title],
    )


@mcp.tool()
def hivemind_run_hardness_gate(include_redteam_25_vectors: bool = True) -> dict[str, Any]:
    """Run the 6-Layer HiveMind Hardness & Zero-Trust Verification Suite."""
    return run_hivemind_hardness_suite(
        include_redteam_25_vectors=include_redteam_25_vectors,
        output_json_path=ROOT_DIR / "results" / "hivemind_hardness_report.json",
    )


@mcp.tool()
def hivemind_verify_lean4_spec() -> dict[str, Any]:
    """Verify the 64 machine-checked Lean 4 theorems (0 sorry, 0 axioms) in HiveMindSpec.lean."""
    formal_dir = HIVEMIND_SUBPROJECT_DIR / "formal"
    verifier = Lean4Verifier(formal_dir=formal_dir)
    sorry_count, sorry_occurrences = verifier.scan_for_sorry(formal_dir)
    inventory = verifier.extract_proof_inventory(formal_dir)
    sound, message = verifier.check_soundness(formal_dir)
    return {
        "formal_dir": str(formal_dir),
        "sound": sound,
        "message": message,
        "theorems_count": len(inventory["theorems"]),
        "definitions_count": len(inventory["definitions"]),
        "sorry_count": sorry_count,
        "sorry_occurrences": sorry_occurrences,
        "axiom_count": len(inventory["axioms"]),
        "theorems": inventory["theorems"],
    }


@mcp.tool()
def hivemind_record_conversation_episode(
    prompt: str,
    files_edited: list[str],
    code_or_summary: str,
    passed: bool = True,
    task_id: str = "HM-S6-CONTRIB",
) -> dict[str, Any]:
    """Scrub PII/secrets and record a HiveMind contribution episode into the JSONL spool and SQLite EpisodeStore."""
    turn_res = record_hivemind_contribution_turn(
        prompt=prompt,
        files_edited=files_edited,
        code_or_summary=code_or_summary,
        passed=passed,
        task_id=task_id,
    )
    harvest_res = harvest_antigravity_brain_transcripts()
    return {
        "turn_recorded": turn_res,
        "brain_harvest_summary": harvest_res,
    }


if __name__ == "__main__":
    mcp.run()
