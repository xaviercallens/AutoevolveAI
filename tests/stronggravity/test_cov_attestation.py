"""Hermetic 100% line/branch coverage tests for execution_attestation.py."""

from __future__ import annotations

import ast
import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import execution_attestation as ea

SRC = Path(ea.__file__)


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    """Never touch the repo's attestation receipt or coverage.json."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(ea, "ATTESTATION_FILE", tmp_path / ".antigravity_attestation")


def _audit(src: str, filename: str = "prod.py") -> list[str]:
    auditor = ea.ImplementationAuditor(filename)
    auditor.visit(ast.parse(src))
    return auditor.violations


# ── module-level UTF-8 reconfiguration ──────────────────────────────────────
class _Stream(io.StringIO):
    def __init__(self, exc: Exception | None = None) -> None:
        super().__init__()
        self.exc = exc
        self.calls: list[str] = []

    def reconfigure(self, encoding: str) -> None:
        self.calls.append(encoding)
        if self.exc:
            raise self.exc


def _load_fresh(monkeypatch, out, err):
    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys, "stderr", err)
    spec = importlib.util.spec_from_file_location("ea_fresh", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_reconfigure_both_streams(monkeypatch):
    out, err = _Stream(), _Stream()
    _load_fresh(monkeypatch, out, err)
    assert out.calls == ["utf-8"] and err.calls == ["utf-8"]


def test_reconfigure_stdout_without_stderr_support(monkeypatch):
    out = _Stream()
    _load_fresh(monkeypatch, out, io.StringIO())
    assert out.calls == ["utf-8"]


def test_reconfigure_stdout_not_supported(monkeypatch):
    _load_fresh(monkeypatch, io.StringIO(), io.StringIO())


def test_reconfigure_error_is_swallowed(monkeypatch):
    out = _Stream(OSError("boom"))
    _load_fresh(monkeypatch, out, _Stream())
    assert out.calls == ["utf-8"]


# ── ImplementationAuditor ───────────────────────────────────────────────────
def test_async_stub_and_empty_body_detected():
    assert any("pass" in v for v in _audit("async def f():\n    pass\n"))
    empty = ea.ImplementationAuditor("x.py")
    fn = ast.parse("def g():\n    return 1\n").body[0]
    fn.body = []
    empty._audit_callable(fn)
    assert "empty stub" in empty.violations[0]


def test_non_stub_raise_is_allowed():
    assert _audit("def f():\n    raise ValueError('x')\n") == []
    assert _audit("def f():\n    raise NotImplementedError\n") != []
    assert _audit("def f():\n    raise NotImplementedError('x')\n") != []


def test_fake_data_assignment_variants():
    src = "def f():\n    a.b = 1\n    ok = 2\n    (x, y) = 1, 2\n    mock_user = 3\n"
    v = _audit(src)
    assert len(v) == 1 and "mock_user" in v[0]
    assert _audit("def f():\n    mock_user = 3\n", "tests/test_x.py") == []


# ── coverage.json validation ────────────────────────────────────────────────
def test_check_coverage_json(tmp_path, capsys):
    cov = tmp_path / "c.json"
    assert ea._check_coverage_json("anse", tmp_path / "missing.json") is False
    cov.write_text("{not json")
    assert ea._check_coverage_json("anse", cov) is False

    cov.write_text(json.dumps({"files": {"anse\\a.py": {"executed_lines": [1]}}}))
    assert ea._check_coverage_json("anse", cov) is True
    cov.write_text(json.dumps({"files": {"other.py": {"executed_lines": []}}}))
    assert ea._check_coverage_json("anse", cov) is True
    cov.write_text(json.dumps({"files": {"anse/a.py": {"executed_lines": []}}}))
    assert ea._check_coverage_json("anse", cov) is False
    assert "Phantom execution" in capsys.readouterr().out
    cov.write_text(json.dumps({}))
    assert ea._check_coverage_json("anse", cov) is True


def test_resolve_test_targets():
    assert ea._resolve_test_targets("m", "t.py") == ["t.py"]
    assert len(ea._resolve_test_targets("anse.symbolic")) == 3
    assert ea._resolve_test_targets("anse.jepa") == ["tests/phase2/test_jepa_world_model.py"]
    assert ea._resolve_test_targets("other") == []


# ── runtime receipt ─────────────────────────────────────────────────────────
def _proc(rc=0, out="", err=""):
    return SimpleNamespace(returncode=rc, stdout=out, stderr=err)


def test_receipt_pytest_failure(monkeypatch, capsys):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: _proc(1, "OUT", "ERR"))
    assert ea.verify_runtime_execution_receipt("m") is False
    text = capsys.readouterr().out
    assert "STDOUT" in text and "STDERR" in text


def test_receipt_pytest_failure_silent(monkeypatch, capsys):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: _proc(2))
    assert ea.verify_runtime_execution_receipt("m") is False
    assert "STDOUT" not in capsys.readouterr().out


def test_receipt_uses_existing_coverage_json(monkeypatch, tmp_path):
    (tmp_path / "coverage.json").write_text(
        json.dumps({"files": {"m/a.py": {"executed_lines": [1]}}})
    )
    calls = []
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: calls.append(a) or _proc())
    assert ea.verify_runtime_execution_receipt("m", "t.py") is True
    assert len(calls) == 1 and "t.py" in calls[0][0]


def test_receipt_uses_dot_coverage_json(monkeypatch, tmp_path):
    (tmp_path / ".coverage.json").write_text(
        json.dumps({"files": {"m/a.py": {"executed_lines": []}}})
    )
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: _proc())
    assert ea.verify_runtime_execution_receipt("m") is False


def test_receipt_generates_coverage_json_via_coverage_cli(monkeypatch, tmp_path):
    def fake_run(cmd, **kw):
        if "coverage" in cmd:
            (tmp_path / "coverage.json").write_text(
                json.dumps({"files": {"m/a.py": {"executed_lines": [3]}}})
            )
        return _proc()

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert ea.verify_runtime_execution_receipt("m") is True


def test_receipt_missing_coverage_data(monkeypatch, capsys):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: _proc())
    assert ea.verify_runtime_execution_receipt("m") is False
    assert "Coverage data missing" in capsys.readouterr().out


# ── git helpers ─────────────────────────────────────────────────────────────
def test_git_diff_files(monkeypatch):
    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: "a.py\n\n b.txt \n")
    assert ea._get_git_diff_files() == ["a.py", "b.txt"]
    for exc in (subprocess.CalledProcessError(1, "git"), FileNotFoundError()):
        def boom(*a, _e=exc, **k):
            raise _e
        monkeypatch.setattr(subprocess, "check_output", boom)
        assert ea._get_git_diff_files() == []
        assert ea._get_untracked_files() == []


def test_untracked_files(monkeypatch):
    out = " M mod.py\n?? new.py\n?? notes.txt\n\nlonely\n"
    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: out)
    assert ea._get_untracked_files() == ["mod.py", "new.py"]


def test_audit_single_file(tmp_path):
    assert ea._audit_single_file(str(tmp_path / "nope.py")) == []
    bad = tmp_path / "bad.py"
    bad.write_text("def (:\n")
    assert "SyntaxError" in ea._audit_single_file(str(bad))[0]
    stub = tmp_path / "stub.py"
    stub.write_text("def f():\n    pass\n")
    assert ea._audit_single_file(str(stub))
    good = tmp_path / "good.py"
    good.write_text("def f():\n    return 1\n")
    assert ea._audit_single_file(str(good)) == []


def test_audit_git_diff(monkeypatch, tmp_path):
    (tmp_path / "s.py").write_text("def f():\n    ...\n")
    monkeypatch.setattr(ea, "_get_git_diff_files", lambda: ["s.py", "readme.md"])
    monkeypatch.setattr(ea, "_get_untracked_files", lambda: ["s.py"])
    v = ea.audit_git_diff()
    assert len(v) == 1 and "ellipsis" in v[0]


# ── proof + attest_execution ────────────────────────────────────────────────
def test_generate_proof(tmp_path):
    token = ea.generate_attestation_proof("mod")
    receipt = json.loads((tmp_path / ".antigravity_attestation").read_text())
    assert receipt["proof_token"] == token and receipt["target_module"] == "mod"
    ea.generate_attestation_proof()
    assert json.loads(ea.ATTESTATION_FILE.read_text())["target_module"] == "workspace"


def test_attest_execution_paths(monkeypatch):
    monkeypatch.setattr(ea, "audit_git_diff", lambda: ["v"])
    assert ea.attest_execution("m") == (False, "", ["v"])

    monkeypatch.setattr(ea, "audit_git_diff", lambda: [])
    monkeypatch.setattr(ea, "verify_runtime_execution_receipt", lambda m, t: False)
    ok, tok, viol = ea.attest_execution("m", "t")
    assert not ok and tok == "" and "m" in viol[0]

    monkeypatch.setattr(ea, "verify_runtime_execution_receipt", lambda m, t: True)
    ok, tok, viol = ea.attest_execution("m")
    assert ok and len(tok) == 32 and viol == []

    ok, tok, _ = ea.attest_execution()
    assert ok and tok


# ── main() ──────────────────────────────────────────────────────────────────
def test_main_violations(monkeypatch, capsys):
    monkeypatch.setattr(ea, "audit_git_diff", lambda: ["bad thing"])
    with pytest.raises(SystemExit) as e:
        ea.main()
    assert e.value.code == 1 and "bad thing" in capsys.readouterr().out


def test_main_module_verification_fails(monkeypatch):
    monkeypatch.setattr(ea, "audit_git_diff", lambda: [])
    monkeypatch.setattr(sys, "argv", ["ea", "mod", "t.py"])
    monkeypatch.setattr(ea, "verify_runtime_execution_receipt", lambda m, t: False)
    with pytest.raises(SystemExit) as e:
        ea.main()
    assert e.value.code == 1


def test_main_success_with_module(monkeypatch, capsys):
    monkeypatch.setattr(ea, "audit_git_diff", lambda: [])
    monkeypatch.setattr(sys, "argv", ["ea", "mod"])
    seen = []
    monkeypatch.setattr(
        ea, "verify_runtime_execution_receipt", lambda m, t: seen.append((m, t)) or True
    )
    with pytest.raises(SystemExit) as e:
        ea.main()
    assert e.value.code == 0 and seen == [("mod", "")]
    assert "PROOF_TOKEN" in capsys.readouterr().out


def test_main_success_without_module(monkeypatch):
    monkeypatch.setattr(ea, "audit_git_diff", lambda: [])
    monkeypatch.setattr(sys, "argv", ["ea"])
    with pytest.raises(SystemExit) as e:
        ea.main()
    assert e.value.code == 0


def test_dunder_main_guard(monkeypatch):
    import runpy

    monkeypatch.setattr(sys, "argv", ["execution_attestation.py"])
    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: "")
    with pytest.raises(SystemExit) as e:
        runpy.run_path(str(SRC), run_name="__main__")
    assert e.value.code == 0


def test_docstring_is_stripped_before_stub_check():
    assert _audit('def f():\n    """doc"""\n    return 1\n') == []
    assert "empty stub" in _audit('def f():\n    """doc only"""\n')[0]
