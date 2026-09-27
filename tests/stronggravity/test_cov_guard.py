"""Hermetic 100% line/branch coverage tests for antigravity_guard.py."""

from __future__ import annotations

import ast
import importlib.util
import io
import runpy
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import antigravity_guard as ag

SRC = Path(ag.__file__)


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
    spec = importlib.util.spec_from_file_location("ag_fresh", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)


@pytest.mark.parametrize("exc", [None, OSError("x"), ValueError("x"), RuntimeError("x")])
def test_stream_reconfigure_paths(monkeypatch, exc):
    out, err = _Stream(exc), _Stream(exc)
    _load_fresh(monkeypatch, out, err)
    assert out.calls == ["utf-8"] and err.calls == ["utf-8"]


def test_streams_without_reconfigure(monkeypatch):
    _load_fresh(monkeypatch, io.StringIO(), io.StringIO())


# ── installed packages ──────────────────────────────────────────────────────
class _Dist:
    def __init__(self, top, meta):
        self._top, self.metadata = top, meta

    def read_text(self, _name):
        return self._top


def test_get_installed_packages(monkeypatch):
    dists = [
        _Dist("Foo\n\n bar \n", {}),
        _Dist(None, {"Name": "My-Pkg"}),
        _Dist(None, {}),
        _Dist(None, {"Name": ""}),
    ]
    monkeypatch.setattr(ag.importlib.metadata, "distributions", lambda: dists)
    assert ag.get_installed_packages() == {"foo", "bar", "my_pkg"}


def test_get_installed_packages_real():
    assert "pytest" in ag.get_installed_packages()


# ── imports / local modules / phantoms ──────────────────────────────────────
def test_extract_top_level_imports():
    tree = ast.parse("import os.path, a as b\nfrom x.y import z\nfrom . import q\nfrom .m import r\n")
    assert ag.extract_top_level_imports(tree) == {"os", "a", "x"}


def test_get_local_modules(tmp_path, monkeypatch):
    root = tmp_path / "root"
    (root / "pkg").mkdir(parents=True)
    (root / "top.py").write_text("")
    (root / "sub").mkdir()
    (root / "sub" / "sibling.py").write_text("")
    (root / "sub" / "inner").mkdir()
    monkeypatch.chdir(root)
    mods = ag._get_local_modules(root / "sub" / "f.py")
    assert {"top", "pkg", "sub", "sibling", "inner", "anse"} <= mods


def test_find_phantom_imports():
    issues = ag._find_phantom_imports({"os", "numpy", "loc", "ghost"}, {"numpy"}, {"loc"})
    assert len(issues) == 1 and "ghost" in issues[0]


def test_audit_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    bad = tmp_path / "bad.py"
    bad.write_text("def (:\n")
    ok, issues = ag.audit_file(bad, set())
    assert not ok and "Syntax Error" in issues[0]
    ghost = tmp_path / "g.py"
    ghost.write_text("import nonexistent_zzz\n")
    ok, issues = ag.audit_file(ghost, set())
    assert not ok and "nonexistent_zzz" in issues[0]
    fine = tmp_path / "f.py"
    fine.write_text("import os\n")
    assert ag.audit_file(fine, set()) == (True, [])


# ── static analyzers ────────────────────────────────────────────────────────
def _rc(seq):
    it = iter(seq)
    return lambda *a, **k: SimpleNamespace(returncode=next(it))


def test_run_static_analyzers(monkeypatch):
    monkeypatch.setattr(subprocess, "run", _rc([1]))
    assert ag.run_static_analyzers(["a.py"]) is False
    monkeypatch.setattr(subprocess, "run", _rc([0, 1]))
    assert ag.run_static_analyzers(["a.py"]) is False
    monkeypatch.setattr(subprocess, "run", _rc([0, 0]))
    assert ag.run_static_analyzers(["a.py"]) is True


# ── target discovery ────────────────────────────────────────────────────────
def test_collect_target_files(tmp_path, monkeypatch):
    for d in ("pkg", "vendor", ".hidden", "build"):
        (tmp_path / d).mkdir()
        (tmp_path / d / "m.py").write_text("")
    (tmp_path / "top.py").write_text("")
    monkeypatch.chdir(tmp_path)
    found = {str(p) for p in ag._collect_target_files()}
    assert found == {"top.py", "pkg/m.py"}


def test_resolve_cli_targets(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["g", "a.py", "notes.txt"])
    assert ag._resolve_cli_targets() == [Path("a.py")]
    monkeypatch.setattr(sys, "argv", ["g"])
    monkeypatch.setattr(ag, "_collect_target_files", lambda: [Path("z.py")])
    assert ag._resolve_cli_targets() == [Path("z.py")]


def test_audit_all_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "ok.py").write_text("import os\n")
    (tmp_path / "bad.py").write_text("import ghost_zzz\n")
    issues = ag._audit_all_files(
        [tmp_path / "missing.py", tmp_path / "ok.py", tmp_path / "bad.py"], set()
    )
    assert len(issues) == 1 and "ghost_zzz" in issues[0]


# ── main ────────────────────────────────────────────────────────────────────
def test_main_issues(monkeypatch, capsys):
    monkeypatch.setattr(ag, "_resolve_cli_targets", lambda: [Path("a.py")])
    monkeypatch.setattr(ag, "get_installed_packages", set)
    monkeypatch.setattr(ag, "_audit_all_files", lambda t, i: ["[a.py] boom"])
    with pytest.raises(SystemExit) as e:
        ag.main()
    assert e.value.code == 1 and "boom" in capsys.readouterr().out


def test_main_static_failure(monkeypatch):
    monkeypatch.setattr(ag, "_resolve_cli_targets", lambda: [Path("a.py")])
    monkeypatch.setattr(ag, "get_installed_packages", set)
    monkeypatch.setattr(ag, "_audit_all_files", lambda t, i: [])
    monkeypatch.setattr(ag, "run_static_analyzers", lambda f: False)
    with pytest.raises(SystemExit) as e:
        ag.main()
    assert e.value.code == 1


def test_main_pass(monkeypatch, capsys):
    monkeypatch.setattr(ag, "_resolve_cli_targets", lambda: [Path("a.py")])
    monkeypatch.setattr(ag, "get_installed_packages", set)
    monkeypatch.setattr(ag, "_audit_all_files", lambda t, i: [])
    monkeypatch.setattr(ag, "run_static_analyzers", lambda f: True)
    with pytest.raises(SystemExit) as e:
        ag.main()
    assert e.value.code == 0 and "PASS" in capsys.readouterr().out


def test_dunder_main_guard(monkeypatch, tmp_path):
    (tmp_path / "t.py").write_text("import os\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["antigravity_guard.py", str(tmp_path / "t.py")])
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0))
    with pytest.raises(SystemExit) as e:
        runpy.run_path(str(SRC), run_name="__main__")
    assert e.value.code == 0
