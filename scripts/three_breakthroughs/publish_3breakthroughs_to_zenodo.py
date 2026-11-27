"""
Zenodo Open-Science Publisher for the 3 Breakthrough Papers (Domains 3A, 3B, 3C)
================================================================================
Publishes each of the 3 5-round Opus peer-reviewed Breakthrough Papers and its
reproducibility bundle (compiled PDF, LaTeX source, Lean 4 formalization & spec,
certified telemetry JSON, and 5-round Opus peer-review report) to Zenodo using
`ZENODO_TOKEN`, mints 3 permanent DOIs, and writes
`results/three_breakthroughs/zenodo_3breakthroughs_receipts.json`.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / "results" / "three_breakthroughs"
PAPERS_DIR = REPO_ROOT / "papers" / "three_breakthroughs"


def load_zenodo_token() -> str:
    if os.environ.get("ZENODO_TOKEN"):
        return os.environ["ZENODO_TOKEN"].strip()
    candidates = [
        REPO_ROOT / ".env",
        Path.home() / ".env",
        Path.home() / ".zenodo_token",
        Path.home() / ".config" / "zenodo" / "token",
    ]
    for p in candidates:
        if p and p.exists():
            for raw in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = raw.strip().removeprefix("export ").strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, val = line.partition("=")
                    if key.strip() in ("ZENODO_TOKEN", "ZENODO_API_TOKEN"):
                        return val.strip().strip('"').strip("'")
                else:
                    return line.strip('"').strip("'")
    raise RuntimeError("No ZENODO_TOKEN found in environment or token files.")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def publish_single_paper_to_zenodo(
    token: str,
    title: str,
    description_html: str,
    keywords: list[str],
    files_to_upload: list[Path],
) -> dict[str, Any]:
    headers_json = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    headers_auth = {"Authorization": f"Bearer {token}"}

    # 1. Create draft deposition
    r_create = requests.post(
        "https://zenodo.org/api/deposit/depositions",
        headers=headers_json,
        json={},
        timeout=60,
    )
    r_create.raise_for_status()
    dep = r_create.json()
    dep_id = dep["id"]
    bucket_url = dep["links"]["bucket"]

    # 2. Upload files to bucket
    uploaded_files: list[dict[str, Any]] = []
    for fpath in files_to_upload:
        with fpath.open("rb") as fh:
            r_up = requests.put(
                f"{bucket_url}/{fpath.name}",
                data=fh,
                headers=headers_auth,
                timeout=120,
            )
            r_up.raise_for_status()
            uploaded_files.append(
                {
                    "filename": fpath.name,
                    "size_bytes": fpath.stat().st_size,
                    "sha256": sha256_file(fpath),
                }
            )

    # 3. Attach metadata
    metadata = {
        "metadata": {
            "title": title,
            "upload_type": "publication",
            "publication_type": "article",
            "creators": [
                {
                    "name": "Callens, Xavier",
                    "affiliation": "SocrateAI Scientific Research & Formal Verification Laboratory",
                }
            ],
            "description": description_html,
            "keywords": keywords,
            "access_right": "open",
            "license": "cc-by-4.0",
        }
    }
    r_meta = requests.put(
        f"https://zenodo.org/api/deposit/depositions/{dep_id}",
        headers=headers_json,
        data=json.dumps(metadata),
        timeout=60,
    )
    r_meta.raise_for_status()

    # 4. Publish deposition
    r_pub = requests.post(
        f"https://zenodo.org/api/deposit/depositions/{dep_id}/actions/publish",
        headers=headers_auth,
        timeout=60,
    )
    r_pub.raise_for_status()
    pub_data = r_pub.json()

    return {
        "deposition_id": dep_id,
        "doi": pub_data.get("doi"),
        "doi_url": pub_data.get("doi_url") or f"https://doi.org/{pub_data.get('doi')}",
        "record_url": pub_data.get("links", {}).get("record_html")
        or f"https://zenodo.org/records/{dep_id}",
        "state": pub_data.get("state"),
        "submitted": pub_data.get("submitted"),
        "title": title,
        "uploaded_files": uploaded_files,
    }


def main() -> None:
    token = load_zenodo_token()
    spec_lean = REPO_ROOT / "formal" / "ANSE" / "Breakthroughs3DomainsSpec.lean"
    proof_lean = REPO_ROOT / "formal" / "ANSE" / "Breakthroughs3Domains.lean"
    st_spec_lean = REPO_ROOT / "formal" / "ANSE" / "StochasticThermodynamicsSpec.lean"
    st_proof_lean = REPO_ROOT / "formal" / "ANSE" / "StochasticThermodynamics.lean"
    gar_spec_lean = REPO_ROOT / "formal" / "ANSE" / "GeneticAutoresearchSpec.lean"
    gar_proof_lean = REPO_ROOT / "formal" / "ANSE" / "GeneticAutoresearch.lean"
    missions_lean = REPO_ROOT / "formal" / "ANSE" / "MensuraElenchusThreeMissions.lean"
    tactics_lean = REPO_ROOT / "formal" / "ANSE" / "LeanMasterAutoTactics.lean"

    papers_config: list[dict[str, Any]] = [
        {
            "paper_code": "PAPER_A_DOMAIN_3A_STELLARATOR_FUSION",
            "title": (
                "Discretization-Free 3D Stellarator Guiding-Center Plasma Confinement, "
                "Dual-Number Relaxation Runge-Kutta Conservation in rusty-SUNDIALS, and "
                "Villani Grazing-Collision Landau Fisher Monotonicity Verified in Lean 4"
            ),
            "description": (
                "<p><strong>Clean Fusion Energy (5-Round Peer-Reviewed Edition):</strong> "
                "Machine-checked Lean 4 formalization (zero <code>sorryAx</code>, zero custom axioms) "
                "and discretization-free solver verification across <code>rusty-SUNDIALS</code>, "
                "<code>SocrateAI-Scientific-Agora-Physique-Cinetique</code>, and <code>LeanFlow MCP</code>. "
                "Certifies Littlejohn's non-canonical 3D stellarator guiding-center Hamiltonian "
                "H_GC(0.25, 0.15, 0.40) = 5601/10000 = 0.5601, exact 3D Lorentz magnetic zero-work "
                "&lt;v, v x B&gt; = 0, mirror trapping margin 399/10000 &gt; 0, Dual-Number RRK energy drift "
                "suppression from 6.9490e-9 (RK4) to 9.2149e-15 (gamma_bar = 1.0000000530), "
                "Villani Theorem 22.6 Landau Fisher dissipation D_I = 6 &gt; 0 with curvature dominance "
                "gamma_bar^2 = 149481/12500 &gt; 9 (c(3,0) &gt;= 4.354632, c(2,0) &gt; 3.363647), and "
                "complex-velocity [1/1] Pade zero-sound closure (u = 10/37, c_0/v_F = 1.851999, "
                "Volterra c_2 = -2/9, c_4 = -1/18).</p>"
            ),
            "keywords": [
                "Stellarator Fusion",
                "Guiding-Center Hamiltonian",
                "Relaxation Runge-Kutta",
                "Landau-Fokker-Planck Equation",
                "Fisher Information Monotonicity",
                "rusty-SUNDIALS",
                "LeanFlow MCP",
                "Lean 4",
            ],
            "files": [
                PAPERS_DIR
                / "paper_a"
                / "PaperA_Stellarator_Fusion_DualRRK_Villani_LeanFlow.pdf",
                PAPERS_DIR
                / "paper_a"
                / "PaperA_Stellarator_Fusion_DualRRK_Villani_LeanFlow.tex",
                RESULTS_DIR / "paper_a_telemetry.json",
                RESULTS_DIR
                / "breakthrough_3a_stellarator_fusion_opus_5round_peer_review.json",
                spec_lean,
                proof_lean,
                missions_lean,
                tactics_lean,
            ],
        },
        {
            "paper_code": "PAPER_B_DOMAIN_3B_NAVIER_STOKES_MENSURA_CAP",
            "title": (
                "Scale-Dual Subgrid Regularization of 3D Navier-Stokes, the Helmholtz "
                "Leray-alpha Isomorphism, Zero-Inertial-Distortion Optimality, and "
                "Continuum Galerkin Computer-Assisted Proofs in Lean 4"
            ),
            "description": (
                "<p><strong>Scale-Dual Subgrid Regularization of 3D Navier-Stokes &amp; Continuum "
                "Galerkin CAP in Lean 4 (5-Round Peer-Reviewed Edition):</strong> Establishes a "
                "machine-checked bridge between momentum-space scale-duality geometry and subgrid-scale "
                "(SGS) turbulence closures for the 3D incompressible Navier-Stokes equations within "
                "<code>LeanFlow MCP</code> (<code>leanflow_mcp</code>) in Lean 4 (zero <code>sorryAx</code>, "
                "zero custom axioms). Certifies: (1) Theorem 2.1 "
                "(<code>leanflow_cap_galerkin_radii_polynomial_contraction</code>): coupling the "
                "scale-dual gradient into the 3D Fourier-Galerkin Navier-Stokes operator attenuates "
                "the infinite-dimensional Stokes tail bound from Z_tail = 1/200 to "
                "Z_tail^dual = C_Sob / (nu * alpha' * M^4) = 1/800 at alpha' = 1/25, tightening "
                "continuum Banach contraction from kappa_tot = 93/250 = 0.372 to "
                "kappa_dual = 1473/4000 = 0.36825 &lt; 1 (P_dual(10^-3) = -2127/4000000 &lt; 0) and "
                "preserving Z_tail^dual = 1/200 even at fourfold lower viscosity nu_weak = 1/400; "
                "(2) Lemma 2.2 (<code>leanflow_piecewise_scale_involution_lemma</code>) &amp; Lemma 2.3 "
                "(<code>leanflow_smooth_vs_piecewise_characterization_lemma</code>): proves the exact "
                "isomorphism k_smooth(alpha', k) = 1 / R_smooth(alpha', 1/|k|) = |k| / (1 + alpha'|k|^2) "
                "with the inverse Helmholtz filter of the Foias-Holm-Titi Leray-alpha / LANS-alpha "
                "models, and proves that k_eff(alpha', k) = min(|k|, 1/(alpha'|k|)) is the unique "
                "scale-involutive SGS operator achieving zero inertial-range distortion; "
                "(3) Theorem 2.4 (<code>leanflow_sym2_hadamard_recurrence_and_rns_inner_product</code>): "
                "Sym^2(L_2) Hadamard triad recurrence for subgrid Reynolds-stress shell products "
                "w_n = u_n * v_n and 3-prime RNS-CRT verification of &lt;(10,20,30), (11,12,14)&gt; = 770; "
                "and (4) Theorem 2.5 (<code>leanflow_taylor_interval_and_spectral_bound</code>): global "
                "3D scale-dual enstrophy ceiling Omega_eff(t) &lt;= E_0 / alpha' on T^3 preventing "
                "finite-time vortex-stretching blow-up, Kolmogorov -2/3 slope error 1/125 = 0.8%, and "
                "viscous propagator enclosure exp(-1/2) in [2329/3840, 233/384].</p>"
            ),
            "keywords": [
                "3D Navier-Stokes Equations",
                "Subgrid-Scale Turbulence Closure",
                "Helmholtz Leray-alpha Filter",
                "Scale-Dual Geometry",
                "Computer-Assisted Proofs",
                "Radii Polynomial",
                "LeanFlow MCP",
                "Lean 4",
            ],
            "files": [
                PAPERS_DIR
                / "paper_b"
                / "PaperB_NavierStokes_Hurricane_Mensura_DualScale_CAP.pdf",
                PAPERS_DIR
                / "paper_b"
                / "PaperB_NavierStokes_Hurricane_Mensura_DualScale_CAP.tex",
                RESULTS_DIR / "paper_b_telemetry.json",
                RESULTS_DIR
                / "breakthrough_3b_navier_stokes_mensura_cap_opus_5round_peer_review.json",
                spec_lean,
                proof_lean,
                missions_lean,
                tactics_lean,
            ],
        },
        {
            "paper_code": "PAPER_C_DOMAIN_3C_FLT_PQC_QUANTUM",
            "title": (
                "Post-Quantum Cryptography from the FLT Modular Machinery: Hellegouarch Minimal "
                "Weierstrass Semistability, Dual-Isogeny Endomorphism Rings, Half-Integral Deuring "
                "Quaternion Orders, and Verified SQIsign in Rust and Lean 4"
            ),
            "description": (
                "<p><strong>Post-Quantum Cryptography from the FLT Modular Machinery "
                "(5-Round Peer-Reviewed Edition):</strong> Machine-checked Lean 4 formalization (zero "
                "<code>sorryAx</code>, zero custom axioms) and constant-time Rust verification "
                "(<code>sqisign_flt_verifier</code> in "
                "<code>sub_projects/socrateai_scientific_quantum_computing/sqisign_flt_verifier/src/lib.rs</code>). "
                "Certifies the constructively inhabited Hellegouarch witness (15, 16, 31) with minimal "
                "Weierstrass curve <code>y^2 + x y = x^3 - 15 x</code>, c_{4,min} = 721, "
                "Delta_unscaled = 55353600, Delta_min = 55353600 / 2^8 = 216225, exact Bezout coprimality "
                "694 * 55353600 - 53280719 * 721 = 1 and 298 * 216225 - 89369 * 721 = 1, canonical Ribet "
                "dyadic remainder (4p - 8) mod p = p - 8 (for p &gt;= 11), and non-coprime obstruction at "
                "(3, 6, 9) (3 | 63); operator-level FLT DualIsogenyAPI trace/norm characteristic identity "
                "Tr(a + b*phi)^2 - 4*N(a + b*phi) = b^2*(t^2 - 4n) &lt; 0; non-commutative Deuring "
                "quaternion reduced norm multiplicativity Nrd(alpha*beta) = Nrd(alpha)*Nrd(beta) and "
                "half-integral maximal order O_0 norm integrality in B_{4m+3,inf}; Gamma_0(15) Hecke "
                "correspondence out-degrees {3, 3, 5, 8}, strict Pizer Ramanujan spectral gap 4*ell &lt; (ell+1)^2, "
                "and 98304 non-backtracking walks; and SQIsign challenge-response soundness "
                "65536 * 6561 = 429981696 with gcd(2^16, 3^8) = 1.</p>"
            ),
            "keywords": [
                "Post-Quantum Cryptography",
                "SQIsign",
                "Supersingular Isogeny",
                "Deuring Correspondence",
                "Maximal Quaternion Order",
                "Fermat's Last Theorem",
                "Rust",
                "Lean 4",
            ],
            "files": [
                PAPERS_DIR
                / "paper_c"
                / "PaperC_FLT_Modular_PQC_SQIsign_Quantum_Rust_Lean4.pdf",
                PAPERS_DIR
                / "paper_c"
                / "PaperC_FLT_Modular_PQC_SQIsign_Quantum_Rust_Lean4.tex",
                RESULTS_DIR / "paper_c_telemetry.json",
                RESULTS_DIR
                / "breakthrough_3c_flt_pqc_quantum_opus_5round_peer_review.json",
                spec_lean,
                proof_lean,
                missions_lean,
                tactics_lean,
            ],
        },
        {
            "paper_code": "PAPER_D_DOMAIN_3D_BIOPHYSICS_GENETICS_ENERGY_MATERIALS",
            "title": (
                "Formalizing Non-Equilibrium Stochastic Thermodynamics, Jarzynski-Crooks "
                "Fluctuation Theorems, and ATP-Dependent Chromatin Remodeling Lattice "
                "Dynamics in Lean 4"
            ),
            "description": (
                "<p><strong>Non-Equilibrium Stochastic Thermodynamics &amp; ATP-Dependent Chromatin "
                "Remodeling Biophysics (5-Round Peer-Reviewed Edition):</strong> Complete, axiom-free "
                "Lean 4 formalization (<code>ANSE.StochasticThermodynamics</code>, 28 theorems, zero "
                "<code>sorryAx</code>, zero custom axioms) and <code>rusty-SUNDIALS</code> numerical "
                "verification (<code>ChromatinRemodelerLatticeEngine</code>) grounded in empirical "
                "single-molecule FRET (smFRET), optical-tweezers, and cryo-EM structures of human "
                "ISWI (<code>SNF2H</code>/<code>SMARCA5</code>, UniProt <code>O60264</code>, "
                "<code>PDB: 6NE3</code> at 3.90 &Aring;) and SWI/SNF (<code>BRG1</code>/<code>SMARCA4</code>, "
                "UniProt <code>P51532</code>, <code>PDB: 6LTJ</code> at 3.70 &Aring;) remodeling the "
                "147-bp Widom 601 nucleosome core particle (<code>NCP147</code>, <code>PDB: 1KX5</code> "
                "at 1.94 &Aring;). Certifies six main theorems: "
                "(1) Theorem 2.1 (<code>ST_T1_master_equation_mass_conservation_and_imex_positivity</code>): "
                "Pauli Master Equation antisymmetric flux identity (Wf)_i = sum_j J_{ij}(f), universal "
                "probability mass conservation d/dt sum_i f_i(t) = 0, unconditional Backward-Euler / "
                "L-stable IMEX positivity f_i^{(k+1)} &gt; 0 for all Delta_t &gt; 0 and all Delta_mu_ATP, "
                "and stiff explicit Forward-Euler CFL breakdown 1 - Delta_t * w_exit = -3/4 &lt; 0; "
                "(2) Theorem 2.2 (<code>ST_T2_schnakenberg_entropy_decomposition_and_second_law</code>): "
                "exact continuous-time Shannon entropy derivative via <code>HasDerivAt</code>, "
                "Schnakenberg network decomposition Sigma_dot(f) = dS_sys/dt + S_med_dot(f), and "
                "universal Second Law Sigma_dot(f) &gt;= 0; "
                "(3) Theorem 2.3 (<code>ST_T3_esposito_van_den_broeck_free_energy_balance</code>): "
                "continuous-time Kullback-Leibler divergence derivative and exact Esposito-Van den Broeck "
                "non-equilibrium free-energy work balance k_B T d/dt D_KL(f || f_eq) = W_ATP_dot(f) - "
                "k_B T Sigma_dot(f) under Local Detailed Balance (Delta_mu_ATP = 20 k_B T = 85.6 pN*nm); "
                "(4) Theorem 2.4 (<code>ST_T4_thermodynamic_uncertainty_relation_and_activity_bound</code>): "
                "universal logarithmic-hyperbolic inequality 2(x-y)^2/(x+y) &lt;= (x-y)ln(x/y) and "
                "finite-state Barato-Seifert-Gingrich Thermodynamic Uncertainty Relation (TUR) "
                "2 J_d(f)^2 &lt;= A_tot(f) Sigma_dot(f) (3-state cycle witness J_cycle = 5/3 s^-1, "
                "A_tot = 7 s^-1, 2 J_cycle^2 = 50/9, TUR prefactor 10/63, eta_TUR = 0.265768 &lt; 1); "
                "(5) Theorem 2.5 (<code>ST_T5_jarzynski_equality_crooks_fluctuation_and_schnakenberg_cycle</code>): "
                "Crooks Fluctuation Theorem ln(P_F(gamma)/P_R(gamma)) = beta(W(gamma) - Delta_F), "
                "Jarzynski Equality &lt;exp(-beta W)&gt; = exp(-beta Delta_F), Second-Law work dissipation "
                "Delta_F &lt;= &lt;W&gt; via <code>Real.add_one_le_exp</code>, and Schnakenberg cycle affinity "
                "recovering the empirical 20-bp outer-turn nucleosome unwrapping barrier "
                "Delta_F_unwrap = 6.5 k_B T = 27.82 pN*nm; and "
                "(6) Theorem 2.6 (<code>ST_T6_mcghee_von_hippel_tonks_girardeau_chromatin_lattice_and_rouse_polymer</code>): "
                "1D McGhee-von Hippel hard-rod steric exclusion g_MvH(147, rho) in (0,1) (53/54 in 200-bp "
                "euchromatin vs. 18/19 in 165-bp heterochromatin), crowding derivative "
                "d/d_rho g_MvH = -1/(1-146*rho)^2 &lt; 0, 1D Tonks-Girardeau hard-rod osmotic pressure "
                "surge 53/18 = 2.9444x, 3D Rouse chromatin polymer Langevin dissipation "
                "dU_Rouse/dt = -zeta_nuc^-1 sum_i G_i^2 &lt;= 0, and smFRET sliding observables "
                "(D_slide = 0.36 bp^2/s, k_cat = 2.4 bp/s).</p>"
            ),
            "keywords": [
                "Stochastic Thermodynamics",
                "ATP-Dependent Chromatin Remodeling",
                "Jarzynski Equality",
                "Crooks Fluctuation Theorem",
                "Schnakenberg Network Thermodynamics",
                "McGhee-von Hippel Lattice Gas",
                "Tonks-Girardeau Hard-Rod Gas",
                "Thermodynamic Uncertainty Relation",
                "ISWI SNF2H SWI/SNF",
                "Lean 4",
            ],
            "files": [
                PAPERS_DIR
                / "paper_d"
                / "PaperD_Biophysics_Genetics_EnergyMaterials_Autoresearch_Lean4.pdf",
                PAPERS_DIR
                / "paper_d"
                / "PaperD_Biophysics_Genetics_EnergyMaterials_Autoresearch_Lean4.tex",
                RESULTS_DIR / "paper_d_telemetry.json",
                RESULTS_DIR
                / "breakthrough_3d_biophysics_genetics_energy_materials_opus_5round_peer_review.json",
                st_spec_lean,
                st_proof_lean,
                spec_lean,
                proof_lean,
            ],
        },
        {
            "paper_code": "PAPER_E_DOMAIN_3E_GENETICS_DNA_REPLICATION_ART",
            "title": (
                "Non-Equilibrium Hopfield-Ninio Proofreading, Chimeric ART-Exo Fidelity, "
                "Gosset E8 Dicodon Quantization, and Topological DNA Supercoiling in "
                "LeanFlow, rusty-SUNDIALS, and Lean 4"
            ),
            "description": (
                "<p><strong>Genetics, DNA Replication, Chimeric ART-Exo Proofreading &amp; "
                "Humanitarian Genomic Medicine (5-Round Peer-Reviewed Edition):</strong> "
                "Machine-checked Lean 4 formalization (zero <code>sorryAx</code>, zero custom axioms across "
                "<code>ANSE.Breakthroughs3Domains</code>, <code>ANSE.GeneticAutoresearch</code>, and "
                "<code>ANSE.StochasticThermodynamics</code>) and native Rust numerical solvers "
                "(<code>sundials_core::genetics</code> in <code>rusty-SUNDIALS</code> and "
                "<code>LeanFlow MCP</code>). Certifies 8 theorems across <code>B3E_T1</code>&ndash;<code>B3E_T5</code> "
                "and <code>GAR_H1</code>&ndash;<code>GAR_H17</code>: "
                "(1) Theorem 2.1 (<code>B3E_T1</code> &amp; <code>ST_T1</code>): m-stage Hopfield-Ninio "
                "kinetic proofreading quadratic/cubic error attenuation E_2(1/100) = 1/10000 and "
                "E_3(1/100) = 1/1000000, continuous-time Pauli Master Equation Local Detailed Balance "
                "unconditional L-stable IMEX positivity f_i^{(k+1)} &gt; 0 (eliminating the explicit "
                "Forward-Euler CFL breakdown -3/4 &lt; 0 at Delta_t = 1/4 &gt; 1/7), and 200-nt ART repeat "
                "synthesis fidelity improvement from 2% to 0.02%; "
                "(2) Theorem 2.2 (<code>B3E_T2</code>): exact Calugareanu-White-Fuller topological "
                "conservation Lk = Tw + Wr, Bi-Helmholtz scale-dual plectoneme regularization with "
                "continuum Galerkin contraction kappa_bi = 5877/16000 = 0.3673125 &lt; 1 "
                "(P_bi(10^-3) = -8523/16000000 &lt; 0), Dual-RRK supercoiling energy conservation, and "
                "ARS(2,2,2) L-stable damping; "
                "(3) Theorem 2.3 (<code>B3E_T3</code>): Deuring quaternion inverted-repeat palindrome "
                "square norm N(alpha * bar(alpha)) = N(alpha)^2 = 40000, Hellegouarch minimal discriminant "
                "locus (c_4,min = 721, Delta_min = 216225, 298*216225 - 89369*721 = 1), and Cerednik-Drinfeld "
                "Hecke tree phylogenetic out-degrees {3, 3, 5, 8}; "
                "(4) Theorem 2.4 (<code>B3E_T4</code>): 1D KJMA genome replication completion "
                "S(1) = exp(-6) &lt;= 1/115 &lt; 1/100 via degree-4 Taylor lower bound T_4(6) = 115 and "
                "Sym^2(L_2) fourth-order bidirectional fork-coalescence recurrence lock; "
                "(5) Theorem 2.5 (<code>B3E_T5</code>): balanced dyadic Haar wavelet Repli-Seq TAD insulation "
                "(C* = 5/2 &gt; 2) and L-stable ARS(2,2,2) IMEX-RRK coupling; "
                "(6) Theorem 2.6 (<code>GAR_H1</code>, <code>GAR_H8</code>, <code>GAR_H9</code>): "
                "resolution of Conjectures C1 and C2 via degree-4 Kramers-Bell exponential torque barrier "
                "enclosure gamma_KB(1/100, 1, 1/5) = 6107/500000 (high-torque Bi-Helmholtz contraction "
                "kappa_bi^KB = 48071/128000 = 0.375555 &lt; 1) and Woodbury-Sherman-Morrison reticulate "
                "Hecke-Haar preconditioning bounded by 2*beta_1 + 1 = 13 &lt; 64; "
                "(7) Theorem 2.7 (<code>GAR_H10</code>, <code>GAR_H11</code>, <code>GAR_H12</code>): "
                "Chimeric ART-Exo fusion (IPR000477 + IPR006133) achieving 83.33x error suppression, "
                "8D Gosset E_8 dicodon lattice quantization across 36,000 empirical dicodons with second "
                "moment G(E_8) = 929/12960 &lt; 1/12 (saving 151/12960 per coordinate), and 222.61x Gen-3 "
                "ANSE energy reduction; and "
                "(8) Theorem 2.8 (<code>GAR_H13</code>&ndash;<code>GAR_H17</code>): clinical translation to "
                "POLE p.Pro286Arg (ClinVar VCV000216066) ultramutator TMB surge 12500/9 &gt; 100 mut/Mb "
                "(6944.44x amplification, FDA KEYTRUDA escape hazard 1/1251 &lt; 10^-3), scarless HBB rs334 "
                "Sickle Cell Prime Editing fidelity F_30^Exo = 1562419/1562500 &gt; 99.99%, mitochondrial "
                "POLG antiviral selectivity SI = 50,000, and 538.84x Gen-5 Socratic Elenchus ANSE "
                "bio-computational energy compression.</p>"
            ),
            "keywords": [
                "DNA Replication",
                "Kinetic Proofreading",
                "Array-Associated Reverse Transcriptase",
                "Chimeric ART-Exo",
                "Gosset E8 Lattice Quantizer",
                "POLE Ultramutator Immunotherapy",
                "Sickle Cell Prime Editing",
                "Topological DNA Supercoiling",
                "rusty-SUNDIALS",
                "Lean 4",
            ],
            "files": [
                PAPERS_DIR
                / "paper_e"
                / "PaperE_Genetics_DNAReplication_ART_LeanFlow_RustySundials_Lean4.pdf",
                PAPERS_DIR
                / "paper_e"
                / "PaperE_Genetics_DNAReplication_ART_LeanFlow_RustySundials_Lean4.tex",
                RESULTS_DIR / "paper_e_telemetry.json",
                RESULTS_DIR
                / "breakthrough_3e_genetics_dna_replication_art_opus_5round_peer_review.json",
                spec_lean,
                proof_lean,
                gar_spec_lean,
                gar_proof_lean,
                st_spec_lean,
                st_proof_lean,
                missions_lean,
                tactics_lean,
            ],
        },
    ]

    out_path = RESULTS_DIR / "zenodo_3breakthroughs_receipts.json"
    existing_by_code: dict[str, dict[str, Any]] = {}
    if out_path.exists():
        try:
            old_data = json.loads(out_path.read_text(encoding="utf-8"))
            for item in old_data.get("receipts", []):
                if item.get("paper_code") and item.get("doi"):
                    existing_by_code[item["paper_code"]] = item
        except Exception:
            existing_by_code = {}

    receipts: list[dict[str, Any]] = []
    for cfg in papers_config:
        for f in cfg["files"]:
            if not f.exists():
                raise FileNotFoundError(f"Missing required artifact for Zenodo upload: {f}")
        code = cfg["paper_code"]
        if code in existing_by_code:
            rec = existing_by_code[code]
            rec_files = {
                uf["filename"]: uf["sha256"] for uf in rec.get("uploaded_files", [])
            }
            disk_files = {f.name: sha256_file(f) for f in cfg["files"]}
            if rec_files == disk_files and rec.get("title") == cfg["title"]:
                receipts.append(rec)
                print(
                    f"Reusing 100%-SHA256-verified DOI for {code} -> DOI: {rec['doi']} ({rec['record_url']})"
                )
                continue
        rec = publish_single_paper_to_zenodo(
            token=token,
            title=cfg["title"],
            description_html=cfg["description"],
            keywords=cfg["keywords"],
            files_to_upload=cfg["files"],
        )
        rec["paper_code"] = code
        receipts.append(rec)
        print(f"Published {code} -> DOI: {rec['doi']} ({rec['record_url']})")

    out_path.write_text(
        json.dumps(
            {
                "trilogy": "FIVE_BREAKTHROUGHS_FRONTIER_PAPERS_3A_3B_3C_3D_3E",
                "published_count": len(receipts),
                "receipts": receipts,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print("ZENODO_3BREAKTHROUGHS_PUBLISHED_OK")


if __name__ == "__main__":
    main()
