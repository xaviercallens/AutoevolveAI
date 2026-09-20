"""
Two-tier sandboxed code executor.

Tier 1 (fast):   subprocess with resource limits — used for most executions.
Tier 2 (secure): Docker container with network isolation — triggered automatically
                 when the code imports a "dangerous" module detected via AST scan.

The public API is a single :class:`SandboxExecutor` that transparently selects
the appropriate tier and returns a uniform :class:`ExecutionResult`.
"""

from __future__ import annotations

import ast
import os
import subprocess
import sys
import tempfile
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path

from anse.config import SandboxConfig, get_config

# ─── Result type ─────────────────────────────────────────────────────────────


@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    returncode: int
    timed_out: bool
    duration_ms: float
    tier_used: int  # 1 or 2
    dangerous_imports: list[str] = field(default_factory=list)
    """AST-detected dangerous imports that triggered tier escalation."""
    peak_ram_mb: float = 0.0
    """Peak RAM consumption in Megabytes during execution."""


# ─── AST safety scanner ──────────────────────────────────────────────────────


class _DangerousImportVisitor(ast.NodeVisitor):
    """Walk an AST and collect imports from a blocklist."""

    def __init__(self, blocklist: list[str]) -> None:
        self.blocklist = set(blocklist)
        self.found: list[str] = []

    def visit_Import(self, node: ast.Import) -> None:  # noqa: N802
        for alias in node.names:
            root = alias.name.split(".")[0]
            if root in self.blocklist:
                self.found.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # noqa: N802
        if node.module:
            root = node.module.split(".")[0]
            if root in self.blocklist:
                self.found.append(node.module)
        self.generic_visit(node)


def scan_dangerous_imports(code: str, blocklist: list[str]) -> list[str]:
    """
    Parse *code* with the AST and return any imports matching *blocklist*.
    Returns an empty list if the code cannot be parsed (syntax error will
    surface later during execution).
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    visitor = _DangerousImportVisitor(blocklist)
    visitor.visit(tree)
    return visitor.found


# ─── Tier 1 — subprocess ─────────────────────────────────────────────────────

_RUNNER_SCRIPT = textwrap.dedent("""
import sys
import runpy
try:
    import resource
except ImportError:
    resource = None

try:
    import psutil
except ImportError:
    psutil = None

import time
import traceback

target = sys.argv[1]
mem_out = sys.argv[2]
time_out = sys.argv[3] if len(sys.argv) > 3 else None
sys.argv = [target] + sys.argv[4:]
exit_code = 0

# Pre-warm runtime environment so module startup latency does not mask pure algorithmic physics
try:
    import numpy  # noqa: F401
except ImportError:
    pass

t_start = time.perf_counter()
try:
    runpy.run_path(target, run_name="__main__")
except SystemExit as e:
    exit_code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
except Exception:
    traceback.print_exc()
    exit_code = 1
finally:
    t_end = time.perf_counter()
    duration_ms = (t_end - t_start) * 1000.0
    try:
        mb = 0.0
        if resource is not None:
            kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            mb = kb / (1024.0 * 1024.0) if sys.platform == "darwin" else kb / 1024.0
        elif psutil is not None:
            proc = psutil.Process()
            mem_info = proc.memory_info()
            mb = getattr(mem_info, "peak_wset", mem_info.rss) / (1024.0 * 1024.0)
        with open(mem_out, "w", encoding="utf-8") as f:
            f.write(f"{mb:.4f}")
        if time_out:
            with open(time_out, "w", encoding="utf-8") as f:
                f.write(f"{duration_ms:.4f}")
    except Exception:
        pass

sys.exit(exit_code)
""").strip()


def _tier1_execute(code: str, timeout: float) -> ExecutionResult:
    """
    Run *code* in a temporary directory via subprocess.
    Inherits no environment variables (clean env).
    Measures duration (ms) and peak RAM (MB).
    """
    with tempfile.TemporaryDirectory(prefix="anse_t1_") as tmpdir:
        script_path = Path(tmpdir) / "solution.py"
        script_path.write_text(code, encoding="utf-8")
        runner_path = Path(tmpdir) / "_runner.py"
        runner_path.write_text(_RUNNER_SCRIPT, encoding="utf-8")
        mem_path = Path(tmpdir) / "_mem.txt"
        time_path = Path(tmpdir) / "_time.txt"

        start = time.perf_counter()
        try:
            sub_env = {"PATH": os.environ.get("PATH", ""), "HOME": tmpdir}
            if sys.platform == "win32":
                for k in (
                    "SYSTEMROOT",
                    "WINDIR",
                    "TEMP",
                    "TMP",
                    "SYSTEMDRIVE",
                    "COMSPEC",
                    "PATHEXT",
                ):
                    if k in os.environ:
                        sub_env[k] = os.environ[k]

            proc = subprocess.run(
                [sys.executable, str(runner_path), str(script_path), str(mem_path), str(time_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmpdir,
                env=sub_env,
            )
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            if time_path.exists():
                try:
                    elapsed_ms = float(time_path.read_text(encoding="utf-8").strip())
                except Exception:
                    pass

            peak_ram = 0.0
            if mem_path.exists():
                try:
                    peak_ram = float(mem_path.read_text(encoding="utf-8").strip())
                except Exception:
                    peak_ram = 0.0

            return ExecutionResult(
                stdout=proc.stdout,
                stderr=proc.stderr,
                returncode=proc.returncode,
                timed_out=False,
                duration_ms=elapsed_ms,
                tier_used=1,
                peak_ram_mb=peak_ram,
            )
        except subprocess.TimeoutExpired:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return ExecutionResult(
                stdout="",
                stderr=f"Execution timed out after {timeout}s",
                returncode=-1,
                timed_out=True,
                duration_ms=elapsed_ms,
                tier_used=1,
                peak_ram_mb=0.0,
            )


# ─── Tier 2 — Docker ─────────────────────────────────────────────────────────


def _tier2_execute(
    code: str,
    timeout: float,
    cfg: SandboxConfig,
    dangerous_imports: list[str],
) -> ExecutionResult:
    """
    Run *code* inside a Docker container for stronger isolation.
    Falls back gracefully to Tier 1 if Docker is unavailable.
    """
    try:
        import docker  # type: ignore[import-untyped]

        client = docker.from_env()
    except Exception:
        # Docker not available — fall back to Tier 1 with a warning in stderr
        result = _tier1_execute(code, timeout)
        result.tier_used = 2
        result.stderr = "[WARN] Docker unavailable, fell back to Tier-1 sandbox.\n" + result.stderr
        result.dangerous_imports = dangerous_imports
        return result

    with tempfile.TemporaryDirectory(prefix="anse_t2_") as tmpdir:
        script_path = Path(tmpdir) / "solution.py"
        script_path.write_text(code, encoding="utf-8")

        start = time.perf_counter()
        try:
            container = client.containers.run(
                image=cfg.docker_image,
                command=["python", "/workspace/solution.py"],
                volumes={tmpdir: {"bind": "/workspace", "mode": "ro"}},
                mem_limit=cfg.docker_mem_limit,
                cpu_count=int(cfg.docker_cpu_count),
                network_disabled=True,
                remove=True,
                detach=False,
                stdout=True,
                stderr=True,
                timeout=int(timeout) + 2,
            )
            elapsed_ms = (time.perf_counter() - start) * 1000
            output = container.decode("utf-8") if isinstance(container, bytes) else str(container)
            return ExecutionResult(
                stdout=output,
                stderr="",
                returncode=0,
                timed_out=False,
                duration_ms=elapsed_ms,
                tier_used=2,
                dangerous_imports=dangerous_imports,
            )
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000
            timed_out = "timed out" in str(exc).lower() or "timeout" in str(exc).lower()
            return ExecutionResult(
                stdout="",
                stderr=str(exc),
                returncode=-1,
                timed_out=timed_out,
                duration_ms=elapsed_ms,
                tier_used=2,
                dangerous_imports=dangerous_imports,
            )


# ─── Public executor ─────────────────────────────────────────────────────────


class SandboxExecutor:
    """
    Transparently selects Tier-1 (subprocess) or Tier-2 (Docker) execution
    based on an AST scan of the code's imports.

    Usage::

        executor = SandboxExecutor()
        result = executor.execute("print('hello')")
        print(result.stdout)  # "hello"
    """

    def __init__(
        self,
        cfg: SandboxConfig | None = None,
        config: SandboxConfig | None = None,
    ) -> None:
        self._cfg = config or cfg or get_config().sandbox

    def execute(self, code: str, force_tier: int | None = None) -> ExecutionResult:
        """
        Execute *code* in the appropriate sandbox tier.

        Parameters
        ----------
        code:
            Raw Python source string to execute.
        force_tier:
            If 1 or 2, skip the AST scan and use that tier directly.
            Useful for testing.

        Returns
        -------
        :class:`ExecutionResult`
        """
        dangerous = scan_dangerous_imports(code, self._cfg.dangerous_modules)

        if force_tier == 1 or (force_tier is None and not dangerous):
            result = _tier1_execute(code, self._cfg.timeout_seconds)
            result.dangerous_imports = dangerous
            return result

        # Tier 2 — dangerous import detected (or force_tier == 2)
        return _tier2_execute(code, self._cfg.timeout_seconds, self._cfg, dangerous)
