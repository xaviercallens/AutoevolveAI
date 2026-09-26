"""mcts_lean_solver's proof gate must not pass on stderr-only Lean failures.

The original evaluate_lean_state() invoked bare `lean` and scored success as
('error' not in res.stdout) -- Lean writes diagnostics to stderr, so a failed
compile with empty stdout scored 1.0 ("VICTOIRE") regardless of what actually
happened. The fixed gate must invoke `lake env lean` (cwd=formal), treat a
non-zero exit code as failure, and additionally fail on sorryAx.

These tests mock subprocess.run (external I/O) and never touch the real Lean
toolchain, so they run unconditionally -- no ANSE_LEAN_TESTS gate is needed.
"""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

from anse.core.mcts_lean_solver import LeanGateResult, evaluate_lean_state


def _completed(returncode: int, stdout: str, stderr: str) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=["lake", "env", "lean"], returncode=returncode, stdout=stdout, stderr=stderr)


class TestLeanGateInvocation:
    """The gate must shell out via `lake env lean`, not bare `lean`."""

    def test_uses_lake_env_lean_with_formal_cwd(self) -> None:
        mock_run = MagicMock(return_value=_completed(0, "", ""))
        with patch("anse.core.mcts_lean_solver.subprocess.run", mock_run):
            evaluate_lean_state(["intro hp", "apply h2"])

        assert mock_run.call_args is not None
        command = mock_run.call_args.args[0]
        assert command[:3] == ["lake", "env", "lean"], "must invoke via lake env, not bare lean"
        assert mock_run.call_args.kwargs["cwd"].endswith("formal")


class TestLeanGateScoring:
    """Score must be 0.0 unless the exit code is 0 AND no sorryAx appears."""

    def test_compile_error_scores_zero_and_carries_stderr(self) -> None:
        with patch(
            "anse.core.mcts_lean_solver.subprocess.run",
            return_value=_completed(1, "", "error: unknown identifier"),
        ):
            result = evaluate_lean_state(["exact hp"])

        assert isinstance(result, LeanGateResult)
        assert result.score == 0.0
        assert "unknown identifier" in result.output

    def test_clean_compile_with_no_sorry_scores_one(self) -> None:
        with patch("anse.core.mcts_lean_solver.subprocess.run", return_value=_completed(0, "", "")):
            result = evaluate_lean_state(["intro hp", "apply h2", "apply h1", "exact hp"])

        assert result.score == 1.0
        assert "sorryAx" not in result.output

    def test_sorry_ax_in_axioms_dump_scores_zero(self) -> None:
        stdout = "modus_tollens depends on axioms: [propext, sorryAx]"
        with patch("anse.core.mcts_lean_solver.subprocess.run", return_value=_completed(0, stdout, "")):
            result = evaluate_lean_state(["sorry"])

        assert result.score == 0.0
        assert "sorryAx" in result.output

    def test_regression_nonzero_exit_with_empty_stdout_scores_zero(self) -> None:
        """The original defect: returncode=1 with empty stdout used to score 1.0."""
        with patch("anse.core.mcts_lean_solver.subprocess.run", return_value=_completed(1, "", "")):
            result = evaluate_lean_state(["apply h1"])

        assert result.score == 0.0
        assert result.score != 1.0
