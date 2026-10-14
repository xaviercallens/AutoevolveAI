"""
Unit tests for AutoevolveAI improvements derived from OptimalEnergyAI (v0.2.0 / v0.3.0)
and Laya-LoRA Peer Review (Reviewer 2) feedback.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from anse.formal.lean_runner import LeanVerificationResult, classify_axiom_footprint
from anse.harness import (
    HardenedAutoresearchLoop,
    Run,
    build_ledger,
    ci_bound_guard,
    preregister,
    two_sided_oracle_check,
)
from anse.jepa.latent_geometry import (
    Convention,
    cloud_energy,
    e_sq,
    e_tri,
    gaussian,
    is_crystallized,
    is_lattice_member,
    jellium_gamma,
    nearest,
    nearest_zn,
    nsm_mc,
    nsm_reference,
    order_report,
    planar_patch,
    poisson_disk,
    radial_interior_mask,
    rescale_to_density,
    structure_factor,
    verify_lattice_decoder,
    yukawa,
)
from anse.v5.laya_system_one import (
    audit_laya_lora_parameters,
    build_provenance_comparative_row,
    calibrate_noul_threshold,
    wilson_ci_95,
)

# ---------------------------------------------------------------------------
# 1. Experiment & Autoresearch Harness Plugin API (`anse.harness`)
# ---------------------------------------------------------------------------


def test_harness_preregister_run_and_ledger_lifecycle(tmp_path: Path) -> None:
    """Verify preregistration, immutable Run records, append-only ledger gate, and disclosed revisions."""
    poc = "demo_poc"
    exp = tmp_path / "experiments" / poc
    exp.mkdir(parents=True)

    runner_py = exp / "run.py"
    runner_py.write_text("# runner\n", encoding="utf-8")
    decide_py = exp / "decide.py"
    decide_py.write_text(
        "def decide(prereg, runs):\n"
        "    ok = all(r['metrics'].get('gain', 0) > 0 for r in runs)\n"
        "    return [{'hypothesis': 'H1', 'verdict': 'PASS' if ok else 'FAIL', 'value': '0.037', 'rule': 'gain > 0'}]\n",
        encoding="utf-8",
    )

    prereg_in = {
        "hypotheses": [{"id": "H1", "statement": "Hexagonal gain > 0"}],
        "runners": {
            f"experiments/{poc}/run.py": "",
            f"experiments/{poc}/decide.py": "",
        },
    }
    (exp / "prereg.in.json").write_text(json.dumps(prereg_in), encoding="utf-8")

    # Negative control: Run must refuse to start before preregistration
    with pytest.raises(FileNotFoundError):
        Run(poc, runner_py, seed=0, budget_s=60.0, config={}, root=tmp_path)

    # Preregister
    prereg_file = preregister(poc, tmp_path)
    assert prereg_file.is_file()
    prereg_data = json.loads(prereg_file.read_text(encoding="utf-8"))
    assert "no result of this problem has been produced" in prereg_data["stage"]

    # Positive control run: all controls pass, metric passes
    run0 = Run(poc, runner_py, seed=0, budget_s=60.0, config={"alpha": 1.0}, root=tmp_path)
    assert run0.control("positive_ctl", True)
    assert run0.control("negative_ctl", True)
    run0.metrics["gain"] = 0.037
    run0.write()

    rc = build_ledger(poc, tmp_path)
    assert rc == 0

    # Re-running ledger with no new runs re-reports last batch status (0)
    assert build_ledger(poc, tmp_path) == 0

    # Overwriting preregistration after runs exist must fail without revise reason
    with pytest.raises(RuntimeError):
        preregister(poc, tmp_path)

    # Disclosed revision records runs_seen
    preregister(poc, tmp_path, revise="Add CI lower bound tolerance")
    revised = json.loads(prereg_file.read_text(encoding="utf-8"))
    assert len(revised["revision_history"]) == 1
    assert revised["revision_history"][0]["runs_seen"] == 1

    # Negative control run: failed control forces status='crash' and exit code 1
    run1 = Run(poc, runner_py, seed=1, budget_s=60.0, config={}, root=tmp_path)
    run1.control("positive_ctl", False, reason="sabotaged control")
    run1.metrics["gain"] = 0.037
    run1.write()

    assert build_ledger(poc, tmp_path) == 1
    # Re-running with no new runs cannot hide the crash
    assert build_ledger(poc, tmp_path) == 1


def test_ci_bound_guard_issue_32() -> None:
    """Verify CI-tolerant theoretical ceiling guard (OptimalEnergyAI Issue #32)."""
    gain_bound = 1.0 - (5.0 / (36.0 * (3.0**0.5))) / (1.0 / 12.0)  # ~0.03775

    # Ideal source where sample mean is slightly above 3.775% due to sampling noise (e.g. 3.81%),
    # but the 95% CI lower bound is <= 3.775%: must PASS (not coin-flip fail).
    ideal_gains = [0.0372, 0.0385, 0.0379, 0.0388, 0.0381]
    res_ideal = ci_bound_guard(ideal_gains, gain_bound, rate_gap=0.002, rate_tol=0.01)
    assert res_ideal["passed"] is True

    # Artefact run where the entire CI sits above the theoretical ceiling: must FAIL
    artefact_gains = [0.052, 0.055, 0.051, 0.054, 0.053]
    res_artefact = ci_bound_guard(artefact_gains, gain_bound, rate_gap=0.002, rate_tol=0.01)
    assert res_artefact["passed"] is False
    assert res_artefact["checks"]["artefact_guard_ok"] is False


def test_two_sided_oracle_check_catches_closer_non_lattice_points() -> None:
    """Verify two-sided cross-check + membership catches closer off-lattice points (H0 Finding 1)."""
    rng = np.random.default_rng(42)
    queries = rng.uniform(-1.0, 1.0, size=(200, 4))
    true_codewords, _ = nearest("D", queries)
    oracle_d = np.einsum("ij,ij->i", queries - true_codewords, queries - true_codewords)

    # Positive control: true D4 decoder passes both distance and lattice membership
    ok_res = two_sided_oracle_check(
        true_codewords, queries, oracle_d, lambda c: is_lattice_member("D", c)
    )
    assert ok_res["passed"] is True
    assert ok_res["mismatches"] == 0

    # Negative control: returning the query itself (distance 0 < oracle_d, off-lattice)
    # A one-sided check `d <= oracle_d` would miss this; two_sided_oracle_check catches both!
    cheating_res = two_sided_oracle_check(
        queries, queries, oracle_d, lambda c: is_lattice_member("D", c)
    )
    assert cheating_res["passed"] is False
    assert cheating_res["closer_than_oracle_violations"] > 0
    assert cheating_res["non_member_violations"] > 0


def test_hardened_autoresearch_loop_3_stage_gate() -> None:
    """Verify the 3-stage autoresearch funnel rejects metric gaming and failed controls."""
    loop = HardenedAutoresearchLoop(
        best_search_metric=0.50,
        best_heldout_metric=0.52,
        best_replicate_median=0.51,
        lower_is_better=True,
        batch_cap=5,
    )

    # Candidate 1: Overfits search split (0.45 < 0.50) but degrades held-out (0.55 > 0.52) -> discard
    r1 = loop.evaluate_candidate(
        "c01_overfit",
        positive_control_ok=True,
        negative_control_ok=True,
        search_fn=lambda: 0.45,
        heldout_fn=lambda: 0.55,
        replicates_fn=lambda: [0.46, 0.47, 0.45],
    )
    assert r1["status"] == "discard"
    assert r1["stage"] == "heldout"
    assert not loop.kept_candidates

    # Candidate 2: Improves search, held-out, and 3-seed median -> keep
    r2 = loop.evaluate_candidate(
        "c02_genuine",
        positive_control_ok=True,
        negative_control_ok=True,
        search_fn=lambda: 0.42,
        heldout_fn=lambda: 0.44,
        replicates_fn=lambda: [0.43, 0.45, 0.41],
    )
    assert r2["status"] == "keep"
    assert r2["kept"] is True
    assert loop.kept_candidates == ["c02_genuine"]
    assert loop.best_replicate_median == pytest.approx(0.43)

    # Candidate 3: Control fails -> crash
    r3 = loop.evaluate_candidate(
        "c03_broken_ctl",
        positive_control_ok=True,
        negative_control_ok=False,
        search_fn=lambda: 0.30,
        heldout_fn=lambda: 0.30,
        replicates_fn=lambda: [0.30, 0.30, 0.30],
    )
    assert r3["status"] == "crash"
    assert loop.crashed is True


# ---------------------------------------------------------------------------
# 2. Universal-Optimality Latent Geometry & Decoders (`anse.jepa.latent_geometry`)
# ---------------------------------------------------------------------------


def test_golden_energies_and_jellium_gamma() -> None:
    """Verify Ex 1.13 Gaussian theta values, Table 3.1 Yukawa values, and Jellium Gamma."""
    # Ex 1.13 at alpha = 1.0: theta_A2 = 1.159595266963928 -> e_tri = 0.159595266963928
    assert e_tri(gaussian(1.0)) == pytest.approx(0.159595266963928, abs=1e-9)
    assert e_sq(gaussian(1.0)) == pytest.approx(0.180340599016097, abs=1e-9)

    # Table 3.1 Yukawa kappa = 2.0, shifted force rc = 8.0, HALF convention
    assert e_tri(yukawa(2.0, 8.0, "force"), conv=Convention.HALF) == pytest.approx(0.3935333668, abs=5e-11)
    assert e_sq(yukawa(2.0, 8.0, "force"), conv=Convention.HALF) == pytest.approx(0.4009647699, abs=5e-11)

    # Cloud energy on an A2 patch interior matches e_tri; HALF is 0.5x ORDERED_PAIRS
    patch = planar_patch("A2", 1200)
    mask = radial_interior_mask(patch, 4.0)
    rep_ord = cloud_energy(patch, gaussian(1.0), mask, conv=Convention.ORDERED_PAIRS)
    rep_half = cloud_energy(patch, gaussian(1.0), mask, conv=Convention.HALF)
    assert abs(rep_ord.gap) < 1e-9
    assert rep_half.value / rep_ord.value == pytest.approx(0.5, abs=1e-12)

    # Jellium Gamma invariant
    gamma = jellium_gamma(n_points=64, lam=0.01, alpha=1.0)
    assert gamma > 0.0


def test_order_report_poisson_finding_2_and_voronoi_issue_2() -> None:
    """Verify H0 Finding 2 (Poisson local psi6 ~0.78 but not Crystallized) and Issue #2 (Voronoi + S(k->0))."""
    rng = np.random.default_rng(7)
    a_patch = planar_patch("A2", 600)
    a_mask = radial_interior_mask(a_patch, 2.0)

    rep_a = order_report(a_patch, a_mask, seed=7, neighbour_rule="1.35d0", with_spectra=True)
    assert rep_a.crystallized is True
    assert rep_a.defect_fraction == 0.0
    assert rep_a.psi6_local_mean == pytest.approx(1.0, abs=1e-6)
    assert rep_a.controls_ok is True

    # Voronoi topological neighbor rule (Issue #2) also certifies interior A2 sites as 6-coordinated crystal
    rep_vor = order_report(a_patch, a_mask, seed=7, neighbour_rule="voronoi", with_spectra=False)
    assert rep_vor.crystallized is True
    assert rep_vor.defect_fraction == 0.0

    # Poisson cloud: local <|psi6|> is high (~0.75-0.82), NOT 0.3, but defect_fraction ~ 1 -> NOT crystallized
    p_cloud = poisson_disk(600, 1.0, rng)
    p1, _, p_mask = rescale_to_density(p_cloud)
    rep_p = order_report(p1, p_mask, seed=7, with_spectra=False)
    assert rep_p.psi6_local_mean is not None and rep_p.psi6_local_mean > 0.65
    assert rep_p.defect_fraction is not None and rep_p.defect_fraction > 0.60
    assert rep_p.crystallized is False
    assert not is_crystallized({"psi6_local_mean": rep_p.psi6_local_mean, "defect_fraction": rep_p.defect_fraction})

    # Window-corrected S(k->0) suppresses the raw finite-aperture peak
    sk_corr = structure_factor(a_patch, a_mask, window_correction=True)
    sk_raw = structure_factor(a_patch, a_mask, window_correction=False)
    assert sk_corr["S"][0] < sk_raw["S"][0]


def test_conway_sloane_decoders_and_nsm() -> None:
    """Verify A2, D4, E8 decoders against brute force + lattice membership + planted wrong decoder."""
    rng = np.random.default_rng(123)
    for kind, dim, rad in (("A2", 2, 3.0), ("D", 4, 2.5), ("E8", 8, 2.0)):
        check = verify_lattice_decoder(kind, dim, rad, queries=2_000, rng=rng)
        assert check["passed"] is True
        assert check["mismatches"] == 0

    # Planted wrong decoder (Z4 rounding used for D4) must be caught by both distance and membership checks
    planted = verify_lattice_decoder("D", 4, 2.5, queries=1_000, rng=rng, decode_fn=nearest_zn)
    assert planted["passed"] is False
    assert planted["mismatches"] > 0
    assert planted["non_member_violations"] > 0

    # Monte Carlo NSM matches Conway-Sloane reference within 1%
    g_a2, _ = nsm_mc("A2", 2, samples=50_000, rng=rng)
    assert g_a2 == pytest.approx(nsm_reference("A2", 2), rel=0.01)


# ---------------------------------------------------------------------------
# 3. Lean 4 Footprint Classifier & Laya-LoRA Peer Review Fixes
# ---------------------------------------------------------------------------


def test_lean_footprint_classification_and_w7_labels() -> None:
    """Verify H0.3 footprint classification and Reviewer 2 W7 sorry obligation labeling."""
    clean = classify_axiom_footprint(["propext", "Classical.choice", "Quot.sound"])
    assert clean["status"] == "proven"
    assert "Verified" in str(clean["verification_label"])

    target = classify_axiom_footprint(["propext", "sorryAx"])
    assert target["status"] == "target"
    assert "Unverified — sorry obligation pending" in str(target["verification_label"])

    rejected = classify_axiom_footprint(["propext", "ctl_cheat"])
    assert rejected["status"] == "rejected"
    assert "ctl_cheat" in str(rejected["verification_label"])

    missing = classify_axiom_footprint(None)
    assert missing["status"] == "missing"

    res_sorry = LeanVerificationResult(
        theorem_name="inv_i3",
        compiled_successfully=True,
        returncode=0,
        elapsed_ms=12.0,
        axioms=["sorryAx"],
        has_sorry=True,
        energy_score=1e6,
        output="",
    )
    assert res_sorry.footprint_status == "target"
    assert res_sorry.verification_label == "[Unverified — sorry obligation pending]"


def test_laya_lora_peer_review_fixes() -> None:
    """Verify Reviewer 2 W1 (LoRA arithmetic), W2 (Wilson CI), W3/W8 (provenance), and W5 (calibration)."""
    # W1: Exact LoRA parameter count (540,672 vs 539,136 -> resolves 1,536 discrepancy)
    audit = audit_laya_lora_parameters()
    assert audit["lora_total_params"] == 540_672
    assert audit["legacy_eq2_discrepancy_resolved"] == 1_536
    assert audit["scaling_factor_alpha_over_r"] == pytest.approx(2.0)
    assert audit["heads"]["NoulHead"] == 769
    assert audit["heads"]["ChoiceHead"] == 207_144
    assert audit["heads"]["ScoreHead"] == 98_561
    assert audit["total_trainable_params"] == 540_672 + 769 + 207_144 + 98_561

    # W2: 11/12 validation set is flagged as statistically inadequate with wide Wilson CI
    ci_small = wilson_ci_95(11, 12)
    assert ci_small["statistically_adequate"] is False
    assert 0.60 <= ci_small["ci_low"] <= 0.66
    assert ci_small["ci_high"] > 0.98

    ci_large = wilson_ci_95(460, 500)
    assert ci_large["statistically_adequate"] is True

    # W5: Calibrate tau_noul to avoid blocking valid PASS cases
    probs = [0.12, 0.18, 0.22, 0.25, 0.72, 0.81, 0.88, 0.93]
    labels = [False, False, False, False, True, True, True, True]
    cal = calibrate_noul_threshold(probs, labels)
    assert cal["best_f1"] == pytest.approx(1.0)
    assert 0.25 < cal["optimal_tau_noul"] <= 0.72

    # W3 & W8: Provenance-tagged comparative row requires citation for literature rows
    row_measured = build_provenance_comparative_row(
        "Laya-LoRA (ModernBERT-base)",
        provenance="measured",
        p50_warm_ms=42.5,
        first_call_cold_ms=3911.6,
        energy_wh_per_1k=0.45,
        environment="CPU 4 threads, PyTorch 2.14, 24 tokens",
    )
    assert row_measured["symbol"] == "✓"
    assert row_measured["p50_warm_ms"].startswith("✓")

    with pytest.raises(ValueError, match="citation"):
        build_provenance_comparative_row(
            "Qwen2.5-0.5B",
            provenance="literature",
            p50_warm_ms=385.0,
            energy_wh_per_1k=4.80,
            environment="CPU 4 threads",
            citation=None,
        )
