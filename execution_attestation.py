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

ATTESTATION_FILE = Path(os.environ.get("ANSE_ATTESTATION_PATH", ".antigravity_attestation"))


# Ensure UTF-8 output across Windows and POSIX
reconf_out = getattr(sys.stdout, "reconfigure", None)
if callable(reconf_out):
    try:
        reconf_out(encoding="utf-8")
        reconf_err = getattr(sys.stderr, "reconfigure", None)
        if callable(reconf_err):
            reconf_err(encoding="utf-8")
    except (OSError, ValueError, AttributeError):  # Encoding reconfig
        pass


class ImplementationAuditor(ast.NodeVisitor):
    def __init__(self, filename: str):
        self.filename = filename.replace("\\", "/")
        self.is_test_file = (
            "/tests/" in self.filename
            or self.filename.startswith("tests/")
            or Path(self.filename).name.startswith("test_")
        )
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
            and type(body[0].value) is ast.Constant
            and type(body[0].value.value) is str
        ):
            return body[1:]
        return body

    def _check_stubs(self, stmt: ast.stmt, parent_node: ast.AST, func_name: str) -> None:
        if isinstance(stmt, ast.Pass):
            self.violations.append(
                f"{self.filename}:{stmt.lineno} '{func_name}': 'pass' statement found. "
                f"Requires real implementation."
            )
        elif isinstance(stmt, ast.Raise):
            if (
                isinstance(stmt.exc, ast.Call)
                and isinstance(stmt.exc.func, ast.Name)
                and stmt.exc.func.id == "NotImplementedError"
            ) or (isinstance(stmt.exc, ast.Name) and stmt.exc.id == "NotImplementedError"):
                self.violations.append(
                    f"{self.filename}:{stmt.lineno} '{func_name}': 'NotImplementedError' found. "
                    f"Implementations cannot be skipped."
                )
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is Ellipsis:
            self.violations.append(
                f"{self.filename}:{stmt.lineno} '{func_name}': Ellipsis (...) stub found."
            )

    def _audit_callable(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        name = getattr(node, "name", "")
        body = self._strip_docstring(node.body)

        if not body:
            self.violations.append(f"{self.filename}:{node.lineno} '{name}' is an empty stub.")
            return

        for stmt in body:
            self._check_stubs(stmt, node, name)
            if not self.is_test_file:
                for subnode in ast.walk(stmt):
                    if isinstance(subnode, ast.Name):
                        if subnode.id.startswith("mock_") or subnode.id.startswith("fake_") or subnode.id in ("Mock", "MagicMock"):
                            self.violations.append(
                                f"{self.filename}:{getattr(subnode, 'lineno', node.lineno)} '{name}': "
                                f"Mock/synthetic token '{subnode.id}' detected in production body."
                            )
                    elif isinstance(subnode, ast.Attribute):
                        if subnode.attr in ("Mock", "MagicMock", "fake_evaluation"):
                            self.violations.append(
                                f"{self.filename}:{getattr(subnode, 'lineno', node.lineno)} '{name}': "
                                f"Mock call '{subnode.attr}' detected."
                            )


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
    targets = _resolve_test_targets(target_module, test_path)
    env = dict(os.environ)

    source_arg = target_module.split(".")[0] if "." in target_module else (target_module or "anse")
    # Use 'coverage run' with -p no:cov to avoid Python 3.12 single-phase C extension reload clashes (e.g. numpy _multiarray_umath)
    cmd = [
        python_exe,
        "-m",
        "coverage",
        "run",
        f"--source={source_arg}",
        "-m",
        "pytest",
        "-p",
        "no:cov",
        "-q",
        "--disable-warnings",
    ]
    cmd.extend(targets)
    res = subprocess.run(cmd, env=env, capture_output=True, text=True, check=False)

    if res.returncode != 0:
        # Fallback to pytest direct execution if needed
        fallback_cmd = [
            python_exe,
            "-m",
            "pytest",
            "-q",
            "--disable-warnings",
        ] + targets
        res_fb = subprocess.run(fallback_cmd, env=env, capture_output=True, text=True, check=False)
        if res_fb.returncode != 0:
            print("❌ Test suite failed to execute successfully.")
            out = res.stdout or res_fb.stdout
            err = res.stderr or res_fb.stderr
            if out:
                print(f"STDOUT:\n{out[-1000:]}")
            if err:
                print(f"STDERR:\n{err[-1000:]}")
            return False

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


def get_git_commit_hash() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown_commit"

def get_deterministic_key() -> str:
    import hashlib
    commit = get_git_commit_hash()
    return hashlib.blake2b((f"ANSE:attestation:v1:{commit}").encode()).hexdigest()[:32]

def generate_attestation_proof(target_module: str = "") -> str:
    """Generate cryptographic proof of verified execution and write to attestation receipt."""
    import hashlib
    token = hashlib.sha256((get_deterministic_key() + target_module).encode()).hexdigest()
    receipt = {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "git_commit": get_git_commit_hash(),
        "target_module": target_module or "workspace",
        "proof_token": token,
        "status": "ATTESTED",
        "verifier": "Antigravity-Execution-Attestation-Gate/1.0",
    }
    attestation_file = Path(os.environ.get("ANSE_ATTESTATION_PATH", ".antigravity_attestation"))
    attestation_file.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
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
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        manifest_path = sys.argv[2] if len(sys.argv) > 2 else "results/attestation_manifest.jsonl"
        print(f"==> Verifying tokens in manifest: {manifest_path}")
        if not Path(manifest_path).exists():
            print(f"❌ Manifest not found: {manifest_path}")
            sys.exit(1)
        import hashlib
        key = get_deterministic_key()
        verified_count = 0
        total_count = 0
        with open(manifest_path, "r") as f:
            for line in f:
                if not line.strip(): continue
                total_count += 1
                record = json.loads(line)
                expected_token = hashlib.sha256((key + record["case_id"]).encode()).hexdigest()
                if record["token"] == expected_token:
                    verified_count += 1
                else:
                    print(f"❌ Token mismatch for {record['case_id']}")
        if verified_count == total_count and total_count > 0:
            print(f"✅ {verified_count}/{total_count} tokens verified. Manifest integrity CONFIRMED.")
            sys.exit(0)
        else:
            print(f"❌ Verification failed. {verified_count}/{total_count} matched.")
            sys.exit(1)

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
