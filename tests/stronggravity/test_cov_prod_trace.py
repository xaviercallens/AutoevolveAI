"""Hermetic 100% line/branch coverage tests for pytest_prod_trace.py.

The plugin is exercised in-process through pytester so coverage observes the hook body.
"""

from __future__ import annotations

import importlib
import sys
from types import SimpleNamespace

import pytest

import pytest_prod_trace as ppt

pytest_plugins = ["pytester"]


def _prod(pytester):
    pkg = pytester.mkdir("prodpkg")
    (pkg / "__init__.py").write_text("")
    (pkg / "impl.py").write_text("def real():\n    return 42\n")
    (pkg / "tests").mkdir()
    (pkg / "tests" / "__init__.py").write_text("")
    (pkg / "tests" / "helper.py").write_text("def h():\n    return 1\n")


def _run(pytester, code, *args):
    _prod(pytester)
    pytester.makepyfile(test_case=code)
    return pytester.runpytest_inprocess("-p", "no:cacheprovider", *args, plugins=[ppt])


def test_module_default_prod_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "anse").mkdir()
    assert importlib.reload(ppt).DEFAULT_PROD_DIR == "anse"
    (tmp_path / "anse").rmdir()
    assert importlib.reload(ppt).DEFAULT_PROD_DIR == "src"
    monkeypatch.undo()
    importlib.reload(ppt)


def test_options_and_marker_registered(pytester):
    res = pytester.runpytest_inprocess("--help", plugins=[ppt])
    res.stdout.fnmatch_lines(["*--prod-dir*", "*--min-prod-calls*", "*prod_dir*"])
    res = pytester.runpytest_inprocess("--markers", plugins=[ppt])
    res.stdout.fnmatch_lines(["*no_prod_trace*"])


def test_real_call_passes(pytester):
    res = _run(
        pytester,
        "def test_ok():\n    from prodpkg.impl import real\n    assert real() == 42\n",
        "--prod-dir=prodpkg",
    )
    res.assert_outcomes(passed=1)


def test_phantom_test_fails(pytester):
    res = _run(pytester, "def test_phantom():\n    assert True\n", "--prod-dir=prodpkg")
    res.assert_outcomes(failed=1)
    res.stdout.fnmatch_lines(["*PHANTOM TEST DETECTED*"])


def test_calls_only_from_tests_dir_do_not_count(pytester):
    res = _run(
        pytester,
        "from prodpkg.tests.helper import h\ndef test_t():\n    assert h() == 1\n",
        "--prod-dir=prodpkg",
    )
    res.assert_outcomes(failed=1)


def test_opt_out_marker(pytester):
    res = _run(
        pytester,
        "import pytest\n@pytest.mark.no_prod_trace\ndef test_meta():\n    assert True\n",
        "--prod-dir=prodpkg",
    )
    res.assert_outcomes(passed=1)


def test_failing_test_not_masked(pytester):
    res = _run(pytester, "def test_bad():\n    assert 1 == 2\n", "--prod-dir=prodpkg")
    res.assert_outcomes(failed=1)
    assert "PHANTOM" not in res.stdout.str()


def test_min_prod_calls_and_ini_fallback(pytester):
    pytester.makeini("[pytest]\nprod_dir = prodpkg\n")
    code = "def test_one():\n    from prodpkg.impl import real\n    real()\n"
    # empty --prod-dir falls back to the ini value; 1 unique call < 5 required
    res = _run(pytester, code, "--prod-dir=", "--min-prod-calls=5")
    res.assert_outcomes(failed=1)
    res.stdout.fnmatch_lines(["*at least 5 call(s)*"])


# ── direct drive of the hook + tracer (coverage cannot observe a live settrace body) ──
def _frame(filename, name="fn", line=1):
    return SimpleNamespace(f_code=SimpleNamespace(co_filename=filename, co_name=name), f_lineno=line)


def _item(marker=None, prod_dir="/nonexistent/prod", ini="/ignored", min_calls=1):
    opts = {"--prod-dir": prod_dir, "--min-prod-calls": min_calls}
    config = SimpleNamespace(getoption=lambda k: opts[k], getini=lambda k: ini)
    return SimpleNamespace(
        nodeid="t::x", config=config, get_closest_marker=lambda n: marker
    )


def _drive(monkeypatch, item, frames, excinfo=None, events=("call",)):
    installed = []
    monkeypatch.setattr(sys, "settrace", lambda f: installed.append(f))
    gen = ppt.pytest_runtest_call(item)
    next(gen)
    tracer = installed[0]
    for ev in events:
        for fr in frames:
            assert tracer(fr, ev, None) is None
    try:
        gen.send(SimpleNamespace(excinfo=excinfo))
    except StopIteration:
        pass
    return installed


def test_drive_opt_out_skips_tracing(monkeypatch):
    installed = _drive_optout(monkeypatch)
    assert installed == []


def _drive_optout(monkeypatch):
    installed = []
    monkeypatch.setattr(sys, "settrace", lambda f: installed.append(f))
    gen = ppt.pytest_runtest_call(_item(marker=object()))
    next(gen)
    with pytest.raises(StopIteration):
        gen.send(None)
    return installed


def test_drive_counts_only_production_frames(monkeypatch):
    frames = [
        _frame("/nonexistent/prod/a.py"),
        _frame("/nonexistent/other/b.py"),
        _frame("/nonexistent/prod/tests/c.py"),
    ]
    # one production call recorded -> passes, tracer restored afterwards
    installed = _drive(monkeypatch, _item(), frames)
    assert len(installed) == 2 and installed[1] is sys.gettrace()
    # non-'call' events are ignored -> phantom
    with pytest.raises(pytest.fail.Exception, match="PHANTOM TEST DETECTED"):
        _drive(monkeypatch, _item(), frames, events=("line", "return"))


def test_drive_ini_fallback_and_excinfo(monkeypatch):
    # falsy --prod-dir falls back to ini; a raised test skips enforcement
    frames = [_frame("/ini/prod/a.py")]
    _drive(monkeypatch, _item(prod_dir="", ini="/ini/prod"), frames)
    _drive(monkeypatch, _item(), [], excinfo=(ValueError, ValueError("x"), None))
    with pytest.raises(pytest.fail.Exception):
        _drive(monkeypatch, _item(min_calls=2), [_frame("/nonexistent/prod/a.py")])
