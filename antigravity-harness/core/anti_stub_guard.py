"""
Anti-Stub Guard: AST Analyzer & Anti-Mock Implementation Auditor.
Rejects placeholder implementations, fake mock data, and simulation shortcuts
under the ANSE Energy Physics paradigm (E = 10^6 on violation).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Violation:
    """Represents a flagged stub, mock, or simulation pattern."""

    filename: str
    lineno: int
    rule: str
    symbol_name: str
    message: str


@dataclass
class AuditResult:
    """Outcome of an anti-stub audit."""

    is_clean: bool
    violations: list[Violation] = field(default_factory=list)
    penalty_energy: float = 0.0

    @property
    def summary(self) -> str:
        if self.is_clean:
            return "Audit PASSED: No stubs or mock simulations detected."
        items = "\n".join(
            f"  - [{v.rule}] {v.filename}:{v.lineno} in '{v.symbol_name}': {v.message}"
            for v in self.violations
        )
        return f"Audit FAILED ({len(self.violations)} violations, Energy penalty={self.penalty_energy:.1e}):\n{items}"


SUSPICIOUS_MOCK_PREFIXES = ("mock_", "dummy_", "fake_", "sample_", "test_data_")
MAX_PENALTY_ENERGY = 1_000_000.0  # Maximum pain in ANSE computational physics


class ASTStubVisitor(ast.NodeVisitor):
    """AST Visitor scanning for stubs, ellipsis, empty bodies, and synthetic artifacts."""

    def __init__(self, filename: str) -> None:
        self.filename = filename.replace("\\", "/")
        self.violations: list[Violation] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_callable(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_callable(node)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        self._check_assignment(node)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        self._check_suspicious_calls(node)
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        self._check_subtraction_identity(node)
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        self._check_tautological_compare(node)
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

    def _check_callable(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        real_body = self._strip_docstring(node.body)

        # 1. Empty body or docstring only
        if not real_body:
            self.violations.append(
                Violation(
                    filename=self.filename,
                    lineno=node.lineno,
                    rule="EMPTY_BODY",
                    symbol_name=node.name,
                    message="Function body has only docstrings or is completely empty.",
                )
            )
            return

        # Enforce minimum structural complexity for numerical PDE/integrator kernels
        # Bypassing the sandbox with just an invariant comment is a known reward hack
        node_count = sum(1 for _ in ast.walk(node))
        if node_count < 50 and any(kw in node.name.lower() for kw in ["eval_python", "solve", "integrate", "kernel"]):
            self.violations.append(
                Violation(
                    filename=self.filename,
                    lineno=node.lineno,
                    rule="TRIVIAL_COMPLEXITY_HACK",
                    symbol_name=node.name,
                    message=f"Numerical kernel too trivial (AST nodes: {node_count} < 50). Suspected reward hack.",
                )
            )
            return

        # 2. Single-statement stubs
        if len(real_body) == 1:
            stmt = real_body[0]

            if isinstance(stmt, ast.Pass):
                self.violations.append(
                    Violation(
                        filename=self.filename,
                        lineno=node.lineno,
                        rule="PASS_STUB",
                        symbol_name=node.name,
                        message="Function body contains only 'pass'.",
                    )
                )
            elif (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Constant)
                and stmt.value.value is Ellipsis
            ):
                self.violations.append(
                    Violation(
                        filename=self.filename,
                        lineno=node.lineno,
                        rule="ELLIPSIS_STUB",
                        symbol_name=node.name,
                        message="Function body contains only '...'.",
                    )
                )
            elif isinstance(stmt, ast.Raise):
                exc = stmt.exc
                exc_id = getattr(exc, "id", "") or getattr(getattr(exc, "func", None), "id", "")
                if exc_id in ("NotImplementedError", "NotImplemented"):
                    self.violations.append(
                        Violation(
                            filename=self.filename,
                            lineno=node.lineno,
                            rule="NOT_IMPLEMENTED_STUB",
                            symbol_name=node.name,
                            message=f"Function raises ungrounded '{exc_id}'.",
                        )
                    )
            elif isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Constant):
                # Flag functions with parameters whose entire body is returning a static constant
                if len(node.args.args) > 0 and stmt.value.value in (True, False, 0, "", None, []):
                    self.violations.append(
                        Violation(
                            filename=self.filename,
                            lineno=node.lineno,
                            rule="TRIVIAL_CONSTANT_RETURN",
                            symbol_name=node.name,
                            message=f"Function takes {len(node.args.args)} parameter(s) but returns constant {stmt.value.value!r} without computation.",
                        )
                    )

    def visit_Try(self, node: ast.Try) -> None:
        if "test" not in self.filename.lower():
            for handler in node.handlers:
                real_hbody = self._strip_docstring(handler.body)
                if len(real_hbody) == 1 and isinstance(real_hbody[0], ast.Pass):
                    self.violations.append(
                        Violation(
                            filename=self.filename,
                            lineno=handler.lineno,
                            rule="SILENT_EXCEPTION_SWALLOW",
                            symbol_name=f"except {getattr(handler.type, 'id', 'Exception')}",
                            message="Exception block silently swallows errors with 'pass'.",
                        )
                    )
        self.generic_visit(node)

    def _check_assignment(self, node: ast.Assign) -> None:
        # Check variable naming for mock/synthetic data in non-test code
        if "test" in self.filename.lower():
            return

        for target in node.targets:
            if isinstance(target, ast.Name):
                name_lower = target.id.lower()
                for prefix in SUSPICIOUS_MOCK_PREFIXES:
                    if name_lower.startswith(prefix):
                        self.violations.append(
                            Violation(
                                filename=self.filename,
                                lineno=node.lineno,
                                rule="SYNTHETIC_MOCK_DATA",
                                symbol_name=target.id,
                                message=f"Suspicious synthetic variable name with prefix '{prefix}'.",
                            )
                        )

    def _check_suspicious_calls(self, node: ast.Call) -> None:
        # Detect time.sleep or mock instantiation in non-test logic
        if "test" in self.filename.lower():
            return

        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "sleep":
            if isinstance(func.value, ast.Name) and func.value.id == "time":
                self.violations.append(
                    Violation(
                        filename=self.filename,
                        lineno=node.lineno,
                        rule="TIME_SLEEP_SIMULATION",
                        symbol_name="time.sleep",
                        message="Detected time.sleep simulation in production logic.",
                    )
                )

        if isinstance(func, ast.Name) and func.id in ("Mock", "MagicMock", "PropertyMock"):
            self.violations.append(
                Violation(
                    filename=self.filename,
                    lineno=node.lineno,
                    rule="MOCK_INSTANTIATION",
                    symbol_name=func.id,
                    message=f"Instantiating unit test mock '{func.id}' in production logic.",
                )
            )

    def _check_subtraction_identity(self, node: ast.BinOp) -> None:
        if "test" in self.filename.lower():
            return
        if isinstance(node.op, ast.Sub):
            # Check for constant subtraction c - c
            if isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant):
                if node.left.value == node.right.value and node.left.value != 0:
                    self.violations.append(
                        Violation(
                            filename=self.filename,
                            lineno=node.lineno,
                            rule="TRIVIAL_IDENTITY_SUBTRACTION",
                            symbol_name="-",
                            message=f"Trivial scalar subtraction ({node.left.value} - {node.right.value}) mocks numerical computation.",
                        )
                    )
            elif isinstance(node.left, ast.Name) and isinstance(node.right, ast.Name):
                if node.left.id == node.right.id:
                    self.violations.append(
                        Violation(
                            filename=self.filename,
                            lineno=node.lineno,
                            rule="TRIVIAL_IDENTITY_SUBTRACTION",
                            symbol_name="-",
                            message=f"Trivial variable self-subtraction ({node.left.id} - {node.right.id}) mocks numerical computation.",
                        )
                    )

    def _check_tautological_compare(self, node: ast.Compare) -> None:
        if "test" in self.filename.lower():
            return
        for op, comp in zip(node.ops, node.comparators):
            if isinstance(op, ast.Eq):
                if isinstance(node.left, ast.Constant) and isinstance(comp, ast.Constant):
                    if node.left.value == comp.value and node.left.value not in (0, 0.0, None, "", False):
                        self.violations.append(
                            Violation(
                                filename=self.filename,
                                lineno=node.lineno,
                                rule="TAUTOLOGICAL_EQUALITY_TEST",
                                symbol_name="==",
                                message=f"Trivial constant equality check ({node.left.value} == {comp.value}) bypasses dynamic verification.",
                            )
                        )


class AntiStubGuard:
    """Audits source code or files against stubbing, fake data, and simulation patterns."""

    def audit_code(self, source_code: str, filename: str = "candidate.py") -> AuditResult:
        """Audits a raw string of Python source code."""
        try:
            tree = ast.parse(source_code, filename=filename)
        except SyntaxError as err:
            return AuditResult(
                is_clean=False,
                violations=[
                    Violation(
                        filename=filename,
                        lineno=err.lineno or 1,
                        rule="SYNTAX_ERROR",
                        symbol_name="<parser>",
                        message=f"Syntax error prevents AST audit: {err.msg}",
                    )
                ],
                penalty_energy=MAX_PENALTY_ENERGY,
            )

        visitor = ASTStubVisitor(filename)
        visitor.visit(tree)

        is_clean = len(visitor.violations) == 0
        penalty = 0.0 if is_clean else MAX_PENALTY_ENERGY
        return AuditResult(is_clean=is_clean, violations=visitor.violations, penalty_energy=penalty)

    def audit_file(self, file_path: str | Path) -> AuditResult:
        """Reads and audits a single file."""
        path = Path(file_path)
        if not path.exists():
            return AuditResult(
                is_clean=False,
                violations=[
                    Violation(
                        filename=str(path),
                        lineno=0,
                        rule="FILE_NOT_FOUND",
                        symbol_name="",
                        message="File does not exist.",
                    )
                ],
                penalty_energy=MAX_PENALTY_ENERGY,
            )

        content = path.read_text(encoding="utf-8", errors="replace")
        return self.audit_code(content, filename=str(path))

    def audit_directory(self, dir_path: str | Path, exclude_tests: bool = True) -> AuditResult:
        """Recursively audits Python files in a directory."""
        path = Path(dir_path)
        all_violations: list[Violation] = []

        ignored_dirs = {".venv", "venv", ".git", "build", "dist", "__pycache__", "node_modules", "vendor", ".scratchpad"}
        for p in path.rglob("*.py"):
            if any(part in ignored_dirs for part in p.parts):
                continue
            if exclude_tests and ("test" in p.name.lower() or "tests" in p.parts):
                continue
            res = self.audit_file(p)
            all_violations.extend(res.violations)

        is_clean = len(all_violations) == 0
        return AuditResult(
            is_clean=is_clean,
            violations=all_violations,
            penalty_energy=0.0 if is_clean else MAX_PENALTY_ENERGY,
        )
