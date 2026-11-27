"""Build the Elenchus claim ledger for the Keldysh/TMD preprint (papers/ar_keldysh_tmd).

Modelled on results/discovery/ledger/build_ledger.py. Every claim gets a content-addressed evidence blob
(evidence/<sha256>.json): verbatim #print axioms lines plus source hashes (Tier A), verbatim primary-source excerpts
(Tier L, from sources/excerpts.json), the argument text (Tier C), result files with claim_licence false (Tier X).
Gate: python3 <elenchus>/tools/ledger.py ledger.json --evidence-dir evidence
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
W = PAPER.parents[1]
EV = HERE / "evidence"
H3 = W / "results/autoresearch/2026-10-25/H3"
C3 = H3 / "contribution"
DATA = PAPER / "data"
RUSTY = Path("/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h3/crates/qf-yukawa-crystal")
HF = Path("/home/callensxavier_gmail_com/hf-data/keldysh_tmd")
UP = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/openai_math_pinned/lean/OAI/Analysis/Triangular/Energy")
EXC = json.loads((HERE / "sources/excerpts.json").read_text())
TOOLCHAIN = "Lean 4.34.1, Mathlib d13f23b723b8a846827a245b89c10fc7d3f11612, openai/math fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb (pinned copy)"
RUSTY_SHA = "2e41505cc9df8c46d2b2d667c89ea53e977218ca"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def blob(obj: dict) -> str:
    raw = json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False).encode()
    d = sha(raw)
    EV.mkdir(parents=True, exist_ok=True)
    (EV / f"{d}.json").write_bytes(raw)
    return f"sha256:{d}"


def file_ref(p: Path) -> dict:
    return {"path": str(p), "sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}


def axiom_lines(compile_json: Path, names: list[str]) -> list[str]:
    out = json.loads(compile_json.read_text())["output"].replace("\n ", " ")
    return [l.strip() for l in out.split("\n") if any(f"'{n}'" in l for n in names)]


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict) -> dict:
    return {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
            "depends_on": depends, "evidence": blob(ev), "audit": None}


def lean_ev(names: list[str], extra: list[Path] | None = None) -> dict:
    full = [f"AutoresearchKeldysh.{n}" for n in names]
    lines = axiom_lines(C3 / "compile_keldysh.json", full)
    if len(lines) != len(full):
        raise SystemExit(f"axiom lines missing for {names}: {lines}")
    srcs = [W / "formal_cert/Autoresearch/KeldyshCM.lean", W / "formal_cert/Autoresearch/Yukawa.lean"] + (extra or [])
    return {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output": lines,
            "allowlist": ["propext", "Classical.choice", "Quot.sound"],
            "compile_transcript": file_ref(C3 / "compile_keldysh.json"), "sources": [file_ref(p) for p in srcs],
            "statement_adequacy": "not audited by a human; definition fidelity of keldysh is Tier C/X (KT-C-0001, KT-X-0002)"}


def cite(keys: list[str]) -> dict:
    return {"kind": "citation", "excerpts": {k: EXC[k] for k in keys}, "excerpt_file": file_ref(HERE / "sources/excerpts.json")}


def num(files: list[Path], **kw: object) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True,
            "instrument": f"rusty-SUNDIALS qf-yukawa-crystal keldysh.rs at {RUSTY_SHA} (not pushed) and mpmath",
            "files": [file_ref(p) for p in files], **kw}


def main() -> int:
    a = json.loads((DATA / "analysis.json").read_text())
    re = json.loads((C3 / "route_e_check.json").read_text())
    up_axioms = [l for l in axiom_lines(W / "results/discovery/D1/compile_Axioms.json",
                                        ["OAI.AtomicTriangular.universal_energy_minimum"])]
    h2_axioms = axiom_lines(W / "results/autoresearch/2026-10-25/H2/contribution/compile_yukawa.json",
                            ["AutoresearchYukawa.admissible_mul", "AutoresearchYukawa.admissible_congr"])
    claims = [
        rec("KT-A-0001", "A", "lean_axioms",
            "Upstream OAI.AtomicTriangular.universal_energy_minimum (openai/math, AI-generated, not peer reviewed): for every g with AdmissiblePotential g and every C with LocallyFinite C and DensityOne C, latticeEnergy g <= energy g C (energies in [0, infinity]). Kernel footprint within the allowlist; certifies the statement about upstream's definitions only.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output": up_axioms,
                 "allowlist": ["propext", "Classical.choice", "Quot.sound"],
                 "compile_transcript": file_ref(W / "results/discovery/D1/compile_Axioms.json"),
                 "sources": [file_ref(UP / "Universal.lean"), file_ref(UP / "Basic.lean")],
                 "statement_adequacy": "AI-audited only (results/discovery/statement_fidelity.md)"}),
        rec("KT-A-0002", "A", "lean_axioms",
            "AutoresearchYukawa.admissible_mul and admissible_congr (H2 lane, imported): the product of two AdmissiblePotential functions is admissible; admissibility depends only on values on (0, infinity).",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output": h2_axioms,
                 "allowlist": ["propext", "Classical.choice", "Quot.sound"],
                 "compile_transcript": file_ref(W / "results/autoresearch/2026-10-25/H2/contribution/compile_yukawa.json"),
                 "sources": [file_ref(W / "formal_cert/Autoresearch/Yukawa.lean")],
                 "statement_adequacy": "not audited by a human"}),
        rec("KT-A-0003", "A", "lean_axioms",
            "AutoresearchKeldysh.laplace_admissible and laplace_iteratedDeriv: for any measure mu and measurable k, m with k >= 0, m >= 0 a.e. and every moment k^n e^{-ck} m integrable (c > 0), t -> integral of exp(-t k) m dmu is AdmissiblePotential, and its n-th iterated derivative at t > 0 equals the integral of (-k)^n exp(-t k) m.",
            [], lean_ev(["laplace_admissible", "laplace_iteratedDeriv"])),
        rec("KT-A-0004", "A", "lean_axioms",
            "Controls of the generic lemma: expNeg_admissible (exp(-eps t) is admissible for eps >= 0, Dirac instance) and signedMix_not_admissible (exp(-t) - 2 exp(-2t) is not admissible: it is negative at t = log(3/2), so m >= 0 is load-bearing).",
            ["KT-A-0003"], lean_ev(["expNeg_admissible", "signedMix_not_admissible"])),
        rec("KT-A-0005", "A", "lean_axioms",
            "erfcx_le_one (erfcx x <= 1 for x >= 0), erfcx_le_inv (erfcx x <= 1/(sqrt(pi) x) for x > 0), keldysh_integrable (for r0 > 0, every moment (1/(4a))^n e^{-c/(4a)} w(a)/(2a) is integrable on (0, infinity)), where erfcx is DEFINED in Lean by (2/sqrt pi) * integral over y > 0 of exp(-(y^2 + 2xy)).",
            [], lean_ev(["erfcx_le_one", "erfcx_le_inv", "keldysh_integrable"])),
        rec("KT-A-0006", "A", "lean_axioms",
            "keldysh_admissible and keldysh_pos: for r0 > 0 the mixture-defined keldysh r0 (t = r^2, keldysh r0 t = integral over a > 0 of w(a)/(2a) exp(-t/(4a)), w(a) = (1/r0) erfcx(sqrt a / r0)) is AdmissiblePotential and strictly positive for t > 0 (non-vacuity).",
            ["KT-A-0003", "KT-A-0005"], lean_ev(["keldysh_admissible", "keldysh_pos"])),
        rec("KT-A-0007", "A", "lean_axioms",
            "triangular_keldysh_optimal: for r0 > 0 and every locally finite density-one C, latticeEnergy (keldysh r0) <= energy (keldysh r0) C in [0, infinity]. Expected to read top <= top (KT-C-0002); finiteness is not proved.",
            ["KT-A-0001", "KT-A-0006"], lean_ev(["triangular_keldysh_optimal"], [UP / "Universal.lean"])),
        rec("KT-A-0008", "A", "lean_axioms",
            "keldyshReg_admissible and triangular_keldyshReg_optimal: for r0 > 0, eps >= 0, keldysh r0 t * exp(-eps t) is admissible and its triangular lattice energy is <= energy of every locally finite density-one C, in [0, infinity]. Finiteness of the lattice energy for eps > 0 is NOT proved (KT-C-0003).",
            ["KT-A-0001", "KT-A-0002", "KT-A-0004", "KT-A-0006"],
            lean_ev(["keldyshReg_admissible", "triangular_keldyshReg_optimal"], [UP / "Universal.lean"])),
        rec("KT-A-0009", "A", "lean_axioms",
            "Planted controls (separate file KeldyshCMControls.lean, importing the built module) are caught by #print axioms: ctl_sorry depends on sorryAx and ctl_axiom depends on the planted axiom ctl_cheat; both compile with rc 0, so exit status is not the gate.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axiom_lines(C3 / "compile_controls.json", ["AutoresearchKeldyshControls.ctl_sorry", "AutoresearchKeldyshControls.ctl_axiom"]),
                 "raw_output": json.loads((C3 / "compile_controls.json").read_text())["output"],
                 "allowlist": ["propext", "Classical.choice", "Quot.sound"], "expected": "both controls OUTSIDE the allowlist",
                 "sources": [file_ref(W / "formal_cert/Autoresearch/KeldyshCMControls.lean"), file_ref(C3 / "compile_controls.json")],
                 "statement_adequacy": "control rows; not audited by a human"}),
        rec("KT-L-0001", "L", "citation",
            "Berkelbach-Hybertsen-Reichman (arXiv:1305.4972v1) Eq. (3): V2D(rho) = pi e^2/((eps1+eps2) rho0) [H0(rho/rho0) - Y0(rho/rho0)] (form derived by Keldysh, their ref. [26] JETP Lett. 29, 658 (1979)); in vacuum rho0 = 2 pi chi2D (Cudazzo et al., their ref. [27] PRB 84, 085406 (2011)).",
            [], cite(["berkelbach_eq3", "berkelbach_r0", "berkelbach_refs"])),
        rec("KT-L-0002", "L", "citation",
            "Berkelbach et al. Table I (DFT+RPA) chi2D: MoS2 6.60, MoSe2 8.23, WS2 6.03, WSe2 7.18 Angstrom; text: MoS2 GW chi2D = 5.0 Angstrom, rho0 approx 30-40 Angstrom. Table II experimental lattice constants a: 3.16, 3.30, 3.16, 3.29 Angstrom.",
            [], cite(["berkelbach_table1", "berkelbach_gw", "berkelbach_table2"])),
        rec("KT-L-0003", "L", "citation",
            "Sandier-Serfaty (arXiv:1011.4617v2) Lemma 3.3: W(Lambda) = -(1/2) log(sqrt(2 pi b) |eta(tau)|^2); Remark 1.5: W approx -0.2011 (triangular), -0.1958 (square); Theorem 2: the triangular lattice uniquely minimises W among lattices.",
            [], cite(["sandier_serfaty_lemma33", "sandier_serfaty_remark15", "sandier_serfaty_thm2"])),
        rec("KT-L-0004", "L", "citation",
            "DLMF 11.5.2 with nu = 0 and 11.2.5: H0(z) - Y0(z) = (2/pi) integral_0^infinity e^{-zt} (1+t^2)^{-1/2} dt for Re z > 0.",
            [], cite(["dlmf_11_5_2", "dlmf_11_2_5"])),
        rec("KT-L-0005", "L", "citation",
            "HuggingFace colabfit/JARVIS_C2DB at revision 432aeba9e505b59d0b3605c6346ac3816c754c02 is licensed CC-BY-4.0 and cites Haastrup et al. (doi:10.1088/2053-1583/aacfc1) and ColabFit doi:10.60732/37c26dae, per its README.",
            [], dict(cite(["c2db_readme"]), readme=file_ref(HF / "colabfit_JARVIS_C2DB/README.md"))),
        rec("KT-C-0001", "C", "argument",
            "Identification (Theorem 2, Step 7 of the paper): for r0 > 0, r > 0, (pi/(2 r0)) [H0 - Y0](r/r0) = integral over a > 0 of w(a)/(2a) exp(-r^2/(4a)) da with w(a) = (1/r0) e^{a/r0^2} erfc(sqrt a / r0). Main route (stage-5 revision, suggested by the stage-4 audit): DLMF 11.5.2 (nu = 0) gives V(r) = (1/r0) int_0^inf e^{-r u/r0} (1+u^2)^{-1/2} du; insert the subordination formula e^{-rho sqrt t} = int_0^inf e^{-t a} rho/(2 sqrt pi) a^{-3/2} e^{-rho^2/(4a)} da (standard, uncited) and swap integrals by Tonelli (all integrands positive); the inner integral int_0^inf u (1+u^2)^{-1/2} e^{-lam u^2} du = (1/2) sqrt(pi/lam) erfcx(sqrt lam) is elementary (v = sqrt(1+u^2)); a = 1/(4b) turns the weight erfcx(1/(2 r0 sqrt a))/(2 r0 a) da into w(b)/(2b) db. Second route: Hankel representation of 2 pi/(k(1+r0 k)) (improper/distributional inversion, table integral uncited), erfc Laplace pair and Weber integral (standard, uncited), Fubini justified by integrating in a first. Human proof, not machine-checked.",
            ["KT-L-0004"], {"kind": "argument", "text_file": file_ref(H3 / "NOTE.md"), "audit_file": file_ref(PAPER / "AUDIT.md"), "paper_section": "Human demonstration, Step 7",
                            "text": "Main route, all integrands nonnegative (Tonelli). (a) DLMF 11.5.2, nu = 0: K0(z) = (2/pi) int_0^inf e^{-zu} (1+u^2)^{-1/2} du, so V(r) = (1/r0) int_0^inf e^{-r u/r0} (1+u^2)^{-1/2} du. (b) Subordination (Levy density, standard, uncited): e^{-rho sqrt t} = int_0^inf e^{-ta} rho/(2 sqrt pi) a^{-3/2} e^{-rho^2/(4a)} da; with rho = u/r0, t = r^2 and Tonelli, V(r) = int_0^inf e^{-ta} a^{-3/2}/(2 sqrt pi r0^2) [int_0^inf u (1+u^2)^{-1/2} e^{-lam u^2} du] da, lam = 1/(4 r0^2 a). (c) With v = sqrt(1+u^2): the inner integral is e^lam int_1^inf e^{-lam v^2} dv = (1/2) sqrt(pi/lam) erfcx(sqrt lam); since sqrt(pi/lam) = 2 r0 sqrt(pi a), V(r) = int_0^inf e^{-ta} rho(a) da with rho(a) = erfcx(1/(2 r0 sqrt a))/(2 r0 a). (d) a = 1/(4b), da = db/(4b^2): rho(a) da = (4b erfcx(sqrt b/r0)/(2 r0)) db/(4b^2) = w(b)/(2b) db, so V(r) = int_0^inf w(b)/(2b) e^{-r^2/(4b)} db = keldysh r0 (r^2)."}),
        rec("KT-C-0002", "C", "argument",
            "latticeEnergy (keldysh r0) is expected to be infinite (V(r) ~ 1/r at large r and the 2D lattice sum of 1/r diverges), so triangular_keldysh_optimal is expected to read top <= top. Not proved or disproved in Lean.",
            ["KT-L-0001"], {"kind": "argument", "text": "sum over |x| <= R of 1/|x| grows like R for a planar lattice; V(r) r -> 1 (NOTE.md asymptotics)."}),
        rec("KT-C-0003", "C", "argument",
            "For eps > 0, latticeEnergy (keldyshReg r0 eps) < top is expected (Gaussian decay, logarithmic but integrable singularity is irrelevant since lattice points are at distance >= 1). Not attempted in Lean; needed before triangular_keldyshReg_optimal is non-trivial in Lean.",
            [], {"kind": "argument", "text": "V(r) e^{-eps r^2} <= C e^{-eps r^2} for r >= minimum lattice distance; Gaussian lattice sums converge."}),
        rec("KT-C-0004", "C", "argument",
            "Units: with eps1 = eps2 = 1 and e^2/(4 pi eps0) = 1, Berkelbach Eq. (3) becomes V(r) = (pi/(2 r0)) [H0 - Y0](r/r0), the potential used here; Fourier transform 2 pi/(k(1+r0 k)).",
            ["KT-L-0001"], {"kind": "argument", "text": "Gaussian-units e^2 replaced by e^2/(4 pi eps0); eps1 + eps2 = 2."}),
        rec("KT-C-0005", "C", "argument",
            "Large-r0 map: as r0 -> infinity, 2 pi/(k(1+r0 k)) ~ (1/r0) 2 pi/k^2, the 2D log kernel; at density one, after rescaling Sandier-Serfaty's cell of area 2 pi to area 1 (which shifts W by a lattice-independent constant), r0 (E_sq - E_tri) -> W_sq - W_tri = (1/2)[q(e^{i pi/3}) - q(i)], q(tau) = log(sqrt(Im tau) |eta(tau)|^2).",
            ["KT-L-0003"], {"kind": "argument", "paper_section": "Numerics, large-r0 control"}),
        rec("KT-C-0006", "C", "argument",
            "Jellium shift: for the neutralised Keldysh energy, E_K - E_C = + pi rho r0 + O(r0^2) for every Bravais lattice, because lim_{k->0} [2 pi/k - 2 pi/(k(1+r0 k))] = 2 pi r0; the lattice-independent term dominates E_K/E_C, and the structure-sensitive quantity is E_sq - E_tri.",
            ["KT-C-0004"], {"kind": "argument", "text_file": file_ref(C3 / "NUMERICS.md")}),
        rec("KT-X-0001", "X", "numeric",
            "Fidelity of the Lean erfcx definition: mpmath (dps 30) integral form vs e^{x^2} erfc x at x in {0, 0.01, 0.3, 1, 2.5, 7, 50}: max rel. err 1.34e-31; perturbed integrand exp(-(y^2 + x y)) differs by >= 5.6e-3 at x > 0 (negative control).",
            ["KT-A-0005"], num([C3 / "fidelity_erfcx.json", C3 / "fidelity_erfcx.py"])),
        rec("KT-X-0002", "X", "numeric",
            f"V(r) cross-check on {a['rust_vs_mpmath_V_max_rel_err']['n_points']} points (r0 in {{0.05, 0.3, 1, 4}}, r in [0.1, 12]): Rust DLMF 11.5.2 quadrature vs mpmath (pi/(2 r0))[H0 - Y0]: max rel. err {a['rust_vs_mpmath_V_max_rel_err']['dlmf']:.1e}; Rust Gaussian mixture (Lean definition) vs mpmath: {a['rust_vs_mpmath_V_max_rel_err']['mixture']:.1e}; kernel identity Vhat_sr + Vhat_lr = 2 pi/(k(1+r0 k)): {a['kernel_identity_max_rel_err']:.1e}. Prior-round mpmath check of the mixture vs closed form (50 radii): 2.1e-21.",
            ["KT-C-0001", "KT-L-0004"], num([DATA / "analysis.json", DATA / "mpmath_refs.json", DATA / "scan.json", H3 / "result_numerics.json"])),
        rec("KT-X-0003", "X", "numeric",
            f"Coulomb-limit positive controls: r0 = 0 lattice Ewald vs jellium.rs N = 288 box differs by {a['coulomb_positive_control']['lattice_tri_minus_jellium_rs_box']:.1e}; vs ten-digit Bonsall-Maradudin/Alves et al. Madelung values: {abs(a['coulomb_positive_control']['lattice_tri_minus_literature']):.1e} (tri), {abs(a['coulomb_positive_control']['lattice_sq_minus_literature']):.1e} (sq); at r0 = 1e-9, E_K - E_C = {a['coulomb_positive_control']['r0_1e-9_dE_tri']:.2e}; (E_K - E_C)/(pi r0) = {a['coulomb_positive_control']['slope_over_pi_at_r0']['1e-08']:.8f} at r0 = 1e-8.",
            ["KT-C-0006"], num([DATA / "analysis.json", DATA / "scan.json", RUSTY / "src/jellium.rs"],
                              literature_note="Madelung constants as hard-coded in jellium.rs and filed as UO-L-0007 in results/discovery/ledger (doi:10.1103/PhysRevB.103.245125, doi:10.1103/PhysRevB.15.1959)")),
        rec("KT-X-0004", "X", "numeric",
            f"Ewald-parameter independence (alpha in {{0.8, 1.6, 3.2}}, r0 in {{0 ... 1e4}}, tri and sq): max rel. spread {a['alpha_independence_max_rel_spread']:.1e}. Negative controls caught: wrong-sign reciprocal half gives spread >= {a['neg_wrong_sign_recip_min_rel_spread']:.1e}; dropped background gives >= {a['neg_no_background_min_rel_spread']:.3f}. Density scaling E(4, 0.7) = 2 E(1, 1.4) to {a['scaling_n4']['rel_diff']:.1e}.",
            [], num([DATA / "analysis.json", DATA / "scan.json"])),
        rec("KT-X-0005", "X", "numeric",
            f"Large-r0 control: r0 (E_sq - E_tri) approaches the Dedekind-eta value {a['log_gas_limit']['eta_formula_W_sq_minus_W_tri']:.10f} with relative deviation {a['log_gas_limit']['r0_times_gap'][0][2]:.1e} at r0 = 1e2 down to {a['log_gas_limit']['r0_times_gap'][-1][2]:.1e} at r0 = 1e6 (no fitted constant).",
            ["KT-C-0005", "KT-L-0003"], num([DATA / "analysis.json", DATA / "large_r0.json"])),
        rec("KT-X-0006", "X", "numeric",
            f"E_sq - E_tri > 0 at all {len(json.loads((DATA / 'scan.json').read_text())['scan'])} sampled r0 sqrt(n) in [1e-3, 1e2] (minimum {a['min_gap_over_scan']:.2e} at r0 = 100; Coulomb value 1.0383e-2). Two lattices only; not a proof and not a comparison with general configurations.",
            ["KT-C-0006"], num([DATA / "scan.json", DATA / "analysis.json"])),
        rec("KT-X-0007", "X", "numeric",
            "Material illustration in vacuum (eps1 = eps2 = 1), r0 = 2 pi chi2D: at n = 1e12 cm^-2, E_tri = -172.97 (MoS2), -159.17 (MoSe2), -178.52 (WS2), -167.74 (WSe2) meV per electron vs -282.31 meV for Coulomb; E_sq - E_tri = 0.961, 0.857, 1.002, 0.922 meV. Static classical Madelung energies only; density grid illustrative.",
            ["KT-L-0002", "KT-C-0004", "KT-C-0006"], num([DATA / "materials_out.json", DATA / "analysis.json"])),
        rec("KT-X-0008", "X", "numeric",
            "HuggingFace illustration: colabfit/JARVIS_C2DB (revision 432aeba9e505b59d0b3605c6346ac3816c754c02) has energy and band gap only, no alpha_2D (22 Hub queries found no dataset with alpha_2D). Its 2H rows c2db_atoms_3238/3150/3223/3118 have PBE lattice constants 3.184/3.320/3.186/3.319 Angstrom vs experimental 3.16/3.30/3.16/3.29 (Berkelbach Table II). Used for phase identification and lattice-constant cross-check only.",
            ["KT-L-0002", "KT-L-0005"], num([DATA / "hf_tmd_rows.json", HF / "search.json", HF / "search2.txt", HF / "tmd_rows.json"])),
        rec("KT-X-0009", "X", "numeric",
            "Paper-stage reruns by a separate agent instance (not independent human verification): cargo test of qf-yukawa-crystal at the rusty commit gives 28 passed, 0 failed, 1 ignored; keldysh_jellium scan output is bit-identical to the Stage-2 scan.json; the Lean recompile of KeldyshCM.lean (no olean written) exits rc 0 in 848.1 s with #print axioms output identical to the producer's compile_keldysh.json. Yukawa.lean sha256 unchanged (a16397de...) and older than H2's compile_yukawa.json.",
            [], num([p for p in [C3 / "rerun_cargo.json", C3 / "rerun_scan.json", C3 / "rerun_cargo.py", C3 / "recompile_paper_stage.json"] if p.exists()])),
        rec("KT-X-0010", "X", "numeric",
            f"Route (e) of Theorem 2 checked with mpmath (dps 30): Struve form vs the DLMF 11.5.2 Laplace form, the subordinated weight form and the Gaussian mixture at four (r0, r) points, the inner erfcx integral at four lambda and the subordination formula at two points: max rel. err {re['positive_max_rel_err']:.1e}. Negative controls caught: inner integrand e^(-lam u) in place of e^(-lam u^2) misses the closed form by >= {re['negative_min_rel_err_inner_perturbed']:.2f}; subordination with a^(-1/2) in place of a^(-3/2) misses e^(-rho sqrt t) by >= {re['negative_min_rel_err_subordination_power']:.2f} (relative).",
            ["KT-C-0001", "KT-L-0004"], num([C3 / "route_e_check.json", C3 / "route_e_check.py"])),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": claims}, indent=1, ensure_ascii=False))
    print(f"claims {len(claims)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
