"""Integration tests for scripts/manage_sub_project.py and the 3 Humanitarian Frontier Subprojects."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


def test_manage_sub_project_help():
    """Verify that manage_sub_project CLI shows help successfully."""
    cmd = [sys.executable, "scripts/manage_sub_project.py", "--help"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert "AutoevolveAI Sub-Project Manager" in res.stdout
    assert "gitclone" in res.stdout
    assert "audit" in res.stdout
    assert "verify-frontiers" in res.stdout
    assert "roadmap" in res.stdout


def test_manage_sub_project_status_and_list_json():
    """Verify that all registered Frontier sub-projects and 16 ecosystem repos are ready."""
    cmd_status = [sys.executable, "scripts/manage_sub_project.py", "status"]
    res_status = subprocess.run(cmd_status, capture_output=True, text=True)
    assert res_status.returncode == 0
    assert "[READY] 3A" in res_status.stdout
    assert "[READY] 3B" in res_status.stdout
    assert "[READY] 3C" in res_status.stdout
    assert "[READY] BACKBONE" in res_status.stdout
    assert "[READY] KINETIC" in res_status.stdout
    assert "[READY] RUNTIME" in res_status.stdout
    assert "[READY] LEANFLOW" in res_status.stdout
    assert "[READY] HIVEMIND" in res_status.stdout

    cmd_list = [sys.executable, "scripts/manage_sub_project.py", "list", "--json"]
    res_list = subprocess.run(cmd_list, capture_output=True, text=True)
    assert res_list.returncode == 0
    payload = json.loads(res_list.stdout)
    slugs = {sp["slug"] for sp in payload["subprojects"]}
    assert {
        "socrateai_scientific_fusion_energy",
        "socrateai_scientific_mechanica_fluidorum",
        "socrateai_scientific_quantum_computing",
        "rusty_sundials",
        "socrateai_scientific_agora_physique_cinetique",
        "runux_ai_runtime",
        "socrateai_scientific_agora_leanflow",
        "hivemind",
    }.issubset(slugs)
    assert len(payload["ecosystem_repositories"]) >= 21


def test_manage_sub_project_verify_frontiers():
    """Verify exact-Q / exact-Z telemetry for Breakthrough Missions 3A, 3B, 3C, Agora Kinetic, RunuX Runtime, LeanFlow MCP, and rusty-SUNDIALS."""
    cmd = [sys.executable, "scripts/manage_sub_project.py", "verify-frontiers", "--json"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert data["overall_status"] == "ALL_FRONTIERS_CERTIFIED"

    # 3A: Clean Fusion Energy (Littlejohn 3D Stellarator Non-Canonical Guiding-Center + Discretization-Free Kinetic Bridge)
    t3a = data["frontier_3a_fusion_energy"]["telemetry"]
    assert t3a["exact_rational_h0"] == "5601/10000"
    assert t3a["exact_float_h0"] == pytest.approx(0.5601)
    assert t3a["dual_rrk_max_energy_drift"] < 1e-13
    assert t3a["noncanonical_littlejohn_dual_rrk_drift"] < 1e-13
    assert t3a["magnetic_moment_mu_drift"] == 0.0
    assert t3a["mirror_trapping_margin_rational"] == "399/10000"
    assert t3a["poisson_bracket_self_zero_residual"] == 0.0
    assert t3a["rk4_max_energy_drift"] > 1e-9
    assert t3a["lorentz_zero_work_residual"] == 0.0
    assert t3a["agora_kinetic_landau_pade11_u_rational"] == "10/37"
    assert t3a["agora_kinetic_volterra_rho2_4_rational"] == "-1/18"
    assert t3a["villani_thm22_6_fisher_gamma_bar_sq_rational"] == "149481/12500"
    assert t3a["discretization_free_kinetic_time_verified"] is True
    assert t3a["weierstrass_ode_discarded_in_paper1b"] is True
    assert t3a["gate_passed"] is True

    # 3B: CAP in Navier-Stokes & Self-Similar Hurricane Boundary-Layer Dynamics + Continuum Galerkin Tail Bound
    t3b = data["frontier_3b_cap_navier_stokes_climate"]["telemetry"]
    assert t3b["contraction_kappa_rational"] == "181/500"
    assert t3b["contraction_kappa_float"] == pytest.approx(0.362)
    assert t3b["ball_image_bound_rational"] == "231/500000"
    assert t3b["self_similar_hurricane_kappa_rational"] == "443/1000"
    assert t3b["self_similar_hurricane_kappa_float"] == pytest.approx(0.443)
    assert t3b["self_similar_hurricane_ball_bound_rational"] == "543/2000000"
    assert t3b["self_similar_hurricane_contracting"] is True
    assert t3b["continuum_galerkin_tail_m10_rational"] == "1/100"
    assert t3b["continuum_total_kappa_rational"] == "93/250"
    assert t3b["continuum_total_kappa_float"] == pytest.approx(0.372)
    assert t3b["discretization_free_continuum_verified"] is True
    assert t3b["ball_self_mapping_verified"] is True
    assert t3b["strict_contraction_verified"] is True
    assert t3b["gate_passed"] is True

    # 3C: FLT-Grounded SQIsign PQC Supersingular Isogeny Soundness & Quantum Computing
    t3c = data["frontier_3c_pqc_and_quantum_computing"]["telemetry"]
    assert t3c["inhabited_witness_abc"] == [15, 16, 31]
    assert t3c["inhabited_witness_delta_scaled"] == 55353600
    assert t3c["inhabited_witness_c4"] == 721
    assert t3c["inhabited_witness_coprime_gcd"] == 1
    assert t3c["isogeny_step8_degrees"] == {"2": 256, "3": 6561, "5": 390625}
    assert t3c["hecke_tower_level15_out_degrees"] == {"2": 3, "3": 3, "5": 5, "7": 8}
    assert t3c["hecke_tower_2isogeny_paths_len16"] == 98304
    assert t3c["qm_quaternion_norm_multiplicativity_verified"] is True
    assert t3c["sqisign_deuring_response_norm"] == 65536
    assert t3c["sqisign_dual_pair_product_degree"] == 429981696
    assert t3c["sqisign_discriminant"] == -196608
    assert t3c["rust_verifier_cargo_test_passed"] is True
    assert t3c["gate_passed"] is True

    # Kinetic Discretization-Free Bridge (`SocrateAI-Scientific-Agora-Physique-Cinetique`)
    tkin = data["kinetic_discretization_free_bridge"]["subproject"]
    assert tkin["landau_pade11_root_u_rational"] == "10/37"
    assert tkin["volterra_rho2_4_rational"] == "-1/18"
    assert tkin["villani_rust_d3_min_bound"] >= 4.3
    assert tkin["villani_rust_d2_min_bound"] > 3.3
    assert tkin["villani_rust_verified"] is True
    assert tkin["gate_passed"] is True

    # RunuX AI Runtime Bridge (`runux-ai-runtime`)
    trnx = data["runux_ai_runtime_bridge"]["subproject"]
    assert trnx["z_tail_rational"] == "1/100"
    assert trnx["continuum_kappa_rational"] == "93/250"
    assert trnx["rust_cargo_test_passed"] is True
    assert trnx["gate_passed"] is True

    # LeanFlow MCP 3-Domains Bridge (`SocrateAI-Scientific-Agora-LeanFlow`)
    tlf = data["leanflow_mcp_3domains_bridge"]["subproject"]
    assert tlf["robertson_cvode_steps"] == 3109
    assert tlf["robertson_cvode_rhs_evals"] == 8848
    assert tlf["robertson_invariants_satisfied"] is True
    assert tlf["domain_3a_lean_tier"] == "A"
    assert tlf["domain_3b_lean_tier"] == "A"
    assert tlf["domain_3c_lean_tier"] == "A"
    assert tlf["domain_3c_deuring_norm"] == 65536
    assert tlf["fail_closed_sorry_rejected"] is True
    assert tlf["fail_closed_false_refuted"] is True
    assert tlf["gate_passed"] is True

    # Backbone: rusty-SUNDIALS
    tbb = data["solver_backbone_rusty_sundials"]
    assert tbb["status"] == "CERTIFIED"
    assert tbb["dual_rrk_relaxation_certificate"]["positive_step"] is True

    # HiveMind Decentralized Sparse MoE Swarm Bridge (`HiveMind`)
    thm = data["hivemind_swarm_bridge"]["subproject"]
    assert thm["lean_theorems_count"] == 77
    assert thm["lean_sorry_count"] == 0
    assert thm["lean_axiom_count"] == 0
    assert thm["nf4_compression_ratio_rational"] == "128/33"
    assert thm["diloco_wire_compression_rational"] == "5000/3"
    assert thm["rtx2070_usable_vram_mib"] == 6656
    assert thm["spot_check_fraction_rational"] == "1/10"
    assert thm["spot_check_boinc_savings_factor"] == 20
    assert thm["multikrum_n10_f3_neighborhood_k"] == 5
    assert thm["btm_top2_active_compute_rational"] == "1/4"
    assert thm["pouw_pool_total_bps"] == 10000
    assert thm["prefix_trie_node_ratio_rational"] == "19/25"
    assert thm["hierarchical_128_moe_gating_ratio_rational"] == "1/8"
    assert thm["rtx_stress_10_stages_passed"] is True
    assert thm["e2e_8_domain_branches_verified"] is True
    assert thm["gate_passed"] is True


def test_manage_sub_project_audit_path(tmp_path: Path):
    """Verify manage_sub_project audit executes harness on a specific target path and all frontier harnesses."""
    from antigravity_harness.core.anti_stub_guard import AntiStubGuard

    sample_file = tmp_path / "valid_sample.py"
    sample_file.write_text(
        "def compute_energy(lat: float, mem: float) -> float:\n"
        '    """Calculates physical energy metric."""\n'
        "    return 0.5 * lat + 0.5 * mem\n"
    )

    cmd = [
        sys.executable,
        "-m",
        "antigravity_harness",
        "audit",
        str(sample_file),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert "Audit PASSED" in res.stdout

    guard = AntiStubGuard()
    for target in (
        "scripts/manage_sub_project.py",
        "sub_projects/socrateai_scientific_fusion_energy/fusion_guiding_center_harness.py",
        "sub_projects/socrateai_scientific_mechanica_fluidorum/cap_navier_stokes_climate_harness.py",
        "sub_projects/socrateai_scientific_quantum_computing/pqc_isogeny_quantum_harness.py",
        "sub_projects/rusty_sundials/rusty_sundials_bridge_harness.py",
        "sub_projects/socrateai_scientific_agora_physique_cinetique/kinetic_discretization_free_harness.py",
        "sub_projects/runux_ai_runtime/runux_runtime_bridge_harness.py",
        "sub_projects/socrateai_scientific_agora_leanflow/leanflow_3domains_harness.py",
        "sub_projects/hivemind/hivemind_swarm_bridge_harness.py",
    ):
        result = guard.audit_file(Path(target))
        assert result.is_clean, f"AntiStubGuard failed on {target}: {result.summary}"
