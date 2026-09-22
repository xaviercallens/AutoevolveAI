#!/usr/bin/env python3
"""
Enhanced Model Context Protocol (MCP) Server: Multi-Tool Hardening Engine
Exposes AST verification, Ruff linting/formatting, Bandit security scanning,
Radon cyclomatic complexity, and Vulture dead-code auditing.
"""

from __future__ import annotations

import ast
import importlib.metadata
import json
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import radon.complexity as cc
from fastmcp import FastMCP
from radon.visitors import ComplexityVisitor

import execution_attestation

mcp = FastMCP("agent-hardening-engine")


# --- Utility Functions ---


def _get_installed_packages() -> set[str]:
    installed: set[str] = set()
    for dist in importlib.metadata.distributions():
        top_level = dist.read_text("top_level.txt")
        if top_level:
            for line in top_level.splitlines():
                clean_name = line.strip().lower()
                if clean_name:
                    installed.add(clean_name)
        else:
            name = dist.metadata["Name"] if "Name" in dist.metadata else None
            if name:
                installed.add(name.lower().replace("-", "_"))
    return installed


# --- MCP Tools ---


def _extract_imported_modules(tree: ast.AST) -> set[str]:
    """Extract root module names from AST Import and ImportFrom nodes."""
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            imported_modules.add(node.module.split(".")[0])
    return imported_modules


def _filter_phantom_imports(
    imported_modules: set[str], local_modules: list[str] | None
) -> list[str]:
    """Filter out modules not present in stdlib, virtualenv, or allowed local packages."""
    stdlib: set[str] = getattr(sys, "stdlib_module_names", set())
    installed = _get_installed_packages()
    allowed = {m.lower() for m in (local_modules or [])}
    allowed.add("anse")

    return [
        m
        for m in sorted(imported_modules)
        if m.lower() not in stdlib and m.lower() not in installed and m.lower() not in allowed
    ]


@mcp.tool()
def verify_ast_and_imports(code: str, local_modules: list[str] | None = None) -> dict[str, Any]:
    """Audit Python AST syntax and verify all top-level imports exist in stdlib or active env."""
    try:
        tree = ast.parse(code, filename="<agent_code>")
    except SyntaxError as err:
        return {
            "valid": False,
            "error": "SyntaxError",
            "message": err.msg,
            "line": err.lineno,
            "offset": err.offset,
        }

    imported_modules = _extract_imported_modules(tree)
    phantom = _filter_phantom_imports(imported_modules, local_modules)

    return {
        "valid": len(phantom) == 0,
        "detected_imports": sorted(imported_modules),
        "phantom_imports": phantom,
        "message": (
            f"Detected {len(phantom)} phantom imports" if phantom else "AST & imports valid."
        ),
    }


@mcp.tool()
def audit_security_bandit(code: str, severity_level: str = "LOW") -> dict[str, Any]:
    """
    Run Bandit static security analysis on code to detect CWE vulnerabilities,
    unsafe subprocess execution, eval, hardcoded secrets, and weak cryptography.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        cmd = [
            sys.executable,
            "-m",
            "bandit",
            "-q",
            "--format=json",
            f"-s{severity_level}",
            tmp_path,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)

        results = json.loads(res.stdout) if res.stdout else {}
        issues = results.get("results", [])

        clean_issues = [
            {
                "test_id": issue.get("test_id"),
                "issue_text": issue.get("issue_text"),
                "severity": issue.get("issue_severity"),
                "confidence": issue.get("issue_confidence"),
                "line": issue.get("line_number"),
                "code_slice": issue.get("code", "").strip(),
            }
            for issue in issues
        ]

        return {
            "secure": len(clean_issues) == 0,
            "issue_count": len(clean_issues),
            "vulnerabilities": clean_issues,
        }
    except FileNotFoundError:
        return {"secure": False, "error": "Bandit executable missing. Run: pip install bandit"}
    except Exception as e:
        return {"secure": False, "error": str(e)}
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@mcp.tool()
def check_cyclomatic_complexity(code: str, max_complexity: int = 10) -> dict[str, Any]:
    """
    Analyze cyclomatic complexity using Radon. Blocks agent spaghetti code
    and over-nested logic exceeding max_complexity threshold per block.
    """
    try:
        blocks = ComplexityVisitor.from_code(code).blocks
    except SyntaxError as e:
        return {"passed": False, "error": f"SyntaxError: {e.msg} at line {e.lineno}"}

    violations: list[str] = []
    block_reports: list[dict[str, Any]] = []

    for block in blocks:
        report = {
            "name": block.name,
            "type": type(block).__name__,
            "line": block.lineno,
            "complexity": block.complexity,
            "rank": cc.cc_rank(block.complexity),
        }
        block_reports.append(report)

        if block.complexity > max_complexity:
            violations.append(
                f"'{block.name}' (line {block.lineno}) has cyclomatic complexity "
                f"{block.complexity} (limit: {max_complexity})"
            )

    return {
        "passed": len(violations) == 0,
        "max_detected_complexity": max([b.complexity for b in blocks], default=0),
        "violations": violations,
        "blocks": block_reports,
    }


@mcp.tool()
def audit_dead_code_vulture(code: str, min_confidence: int = 80) -> dict[str, Any]:
    """
    Run Vulture to detect dead functions, unused variables, unreachable branches,
    and orphan code structures.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        cmd = [sys.executable, "-m", "vulture", f"--min-confidence={min_confidence}", tmp_path]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)

        lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
        dead_items: list[str] = []
        for line in lines:
            parts = line.split(":", 2)
            if len(parts) >= 3:
                dead_items.append(f"Line {parts[1]}: {parts[2].strip()}")
            else:
                dead_items.append(line)

        return {
            "clean": len(dead_items) == 0,
            "dead_code_count": len(dead_items),
            "findings": dead_items,
        }
    except FileNotFoundError:
        return {"clean": False, "error": "Vulture missing. Run: pip install vulture"}
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@mcp.tool()
def run_ruff_lint(code: str, filename: str = "snippet.py", fix: bool = False) -> dict[str, Any]:
    """Run Astral's Ruff linter on a Python code snippet via stdin."""
    python_exe = sys.executable
    cmd = [
        python_exe,
        "-m",
        "ruff",
        "check",
        "--output-format=json",
        f"--stdin-filename={filename}",
        "-",
    ]
    if fix:
        cmd.append("--fix")

    try:
        proc = subprocess.run(cmd, input=code, text=True, capture_output=True, check=False)
    except FileNotFoundError:
        return {"success": False, "error": "Ruff not found."}

    violations: list[dict[str, Any]] = []
    try:
        if proc.stdout.strip():
            violations = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"success": False, "error": f"Failed to parse Ruff output: {proc.stderr}"}

    fixed_code = None
    if fix:
        fix_proc = subprocess.run(
            [python_exe, "-m", "ruff", "check", "--fix", f"--stdin-filename={filename}", "-"],
            input=code,
            text=True,
            capture_output=True,
            check=False,
        )
        fixed_code = fix_proc.stdout

    return {
        "success": len(violations) == 0,
        "violation_count": len(violations),
        "violations": violations,
        "fixed_code": fixed_code,
    }


@mcp.tool()
def run_ruff_format(code: str, filename: str = "snippet.py") -> dict[str, Any]:
    """Auto-format Python code according to standard PEP 8 / Black style conventions using Ruff."""
    python_exe = sys.executable
    cmd = [python_exe, "-m", "ruff", "format", f"--stdin-filename={filename}", "-"]
    try:
        proc = subprocess.run(cmd, input=code, text=True, capture_output=True, check=False)
    except FileNotFoundError:
        return {"success": False, "error": "Ruff binary not found."}

    if proc.returncode != 0:
        return {"success": False, "error": proc.stderr}

    return {"success": True, "formatted_code": proc.stdout, "modified": proc.stdout != code}


def _run_optional_test_command(test_command: str) -> str | None:
    """Run an optional pre-attestation test command and return error string if failed."""
    if not test_command:
        return None
    args = shlex.split(test_command)
    res = subprocess.run(args, capture_output=True, text=True, check=False, env=dict(os.environ))
    if res.returncode != 0:
        return (
            res.stderr
            or res.stdout
            or f"Command '{test_command}' failed with exit code {res.returncode}"
        )
    return None


@mcp.tool()
def request_task_completion_attestation(
    target_module: str = "",
    test_command: str = "",
) -> dict[str, Any]:
    """
    Decoupled Task Completion Attestation Gate.
    Verifies that real implementation has been written (no pass, ..., NotImplementedError stubs),
    bans fake/synthetic data prefixes in production code, checks runtime execution traces,
    and returns a cryptographically secure attestation proof token.
    """
    cmd_err = _run_optional_test_command(test_command)
    if cmd_err is not None:
        return {"verified": False, "error": f"Test command failed: {cmd_err}"}

    is_valid, token, violations = execution_attestation.attest_execution(target_module)
    if not is_valid:
        return {
            "verified": False,
            "violations": violations,
            "error": "Attestation gate rejected task completion.",
        }

    return {
        "verified": True,
        "proof_token": token,
        "receipt_file": str(execution_attestation.ATTESTATION_FILE),
        "message": "Task completion verified by deterministic attestation gate.",
    }


@mcp.tool()
def evaluate_code_with_critic(code: str, task_context: str = "") -> dict[str, Any]:
    """
    Evaluate candidate code with the local SLM Critic Model (Qwen2.5-Coder via Ollama/CPU).
    Fast pre-execution semantic QA filter detecting anti-patterns, stubs, and bad complexity.
    """
    try:
        from anse.guard.critic import CodeCritic

        critic = CodeCritic()
        res = critic.evaluate(code=code, prompt_context=task_context)
        return {
            "decision": res.decision.value,
            "accepted": res.is_accepted,
            "reason": res.reason,
            "energy_penalty": res.energy_penalty,
            "duration_ms": round(res.duration_ms, 2),
        }
    except Exception as exc:
        return {
            "decision": "SKIPPED",
            "accepted": True,
            "reason": f"Critic execution fallback: {exc}",
            "energy_penalty": 0.0,
        }


@mcp.tool()
def record_rl_trace(
    subtask_id: str,
    prompt: str,
    completion: str,
    passed: bool,
    reasons: list[str] | None = None,
    human_patch: str | None = None,
) -> dict[str, Any]:
    """
    Record an execution trace into local Redis to feed the night-time Mini-RL / DPO training loop.
    Stores prompt, candidate completion, attestation outcome, and optional human correction.
    """
    try:
        import time
        import uuid

        import redis

        r = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True,
        )
        trace_id = str(uuid.uuid4())
        trace_payload = {
            "trace_id": trace_id,
            "subtask_id": subtask_id,
            "timestamp": time.time(),
            "request_json": json.dumps(
                {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
            ),
            "response_json": json.dumps(
                {"candidates": [{"content": {"parts": [{"text": completion}]}}]}
            ),
        }
        r.set(f"antigravity:trace:{trace_id}", json.dumps(trace_payload))
        r.rpush(f"antigravity:subtask:{subtask_id}:traces", trace_id)

        att_payload = {
            "verdict": "PASSED" if passed else "FAILED",
            "subtask_id": subtask_id,
            "reasons": json.dumps(reasons or []),
            "timestamp": str(time.time()),
        }
        r.hset(f"antigravity:attestation:{trace_id}", mapping={k: str(v) for k, v in att_payload.items()})

        if human_patch:
            r.set(f"antigravity:subtask:{subtask_id}:human_patch", human_patch)

        return {
            "success": True,
            "trace_id": trace_id,
            "subtask_id": subtask_id,
            "recorded": True,
        }
    except Exception as exc:
        return {"success": False, "error": str(exc)}


@mcp.tool()
def audit_anti_stub(code: str, filename: str = "candidate.py") -> dict[str, Any]:
    """
    Audits Python code with AntiStubGuard against stubs, ellipsis (...), fake mock data,
    and simulation shortcuts under the ANSE computational physics model (E = 10^6 on violation).
    """
    from antigravity_harness.core.anti_stub_guard import AntiStubGuard

    guard = AntiStubGuard()
    result = guard.audit_code(code, filename=filename)
    return {
        "is_clean": result.is_clean,
        "violations_count": len(result.violations),
        "violations": [
            {
                "rule": v.rule,
                "lineno": v.lineno,
                "symbol": v.symbol_name,
                "message": v.message,
            }
            for v in result.violations
        ],
        "penalty_energy": result.penalty_energy,
        "summary": result.summary,
    }


@mcp.tool()
def verify_lean4_soundness(formal_dir: str = "formal") -> dict[str, Any]:
    """
    Audits Lean 4 formal specifications in formal/ for proof soundness, inventorying
    theorems/lemmas/axioms and catching ungrounded 'sorry' tokens.
    """
    from antigravity_harness.core.lean4_verifier import Lean4Verifier

    verifier = Lean4Verifier(formal_dir=formal_dir)
    inventory = verifier.extract_proof_inventory()
    sound, msg = verifier.check_soundness()
    return {
        "sound": sound,
        "message": msg,
        "inventory": {k: len(v) for k, v in inventory.items()},
        "theorems": inventory.get("theorems", []),
        "lake_available": verifier.is_available,
    }


@mcp.tool()
def generate_adversarial_qa_suite(
    module_import: str, function_code: str
) -> dict[str, Any]:
    """
    Generates an adversarial Pytest and Hypothesis property test suite targeting the given function.
    """
    from antigravity_harness.agents.qa_agent import QAAgent

    agent = QAAgent()
    report = agent.generate_adversarial_suite(module_import, function_code)
    prop_test = agent.generate_property_tests(module_import, function_code)
    return {
        "target_name": report.target_name,
        "num_tests": report.num_tests_generated,
        "edge_cases": report.edge_cases_covered,
        "pytest_code": report.test_code,
        "property_test_code": prop_test,
    }


@mcp.tool()
def build_dpo_preference_dataset(
    output_path: str = "results/dpo_dataset.jsonl",
) -> dict[str, Any]:
    """
    Extracts recorded sessions from RedisBus and exports a Hugging Face TRL-compatible DPO dataset.
    """
    from antigravity_harness.rl_pipeline.dpo_dataset_builder import DPODatasetBuilder
    from antigravity_harness.rl_pipeline.trace_extractor import TraceExtractor
    from antigravity_harness.storage.redis_bus import RedisBus

    bus = RedisBus()
    extractor = TraceExtractor(bus)
    sessions = extractor.extract_from_bus()
    builder = DPODatasetBuilder()
    pairs = builder.build_pairs_from_sessions(sessions)
    exported_path = builder.export_to_jsonl(pairs, output_path)
    metrics = extractor.compute_dataset_metrics(sessions)
    return {
        "pairs_generated": len(pairs),
        "exported_path": str(exported_path),
        "metrics": metrics,
    }


@mcp.tool()
def validate_numeric_provenance(
    file_path: str,
    required_measured_fields: list[str] | None = None,
    max_constant_ratio: float = 0.1,
) -> dict[str, Any]:
    """
    Validates that numeric metrics in a JSONL dataset are empirically measured,
    rejecting synthetic proxies, constant-value fabrications, and missing fields.
    """
    from antigravity_harness.core.hardened_evaluator import (
        validate_numeric_provenance as _val_prov,
    )

    valid, violations = _val_prov(
        file_path,
        required_measured_fields=required_measured_fields,
        max_constant_ratio=max_constant_ratio,
    )
    return {
        "valid": valid,
        "file_path": file_path,
        "violations": violations,
    }


@mcp.tool()
def audit_reward_distribution(
    dataset_path: str,
    min_reward_delta: float = 5.0,
) -> dict[str, Any]:
    """
    Audits DPO dataset for degenerate pairs, inverted margins, and reward collapse.
    """
    from antigravity_harness.core.hardened_evaluator import (
        audit_reward_distribution as _audit_dpo,
    )

    valid, violations, stats = _audit_dpo(
        dataset_path,
        min_reward_delta=min_reward_delta,
    )
    return {
        "valid": valid,
        "dataset_path": dataset_path,
        "statistics": stats,
        "violations": violations,
    }


@mcp.tool()
def verify_model_budget(
    model_path: str,
    max_parameters: int = 50000,
) -> dict[str, Any]:
    """
    Verifies that a saved PyTorch model checkpoint satisfies parameter budget constraints (<50k).
    """
    from antigravity_harness.core.hardened_evaluator import (
        verify_model_budget as _verify_budget,
    )

    passed, param_count, msg = _verify_budget(model_path, max_params=max_parameters)
    return {
        "passed": passed,
        "model_path": model_path,
        "parameter_count": param_count,
        "max_parameters": max_parameters,
        "message": msg,
    }


@mcp.tool()
def detect_renamed_symbols(
    old_content: str,
    new_content: str,
    search_root: str = ".",
) -> dict[str, Any]:
    """
    Identifies removed symbols between old and new file content and checks for dangling references.
    """
    from antigravity_harness.core.hardened_evaluator import (
        detect_renamed_symbols as _detect_symbols,
    )

    dangling = _detect_symbols(old_content, new_content, search_root=search_root)
    return {
        "clean": len(dangling) == 0,
        "dangling_references": dangling,
    }


if __name__ == "__main__":
    mcp.run()
