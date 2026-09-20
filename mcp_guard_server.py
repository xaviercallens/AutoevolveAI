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
            "rank": cc.letter_grade(block.complexity),
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


if __name__ == "__main__":
    mcp.run()
