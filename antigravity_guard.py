#!/usr/bin/env python3
"""
Antigravity Guard: Deterministic verification harness for agent-generated Python code.
Checks AST integrity, audits phantom imports, and runs Ruff + MyPy validation.
"""

from __future__ import annotations

import ast
import importlib.metadata
import logging
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Ensure UTF-8 output even in Windows cmd/powershell cp1252 environments
reconf_out = getattr(sys.stdout, "reconfigure", None)
if callable(reconf_out):
    try:
        reconf_out(encoding="utf-8")
    except (OSError, ValueError) as exc:
        logger.debug("Could not reconfigure stdout to utf-8: %s", exc)
    except Exception as exc:
        logger.exception("Unexpected error reconfiguring stdout: %s", exc)
reconf_err = getattr(sys.stderr, "reconfigure", None)
if callable(reconf_err):
    try:
        reconf_err(encoding="utf-8")
    except (OSError, ValueError) as exc:
        logger.debug("Could not reconfigure stderr to utf-8: %s", exc)
    except Exception as exc:
        logger.exception("Unexpected error reconfiguring stderr: %s", exc)


def get_installed_packages() -> set[str]:
    """Retrieve all top-level package names installed in the active environment."""
    installed: set[str] = set()
    for dist in importlib.metadata.distributions():
        top_level = dist.read_text("top_level.txt")
        if top_level:
            for line in top_level.splitlines():
                if line.strip():
                    installed.add(line.strip().lower())
        else:
            name = dist.metadata["Name"] if "Name" in dist.metadata else None
            if name:
                installed.add(name.lower().replace("-", "_"))
    return installed


def extract_top_level_imports(tree: ast.AST) -> set[str]:
    """Extract all root module names from AST Import and ImportFrom nodes."""
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            modules.add(node.module.split(".")[0])
    return modules


def _get_local_modules(file_path: Path) -> set[str]:
    """Identify project root and directory-local modules."""
    project_root = Path.cwd().resolve()
    file_dir = file_path.parent.resolve()
    local_modules = {p.stem.lower() for p in project_root.glob("*.py")}.union(
        {p.name.lower() for p in project_root.iterdir() if p.is_dir()}
    )
    local_modules.update({p.stem.lower() for p in file_dir.glob("*.py")})
    local_modules.update({p.name.lower() for p in file_dir.iterdir() if p.is_dir()})
    local_modules.add("anse")
    return local_modules


def _find_phantom_imports(
    imports: set[str], installed_pkgs: set[str], local_modules: set[str]
) -> list[str]:
    """Find imports not belonging to stdlib, virtualenv, or local project."""
    stdlib: set[str] = getattr(sys, "stdlib_module_names", set())
    issues: list[str] = []
    for mod in sorted(imports):
        mod_norm = mod.lower()
        if (
            mod_norm not in stdlib
            and mod_norm not in installed_pkgs
            and mod_norm not in local_modules
        ):
            issues.append(
                f"Hallucinated import: '{mod}' not found in stdlib, virtualenv, or local."
            )
    return issues


def audit_file(file_path: Path, installed_pkgs: set[str]) -> tuple[bool, list[str]]:
    """Audit an individual Python file for syntax, phantom imports, and errors."""
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as err:
        return False, [f"AST Syntax Error at line {err.lineno}: {err.msg}"]

    imports = extract_top_level_imports(tree)
    local_modules = _get_local_modules(file_path)
    issues = _find_phantom_imports(imports, installed_pkgs, local_modules)
    return len(issues) == 0, issues


def run_static_analyzers(target_paths: list[str]) -> bool:
    """Run Ruff and MyPy on specified files."""
    python_exe = sys.executable

    print("Running Ruff lint & syntax checks...")
    ruff_res = subprocess.run([python_exe, "-m", "ruff", "check"] + target_paths)
    if ruff_res.returncode != 0:
        return False

    print("Running MyPy type checks...")
    mypy_res = subprocess.run([python_exe, "-m", "mypy", "--ignore-missing-imports"] + target_paths)
    return mypy_res.returncode == 0


def _collect_target_files() -> list[Path]:
    """Identify python files to check if none specified in CLI."""
    excluded = {"build", "dist", "__pycache__", "vendor", ".venv", ".git", ".agents", "results"}
    return [
        f
        for f in Path(".").rglob("*.py")
        if not any(part in excluded or part.startswith(".") for part in f.parts)
    ]


def _resolve_cli_targets() -> list[Path]:
    """Determine target files from arguments or default search."""
    cli_files = [Path(p) for p in sys.argv[1:] if p.endswith(".py")]
    return cli_files or _collect_target_files()


def _audit_all_files(target_files: list[Path], installed: set[str]) -> list[str]:
    """Run audit_file on all target files and aggregate issues."""
    all_issues: list[str] = []
    for f in target_files:
        if not f.is_file():
            continue
        ok, file_issues = audit_file(f, installed)
        if not ok:
            for issue in file_issues:
                all_issues.append(f"[{f}] {issue}")
    return all_issues


def main() -> None:
    target_files = _resolve_cli_targets()
    installed = get_installed_packages()
    all_issues = _audit_all_files(target_files, installed)

    if all_issues:
        print("\n[FAIL] Antigravity Guard Failed: Hallucination or Syntax Violations Found:")
        for issue in all_issues:
            print(f"  - {issue}")
        sys.exit(1)

    files_str = [str(f) for f in target_files]
    if not run_static_analyzers(files_str):
        print("\n[FAIL] Static analysis failed.")
        sys.exit(1)

    print("\n[PASS] All code passed AST verification, import auditing, and type checks.")
    sys.exit(0)


if __name__ == "__main__":
    main()
