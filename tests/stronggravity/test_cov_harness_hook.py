"""Hermetic branch-coverage tests for harness_hook.py."""

from __future__ import annotations

import json
import runpy
import shlex
import sys
from pathlib import Path

import pytest

import harness_hook as hh

PY = shlex.quote(sys.executable)
GOOD = "def solve(nums):\n    return sum(nums)\n"


@pytest.fixture(autouse=True)
def _isolated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # attestation receipts and default DPO output must never touch the repo tree
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(hh, "PROJECT_ROOT", tmp_path)


def test_evaluate_syntax_error(tmp_path: Path) -> None:
    r = hh.evaluate_in_harness("def broken(:\n", tmp_path / "t.py", "true")
    assert (r.energy, r.returncode) == (100.0, -1)
    assert "SyntaxError" in r.feedback and not (tmp_path / "t.py").exists()


def test_evaluate_ast_violation_blocks_execution(tmp_path: Path) -> None:
    r = hh.evaluate_in_harness("def f():\n    pass\n", tmp_path / "t.py", "true")
    assert r.returncode == -2 and r.ast_violations and "Whistleblower" in r.feedback
    assert not (tmp_path / "t.py").exists()


def test_evaluate_success_writes_file_and_mints_token(tmp_path: Path) -> None:
    target = tmp_path / "sub" / "t.py"
    r = hh.evaluate_in_harness(GOOD, target, f"{PY} -c 'pass'")
    assert r.is_valid and r.energy == 0.0 and r.proof_token
    assert target.read_text(encoding="utf-8") == GOOD


def test_evaluate_failure_feedback_prefers_stderr_then_stdout(tmp_path: Path) -> None:
    t = tmp_path / "t.py"
    r = hh.evaluate_in_harness(GOOD, t, f"{PY} -c 'import sys; sys.stderr.write(\"E!\"); sys.exit(2)'")
    assert r.energy == 100.0 and r.returncode == 2 and r.feedback == "E!"
    r = hh.evaluate_in_harness(GOOD, t, f"{PY} -c 'print(\"O!\"); raise SystemExit(1)'")
    assert r.feedback == "O!"


def test_evaluate_timeout(tmp_path: Path) -> None:
    r = hh.evaluate_in_harness(
        GOOD, tmp_path / "t.py", f"{PY} -c 'import time; time.sleep(5)'", timeout_sec=0.2
    )
    assert r.returncode == -3 and "timed out" in r.feedback


def test_evaluate_can_skip_ast_checks(tmp_path: Path) -> None:
    r = hh.evaluate_in_harness(
        "def f():\n    pass\n", tmp_path / "t.py", f"{PY} -c 'pass'", check_ast_stubs=False
    )
    assert r.is_valid


class ScriptedAgent:
    def __init__(self, codes: list[str]) -> None:
        self.codes, self.prompts = list(codes), []

    def think(self, prompt: str) -> tuple[str, str]:
        self.prompts.append(prompt)
        return "thought", self.codes.pop(0)


def test_fallback_agent_two_turns() -> None:
    a = hh.FallbackMockAgent()
    first, second = a.think("p")[1], a.think("p")[1]
    assert "if not nums" not in first and "if not nums" in second


def test_copilot_converges_and_records_dpo(tmp_path: Path) -> None:
    target = tmp_path / "impl.py"
    target.write_text("ORIGINAL = 1\n")
    marker = tmp_path / "attempt"
    # harness passes only on second call (marker exists after first)
    cmd = (
        f"{PY} -c \"import pathlib,sys; m=pathlib.Path(r'{marker}'); "
        f"ok=m.exists(); m.write_text('x'); sys.exit(0 if ok else 1)\""
    )
    agent = ScriptedAgent(["def a():\n    return 1\n", "def a():\n    return 2\n"])
    s = hh.active_inference_copilot("do it", target, cmd, agent=agent)
    assert s.converged and s.attempts_used == 2 and s.proof_token and s.dpo_pair_recorded
    assert "ATTEMPT 1" in agent.prompts[1]
    pairs = (tmp_path / ".scratchpad" / "golden_dpo_pairs.jsonl").read_text().splitlines()
    assert json.loads(pairs[0])["metadata"]["attempts"] == 2


def test_copilot_uses_default_agent_and_first_try_success(tmp_path: Path) -> None:
    target = tmp_path / "new.py"  # does not exist → orig_content None
    s = hh.active_inference_copilot("p", target, f"{PY} -c 'pass'")
    assert s.converged and s.attempts_used == 1 and s.dpo_pair_recorded is False


def test_copilot_failure_rolls_back_original(tmp_path: Path) -> None:
    target = tmp_path / "impl.py"
    target.write_text("ORIGINAL = 1\n")
    agent = ScriptedAgent(["def a():\n    return 1\n"] * 2)
    s = hh.active_inference_copilot("p", target, "false", agent=agent, max_attempts=2)
    assert not s.converged and s.final_code is None and s.attempts_used == 2
    assert target.read_text() == "ORIGINAL = 1\n"


def test_copilot_failure_without_backup_or_original_leaves_file(tmp_path: Path) -> None:
    target = tmp_path / "impl.py"
    target.write_text("ORIGINAL = 1\n")
    s = hh.active_inference_copilot(
        "p", target, "false", agent=ScriptedAgent(["def a():\n    return 1\n"]),
        max_attempts=1, backup_original=False,
    )
    assert not s.converged and "return 1" in target.read_text()

    fresh = tmp_path / "fresh.py"  # backup requested but nothing to restore
    s = hh.active_inference_copilot(
        "p", fresh, "false", agent=ScriptedAgent(["def a():\n    return 1\n"]), max_attempts=1
    )
    assert not s.converged and fresh.exists()


def test_handle_outcome_converged_without_prior_failure(tmp_path: Path) -> None:
    assert hh._handle_copilot_outcome(True, None, "code", "p", tmp_path / "f.py", None, 1, True) is False


def test_record_dpo_custom_dir_default_dir_and_oserror(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert hh.record_golden_signal_dpo("p", " c ", " r ", output_dir=tmp_path / "o")
    rec = json.loads((tmp_path / "o" / "golden_dpo_pairs.jsonl").read_text())
    assert rec["chosen"] == "c" and rec["rejected"] == "r" and rec["metadata"] == {}

    assert hh.record_golden_signal_dpo("p", "c", "r", metadata={"k": 1})
    assert (tmp_path / ".scratchpad" / "golden_dpo_pairs.jsonl").exists()

    def boom(*a: object, **k: object) -> None:
        raise OSError("disk full")

    monkeypatch.setattr("builtins.open", boom)
    assert hh.record_golden_signal_dpo("p", "c", "r", output_dir=tmp_path / "o") is False


def test_shadow_mode_match_and_surprise(tmp_path: Path) -> None:
    same = hh.shadow_mode_observe("x = 1\n", "x = 1", "p", "f.py")
    assert same["is_exact_match"] and same["surprise_energy"] == 0.0 and not same["dpo_pair_logged"]

    diff = hh.shadow_mode_observe("x = 1\n", "x = 2\ny = 3\n", "p", "f.py")
    assert not diff["is_exact_match"] and diff["surprise_energy"] > 0
    assert diff["dpo_pair_logged"] and "human_solution.py" in diff["unified_diff"]

    huge = hh.shadow_mode_observe("\n".join("a" * i for i in range(30)), "z", "p", "f.py")
    assert huge["surprise_energy"] == 100.0  # capped


def test_main_banner_and_module_guard(capsys: pytest.CaptureFixture[str]) -> None:
    hh.main()
    assert "Harness Hook" in capsys.readouterr().out
    runpy.run_path(str(Path(hh.__file__)), run_name="__main__")
    assert "Harness Hook" in capsys.readouterr().out


def test_project_root_sys_path_insertion(monkeypatch: pytest.MonkeyPatch) -> None:
    root = str(Path(hh.__file__).resolve().parent)
    monkeypatch.setattr(sys, "path", [p for p in sys.path if p != root])
    runpy.run_path(str(Path(hh.__file__)), run_name="not_main")
    assert sys.path[0] == root
    runpy.run_path(str(Path(hh.__file__)), run_name="not_main")  # already present: no duplicate
    assert sys.path.count(root) == 1
