"""Hermetic 100% line/branch coverage tests for .antigravity/hooks/hardened_gate.py."""

from __future__ import annotations

import importlib.util
import io
import runpy
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

SRC = Path(__file__).resolve().parents[2] / ".antigravity" / "hooks" / "hardened_gate.py"


class _Stream(io.StringIO):
    def __init__(self, exc: Exception | None = None) -> None:
        super().__init__()
        self.exc, self.calls = exc, []

    def reconfigure(self, encoding: str) -> None:
        self.calls.append(encoding)
        if self.exc:
            raise self.exc


def _load(name="hg"):
    spec = importlib.util.spec_from_file_location(name, SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def hg():
    return _load()


@pytest.mark.parametrize("stream", [_Stream(), _Stream(OSError("x")), io.StringIO()])
def test_stdout_reconfigure_paths(monkeypatch, stream):
    monkeypatch.setattr(sys, "stdout", stream)
    _load("hg_fresh")
    assert getattr(stream, "calls", ["utf-8"]) == ["utf-8"]


def test_audit_file_ast(hg, tmp_path, capsys):
    good, bad = tmp_path / "g.py", tmp_path / "b.py"
    good.write_text("x = 1\n")
    bad.write_text("def (:\n")
    assert hg.audit_file_ast(good) is True
    assert hg.audit_file_ast(bad) is False
    assert "SyntaxError" in capsys.readouterr().out


def test_audit_file_complexity(hg, tmp_path, capsys):
    simple = tmp_path / "s.py"
    simple.write_text("def f():\n    return 1\n")
    assert hg.audit_file_complexity(simple) is True

    complex_ = tmp_path / "c.py"
    complex_.write_text("def f(x):\n" + "".join(f"    if x == {i}:\n        return {i}\n" for i in range(12)))
    assert hg.audit_file_complexity(complex_) is False
    assert "Complexity too high" in capsys.readouterr().out
    assert hg.audit_file_complexity(complex_, max_cc=50) is True

    unparsable = tmp_path / "u.py"
    unparsable.write_text("def (:\n")
    assert hg.audit_file_complexity(unparsable) is False


def _rc(seq):
    it = iter(seq)
    return lambda *a, **k: SimpleNamespace(returncode=next(it))


def test_run_pipeline_local_checks_fail_fast(hg, tmp_path, monkeypatch):
    monkeypatch.setattr(subprocess, "run", _rc([]))  # would raise StopIteration if reached
    bad = tmp_path / "bad.py"
    bad.write_text("def (:\n")
    assert hg.run_pipeline([str(bad)]) is False

    complex_ = tmp_path / "c.py"
    complex_.write_text("def f(x):\n" + "".join(f"    if x == {i}:\n        return {i}\n" for i in range(12)))
    assert hg.run_pipeline([str(complex_)]) is False


@pytest.mark.parametrize("codes", [[1], [0, 1], [0, 0, 1], [0, 0, 0, 1], [0, 0, 0, 0]])
def test_run_pipeline_tool_stages(hg, tmp_path, monkeypatch, codes):
    ok = tmp_path / "ok.py"
    ok.write_text("x = 1\n")
    monkeypatch.setattr(subprocess, "run", _rc(codes))
    # non-.py entries and missing files are skipped by the local-check loop
    targets = [str(ok), str(tmp_path / "missing.py"), str(tmp_path / "notes.txt")]
    assert hg.run_pipeline(targets) is (codes == [0, 0, 0, 0])


def test_dunder_main_explicit_targets(tmp_path, monkeypatch):
    ok = tmp_path / "ok.py"
    ok.write_text("x = 1\n")
    monkeypatch.setattr(sys, "argv", [str(SRC), str(ok), "ignored.txt"])
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0))
    with pytest.raises(SystemExit) as e:
        runpy.run_path(str(SRC), run_name="__main__")
    assert e.value.code == 0


def test_dunder_main_discovers_targets_and_fails(tmp_path, monkeypatch):
    for d in ("pkg", "vendor", ".hidden"):
        (tmp_path / d).mkdir()
        (tmp_path / d / "m.py").write_text("x = 1\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", [str(SRC)])
    seen = []

    def fake_run(cmd, **kw):
        seen.append(cmd)
        return SimpleNamespace(returncode=1)

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(SystemExit) as e:
        runpy.run_path(str(SRC), run_name="__main__")
    assert e.value.code == 1
    assert seen[0][-1] == str(Path("pkg") / "m.py") and len(seen[0]) == 5
