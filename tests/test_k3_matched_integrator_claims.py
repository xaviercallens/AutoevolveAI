"""The K3-ASTRO-01/09 integrator claims must match the matched comparison, and the withdrawn ones must stay gone."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import k3_matched_integrator_comparison as m  # noqa: E402

RESULT = json.loads((REPO / "results" / "k3_matched_integrator_comparison.json").read_text())
PAPERS = REPO / "papers" / "phd_k3_astrophysics"
WITHDRAWN = ("16.4\\%", "-16.4\\%", "85.1\\%", "285264.686056", "42500.42762", "four orders of magnitude relative")


def test_result_file_controls_hold():
    c = RESULT["controls"]
    assert all(abs(o - 4) < 0.15 for o in c["observed_orders"]["rk4"] + c["observed_orders"]["yoshida4"])
    assert all(abs(o - 2) < 0.15 for o in c["observed_orders"]["verlet"])
    assert c["original_protocol_reproduced"]["claimed_improvement_pct"] == 16.38


def test_original_16_percent_comes_from_scoring_two_different_functions():
    """Negative control: re-run the original mismatched protocol; it reproduces 16.38% with both drifts at noise level."""
    o = m.original_mismatched_protocol()
    assert abs(o["claimed_improvement_pct"] - 16.38) < 0.05
    assert o["rk4_drift_of_H_A"] < 1e-9 and o["yoshida_drift_of_H_B"] < 1e-9
    matched = m.run("rk4", 0.005, 2000, 1.5265) , m.run("yoshida4", 0.005, 2000, 1.5265)
    assert matched[1]["max_rel_drift"] / matched[0]["max_rel_drift"] > 10      # matched, RK4 is far smaller at T=10


def test_rk4_drift_grows_with_time_and_yoshida_does_not():
    g = RESULT["drift_growth_with_time_dt_0.02"]
    assert g["rk4"][2] / g["rk4"][0] > 50
    assert max(g["yoshida4"]) / min(g["yoshida4"]) < 1.001
    assert g["yoshida4"][2] < g["rk4"][2] and g["yoshida4"][0] > g["rk4"][0]    # the crossover the paper states


def test_withdrawn_claims_are_gone_from_papers_and_builder():
    files = [PAPERS / "K3_ASTRO_01_v4.tex", PAPERS / "K3_ASTRO_09_v4.tex", PAPERS / "problem_01_attractor_geodesics.tex",
             REPO / "scripts" / "phd_k3_pipeline" / "build_papers_v14_0.py"]
    for f in files:
        text = f.read_text()
        assert not [w for w in WITHDRAWN if w in text and "withdrawn" not in text.split(w)[0][-200:] + text.split(w)[1][:200]], f


def test_verlet_factors_quoted_in_problem_01_match_the_data():
    row = {(r["T"], r["dt"]): r for r in RESULT["matched_dt_grid"]}
    text = (PAPERS / "problem_01_attractor_geodesics.tex").read_text()
    for dt in (0.05, 0.02, 0.005):
        f = row[(10.0, dt)]["verlet"]["max_rel_drift"] / row[(10.0, dt)]["yoshida4"]["max_rel_drift"]
        assert f"{f:.1e}".replace("e+0", "e+0") in text.replace("e+0", "e+0"), (dt, f)


ATTR = json.loads((REPO / "results" / "k3_09_carter_attribution.json").read_text())


def test_problem_09_85_percent_is_a_ratio_of_integration_times():
    aw = ATTR["as_written"]
    assert aw["protocol"]["T_yoshida"] < aw["protocol"]["T_rk4"] / 2           # the arms did not run equally long
    assert abs(aw["ratio"] - 0.149) < 0.005                                      # the claimed 85.1%
    for key in ("equal T=1.5, unequal dt", "matched dt=0.005, equal T=1.5"):
        assert abs(ATTR["arms"][key]["ratio"] - 1.0) < 1e-3, key                 # at equal T the methods are indistinguishable
    assert 1.8 < ATTR["controls"]["drift_vs_T_log_log_slope"] < 2.3              # drift ~ T^2, so a time ratio of 0.4 gives ~0.16


def test_problem_09_drift_is_a_property_of_the_equations_not_the_step():
    r = ATTR["controls"]["dt_refinement_rk4_drift_at_T_1.5"]
    vals = list(r.values())
    assert min(vals) > 0.1 and max(vals) - min(vals) < 1e-5                      # a method error would vanish as dt -> 0


def test_forced_substitution_is_gone_from_the_generator():
    src = (REPO / "scripts" / "phd_k3_pipeline" / "generate_numerical_data_v13_9.py").read_text()
    assert "E_improved = E_baseline * 0.45" not in src
    sys.path.insert(0, str(REPO / "scripts" / "phd_k3_pipeline"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("g139", REPO / "scripts" / "phd_k3_pipeline" / "generate_numerical_data_v13_9.py")
    g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
    r = g.compute_k3_09_carter_geodesics(dt_y=0.005)                             # matched dt: Yoshida is NOT better
    assert r["energy_improved"] == r["energy_baseline"] or abs(r["energy_improved"] / r["energy_baseline"] - 1.0) < 1e-3
    assert r["gate_passed"] is False and r["improvement_pct"] <= 0.1             # reported as measured; the gate fails
