#!/usr/bin/env python3
"""
Test Rigor Guard: Static AST auditor enforcing real, non-stubbed unit tests.
Fails on: pass, ellipsis (...), NotImplementedError, tautologies, or zero assertions.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

# Ensure UTF-8 output across Windows and POSIX
reconf_out = getattr(sys.stdout, "reconfigure", None)
if callable(reconf_out):
    try:
        reconf_out(encoding="utf-8")
    except (OSError, ValueError, AttributeError):  # Encoding reconfig
        pass
reconf_err = getattr(sys.stderr, "reconfigure", None)
if callable(reconf_err):
    try:
        reconf_err(encoding="utf-8")
    except (OSError, ValueError, AttributeError):  # Encoding reconfig
        pass


class TestStubAuditor(ast.NodeVisitor):
    __test__ = False

    def __init__(self, filename: str):

        self.filename = filename
        self.violations: list[str] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._audit_test_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._audit_test_function(node)
        self.generic_visit(node)

    def _get_functional_body(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[ast.stmt]:
        body = node.body
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            return body[1:]
        return body

    def _check_forbidden_stubs(self, body_stmts: list[ast.stmt], name: str) -> bool:
        has_forbidden_stub = False
        for stmt in body_stmts:
            if isinstance(stmt, ast.Pass):
                self.violations.append(
                    f"{self.filename}:{stmt.lineno} -> '{name}': Uses 'pass' stub."
                )
                has_forbidden_stub = True
            elif (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Constant)
                and stmt.value.value is Ellipsis
            ):
                self.violations.append(
                    f"{self.filename}:{stmt.lineno} -> '{name}': Uses ellipsis (...) stub."
                )
                has_forbidden_stub = True
            elif self._is_not_implemented(stmt):
                self.violations.append(
                    f"{self.filename}:{stmt.lineno} -> '{name}': Raises NotImplementedError."
                )
                has_forbidden_stub = True
        return has_forbidden_stub

    def _is_not_implemented(self, stmt: ast.stmt) -> bool:
        if isinstance(stmt, ast.Raise):
            if isinstance(stmt.exc, ast.Name) and stmt.exc.id == "NotImplementedError":
                return True
            if (
                isinstance(stmt.exc, ast.Call)
                and getattr(stmt.exc.func, "id", "") == "NotImplementedError"
            ):
                return True
        return False

    def _count_valid_assertions(self, node: ast.AST, name: str) -> int:
        count = 0
        for sub in ast.walk(node):
            if isinstance(sub, ast.Assert):
                if self._is_tautology(sub.test):
                    self.violations.append(
                        f"{self.filename}:{sub.lineno} -> '{name}': Tautological assert detected."
                    )
                else:
                    count += 1
            elif isinstance(sub, ast.With):
                for item in sub.items:
                    if isinstance(item.context_expr, ast.Call) and "raises" in ast.unparse(
                        item.context_expr.func
                    ):
                        count += 1
            elif isinstance(sub, ast.Call):
                func_str = ast.unparse(sub.func)
                if (
                    func_str.startswith("assert_")
                    or ".assert_" in func_str
                    or "testing.assert" in func_str
                    or func_str.startswith("self.assert")
                ):
                    count += 1
        return count

    def _audit_test_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        name = getattr(node, "name", "")
        if not name.startswith("test_"):
            return

        body_stmts = self._get_functional_body(node)
        if not body_stmts:
            self.violations.append(
                f"{self.filename}:{node.lineno} -> '{name}': "
                f"Empty test body (only docstring or blank)."
            )
            return

        has_stub = self._check_forbidden_stubs(body_stmts, name)
        assert_count = self._count_valid_assertions(node, name)

        if assert_count == 0 and not has_stub:
            self.violations.append(
                f"{self.filename}:{node.lineno} -> '{name}': "
                f"Test contains 0 assertions or pytest.raises blocks."
            )

    def _is_tautology(self, test_expr: ast.AST) -> bool:
        """Flags literal truthy checks and identical comparison sides."""
        # assert True / assert 1 / assert "string"
        if isinstance(test_expr, ast.Constant) and bool(test_expr.value) is True:
            return True

        # assert x == x or assert result is result
        if isinstance(test_expr, ast.Compare):
            left_dump = ast.dump(test_expr.left)
            for comparator in test_expr.comparators:
                if ast.dump(comparator) == left_dump:
                    return True
        return False


def audit_test_path(path: Path) -> tuple[bool, list[str]]:
    try:
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(path))
    except SyntaxError as e:
        return False, [f"{path}:{e.lineno} -> SyntaxError: {e.msg}"]

    auditor = TestStubAuditor(str(path))
    auditor.visit(tree)
    return len(auditor.violations) == 0, auditor.violations


def main() -> None:
    target_paths = (
        [Path(p) for p in sys.argv[1:]]
        if len(sys.argv) > 1
        else list(Path("tests").rglob("test_*.py"))
    )
    failed = False
    all_violations: list[str] = []

    for path in target_paths:
        if path.is_file() and path.name.startswith("test_"):
            ok, issues = audit_test_path(path)
            if not ok:
                failed = True
                all_violations.extend(issues)

    if failed:
        print("\n[FAIL] Stub Detection Failed! Hollow tests detected:")
        for v in all_violations:
            print(f"   {v}")
        sys.exit(1)

    print(f"\n[PASS] All tests in {len(target_paths)} file(s) passed anti-stub AST validation.")
    sys.exit(0)


if __name__ == "__main__":
    main()
