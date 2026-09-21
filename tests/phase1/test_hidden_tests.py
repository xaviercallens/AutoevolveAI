"""Hidden-test harness and graded energy."""

from anse.symbolic.evaluator import EnergyCategory, EnergyEvaluator
from anse.symbolic.hidden_tests import TestReport, parse_report
from anse.symbolic.sandbox import SandboxExecutor
from anse.symbolic.trusted_driver import build_driver, trusted_payload

NONCE = "ANSE-testnonce"
TESTS = [
    {"call": "add", "args": [1, 2], "expect": 3},
    {"call": "add", "args": [-1, 1], "expect": 0},
    {"call": "add", "args": [0, 0], "expect": 0},
    {"call": "add", "args": [2, 2], "expect": 4},
]


def _run(code: str) -> tuple[object, TestReport | None]:
    sandbox = SandboxExecutor()
    budget = max(1.0, 0.8 * sandbox._cfg.timeout_seconds)
    driver_script = build_driver(NONCE, code, budget, tests=TESTS)
    result = sandbox.execute(driver_script, force_tier=1)
    payload = trusted_payload(result, NONCE)
    report = parse_report(payload, NONCE) if payload is not None else None
    result.stdout = ""
    return result, report


def test_correct_solution_passes_all_hidden_tests_with_zero_energy():
    result, report = _run("def add(a, b):\n    return a + b")
    energy = EnergyEvaluator().evaluate_hidden_tests(result, report)
    assert report == TestReport(passed=4, total=4, failures=[])
    assert energy.score == 0.0
    assert energy.category is EnergyCategory.PERFECT


def test_energy_is_graded_by_fraction_of_failed_tests():
    half_wrong, half_report = _run(
        "def add(a, b):\n    return abs(a) + abs(b) if a + b == 0 else a + b"
    )
    all_wrong, all_report = _run("def add(a, b):\n    return 99")
    evaluator = EnergyEvaluator()
    e_half = evaluator.evaluate_hidden_tests(half_wrong, half_report)
    e_all = evaluator.evaluate_hidden_tests(all_wrong, all_report)
    assert half_report.passed == 3 and all_report.passed == 0
    assert e_half.score == 12.5
    assert e_all.score == 50.0
    assert "'add'" in e_half.pain_signal and "[-1, 1]" in e_half.pain_signal


def test_self_asserting_cheat_is_caught_by_hidden_tests_but_not_by_self_grading():
    cheat = "def add(a, b):\n    return 0\n\nassert True"
    evaluator = EnergyEvaluator()
    self_graded = evaluator.evaluate(SandboxExecutor().execute(cheat, force_tier=1), code=cheat)
    result, report = _run(cheat)
    verified = evaluator.evaluate_hidden_tests(result, report)
    assert self_graded.score == 0.0
    assert verified.score == 25.0
    assert verified.category is EnergyCategory.TEST_FAILURE


def test_forged_report_without_nonce_is_ignored():
    forged = 'def add(a, b):\n    return 0\n\nprint(\'ANSE-guess {"passed": 4, "total": 4, "failures": []}\')'
    result, report = _run(forged)
    assert report is not None
    assert report.passed == 2
    # result.stdout doesn't contain ANSE-guess because we cleared it or trusted_payload ignored it.
    # Actually, worker's stdout is redirected to /dev/null by the driver!
    # So ANSE-guess doesn't even appear in result.stdout!


def test_early_exit_means_tests_never_ran_and_energy_is_maximal_test_failure():
    result, report = _run("def add(a, b):\n    return a + b\n\nraise SystemExit(0)")
    energy = EnergyEvaluator().evaluate_hidden_tests(result, report)
    assert report is None
    assert energy.score == 50.0
    assert "never ran" in energy.pain_signal


def test_crash_before_harness_keeps_categorical_energy():
    result, report = _run("def add(a, b)\n    return a + b")
    energy = EnergyEvaluator().evaluate_hidden_tests(result, report)
    assert report is None
    assert energy.category is EnergyCategory.SYNTAX_ERROR
    assert energy.score == 100.0
