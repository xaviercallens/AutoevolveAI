"""The Phase 3 component suite must be internally sound before it is used to judge the hypervisor."""

import random
from pathlib import Path

import pytest
import yaml

from anse.autopoiesis.hypervisor import AutopoiesisHypervisor
from anse.autopoiesis.registry import ComponentRegistry

SUITE = yaml.safe_load((Path(__file__).parents[2] / "tasks" / "phase3_evolution.yaml").read_text())[
    "components"
]
IDS = [c["name"] for c in SUITE]


@pytest.fixture
def hypervisor(tmp_path):
    return AutopoiesisHypervisor(ComponentRegistry(tmp_path / "registry"))


def test_suite_has_four_to_five_uniquely_named_components_with_every_field():
    assert 4 <= len(SUITE) <= 5
    assert len(set(IDS)) == len(SUITE)
    required = {
        "name",
        "entry",
        "description",
        "parent",
        "child_fast",
        "child_wrong",
        "tests",
        "workload",
        "probe_args",
        "probe_expected",
        "fuzz",
    }
    for component in SUITE:
        assert required <= set(component), component["name"]
        assert len(component["tests"]) >= 5, component["name"]
        assert "BENCH_RESULT" in component["workload"], component["name"]


@pytest.mark.parametrize("component", SUITE, ids=IDS)
def test_parent_and_fast_child_pass_every_hidden_test_and_wrong_child_does_not(
    component, hypervisor
):
    total = len(component["tests"])
    parent = hypervisor.run_hidden_tests(component["parent"], component["tests"])
    fast = hypervisor.run_hidden_tests(component["child_fast"], component["tests"])
    wrong = hypervisor.run_hidden_tests(component["child_wrong"], component["tests"])
    assert parent is not None and (parent.passed, parent.failures) == (total, [])
    assert fast is not None and (fast.passed, fast.failures) == (total, [])
    # the wrong child must run (it is a plausible optimisation, not a crash) and must be caught
    assert wrong is not None and wrong.total == total
    assert 0 < wrong.passed < total


@pytest.mark.parametrize("component", SUITE, ids=IDS)
def test_workload_is_deterministic_heavy_for_the_parent_and_agrees_with_the_fast_child(
    component, hypervisor
):
    parent = hypervisor.measure_once(component["parent"], component["workload"])
    again = hypervisor.measure_once(component["parent"], component["workload"])
    fast = hypervisor.measure_once(component["child_fast"], component["workload"])
    assert parent.valid and again.valid and fast.valid
    assert parent.output == again.output == fast.output
    assert parent.output not in (None, "None", "[]", "''")
    assert parent.duration_ms >= 20.0  # above interpreter noise, as the domination rule assumes


@pytest.mark.parametrize("component", SUITE, ids=IDS)
def test_probe_call_gives_the_expected_answer_on_parent_and_fast_child(component, tmp_path):
    registry = ComponentRegistry(tmp_path / "probe")
    registry.register(component["name"], component["parent"])
    parent_fn = getattr(registry.load_active(component["name"]), component["entry"])
    assert parent_fn(*component["probe_args"]) == component["probe_expected"]
    registry.promote(component["name"], component["child_fast"], {"reason": "suite self-check"})
    child_fn = getattr(registry.load_active(component["name"]), component["entry"])
    assert child_fn(*component["probe_args"]) == component["probe_expected"]
    assert registry.active_version(component["name"]) == 2


@pytest.mark.parametrize("component", SUITE, ids=IDS)
def test_held_out_fuzz_oracle_clears_the_fast_child_and_convicts_the_wrong_child(
    component, hypervisor
):
    inputs = eval(component["fuzz"], {"rng": random.Random(20260921)})
    assert len(inputs) >= 80
    assert inputs == eval(
        component["fuzz"], {"rng": random.Random(20260921)}
    )  # seeded: reproducible evidence
    fast = hypervisor.differential_test(
        component["parent"], component["child_fast"], component["entry"], inputs
    )
    wrong = hypervisor.differential_test(
        component["parent"], component["child_wrong"], component["entry"], inputs
    )
    assert (fast.completed, fast.total, fast.mismatches) == (True, len(inputs), 0)
    assert (
        wrong.completed is True and wrong.mismatches > 0
    )  # the oracle has the power to see a wrong child
    assert component["entry"] in wrong.examples[0]


# The reviewer's attack on the real suite: a wrong child that reads its own source for the report
# nonce, prints a forged all-passed report and exits before any check can run.
SELF_APPROVAL = """
import re, json
_found = re.findall(r"ANSE-[0-9a-f]{16,}", open(__file__).read())
for _nonce in _found or ["ANSE-" + "0" * 32]:
    print(_nonce + " " + json.dumps({"passed": 6, "total": 6, "failures": []}), flush=True)
    print(_nonce + " " + json.dumps({"output": "[False, False, True, True]", "duration_ms": 0.01, "peak_ram_mb": 1.0}), flush=True)
if _found:
    raise SystemExit(0)
"""


def test_self_approving_wrong_child_is_scored_honestly_and_never_promoted(tmp_path):
    component = next(c for c in SUITE if c["name"] == "has_pair_with_sum")
    registry = ComponentRegistry(tmp_path / "registry")
    registry.register(component["name"], component["parent"])
    hypervisor = AutopoiesisHypervisor(registry)
    attacker = component["child_wrong"] + SELF_APPROVAL
    decision = hypervisor.evolve(
        component["name"], attacker, component["tests"], component["workload"]
    )
    assert (decision.promoted, decision.stage) == (False, "equivalence")
    assert (decision.equivalence.child_passed, decision.equivalence.total) == (
        4,
        6,
    )  # its honest score
    assert registry.active_version(component["name"]) == 1
    assert registry.lineage(component["name"])[-1]["decision"] == "rejected"
    sample = hypervisor.measure_once(attacker, component["workload"])
    assert sample.valid is True
    assert (
        sample.duration_ms != 0.01 and sample.peak_ram_mb > 5.0
    )  # the driver's numbers, not the forged 0.01 ms / 1 MB
