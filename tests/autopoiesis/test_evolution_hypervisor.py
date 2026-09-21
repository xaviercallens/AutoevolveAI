"""Hypervisor gates: equivalence (hidden tests), benchmark output, paired domination rule, swap."""

import pytest

from anse.autopoiesis.hypervisor import (
    AutopoiesisHypervisor,
    DominationRule,
    build_driver,
    judge_domination,
    required_pair_wins,
    trusted_payload,
)
from anse.autopoiesis.registry import ComponentRegistry
from anse.symbolic.hidden_tests import attach_harness, parse_report
from anse.symbolic.sandbox import ExecutionResult, SandboxExecutor

# Tiny deterministic component: the parent is ~two orders of magnitude slower than the child.
PARENT = "def total(n):\n    s = 0\n    for i in range(n + 1):\n        s += i\n    return s\n"
FAST = "def total(n):\n    return n * (n + 1) // 2\n"
WRONG = "def total(n):\n    return n * n // 2\n"  # even faster to type, wrong for every n >= 1
RIGHT_ONLY_WHEN_SMALL = "def total(n):\n    return n * (n + 1) // 2 if n < 1000 else 0\n"
TESTS = [
    "assert total(0) == 0",
    "assert total(1) == 1",
    "assert total(10) == 55",
    "assert total(100) == 5050",
]
WORKLOAD = "BENCH_RESULT = total(1_500_000)\n"
QUICK_RULE = DominationRule(samples=5, max_sign_test_p=0.05)  # 5 of 5 pairs, p = 1/32


@pytest.fixture
def hypervisor(tmp_path):
    registry = ComponentRegistry(tmp_path / "registry")
    registry.register("total", PARENT)
    return AutopoiesisHypervisor(registry, rule=QUICK_RULE)


# ─── Domination rule (pure, deterministic) ───────────────────────────────────


def test_clear_improvement_dominates_and_reports_paired_statistics():
    parent = [150.0, 152.0, 149.0, 300.0, 151.0, 150.5, 148.0, 153.0, 150.0, 149.5, 151.5, 150.0]
    child = [40.0, 41.0, 39.5, 42.0, 40.5, 40.0, 41.5, 39.0, 40.0, 40.5, 41.0, 40.0]
    verdict = judge_domination(parent, child)
    assert verdict.dominates is True
    assert (verdict.pair_wins, verdict.pairs, verdict.pair_wins_required) == (12, 12, 11)
    assert verdict.gain == pytest.approx(
        110.0, abs=1.0
    )  # the 300 ms load spike does not move the median
    assert verdict.gain > verdict.threshold >= 0.05 * verdict.parent_median


def test_identical_and_symmetric_noise_samples_never_dominate():
    flat = judge_domination([100.0] * 12, [100.0] * 12)
    assert flat.dominates is False
    assert flat.pair_wins == 0
    # A/A on a noisy machine: each side wins half of the pairs by a wide margin
    parent = [100.0, 180.0] * 6
    child = [180.0, 100.0] * 6
    noisy = judge_domination(parent, child)
    assert noisy.dominates is False
    assert noisy.pair_wins == 6
    assert "6/12" in noisy.reason


def test_load_regime_shift_that_fools_marginal_medians_is_cancelled_by_pairing():
    # Machine gets slower half-way; A/A twin is within +-1 of its pair, alternating sign.
    parent = [100.0] * 6 + [200.0] * 6
    child = [p + (1.0 if i % 2 else -1.0) for i, p in enumerate(parent)]
    verdict = judge_domination(parent, child)
    assert verdict.dominates is False
    assert abs(verdict.gain) <= 1.0


def test_one_lost_pair_is_tolerated_at_twelve_samples_but_two_are_not():
    parent = [150.0] * 12
    one_spike = [40.0] * 11 + [400.0]
    two_spikes = [40.0] * 10 + [400.0, 400.0]
    assert judge_domination(parent, one_spike).dominates is True
    rejected = judge_domination(parent, two_spikes)
    assert rejected.dominates is False
    assert (rejected.pair_wins, rejected.pair_wins_required) == (10, 11)


def test_consistent_but_tiny_gain_is_below_the_practical_floor_with_exact_boundary():
    parent = [100.0] * 12
    assert judge_domination(parent, [99.0] * 12).dominates is False  # wins 12/12 but only 1 %
    at_floor = judge_domination(parent, [95.0] * 12)  # gain == 5 % exactly: not "exceeds"
    assert at_floor.dominates is False
    assert at_floor.gain == at_floor.threshold == 5.0
    assert judge_domination(parent, [94.9] * 12).dominates is True


def test_gain_must_exceed_measured_noise_not_just_the_floor():
    parent = [100.0] * 12
    # child always wins, median gain 10 %, but the gains are all over the place (1 .. 50)
    child = [99.0, 50.0, 98.0, 60.0, 90.0, 99.0, 55.0, 90.0, 97.0, 52.0, 90.0, 96.0]
    verdict = judge_domination(parent, child)
    assert verdict.pair_wins == 12
    assert verdict.threshold > 0.05 * verdict.parent_median  # noise term is the binding one
    assert verdict.dominates is False
    assert "noise threshold" in verdict.reason


def test_required_pair_wins_matches_the_binomial_tail_and_tightens_with_alpha():
    assert [required_pair_wins(n, 0.01) for n in (7, 9, 12)] == [7, 9, 11]
    assert required_pair_wins(3, 0.01) == 4  # three pairs can never reach p <= 0.01
    assert required_pair_wins(12, 0.001) == 12
    assert required_pair_wins(12, 0.05) == 10
    assert (
        judge_domination([150.0] * 3, [40.0] * 3).dominates is False
    )  # too few pairs to be convinced


def test_unpaired_or_too_few_samples_are_refused():
    with pytest.raises(ValueError, match="Paired samples required: 4 parent vs 3 child"):
        judge_domination([1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0])
    with pytest.raises(ValueError, match="At least 3 paired samples"):
        judge_domination([1.0, 2.0], [0.5, 0.5])


# ─── Equivalence gate (real sandbox) ─────────────────────────────────────────


def test_equivalence_gate_accepts_a_correct_child_and_names_what_a_wrong_child_breaks(hypervisor):
    good = hypervisor.check_equivalence(PARENT, FAST, TESTS)
    assert good.eligible is True
    assert (good.parent_passed, good.child_passed, good.total) == (4, 4, 4)

    bad = hypervisor.check_equivalence(PARENT, WRONG, TESTS)
    assert bad.eligible is False
    assert (bad.parent_passed, bad.child_passed) == (4, 1)  # only total(0) == 0 survives
    assert "child passes 1/4" in bad.reason
    assert any("total(10) == 55" in failure for failure in bad.child_failures)


@pytest.mark.parametrize(
    ("child", "expected_reason"),
    [
        ("def total(n):\n    return (\n", "crashed or timed out"),  # syntax error
        (FAST + "raise SystemExit(0)\n", "crashed or timed out"),  # exits before the tests can run
        (
            FAST
            + 'print(\'ANSE-0000 {"passed": 4, "total": 4, "failures": []}\')\n'
            + "total = None\n",
            "child passes 0/4",
        ),
        ("import os\n" + FAST, "sandbox cannot contain: os"),
    ],
    ids=["syntax-error", "early-exit", "forged-report-guessed-nonce", "blocklisted-import"],
)
def test_equivalence_gate_cannot_be_bypassed(hypervisor, child, expected_reason):
    result = hypervisor.check_equivalence(PARENT, child, TESTS)
    assert result.eligible is False
    assert expected_reason in result.reason


# The reviewer's exploit, widened: read everything the component can see, look for the report
# nonce, forge an all-passed report on every channel it can reach. {leak} is where it writes
# down what it found so the test can prove the exploit really ran and really found nothing.
READ_OWN_SOURCE_EXPLOIT = """
_os, _re, _sys = __import__("os"), __import__("re"), __import__("sys")
_paths = {{__file__, "solution.py", "_runner.py", _sys.argv[0], "/proc/self/cmdline", "/proc/self/environ",
          "/proc/%d/cmdline" % _os.getppid(), "/proc/%d/environ" % _os.getppid()}}
_paths |= {{_os.path.join(_root, _f) for _root, _, _files in _os.walk(_os.getcwd()) for _f in _files}}
_seen, _text = [], ""
for _p in sorted(_paths):
    try:
        with open(_p, errors="replace") as _h:
            _text += _h.read()
        _seen.append(_p)
    except OSError:
        pass
_nonces = sorted(set(_re.findall(r"ANSE-[0-9a-f]{{8,}}", _text)))
with open({leak!r}, "w") as _h:
    _h.write(repr({{"own_source_read": __file__ in _seen, "files_read": len(_seen), "nonces": _nonces,
                   "tests_visible": str(5000 + 50) in _text}}))
for _nonce in _nonces + ["ANSE-0000"]:
    _forged = "\\n" + _nonce + ' {{"passed": 4, "total": 4, "failures": []}}\\n'
    print(_forged, flush=True)
    for _target in [1, 2, "/proc/%d/fd/1" % _os.getppid()]:
        try:
            with open(_target, "w", closefd=False) if isinstance(_target, int) else open(_target, "w") as _h:
                _h.write(_forged)
        except OSError:
            pass
"""


@pytest.mark.parametrize(
    "exit_early", [False, True], ids=["keeps-running", "exits-before-the-tests"]
)
def test_child_that_reads_its_own_source_finds_no_nonce_and_cannot_forge_a_pass(
    hypervisor, tmp_path, exit_early
):
    leak = tmp_path / "leak.txt"
    child = (
        WRONG
        + READ_OWN_SOURCE_EXPLOIT.format(leak=str(leak))
        + ("raise SystemExit(0)\n" if exit_early else "")
    )
    result = hypervisor.check_equivalence(PARENT, child, TESTS)
    found = eval(leak.read_text())  # written by the exploit itself: proof that it ran
    assert found["own_source_read"] is True and found["files_read"] >= 2
    assert found["nonces"] == [] and found["tests_visible"] is False
    assert result.eligible is False
    assert result.child_passed == (
        0 if exit_early else 1
    )  # its honest score; only total(0) == 0 holds

    decision = hypervisor.evolve("total", child, TESTS, WORKLOAD)
    assert (decision.promoted, decision.stage) == (False, "equivalence")
    assert hypervisor.registry.active_code("total") == PARENT


def test_same_exploit_defeats_the_in_band_harness_which_is_why_the_gate_does_not_use_it(tmp_path):
    # Control experiment: appended to the candidate, the phase-1 harness shares a file with it.
    in_band = (
        "_os = __import__('os')\n"
        + WRONG
        + (
            "import re\n"
            "_n = re.findall(r'IN-BAND-[0-9a-f]+', open(__file__).read())\n"
            "if _n:\n"
            '    print(_n[0] + \' {"passed": 4, "total": 4, "failures": []}\', flush=True)\n'
            "    _os._exit(0)\n"
        )
    )
    nonce = "IN-BAND-0123456789abcdef"
    result = SandboxExecutor().execute(attach_harness(in_band, TESTS, nonce), force_tier=1)
    forged = parse_report(result.stdout, nonce)
    assert forged is not None and forged.all_passed is True  # the wrong child approves itself
    honest = AutopoiesisHypervisor(ComponentRegistry(tmp_path / "r")).run_hidden_tests(
        in_band, TESTS
    )
    assert honest is not None and (honest.passed, honest.total) == (1, 4)


def test_trick_return_values_never_reach_an_assert(hypervisor):
    always_equal = (
        "class _Yes:\n"
        "    def __eq__(self, other):\n        return True\n"
        "    def __repr__(self):\n        return 'yes'\n"
        "def total(n):\n    return _Yes()\n"
    )
    lying_int = "class _Int(int):\n    def __eq__(self, other):\n        return True\n    __hash__ = int.__hash__\ndef total(n):\n    return _Int(7)\n"
    opaque = hypervisor.check_equivalence(PARENT, always_equal, TESTS)
    assert opaque.eligible is False and opaque.child_passed == 0
    assert any("not a Python literal" in failure for failure in opaque.child_failures)
    subclass = hypervisor.check_equivalence(PARENT, lying_int, TESTS)
    assert (
        subclass.eligible is False and subclass.child_passed == 0
    )  # crosses the pipe as a plain 7


def test_exceptions_raised_by_the_component_reach_the_tests_with_their_builtin_type(hypervisor):
    strict = "def total(n):\n    if n < 0:\n        raise ValueError('negative')\n    return n * (n + 1) // 2\n"
    tests = [
        "try:\n    total(-1)\nexcept ValueError as exc:\n    assert 'negative' in str(exc)\nelse:\n    raise AssertionError('no ValueError')",
        "assert total(4) == 10",
    ]
    strict_report = hypervisor.run_hidden_tests(strict, tests)
    lenient_report = hypervisor.run_hidden_tests(FAST, tests)
    assert strict_report is not None and (strict_report.passed, strict_report.total) == (2, 2)
    assert lenient_report is not None and lenient_report.passed == 1
    assert "no ValueError" in lenient_report.failures[0]


# ─── Driver plumbing (pure) ──────────────────────────────────────────────────


def test_driver_needs_exactly_one_mode_and_keeps_secrets_out_of_the_worker_source():
    with pytest.raises(ValueError, match="exactly one of tests/workload/calls"):
        build_driver("ANSE-x", FAST, 5.0)
    with pytest.raises(ValueError, match="exactly one"):
        build_driver("ANSE-x", FAST, 5.0, tests=TESTS, workload=WORKLOAD)
    driver = build_driver("ANSE-secret-nonce", FAST, 5.0, tests=TESTS)
    compile(driver, "driver.py", "exec")  # must be valid Python whatever the component contains
    header, _, body = driver.partition("\nimport ast, builtins")
    worker_literal = next(line for line in header.splitlines() if line.startswith("_WORKER = "))
    assert "ANSE-secret-nonce" in header and "ANSE-secret-nonce" not in worker_literal
    assert "5050" not in worker_literal and "os.unlink(_self)" in body


def test_only_a_clean_exit_with_the_report_as_last_line_is_trusted():
    def run(stdout: str, returncode: int = 0, timed_out: bool = False) -> ExecutionResult:
        return ExecutionResult(
            stdout=stdout,
            stderr="",
            returncode=returncode,
            timed_out=timed_out,
            duration_ms=1.0,
            tier_used=1,
        )

    assert trusted_payload(run('noise\nN-1 {"passed": 1}\n\n'), "N-1") == 'N-1 {"passed": 1}'
    assert (
        trusted_payload(run('N-1 {"passed": 1}\nsomething wrote after the report\n'), "N-1") is None
    )
    assert trusted_payload(run('N-1 {"passed": 1}\n', returncode=1), "N-1") is None
    assert trusted_payload(run('N-1 {"passed": 1}\n', timed_out=True), "N-1") is None
    assert trusted_payload(run('N-10 {"passed": 1}\n'), "N-1") is None  # prefix of another nonce
    assert trusted_payload(run(""), "N-1") is None


def test_equivalence_cannot_be_established_without_hidden_tests(hypervisor):
    result = hypervisor.check_equivalence(PARENT, FAST, [])
    assert result.eligible is False
    assert "no hidden tests" in result.reason


# ─── Measurement (real sandbox) ──────────────────────────────────────────────


def test_measure_once_reports_the_benchmark_result_and_ignores_stray_prints(hypervisor):
    chatty = FAST + "print('debug: BENCH_RESULT = 7')\n"
    sample = hypervisor.measure_once(chatty, WORKLOAD)
    assert sample.valid is True
    assert sample.output == str(1_500_000 * 1_500_001 // 2)
    assert sample.energy == pytest.approx(sample.duration_ms + sample.peak_ram_mb)
    assert sample.peak_ram_mb > 0


def test_measure_once_marks_a_crashing_benchmark_invalid_and_interleaving_stops_early(hypervisor):
    crashing = "def total(n):\n    raise RuntimeError('boom')\n"
    sample = hypervisor.measure_once(crashing, WORKLOAD)
    assert sample.valid is False
    assert sample.output is None
    assert sample.energy >= 1e6
    parents, children = hypervisor.measure_interleaved(PARENT, crashing, WORKLOAD)
    assert (len(parents), len(children)) == (1, 1)  # no point burning the remaining pairs


def test_component_cannot_shorten_skip_or_forge_its_own_measurement(hypervisor):
    honest = hypervisor.measure_once(PARENT, WORKLOAD)
    frozen_clock = (
        "import time\ntime.perf_counter = lambda: 0.0\ntime.monotonic = lambda: 0.0\ntime.time = lambda: 0.0\n"
        + PARENT
        + "print('ANSE-BENCH-0000 42')\n"
    )
    cheat = hypervisor.measure_once(frozen_clock, WORKLOAD)
    assert cheat.valid is True and cheat.output == honest.output  # the forged line is ignored
    assert (
        cheat.duration_ms > 0.2 * honest.duration_ms
    )  # clocked by the driver, not by the component
    skipped = hypervisor.measure_once(FAST + "raise SystemExit(0)\n", WORKLOAD)
    assert skipped.valid is False and skipped.output is None
    assert skipped.energy >= 1e6


def test_differential_test_finds_divergence_the_hidden_tests_miss(hypervisor):
    inputs = [[n] for n in (0, 1, 7, 999, 1000, 2500)]
    same = hypervisor.differential_test(PARENT, FAST, "total", inputs)
    assert (same.completed, same.total, same.mismatches, same.agrees) == (True, 6, 0, True)
    drift = hypervisor.differential_test(PARENT, RIGHT_ONLY_WHEN_SMALL, "total", inputs)
    assert (drift.completed, drift.mismatches, drift.agrees) == (True, 2, False)
    assert "total(1000,)" in drift.examples[0] and "candidate ok 0" in drift.examples[0]
    broken = hypervisor.differential_test(PARENT, "def total(n):\n    return (\n", "total", inputs)
    assert (broken.completed, broken.mismatches, broken.agrees) == (False, 6, False)


# ─── Full pipeline (real sandbox + registry) ─────────────────────────────────


def test_correct_faster_child_is_promoted_with_a_complete_lineage_record(hypervisor):
    decision = hypervisor.evolve("total", FAST, TESTS, WORKLOAD)
    assert decision.promoted is True
    assert (decision.parent_version, decision.child_version) == (1, 2)
    assert decision.speedup is not None and decision.speedup > 5
    assert hypervisor.registry.active_code("total") == FAST
    entry = hypervisor.registry.lineage("total")[-1]
    assert (entry["decision"], entry["parent_version"], entry["child_version"]) == (
        "promoted",
        1,
        2,
    )
    assert entry["child_energy"] < entry["parent_energy"]
    assert (entry["child_tests_passed"], entry["tests_total"], entry["samples_per_side"]) == (
        4,
        4,
        5,
    )
    assert hypervisor.rollback("total") == 1
    assert hypervisor.registry.active_code("total") == PARENT


def test_fast_but_wrong_child_is_rejected_before_any_timing_and_the_parent_stays_live(hypervisor):
    decision = hypervisor.evolve("total", WRONG, TESTS, WORKLOAD)
    assert decision.promoted is False
    assert decision.stage == "equivalence"
    assert decision.child_samples == []  # correctness is settled before speed is even measured
    assert hypervisor.registry.versions("total") == [1]
    entry = hypervisor.registry.lineage("total")[-1]
    assert (entry["decision"], entry["child_version"], entry["child_tests_passed"]) == (
        "rejected",
        None,
        1,
    )


def test_child_that_passes_hidden_tests_but_diverges_on_the_benchmark_is_rejected(hypervisor):
    decision = hypervisor.evolve("total", RIGHT_ONLY_WHEN_SMALL, TESTS, WORKLOAD)
    assert decision.equivalence.eligible is True
    assert decision.promoted is False
    assert decision.stage == "benchmark"
    assert "differs from the parent's" in decision.reason
    assert hypervisor.registry.active_version("total") == 1
