"""Fail-closed Python/Rust candidate gate backed by GWAYA (github.com/xaviercallens/GWAYA-GwenLayaOpenModel, v3.7.1).

A candidate is ACCEPTed only if (1) the AST zero-stub audit is clean AND (2) the candidate plus its tests
actually ran to exit 0 inside GWAYA's bubblewrap sandbox. Anything that cannot be established is BLOCKED,
never accepted: no bwrap isolation, no rustc, a timeout. This matches CLAUDE.md ("a stage that cannot run
reports BLOCKED") and never sets GWAYA_ALLOW_UNISOLATED -- untrusted code is not run without isolation.

Lean verification is deliberately NOT routed through here: it goes through anse/formal/lean_runner.py only.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Literal

from gwaya.ast_audit import ZeroStubAudit
from gwaya.oracles import RustCompilerOracle
from gwaya.sandbox import is_sandbox_available, run_in_sandbox

Status = Literal["ACCEPT", "REJECT", "BLOCKED"]
SandboxRunner = Callable[..., tuple[bool, str, str, bool]]


@dataclass(frozen=True)
class GateVerdict:
    status: Status
    language: str
    reasons: tuple[str, ...] = field(default_factory=tuple)
    stdout: str = ""
    stderr: str = ""

    @property
    def accepted(self) -> bool:
        return self.status == "ACCEPT"


def verify_python(
    code: str,
    tests: str = "",
    *,
    timeout_s: float = 10.0,
    sandbox_available: Callable[[], bool] = is_sandbox_available,
    runner: SandboxRunner = run_in_sandbox,
) -> GateVerdict:
    """Gate a Python candidate. `tests` (asserts) are appended and must run to exit 0; with no tests the
    candidate must still import/execute cleanly, which is a weaker check -- callers should pass tests."""
    audit = ZeroStubAudit.audit_python_code(code)
    if not audit.is_clean:
        return GateVerdict("REJECT", "python", tuple(audit.violations))
    if not sandbox_available():
        return GateVerdict("BLOCKED", "python", ("bwrap isolation unavailable: refusing to execute untrusted code",))
    program = code.rstrip() + "\n\n" + tests.strip() + "\n" if tests.strip() else code
    ok, out, err, timed_out = runner(
        [sys.executable, "-I", "/work/cand.py"],
        timeout_s=timeout_s, mem_mb=1024, cpu_s=int(timeout_s) + 5, files={"cand.py": program},
    )
    if timed_out:
        return GateVerdict("BLOCKED", "python", (f"timed out after {timeout_s}s",), out, err)
    if "UNVERIFIED" in (err or ""):
        return GateVerdict("BLOCKED", "python", ((err or "").strip()[-200:],), out, err)
    if not ok:
        return GateVerdict("REJECT", "python", ("execution failed: " + (err or "").strip()[-200:],), out, err)
    return GateVerdict("ACCEPT", "python", (), out, err)


def verify_rust(code: str, *, oracle: RustCompilerOracle | None = None) -> GateVerdict:
    """Gate a Rust snippet: placeholder-macro rejection + `rustc --emit=metadata` in the sandbox."""
    audit = ZeroStubAudit.audit_rust_code(code)
    if not audit.is_clean:
        return GateVerdict("REJECT", "rust", tuple(audit.violations))
    res = (oracle or RustCompilerOracle()).verify_snippet(code)
    if res.details.get("unverified"):
        return GateVerdict("BLOCKED", "rust", (res.error_message,), res.stdout, res.stderr)
    if not res.success:
        return GateVerdict("REJECT", "rust", (res.error_message,), res.stdout, res.stderr)
    return GateVerdict("ACCEPT", "rust", (), res.stdout, res.stderr)
