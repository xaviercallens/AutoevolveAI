"""
Tests for Pytest Production Code Trace Enforcement Plugin.
Verifies that phantom tests with zero production calls are flagged and failed,
while real tests and marked meta-tests pass without error.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

TMP_TEST_DIR = Path(".tmp_trace_tests")


def _run_sub_pytest(code: str, test_filename: str) -> tuple[int, str]:
    TMP_TEST_DIR.mkdir(exist_ok=True)
    test_file = TMP_TEST_DIR / test_filename
    test_file.write_text(code, encoding="utf-8")
    try:
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "-p",
            "pytest_prod_trace",
            "-q",
            "--disable-warnings",
            str(test_file),
        ]
        env = dict(os.environ)
        res = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
        combined_output = res.stdout + res.stderr
        return res.returncode, combined_output
    finally:
        test_file.unlink(missing_ok=True)
        try:
            TMP_TEST_DIR.rmdir()
        except OSError:
            pass


def test_prod_trace_catches_cheating_phantom_test():
    code = "def test_simulated_math():\n    result = 1 + 2\n    assert result == 3\n"
    rc, output = _run_sub_pytest(code, "test_cheating.py")
    assert rc != 0
    assert "PHANTOM TEST DETECTED" in output
    assert "Expected at least 1 call(s) into 'anse/'" in output


def test_prod_trace_allows_marked_meta_tests():
    code = (
        "import pytest\n\n"
        "@pytest.mark.no_prod_trace\n"
        "def test_meta_check():\n"
        "    assert 42 == 42\n"
        "    assert True is not False\n"
    )
    rc, output = _run_sub_pytest(code, "test_meta.py")
    assert rc == 0
    assert "1 passed" in output


def test_prod_trace_passes_real_production_execution():
    code = (
        "from anse.symbolic.parser import extract_code\n\n"
        "def test_real_parser_call():\n"
        "    res = extract_code('```python\\nx = 1 + 2\\n```')\n"
        "    assert 'x = 1 + 2' in res.code\n"
        "    assert res.confidence > 0.0\n"
    )
    rc, output = _run_sub_pytest(code, "test_real_call.py")
    assert rc == 0, f"Sub-pytest failed: {output}"
    assert "1 passed" in output
