#!/usr/bin/env python3
"""
Execution Attestation Gate: Validates real execution and rejects phantom completions,
stubbed bodies, and hardcoded synthetic data.
"""

from __future__ import annotations

import ast
import datetime
import json
import os
import secrets
import subprocess
import sys
from pathlib import Path

ATTESTATION_FILE = Path(".antigravity_attestation")


# Ensure UTF-8 output across Windows and POSIX
reconf_out = getattr(sys.stdout, "reconfigure", None)
if callable(reconf_out):
    try:
        reconf_out(encoding="utf-8")
        reconf_err = getattr(sys.stderr, "reconfigure", None)
        if callable(reconf_err):
            reconf_err(encoding="utf-8")
    except Exception:
        pass

SUSPICIOUS_DATA_PREFIXES = ("mock_", "dummy_", "fake_", "sample_", "test_data_")


class ImplementationAuditor(ast.NodeVisitor):
    def __init__(self, filename: str):
        self.filename = filename.replace("\\", "/")
        self.violations: list[str] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._audit_callable(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._audit_callable(node)
        self.generic_visit(node)

    def _strip_docstring(self, body: list[ast.stmt]) -> list[ast.stmt]:
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            return body[1:]
        return body

    def _check_stubs(
        self, stmt: ast.stmt, node: ast.FunctionDef | ast.AsyncFunctionDef, name: str
    ) -> None:

        if isinstance(stmt, ast.Pass):
            self.violations.append(f"{self.filename}:{node.lineno} '{name}' uses 'pass' stub.")
        elif (
            isinstance(stmt, ast.Expr)
            and isinstance(stmt.value, ast.Constant)
            and stmt.value.value is Ellipsis
        ):
            self.violations.append(
                f"{self.filename}:{node.lineno} '{name}' uses ellipsis (...) stub."
            )
        elif isinstance(stmt, ast.Raise):
            exc_id = getattr(stmt.exc, "id", "") or getattr(
                getattr(stmt.exc, "func", None), "id", ""
            )
            if exc_id == "NotImplementedError":
                self.violations.append(
                    f"{self.filename}:{node.lineno} '{name}' raises NotImplementedError."
                )

    def _check_fake_data(self, stmt: ast.stmt) -> None:
        if not isinstance(stmt, ast.Assign) or "tests/" in self.filename:
            return
        for target in stmt.targets:
            if isinstance(target, ast.Name):
                var_name = target.id.lower()
                if any(var_name.startswith(p) for p in SUSPICIOUS_DATA_PREFIXES):
                    self.violations.append(
                        f"{self.filename}:{stmt.lineno} '{var_name}': Hardcoded synthetic data "
                        f"detected in production logic. Real retrieval required."
                    )

    def _audit_callable(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        name = getattr(node, "name", "")
        body = self._strip_docstring(node.body)

        if not body:
            self.violations.append(f"{self.filename}:{node.lineno} '{name}' is an empty stub.")
            return

        if len(body) == 1:
            self._check_stubs(body[0], node, name)

        for stmt in body:
            self._check_fake_data(stmt)


def _check_coverage_json(target_module: str, cov_file: Path) -> bool:
    """Validate that coverage data recorded non-zero lines executed for target_module."""
    try:
        with open(cov_file, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False

    files = data.get("files", {})
    for filepath, details in files.items():
        clean_path = filepath.replace("\\", "/")
        if target_module in clean_path:
            executed_lines = len(details.get("executed_lines", []))
            if executed_lines == 0:
                print(f"❌ Phantom execution detected: 0 lines executed in {filepath}.")
                return False
    return True


def _resolve_test_targets(target_module: str, test_path: str = "") -> list[str]:
    """Resolve specific test target paths for the module to ensure fast, deterministic verification."""
    if test_path:
        return [test_path]
    if target_module == "anse.symbolic":
        return [
            "tests/phase1/test_sandbox.py",
            "tests/phase1/test_evaluator.py",
            "tests/phase1/test_parser.py",
        ]
    if target_module == "anse.jepa":
        return ["tests/phase2/test_jepa_world_model.py"]
    return []


def verify_runtime_execution_receipt(target_module: str, test_path: str = "") -> bool:
    """Runs pytest under coverage to prove the modified code actually executed at runtime."""
    python_exe = sys.executable
    cmd = [
        python_exe,
        "-m",
        "pytest",
        f"--cov={target_module}",
        "--cov-report=json",
        "-q",
        "--disable-warnings",
    ]
    targets = _resolve_test_targets(target_module, test_path)
    cmd.extend(targets)
    env = dict(os.environ)
    res = subprocess.run(cmd, env=env, capture_output=True, text=True, check=False)

    if res.returncode != 0:
        print("❌ Test suite failed to execute successfully.")
        if res.stdout:
            print(f"STDOUT:\n{res.stdout[-1000:]}")
        if res.stderr:
            print(f"STDERR:\n{res.stderr[-1000:]}")
        return False

    cov_file = Path("coverage.json") if Path("coverage.json").exists() else Path(".coverage.json")
    if not cov_file.exists():
        subprocess.run(
            [python_exe, "-m", "coverage", "json", "-o", "coverage.json"],
            env=env,
            check=False,
        )
        cov_file = Path("coverage.json")

    if not cov_file.exists():
        print("❌ Coverage data missing. The test suite did not record execution traces.")
        return False

    return _check_coverage_json(target_module, cov_file)


def _get_git_diff_files() -> list[str]:
    """Retrieve modified file paths tracked by git relative to HEAD."""
    try:
        diff_output = subprocess.check_output(
            ["git", "diff", "--name-only", "--diff-filter=d", "HEAD"], text=True
        )
        return [line.strip() for line in diff_output.splitlines() if line.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def _get_untracked_files() -> list[str]:
    """Retrieve untracked or newly staged Python files from git status."""
    try:
        status_output = subprocess.check_output(["git", "status", "--porcelain"], text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    diff_files: list[str] = []
    for line in status_output.splitlines():
        parts = line.strip().split(maxsplit=1)
        if len(parts) == 2 and parts[1].endswith(".py"):
            diff_files.append(parts[1])
    return diff_files


def _audit_single_file(filepath: str) -> list[str]:
    """Parse and audit a single Python file for stubs and fake data."""
    path = Path(filepath)
    if not path.is_file():
        return []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=filepath)
        auditor = ImplementationAuditor(filepath)
        auditor.visit(tree)
        return auditor.violations
    except SyntaxError as err:
        return [f"{filepath}:{err.lineno} SyntaxError: {err.msg}"]


def audit_git_diff() -> list[str]:
    """Inspects all modified, staged, and untracked Python files in the current workspace."""
    diff_files = set(_get_git_diff_files())
    diff_files.update(_get_untracked_files())

    py_files = sorted(f for f in diff_files if f.endswith(".py"))
    all_violations: list[str] = []
    for f in py_files:
        all_violations.extend(_audit_single_file(f))
    return all_violations


def generate_attestation_proof(target_module: str = "") -> str:
    """Generate cryptographic proof of verified execution and write to attestation receipt."""
    token = secrets.token_hex(16)
    receipt = {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "target_module": target_module or "workspace",
        "proof_token": token,
        "status": "ATTESTED",
        "verifier": "Antigravity-Execution-Attestation-Gate/1.0",
    }
    ATTESTATION_FILE.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return token


def attest_execution(target_module: str = "", test_path: str = "") -> tuple[bool, str, list[str]]:
    """Programmatic entry point to perform complete audit and mint proof token."""
    violations = audit_git_diff()
    if violations:
        return False, "", violations

    if target_module:
        if not verify_runtime_execution_receipt(target_module, test_path):
            return False, "", [f"Runtime coverage verification failed for module: {target_module}"]

    token = generate_attestation_proof(target_module)
    return True, token, []


def main() -> None:
    print("==> Auditing workspace for hollow implementations and phantom completions...")
    violations = audit_git_diff()

    if violations:
        print("\n❌ ATTESTATION FAILED: Code contains stubs or simulated data:")
        for v in violations:
            print(f"   {v}")
        sys.exit(1)

    module = sys.argv[1] if len(sys.argv) > 1 else ""
    test_path = sys.argv[2] if len(sys.argv) > 2 else ""
    if module:
        print(f"==> Verifying runtime execution trace for '{module}'...")
        if not verify_runtime_execution_receipt(module, test_path):
            sys.exit(1)

    token = generate_attestation_proof(module)
    print("\n✅ Verification passed: Real implementation verified with zero stubs.")
    print(f"[PROOF_TOKEN: {token}]")
    sys.exit(0)


if __name__ == "__main__":
    main()
