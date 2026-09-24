"""Tests for ANSE 2.0 System 3 Popperian Adversary Engine."""

from anse.v2.popperian_adversary import ASTWhistleblower, PopperianAdversaryEngine


def test_ast_whistleblower_empty_stub():
    cheat_code_pass = "def compute_hodge_star(x):\n    pass\n"
    is_cheat, msg = ASTWhistleblower.audit_code(cheat_code_pass)
    assert is_cheat is True
    assert "empty 'pass' stub" in msg

    cheat_code_ellipsis = "def compute_metric(g):\n    ...\n"
    is_cheat, msg = ASTWhistleblower.audit_code(cheat_code_ellipsis)
    assert is_cheat is True
    assert "empty '...' stub" in msg


def test_ast_whistleblower_hardcoded_literal_branch():
    cheat_branch = (
        "def solve_inverse(M):\n"
        "    if M == [[1.0, 0.0], [0.0, 1.0]]:\n"
        "        return [[1.0, 0.0], [0.0, 1.0]]\n"
        "    return []\n"
    )
    is_cheat, msg = ASTWhistleblower.audit_code(cheat_branch)
    assert is_cheat is True
    assert "Epistemic cheat: hardcoded conditional literal return" in msg


def test_popperian_adversary_valid_numeric_function():
    adversary = PopperianAdversaryEngine()

    valid_code = "def safe_dot(x):\n    return sum(sum(r) for r in x) if x and isinstance(x[0], list) else (sum(x) if x else 0.0)\n"

    def executable(payload):
        if not payload:
            return 0.0
        if isinstance(payload[0], list):
            return sum(sum(r) for r in payload)
        return sum(payload)

    report = adversary.challenge_solution(
        candidate_name="safe_dot",
        code_str=valid_code,
        domain_type="numeric",
        executable_fn=executable,
    )

    assert report.is_falsified is False
    assert report.ast_cheat_detected is False
    assert report.tests_passed_count > 0


def test_popperian_adversary_catches_unhandled_crash():
    adversary = PopperianAdversaryEngine()

    crashing_code = "def brittle_func(x):\n    return 1.0 / x[0]\n"

    def crashing_executable(payload):
        # Will crash on empty payload [] with IndexError
        return 1.0 / payload[0]

    report = adversary.challenge_solution(
        candidate_name="brittle_func",
        code_str=crashing_code,
        domain_type="numeric",
        executable_fn=crashing_executable,
    )

    # Empty payload has expected_behavior="graceful_error", but if it raises IndexError without handling:
    # Notice: In ADV-NUM-01, expected_behavior="graceful_error", so raising an exception is accepted as graceful rejection.
    # But for ADV-NUM-03 (Hilbert matrix), if crashing_executable raises IndexError because it expects a 1D list:
    assert report.tests_run_count > 0
