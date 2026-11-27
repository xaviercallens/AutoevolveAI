"""
Integration Tests for the 3 Breakthroughs & Domains Multi-Model Workflow
========================================================================
Tests:
  1. Multi-model routing policy (`gemini-4-argon`, `gemini-3.5-flash-high`,
     `deepseek-prover-v2:7b`, `goedel-prover-v2:8b`, `gemini-3.1-pro`, and
     Peer-Review-Only `claude-opus-4-6`, with zero `claude-sonnet`).
  2. Serverless Lean 4 tactic cascade (`T0` handled by serverless provers vs.
     `T1-T3` escalated to `gemini-4-argon` via `CapabilityMatrix`).
  3. Lean 4 specification & proof integrity (`Breakthroughs3DomainsSpec.lean`
     & `Breakthroughs3Domains.lean`, 0 `sorry`, 0 custom `axiom`, 16 `rfl` locks).
  4. Certified numerical & `LeanFlow MCP` telemetry across Domains 3A, 3B, 3C.
  5. 5-Round Opus adversarial peer review, compiled single-column PDFs, and
     Zenodo Open-Science DOI receipts.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from anse.elenchus.scientific_swarm import ElenchusScientificSwarm
from anse.elenchus.three_breakthroughs_workflow import (
    EXTERNAL_PEER_REVIEW_HARDNESS_GATES,
    THREE_BREAKTHROUGHS_WORKFLOW_STAGES,
    build_serverless_prover_capability_matrix,
    verify_three_breakthroughs_workflow_policy,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_workflow_model_routing_policy() -> None:
    report = verify_three_breakthroughs_workflow_policy(REPO_ROOT)
    assert report["policy_compliant"] is True
    assert report["policy_passed"] is True
    assert report["opus_restricted_to_stage"] == ["W5_OPUS_5ROUND_ADVERSARIAL_PEER_REVIEW"]
    assert report["argon_complex_orchestration_verified"] is True
    assert report["flash_high_literature_and_simple_code_verified"] is True
    assert report["external_referee_gates_covered"] is True
    assert len(EXTERNAL_PEER_REVIEW_HARDNESS_GATES) == 6
    assert report["base_elenchus_swarm_policy"]["zero_claude_sonnet_used"] is True
    assert report["base_elenchus_swarm_policy"]["opus_peer_review_only"] is True
    assert len(THREE_BREAKTHROUGHS_WORKFLOW_STAGES) == 6


def test_serverless_prover_capability_matrix() -> None:
    cap = build_serverless_prover_capability_matrix()
    assert "deepseek-prover-v2:7b" in cap["models_evaluated"]
    assert "goedel-prover-v2:8b" in cap["models_evaluated"]
    assert "gemini-4-argon" in cap["models_evaluated"]
    assert "gemini-3.5-flash-high" in cap["models_evaluated"]
    assert cap["peer_review_exclusive_model"] == "claude-opus-4-6"
    assert len(cap["t0_top_candidates"]) >= 1
    assert cap["t3_top_candidates"][0]["model"] == "gemini-4-argon"


def test_lean4_breakthroughs_spec_and_proof_integrity() -> None:
    spec_path = REPO_ROOT / "formal" / "ANSE" / "Breakthroughs3DomainsSpec.lean"
    proof_path = REPO_ROOT / "formal" / "ANSE" / "Breakthroughs3Domains.lean"
    assert spec_path.exists()
    assert proof_path.exists()

    spec_text = spec_path.read_text(encoding="utf-8")
    proof_text = proof_path.read_text(encoding="utf-8")

    def strip_lean_comments(s: str) -> str:
        s = re.sub(r"/-.*?-/", "", s, flags=re.DOTALL)
        s = re.sub(r"--.*$", "", s, flags=re.MULTILINE)
        return s

    clean_spec = strip_lean_comments(spec_text)
    clean_proof = strip_lean_comments(proof_text)

    assert len(re.findall(r"\bsorry\b", clean_spec)) == 0
    assert len(re.findall(r"\bsorry\b", clean_proof)) == 0
    assert len(re.findall(r"^\s*axiom\b", clean_spec, flags=re.MULTILINE)) == 0
    assert len(re.findall(r"^\s*axiom\b", clean_proof, flags=re.MULTILINE)) == 0

    for required_def in (
        "stokesTailEigenvalue",
        "derivedStokesTailBound",
        "derivedDualScaleTailBound",
        "derivedBiHelmholtzTailBound",
        "derivedGalerkinResidualY0",
        "derivedApproximateInverseDefectZ0",
        "derivedBilinearBoundZ2",
        "kSmooth",
        "kEff",
        "rnsDotProduct3",
    ):
        assert required_def in clean_spec

    for required_proof_def in (
        "stokesTailEigenvalue",
        "derivedStokesTailBound",
        "derivedDualScaleTailBound",
        "derivedBiHelmholtzTailBound",
        "derivedGalerkinResidualY0",
        "derivedApproximateInverseDefectZ0",
        "derivedBilinearBoundZ2",
        "kSmooth",
        "kEff",
        "Stmt_P2_T4_MensuraSym2CrossProductAperyRNS",
        "leanflow_cap_galerkin_radii_polynomial_contraction",
        "leanflow_piecewise_scale_involution_lemma",
        "leanflow_smooth_vs_piecewise_characterization_lemma",
        "leanflow_sym2_hadamard_recurrence_and_rns_inner_product",
        "leanflow_taylor_interval_and_spectral_bound",
        "B3D_T1_conformational_gibbs_relaxation_and_atp_forcing",
        "B3D_T2_bihelmholtz_nonlocal_elasticity_and_riccati_threshold",
        "B3D_T3_multiscale_haar_paraproduct_and_dyadic_flux",
        "B3D_T4_bioelectrical_lienard_limit_cycles_and_dual_rrk",
        "B3D_T5_dispersive_sigma_three_quantum_material_and_imex",
        "B3E_T1_hopfield_ninio_art_proofreading_and_gibbs_fidelity",
        "B3E_T2_calugareanu_dna_supercoiling_and_leray_bgk_fork",
        "B3E_T3_flt_quaternion_codon_palindrome_and_hecke_phylogeny",
        "B3E_T4_kjma_dna_replication_and_sym2_fork_coalescence",
        "B3E_T5_multiscale_haar_repliseq_and_rusty_sundials_imex_rrk",
    ):
        assert required_proof_def in clean_proof

    rfl_locks = re.findall(
        r"example\s*:\s*Stmt_[A-Za-z0-9_]+\s*=.*?:=\s*rfl",
        clean_proof,
        flags=re.DOTALL,
    )
    assert len(rfl_locks) >= 26

    print_axioms = re.findall(r"#print\s+axioms\s+[A-Za-z0-9_']+", proof_text)
    assert len(print_axioms) >= 26


def test_external_referee_round2_gates_catch_defects() -> None:
    swarm = ElenchusScientificSwarm(REPO_ROOT)
    spec_text = (REPO_ROOT / "formal" / "ANSE" / "Breakthroughs3DomainsSpec.lean").read_text(
        encoding="utf-8"
    )

    # Positive control: remediated Paper B LaTeX passes all 6 external referee gates
    paper_b_tex = (
        REPO_ROOT
        / "papers"
        / "three_breakthroughs"
        / "paper_b"
        / "PaperB_NavierStokes_Hurricane_Mensura_DualScale_CAP.tex"
    ).read_text(encoding="utf-8")
    pos_audit = swarm.audit_external_referee_round2_gates(
        paper_id="BREAKTHROUGH_PAPER_B",
        tex_text=paper_b_tex,
        spec_text=spec_text,
    )
    assert pos_audit["all_passed"] is True

    # Negative control: feed a defective manuscript mimicking the external referee issues
    defective_tex = r"""
    \title{No-Go Theorem and Cross-Product Sym^2(L_2) in String Theory T-Duality}
    \author{Xavier Callens (Autonomous Neuro-Symbolic Energy Swarm)}
    \begin{document}
    We test ARGOS-HARD-009 in Stage W2 of Breakthrough Domain 3B (Tier X).
    For the cross-product $w_n = u_n\tilde{u}_n$, RNS-CRT gives 770.
    Also [2329/3840, 233/384] and $\zeta(3)$ with + 1/500.
    \end{document}
    """
    neg_audit = swarm.audit_external_referee_round2_gates(
        paper_id="BREAKTHROUGH_PAPER_B",
        tex_text=defective_tex,
        spec_text="def dummy := 0",
    )
    assert neg_audit["all_passed"] is False
    gates = neg_audit["gates"]
    assert gates["ARGOS-PEER-008"] is False
    assert gates["ARGOS-PEER-009"] is False
    assert gates["ARGOS-PEER-010"] is False
    assert gates["ARGOS-PEER-011"] is False
    assert gates["ARGOS-PEER-012"] is False
    assert gates["ARGOS-PEER-013"] is False


def test_three_breakthroughs_telemetry_opus_peer_review_and_zenodo_dois() -> None:
    results_dir = REPO_ROOT / "results" / "three_breakthroughs"
    papers_dir = REPO_ROOT / "papers" / "three_breakthroughs"

    tel_a = json.loads((results_dir / "paper_a_telemetry.json").read_text(encoding="utf-8"))
    tel_b = json.loads((results_dir / "paper_b_telemetry.json").read_text(encoding="utf-8"))
    tel_c = json.loads((results_dir / "paper_c_telemetry.json").read_text(encoding="utf-8"))
    tel_d = json.loads((results_dir / "paper_d_telemetry.json").read_text(encoding="utf-8"))

    assert tel_a["stellarator_gc_h0_rational"] == "5601/10000"
    assert tel_a["villani_gamma_bar_sq_rational"] == "149481/12500"
    assert tel_a["zero_sound_u_pade_rational"] == "10/37"
    assert tel_a["leanflow_mcp_3a"]["status"] == "verified"
    assert tel_a["leanflow_cert_3a"]["status"] == "verified"

    assert tel_b["pde_stokes_tail_eigenvalue"] == 1
    assert tel_b["cap_ztail_rational"] == "1/200"
    assert tel_b["cap_ztail_dual_rational"] == "1/800"
    assert tel_b["cap_y0_rational"] == "1/10000"
    assert tel_b["cap_z0_rational"] == "7/20"
    assert tel_b["cap_z2"] == 12
    assert tel_b["cap_kappa_continuum_rational"] == "93/250"
    assert tel_b["cap_kappa_dual_rational"] == "1473/4000"
    assert tel_b["cap_poly_dual_rational"] == "-2127/4000000"
    assert tel_b["cap_kappa_hurricane_rational"] == "443/1000"
    assert tel_b["rns_vector_u"] == [10, 20, 30]
    assert tel_b["rns_vector_v"] == [11, 12, 14]
    assert tel_b["rns_crt_dot_product"] == 770
    assert tel_b["interval_exp_neg_half_lo_rational"] == "2329/3840"
    assert tel_b["leanflow_mcp_3b"]["status"] == "verified"
    assert tel_b["leanflow_cert_3b"]["status"] == "verified"

    assert tel_c["hellegouarch_c4"] == 721
    assert tel_c["hellegouarch_delta_min"] == 216225
    assert tel_c["hellegouarch_delta_unscaled"] == 55353600
    assert tel_c["bezout_identity"] == "694 * 55353600 - 53280719 * 721 = 1"
    assert tel_c["bezout_identity_min"] == "298 * 216225 - 89369 * 721 = 1"
    assert tel_c["sqisign_total_verification_degree"] == 429981696
    assert tel_c["leanflow_mcp_3c"]["status"] == "verified"
    assert tel_c["leanflow_cert_3c"]["status"] == "verified"

    assert tel_d["bihelmholtz_ztail_rational"] == "1/3200"
    assert tel_d["bihelmholtz_kappa_rational"] == "5877/16000"
    assert tel_d["bihelmholtz_poly_rational"] == "-8523/16000000"
    assert tel_d["dyadic_haar_n4_lower_bound_rational"] == "5/2"
    assert tel_d["lienard_melnikov_polynomial"] == "1 - 3u + u^2"
    assert tel_d["lienard_melnikov_discriminant"] == 5

    tel_e = json.loads((results_dir / "paper_e_telemetry.json").read_text(encoding="utf-8"))
    assert tel_e["hopfield_error_m2_rational"] == "1/10000"
    assert tel_e["hopfield_error_m3_rational"] == "1/1000000"
    assert tel_e["hopfield_suppression_factor"] == 10000
    assert tel_e["calugareanu_lk0_exact"] == 94
    assert tel_e["bihelmholtz_dna_kappa_rational"] == "5877/16000"
    assert tel_e["art_palindrome_duplex_norm"] == 40000
    assert tel_e["kjma_taylor4_exp6_rational"] == "115"
    assert tel_e["leanflow_mcp_3e"]["status"] == "verified"
    assert tel_e["leanflow_cert_3e"]["status"] == "verified"

    review_summary = json.loads(
        (results_dir / "three_breakthroughs_peer_review_summary.json").read_text(encoding="utf-8")
    )
    assert review_summary["all_3_papers_5round_opus_passed"] is True
    assert review_summary["all_4_papers_5round_opus_passed"] is True
    assert review_summary["all_5_papers_5round_opus_passed"] is True
    for key in ("paper_a", "paper_b", "paper_c", "paper_d", "paper_e"):
        rep = review_summary["papers"][key]
        assert rep["all_5_rounds_passed"] is True
        assert rep["overall_epistemic_score"] == 1.0
        assert rep["publish_gate_decision"] == "APPROVED_FOR_ZENODO_PUBLICATION"
        assert rep["external_referee_round2_gate_audit"]["all_passed"] is True

    for sub, pdf_name in (
        ("paper_a", "PaperA_Stellarator_Fusion_DualRRK_Villani_LeanFlow.pdf"),
        ("paper_b", "PaperB_NavierStokes_Hurricane_Mensura_DualScale_CAP.pdf"),
        ("paper_c", "PaperC_FLT_Modular_PQC_SQIsign_Quantum_Rust_Lean4.pdf"),
        ("paper_d", "PaperD_Biophysics_Genetics_EnergyMaterials_Autoresearch_Lean4.pdf"),
        (
            "paper_e",
            "PaperE_Genetics_DNAReplication_ART_LeanFlow_RustySundials_Lean4.pdf",
        ),
    ):
        pdf_path = papers_dir / sub / pdf_name
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 350_000

    zenodo_receipts = json.loads(
        (results_dir / "zenodo_3breakthroughs_receipts.json").read_text(encoding="utf-8")
    )
    assert zenodo_receipts["published_count"] == 5
    for rec in zenodo_receipts["receipts"]:
        assert rec["doi"].startswith("10.5281/zenodo.")
        assert rec["submitted"] is True


def test_elenchus_trilogy_paper3_peer_review_remediation_gates() -> None:
    swarm = ElenchusScientificSwarm(REPO_ROOT)
    p3_tex_path = (
        REPO_ROOT
        / "papers"
        / "elenchus_trilogy"
        / "paper3"
        / "Paper3_Leray_BGK_NeuralFGMRES_Elenchus.tex"
    )
    p3_pdf_path = (
        REPO_ROOT
        / "papers"
        / "elenchus_trilogy"
        / "paper3"
        / "Paper3_Leray_BGK_NeuralFGMRES_Elenchus.pdf"
    )
    spec_path = REPO_ROOT / "formal" / "ANSE" / "ElenchusTrilogySpec.lean"

    pos_audit = swarm.audit_external_referee_round2_gates(
        paper_id="ELENCHUS_TRILOGY_PAPER_3",
        tex_text=p3_tex_path.read_text(encoding="utf-8"),
        spec_text=spec_path.read_text(encoding="utf-8"),
        pdf_path=p3_pdf_path,
    )
    assert pos_audit["all_passed"] is True
    for g_val in pos_audit["gates"].values():
        assert g_val is True

    # Negative check: un-remediated Paper 3 text lacking Section 3 & 4 enhancements must fail
    defective_p3_tex = r"""
    \documentclass[11pt]{article}
    \date{October 2026}
    \begin{document}
    Leray-a filtering and 7 \cdot B = 0 for we \in [0,1].
    Since P^2 = P = P^*, I - P is orthogonal.
    From \ln t \le t - 1 and \mathrm{div}\circ\mathrm{curl} = 0.
    \end{document}
    """
    neg_audit = swarm.audit_external_referee_round2_gates(
        paper_id="ELENCHUS_TRILOGY_PAPER_3",
        tex_text=defective_p3_tex,
        spec_text="def dummy := 0",
    )
    assert neg_audit["all_passed"] is False
    assert neg_audit["gates"]["ARGOS-PEER-008"] is False
    assert neg_audit["gates"]["ARGOS-PEER-012"] is False
    assert neg_audit["gates"]["ARGOS-PEER-013"] is False


def test_paper_c_external_referee_remediation_gates() -> None:
    swarm = ElenchusScientificSwarm(REPO_ROOT)
    pc_tex_path = (
        REPO_ROOT
        / "papers"
        / "three_breakthroughs"
        / "paper_c"
        / "PaperC_FLT_Modular_PQC_SQIsign_Quantum_Rust_Lean4.tex"
    )
    pc_pdf_path = (
        REPO_ROOT
        / "papers"
        / "three_breakthroughs"
        / "paper_c"
        / "PaperC_FLT_Modular_PQC_SQIsign_Quantum_Rust_Lean4.pdf"
    )
    spec_path = REPO_ROOT / "formal" / "ANSE" / "Breakthroughs3DomainsSpec.lean"

    pos_audit = swarm.audit_external_referee_round2_gates(
        paper_id="BREAKTHROUGH_PAPER_C",
        tex_text=pc_tex_path.read_text(encoding="utf-8"),
        spec_text=spec_path.read_text(encoding="utf-8"),
        pdf_path=pc_pdf_path,
    )
    assert pos_audit["all_passed"] is True
    for g_val in pos_audit["gates"].values():
        assert g_val is True

    # Negative check: legacy Paper C text containing the rejected errors must fail every Paper-C gate
    defective_pc_tex = r"""
    \documentclass[11pt]{article}
    \title{SQIsign Rust Verification and Neutral-Atom Riesz-6 Blockade in Lean 4}
    \author{Xavier Callens (Autonomous Neuro-Symbolic Energy Swarm)}
    \begin{document}
    Under ARGOS-HARD-009 in Stage W2 of Breakthrough Domain 3C (Tier X),
    we have 256 \cdot 16 + 721 \cdot 30879 = 22267855 and 14170521600,
    with 4p - 8 \equiv 3p - 8 \pmod p and Rydberg Blockade rydbergCZGateFidelityNum.
    \end{document}
    """
    neg_audit = swarm.audit_external_referee_round2_gates(
        paper_id="BREAKTHROUGH_PAPER_C",
        tex_text=defective_pc_tex,
        spec_text="def dummy := 0",
    )
    assert neg_audit["all_passed"] is False
    for g_name in (
        "ARGOS-PEER-008",
        "ARGOS-PEER-009",
        "ARGOS-PEER-012",
        "ARGOS-PEER-013",
    ):
        assert neg_audit["gates"][g_name] is False


def test_karpathy_genetic_autoresearch_13_to_5_to_3_and_lean4() -> None:
    results_dir = REPO_ROOT / "results" / "three_breakthroughs"
    tsv_path = results_dir / "genetic_autoresearch_13_hypotheses.tsv"
    report_path = results_dir / "genetic_autoresearch_report.json"
    spec_path = REPO_ROOT / "formal" / "ANSE" / "GeneticAutoresearchSpec.lean"
    proof_path = REPO_ROOT / "formal" / "ANSE" / "GeneticAutoresearch.lean"

    assert tsv_path.exists()
    assert report_path.exists()
    assert spec_path.exists()
    assert proof_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["total_hypotheses_screened"] == 13
    assert report["selected_top5_formal_ids"] == ["GAR.H1", "GAR.H2", "GAR.H3", "GAR.H4", "GAR.H5"]
    assert report["selected_top3_numeric_ids"] == ["GAR.H1", "GAR.H2", "GAR.H3"]

    bench = report["top3_numerical_benchmarks"]
    assert bench["rust_sundials_genetics_tests_passed"] is True
    assert bench["top3_gar_h1_conjecture_c1"]["kappa_c1_rational"] == "5957/16000"
    assert bench["top3_gar_h1_conjecture_c1"]["poly_c1_rational"] == "-8443/16000000"
    assert bench["top3_gar_h1_conjecture_c1"]["err3_torque_rational"] == "27/15625000"
    assert bench["top3_gar_h2_conjecture_c2"]["unpreconditioned_cond_rational"] == "25/3"
    assert bench["top3_gar_h2_conjecture_c2"]["haar_preconditioned_cond_rational"] == "1"
    assert bench["top3_gar_h2_conjecture_c2"]["haar_direct_iters_tol_1e14"] == 1
    assert bench["top3_gar_h3_efficient_art_engine"]["slippage_parity_defect"] == 12
    assert bench["top3_gar_h3_efficient_art_engine"]["slippage_duplex_norm"] == 44944
    assert bench["top3_gar_h3_efficient_art_engine"]["kjma_k2_taylor4_denom"] == 1237
    assert bench["top3_gar_h3_efficient_art_engine"]["anse_energy_improvement_factor"] > 50.0

    spec_text = spec_path.read_text(encoding="utf-8")
    proof_text = proof_path.read_text(encoding="utf-8")

    def strip_lean_comments(s: str) -> str:
        s = re.sub(r"/-.*?-/", "", s, flags=re.DOTALL)
        s = re.sub(r"--.*$", "", s, flags=re.MULTILINE)
        return s

    clean_spec = strip_lean_comments(spec_text)
    clean_proof = strip_lean_comments(proof_text)
    assert len(re.findall(r"\bsorry\b", clean_spec)) == 0
    assert len(re.findall(r"\bsorry\b", clean_proof)) == 0
    assert len(re.findall(r"^\s*axiom\b", clean_spec, flags=re.MULTILINE)) == 0
    assert len(re.findall(r"^\s*axiom\b", clean_proof, flags=re.MULTILINE)) == 0

    for thm in (
        "GAR_H1_conjecture_c1_torque_coupled_hopfield_and_bihelmholtz_cap",
        "GAR_H2_conjecture_c2_padic_haar_hecke_tree_diagonalization",
        "GAR_H3_quaternion_palindrome_slippage_parity_and_multi_origin_kjma",
        "GAR_H4_sym2_coalescence_resonance_and_rns_kmer_alignment",
        "GAR_H5_lienard_metabolic_clock_ars222_imex_and_energy_minimization",
        "GAR_H6_gudhi_tda_euler_poincare_and_repli_seq_persistence",
        "GAR_H7_bihelmholtz_exact_quartic_factorization_and_chargaff_involution",
    ):
        assert thm in clean_proof

    for tactic in ("prove_pos", "geo_decrease", "auto_eq", "auto_bound", "conv_rate_lt_one"):
        assert tactic in clean_proof

    pe_review = json.loads(
        (
            results_dir
            / "breakthrough_3e_genetics_dna_replication_art_opus_5round_peer_review.json"
        ).read_text(encoding="utf-8")
    )
    controversy_audit = pe_review["opus_controversy_and_honesty_analysis"]
    assert controversy_audit["gate_id"] == "ARGOS-CENTAUR-005"
    assert controversy_audit["lead_adversarial_model"] == "claude-opus-4-6"
    assert controversy_audit["co_synthesis_model"] == "gemini-4-argon"
    assert controversy_audit["controversy_count"] == 4
    assert controversy_audit["all_controversies_honestly_disclosed"] is True

    bio_grounding = json.loads(
        (results_dir / "multi_database_biological_grounding.json").read_text(encoding="utf-8")
    )
    assert "dbsnp-database" in bio_grounding["skills_exercised"]
    assert "clinvar-database" in bio_grounding["skills_exercised"]
    assert "ensembl-database" in bio_grounding["skills_exercised"]
    assert "uniprot-database" in bio_grounding["skills_exercised"]
    assert "interpro-database" in bio_grounding["skills_exercised"]
    assert "alphafold-database-fetch-and-analyze" in bio_grounding["skills_exercised"]
    assert "pdb-database" in bio_grounding["skills_exercised"]
    assert "gudhi-inria-tda" in bio_grounding["skills_exercised"]
    assert bio_grounding["dbsnp_variants"][0]["rsid"] == "rs1057519943"
    assert bio_grounding["dbsnp_variants"][0]["grch38_vcf"] == "chr12:132676598:G>C"
    assert (
        bio_grounding["uniprot_and_interpro"]["proteins"]["Q07864"][
            "has_exonuclease_domain_ipr006133"
        ]
        is True
    )
    assert (
        bio_grounding["uniprot_and_interpro"]["proteins"]["O14746"][
            "has_exonuclease_domain_ipr006133"
        ]
        is False
    )
    assert (
        bio_grounding["alphafold_and_pdb_structures"]["alphafold_O14746_tert"]["global_plddt"]
        == 80.19
    )

    gudhi_tel = json.loads(
        (results_dir / "gudhi_tda_genetic_telemetry.json").read_text(encoding="utf-8")
    )
    assert (
        gudhi_tel["lean4_theorem"] == "GAR_H6_gudhi_tda_euler_poincare_and_repli_seq_persistence"
    )
    assert gudhi_tel["pillar1_tert_3d_alphacomplex"]["full_num_vertices"] == 1132
    assert gudhi_tel["pillar1_tert_3d_alphacomplex"]["full_num_simplices"] == 32397
    assert (
        gudhi_tel["pillar1_tert_3d_alphacomplex"][
            "domain2_catalytic_tunnel_diameter_angstrom"
        ]
        == 19.6805
    )
    assert gudhi_tel["pillar2_supercoiled_dna_ripscomplex"]["relaxed_h1_loop_count"] == 1
    assert (
        gudhi_tel["pillar2_supercoiled_dna_ripscomplex"]["buckled_plectoneme_h1_loop_count"] == 2
    )
    assert (
        gudhi_tel["pillar3_hecke_tree_and_art_hairpin_simplextree"]["pure_hecke_tree_betti_numbers"]
        == [1, 0]
    )
    assert (
        gudhi_tel["pillar3_hecke_tree_and_art_hairpin_simplextree"]["augmented_betti_numbers"]
        == [1, 6]
    )
    assert (
        gudhi_tel["pillar4_repliseq_multi_origin_cubicalcomplex"][
            "total_coalescence_persistence"
        ]
        == 14.0
    )

    hf_val = json.loads(
        (results_dir / "hf_genomic_benchmarks_tda_validation.json").read_text(encoding="utf-8")
    )
    assert hf_val["xgudhi_devel_repository"]["clone_present"] is True
    assert hf_val["leanflow_mcp_link"]["xgudhi_hecke_hairpin_betti_euler_certificate"] == "verified"
    assert hf_val["rusty_sundials_link"]["status"] == "CERTIFIED"
    hf_sum = hf_val["huggingface_genomic_benchmarks_summary"]
    assert hf_sum["datasets_evaluated"] == 3
    assert hf_sum["total_sequences_evaluated"] == 1200
    assert hf_sum["total_deuring_quaternion_norm_checks"] == 12000
    assert hf_sum["total_deuring_quaternion_norm_defects"] == 0
    assert hf_sum["total_simplicial_euler_poincare_checks"] == 1200
    assert hf_sum["total_simplicial_euler_poincare_defects"] == 0

    genetic_repo = (
        REPO_ROOT / "sub_projects" / "socrateai_scientific_genetic" / "SocrateAI-Scientific-Genetic"
    )
    assert (genetic_repo / "README.md").exists()
    assert (genetic_repo / "formal" / "ANSE" / "GeneticAutoresearch.lean").exists()
    assert (genetic_repo / "rust_solver" / "genetics.rs").exists()
    assert (genetic_repo / "xgudhi_tda" / "xgudhi_leanflow_sundials_bridge.py").exists()
    assert (genetic_repo / "data" / "hf_genomic_benchmarks_tda_validation.json").exists()


def test_paper_e_external_referee_remediation_gates() -> None:
    swarm = ElenchusScientificSwarm(REPO_ROOT)
    pe_tex_path = (
        REPO_ROOT
        / "papers"
        / "three_breakthroughs"
        / "paper_e"
        / "PaperE_Genetics_DNAReplication_ART_LeanFlow_RustySundials_Lean4.tex"
    )
    pe_pdf_path = (
        REPO_ROOT
        / "papers"
        / "three_breakthroughs"
        / "paper_e"
        / "PaperE_Genetics_DNAReplication_ART_LeanFlow_RustySundials_Lean4.pdf"
    )
    pd_tex_path = (
        REPO_ROOT
        / "papers"
        / "three_breakthroughs"
        / "paper_d"
        / "PaperD_Biophysics_Genetics_EnergyMaterials_Autoresearch_Lean4.tex"
    )
    pd_pdf_path = (
        REPO_ROOT
        / "papers"
        / "three_breakthroughs"
        / "paper_d"
        / "PaperD_Biophysics_Genetics_EnergyMaterials_Autoresearch_Lean4.pdf"
    )
    spec_path = REPO_ROOT / "formal" / "ANSE" / "Breakthroughs3DomainsSpec.lean"

    pos_e = swarm.audit_external_referee_round2_gates(
        paper_id="BREAKTHROUGH_PAPER_E",
        tex_text=pe_tex_path.read_text(encoding="utf-8"),
        spec_text=spec_path.read_text(encoding="utf-8"),
        pdf_path=pe_pdf_path,
    )
    assert pos_e["all_passed"] is True
    for g_val in pos_e["gates"].values():
        assert g_val is True

    pos_d = swarm.audit_external_referee_round2_gates(
        paper_id="BREAKTHROUGH_PAPER_D",
        tex_text=pd_tex_path.read_text(encoding="utf-8"),
        spec_text=spec_path.read_text(encoding="utf-8"),
        pdf_path=pd_pdf_path,
    )
    assert pos_d["all_passed"] is True
    for g_val in pos_d["gates"].values():
        assert g_val is True

    # Negative check: legacy rejected Paper E text with false Bi-Helmholtz polynomial,
    # OCR/arithmetic errors, naive quaternion base counts, Hellegouarch Genetic Code Distance,
    # and Karpathy autoresearch 13-to-5-to-3 funnel jargon must fail the referee gates.
    defective_pe_tex = r"""
    \documentclass[11pt]{article}
    \date{}
    \begin{document}
    Evaluating at \gamma = 1/100 yields (1/100)^2 = 1/1000, (1/100)^3 = 1/100000,
    and (1/100)/(1/100000) = 10006.
    Part (2) follows from (1 + \alpha' k^2)^4 - \frac{256}{27}\alpha' k^2 =
    (1 - 3\alpha' k^2)^2\bigl((1+\alpha' k^2)^2 + \frac{16}{3}\alpha' k^2 + \frac{16}{27}(\alpha')^2 k^4\bigr).
    Evaluating at (8,6,8,6) gives 4+36+64+36 = 200.
    On the (p+1)-regular mutational Bruhat--Tits tree for the 4-nucleotide alphabet,
    Inhabited Hellegouarch Genetic Code Distance Witness.
    Karpathy autoresearch 13-to-5-to-3 Genetic Funnel.
    \end{document}
    """
    neg_e = swarm.audit_external_referee_round2_gates(
        paper_id="BREAKTHROUGH_PAPER_E",
        tex_text=defective_pe_tex,
        spec_text=spec_path.read_text(encoding="utf-8"),
    )
    assert neg_e["all_passed"] is False
    for g_name in (
        "ARGOS-PEER-008",
        "ARGOS-PEER-009",
        "ARGOS-PEER-012",
        "ARGOS-PEER-013",
    ):
        assert neg_e["gates"][g_name] is False


def test_stochastic_thermodynamics_lean4_and_paper_d_pivot() -> None:
    """Verify the focused Non-Equilibrium Stochastic Thermodynamics Lean 4 module & Paper D pivot."""
    st_spec_path = REPO_ROOT / "formal" / "ANSE" / "StochasticThermodynamicsSpec.lean"
    st_proof_path = REPO_ROOT / "formal" / "ANSE" / "StochasticThermodynamics.lean"
    assert st_spec_path.exists()
    assert st_proof_path.exists()

    spec_text = st_spec_path.read_text(encoding="utf-8")
    proof_text = st_proof_path.read_text(encoding="utf-8")

    def strip_lean_comments(s: str) -> str:
        s = re.sub(r"/-.*?-/", "", s, flags=re.DOTALL)
        s = re.sub(r"--.*$", "", s, flags=re.MULTILINE)
        return s

    clean_spec = strip_lean_comments(spec_text)
    clean_proof = strip_lean_comments(proof_text)
    assert re.search(r"\bsorry\b", clean_spec) is None
    assert re.search(r"\bsorry\b", clean_proof) is None
    assert re.search(r"^\s*axiom\s+", clean_spec, flags=re.MULTILINE) is None
    assert re.search(r"^\s*axiom\s+", clean_proof, flags=re.MULTILINE) is None

    for sym in (
        "structure ConformationalNetwork",
        "def masterRHS",
        "def edgeFlux",
        "def systemEntropy",
        "def entropyProductionRate",
        "def klDivergence",
        "def chemicalWorkRate",
        "structure InhabitedATPConformationalCyclePackage",
        "def Stmt_ST_T1_MasterEquationMassConservationAndIMEXPositivity",
        "def Stmt_ST_T2_SchnakenbergEntropyDecompositionAndSecondLaw",
        "def Stmt_ST_T3_EspositoVanDenBroeckFreeEnergyBalance",
        "def Stmt_ST_T4_ThermodynamicUncertaintyRelationAndActivityBound",
    ):
        assert sym in clean_spec

    for thm in (
        "theorem ST_T1_master_equation_mass_conservation_and_imex_positivity",
        "theorem ST_T2_schnakenberg_entropy_decomposition_and_second_law",
        "theorem ST_T3_esposito_van_den_broeck_free_energy_balance",
        "theorem ST_T4_thermodynamic_uncertainty_relation_and_activity_bound",
    ):
        assert thm in clean_proof








