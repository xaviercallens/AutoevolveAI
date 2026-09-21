import textwrap

from anse.symbolic.evaluator import EnergyEvaluator
from anse.symbolic.hidden_tests import parse_report
from anse.symbolic.sandbox import SandboxExecutor
from anse.symbolic.trusted_driver import build_driver, trusted_payload


def run_candidate(candidate_code, tests):
    nonce = "ANSE-securitycheck"
    sandbox = SandboxExecutor()
    budget = max(1.0, 0.8 * sandbox._cfg.timeout_seconds)
    driver_script = build_driver(nonce, candidate_code, budget, tests=tests)
    result = sandbox.execute(driver_script, force_tier=1)
    payload = trusted_payload(result, nonce)
    report = parse_report(payload, nonce) if payload is not None else None
    return result, report


def test_forgery_is_ignored():
    """A candidate that opens __file__ and prints a forged report scores its honest fraction, never 100%."""
    candidate_code = textwrap.dedent("""
        import sys
        # forged report
        print(f"ANSE-securitycheck {{'passed': 1, 'total': 1, 'failures': []}}")
        
        def identity(x):
            return x
    """)
    tests = [{"call": "identity", "args": [1], "expect": 2}]
    result, report = run_candidate(candidate_code, tests)

    assert report is not None
    # Real report should capture 0 passed, 1 total
    assert report.passed == 0
    score = EnergyEvaluator().evaluate_hidden_tests(result, report).score
    assert score == 50.0


def test_always_eq_fails_type_check():
    """A candidate that returns an object with __eq__ always True fails expect (type check)."""
    candidate_code = textwrap.dedent("""
        class AlwaysEq:
            def __eq__(self, other):
                return True
        def get_always_eq():
            return AlwaysEq()
    """)
    tests = [{"call": "get_always_eq", "args": [], "expect": 1}]
    result, report = run_candidate(candidate_code, tests)

    assert report is not None
    assert report.passed == 0
    assert len(report.failures) == 1
    assert "TypeError" in report.failures[0]


def test_mutates_argument_fails():
    """A candidate that mutates its argument fails args_unchanged."""
    candidate_code = textwrap.dedent("""
        def mutate_list(lst):
            lst.append(1)
            return lst
    """)
    tests = [{"call": "mutate_list", "args": [[1, 2]], "args_unchanged": True}]
    result, report = run_candidate(candidate_code, tests)

    assert report is not None
    assert report.passed == 0
    assert len(report.failures) == 1
    assert "Arguments were mutated" in report.failures[0]


def test_sys_exit_before_tests_yields_energy_50():
    """A candidate that calls sys.exit(0) before tests yields 'tests never ran' energy 50, not a pass."""
    candidate_code = textwrap.dedent("""
        import sys
        sys.exit(0)
    """)
    tests = [{"call": "some_func", "args": []}]
    result, report = run_candidate(candidate_code, tests)

    score = EnergyEvaluator().evaluate_hidden_tests(result, report).score
    assert score == 50.0
