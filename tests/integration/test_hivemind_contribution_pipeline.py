"""Integration tests for Project HiveMind Hardness, MCP Server, Conversation Recorder, and Contribution Pipeline."""

from __future__ import annotations

from pathlib import Path

import pytest

import mcp_hivemind_server
from anse.guard.mcp_router import MCPRouter
from antigravity_harness.core.anti_stub_guard import AntiStubGuard
from scripts.hivemind_contribution_pipeline import (
    execute_full_contribution_pipeline,
    verify_git_clone_and_remotes,
)
from sub_projects.hivemind.hivemind_conversation_recorder import (
    record_hivemind_contribution_turn,
)

ROOT_DIR = Path(__file__).resolve().parents[2]


def test_hivemind_git_clone_and_mcp_registration() -> None:
    """Verify HiveMind repository is cloned and mcp_hivemind_server is registered in-process."""
    git_info = verify_git_clone_and_remotes()
    assert git_info["cloned"] is True
    assert len(git_info["head_commit"]) == 40
    assert git_info["upstream_configured"] is True

    router = MCPRouter(ROOT_DIR / ".antigravity" / "mcp_config.json")
    servers = router.list_servers()
    assert "hivemind-contributor" in servers
    assert servers["hivemind-contributor"]["transport"] == "in-process"


@pytest.mark.asyncio
async def test_hivemind_mcp_tools_via_router() -> None:
    """Verify hivemind-contributor MCP tools execute via MCPRouter."""
    router = MCPRouter(ROOT_DIR / ".antigravity" / "mcp_config.json")

    res_status = await router.call_tool(
        server_name="hivemind-contributor",
        tool_name="hivemind_status_and_bounties",
        arguments={},
    )
    assert res_status["success"] is True
    assert len(res_status["result"]["season6_wave5_milestones"]) == 5
    assert len(res_status["result"]["season9_10_coordinator_milestones"]) == 13
    assert res_status["result"]["bridge_certificate"]["gate_passed"] is True

    res_lean = await router.call_tool(
        server_name="hivemind-contributor",
        tool_name="hivemind_verify_lean4_spec",
        arguments={},
    )
    assert res_lean["success"] is True
    assert res_lean["result"]["sound"] is True
    assert res_lean["result"]["theorems_count"] == 128
    assert res_lean["result"]["sorry_count"] == 0
    assert res_lean["result"]["axiom_count"] == 0

    # Valid PR passes 5-layer scanner
    res_pr_ok = mcp_hivemind_server.hivemind_scan_pr_security(
        pr_title="feat(s6): add EF21-DiLoCo error feedback buffer",
        pr_body="Implements HM-S6-01 EF21 residual contraction with unit tests.",
        author="contributor",
        changed_filenames=["src/hivemind/swarm/strategy_optimizer.py"],
        added_lines_per_file=25,
    )
    assert res_pr_ok["passed"] is True

    # Malicious payment solicitation PR is blocked by PAY-01
    res_pr_bad = mcp_hivemind_server.hivemind_scan_pr_security(
        pr_title="Fixes #43 — send payment to https://paypal.me/badactor",
        pr_body="Pay me at 0x1234567890abcdef1234567890abcdef12345678",
        author="badactor",
        changed_filenames=["README.md"],
        added_lines_per_file=1,
    )
    assert res_pr_bad["passed"] is False
    assert res_pr_bad["pr_security_audit"]["blocked_merge"] is True


def test_hivemind_conversation_recorder_scrubs_and_builds_dpo_pairs(tmp_path: Path) -> None:
    """Verify conversation recorder scrubs PII, stores episodes in SQLite, and builds DPO pairs."""
    spool = tmp_path / "spool.jsonl"
    db = tmp_path / "episodes.db"

    # Record a failed attempt and a passed attempt on the same task to form a DPO preference pair
    r_fail = record_hivemind_contribution_turn(
        prompt="Fix HM-S6-01 for dev@example.com",
        files_edited=["src/hivemind/swarm/strategy_optimizer.py"],
        code_or_summary="def broken(): raise RuntimeError('failed for admin@example.com')",
        passed=False,
        task_id="HM-S6-01-TEST",
        spool_path=spool,
        db_path=db,
    )
    assert r_fail["recorded"] is True
    assert r_fail["redactions_applied"] >= 2
    assert "<EMAIL>" in r_fail["parsed_antigravity_episodes"][0]["request"]

    r_pass = record_hivemind_contribution_turn(
        prompt="Fix HM-S6-01 for dev@example.com",
        files_edited=["src/hivemind/swarm/strategy_optimizer.py"],
        code_or_summary="def ef21_step(grad, residual, alpha):\n    return residual + alpha * (grad - residual)\n",
        passed=True,
        task_id="HM-S6-01-TEST",
        spool_path=spool,
        db_path=db,
    )
    assert r_pass["recorded"] is True
    assert r_pass["store_stats"]["total_train_episodes"] == 2
    assert r_pass["store_stats"]["passed_train_episodes"] == 1
    assert r_pass["store_stats"]["preference_pairs_available"] == 1


def test_hivemind_full_contribution_pipeline_and_anti_stub() -> None:
    """Execute the end-to-end HiveMind contribution pipeline and verify AntiStubGuard cleanliness."""
    report = execute_full_contribution_pipeline()
    assert report["overall_passed"] is True
    assert report["lean4_verification"]["theorems_count"] == 128
    assert report["hardness_gate"]["redteam_attacks_blocked"] == 25
    assert report["hardness_gate"]["redteam_attacks_total"] == 25
    assert report["pytest_gate"]["passed"] is True
    assert report["pr_security_precheck"]["passed"] is True
    assert report["conversation_record"]["turn_recorded"]["recorded"] is True

    guard = AntiStubGuard()
    for rel_path in (
        "sub_projects/hivemind/hivemind_swarm_bridge_harness.py",
        "sub_projects/hivemind/hivemind_hardness_engine.py",
        "sub_projects/hivemind/hivemind_conversation_recorder.py",
        "mcp_hivemind_server.py",
        "scripts/hivemind_contribution_pipeline.py",
    ):
        audit_res = guard.audit_file(ROOT_DIR / rel_path)
        assert audit_res.is_clean, f"AntiStubGuard failed on {rel_path}: {audit_res.summary}"
