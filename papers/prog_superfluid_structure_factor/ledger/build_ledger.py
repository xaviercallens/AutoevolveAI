"""Build the Elenchus claim ledger for the P6 preprint (papers/prog_superfluid_structure_factor).

Modelled on papers/ar_dipolar_exciton/ledger/build_ledger.py. Every claim gets a content-addressed evidence blob
(evidence/<sha256>.json): verbatim #print axioms lines plus source hashes (Tier A), verbatim source excerpts (Tier L, from
sources/excerpts.json), the argument text (Tier C), result files with claim_licence false (Tier X).
Closure rule of the gate: a claim may not be filed above the effective tier of anything it rests on, so the Tier C physical
glosses rest only on A and L rows; the data arithmetic is filed at Tier X.
Gate: python3 <elenchus>/tools/ledger.py ledger.json --evidence-dir evidence   (see run_gate.py)
Run:  /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I build_ledger.py
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
P6 = W / "results/programmes/2026-10-25/P6"
LEAN = W / "formal_cert/Programmes/FeynmanBijl"
EXC = json.loads((HERE / "sources/excerpts.json").read_text())
R = json.loads((P6 / "results.json").read_text())
HE, BEC = R["he4"], R["bec"]
TOOLCHAIN = "Lean 4.34.1, Mathlib d13f23b723b8a846827a245b89c10fc7d3f11612, openai/math fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb (pinned copy; no openai/math theorem is imported)"
CJ = {t: P6 / f"lean/compile_{t}.json" for t in ["basic", "negctl", "posctl", "controls"]}
AUDIT_MD = PAPER / "AUDIT.md"
AUDIT_OUT = Path("/home/callensxavier_gmail_com/programmes-2026-10-25/P6/audit/out")
STATUS = ("stage WORK2 producer compile (results/programmes/2026-10-25/P6/FEYNMAN_BIJL.md, lean/axiom_gate.json GATE PASS); "
          "re-elaborated once more at the paper stage by the same AI pipeline (papers/prog_superfluid_structure_factor/rerun/); "
          "then independently recompiled by a separate AI auditor with a private olean build (AUDIT.md): rc 0, sha256 equal, "
          "#print axioms identical (all within the whitelist), planted ctl_sorry/ctl_axiom and two auditor mutations caught; "
          "NO human audit (audit: null)")


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


def axiom_lines(names: list[str], tag: str) -> list[str]:
    out = json.loads(CJ[tag].read_text())["output"].replace("\n ", " ")
    lines = [l.strip() for l in out.split("\n") if any(f"'{n}'" in l for n in names)]
    if len(lines) != len(names):
        raise SystemExit(f"axiom lines missing for {names}: {lines}")
    return lines


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict) -> dict:
    return {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
            "depends_on": depends, "evidence": blob(ev), "audit": None}


def audit_ref() -> dict:
    refs = {"audit_report": file_ref(AUDIT_MD), "who": "separate AI agent (Claude), stage AUDIT; not a human"}
    for n in ("summary.json", "m1_mut.json", "m2_planted.json"):
        if (AUDIT_OUT / n).exists():
            refs[n] = file_ref(AUDIT_OUT / n)
    return refs


def lean_ev(names: list[str], src: str, tag: str) -> dict:
    return {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output": axiom_lines(["ProgFeynmanBijl." + n for n in names], tag),
            "allowlist": ["propext", "Classical.choice", "Quot.sound"], "compile_transcript": file_ref(CJ[tag]),
            "sources": [file_ref(LEAN / src)], "status": STATUS, "statement_adequacy": "not audited by a human",
            "independent_recompile": audit_ref()}


def cite(keys: list[str], **kw: object) -> dict:
    return {"kind": "citation", "excerpts": {k: EXC[k] for k in keys}, "excerpt_file": file_ref(HERE / "sources/excerpts.json"), **kw}


def num(files: list[Path], **kw: object) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True,
            "instrument": "numpy/scipy/matplotlib scripts of lane P6 (results/programmes/2026-10-25/P6/scripts); no rusty-SUNDIALS or LeanFlow code was used or changed",
            "files": [file_ref(p) for p in files], **kw}


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    vc = HE["verdict_counts"]
    rr = HE["roton_region_1p7_2p4"]
    on = HE["onset"]
    pn = {d["sigma"]: d["frac_trials_with_REFUTED"] for d in HE["controls"]["positive_with_noise"]}
    cf = BEC["convention_failures_of_trapped_model"]
    sk = [P6 / "data/bec_stamper_kurn_fig3a_tierX.csv"]
    claims = [
        rec("PH-A-0001", "A", "lean_axioms",
            "ProgFeynmanBijl.double_comm_expect (with inner_eig_H): for a symmetric H on a finite-dimensional complex inner product space, H psi = E0 psi (E0 real) and any operator rho with Mathlib adjoint rho^dagger: <psi, [rho^dagger,[H,rho]] psi> = A(rho) + A(rho^dagger), where A(X) = <X psi, H X psi> - E0 <X psi, X psi>. No further hypothesis.",
            [], lean_ev(["inner_eig_H", "double_comm_expect"], "Basic.lean", "basic")),
        rec("PH-A-0002", "A", "lean_axioms",
            "excess_eq_half, excess_re, rayleigh_normalised, trial_energy_eq: under the symmetry hypothesis A(rho^dagger) = A(rho) (hsym) and a real double-commutator value f, A(rho) = f/2, and for N > 0, rho psi != 0 the normalised trial state rho psi/||rho psi|| has re<phi,H phi> - E0 = f/(2 N S) with S = ||rho psi||^2/N.",
            ["PH-A-0001"], lean_ev(["excess_eq_half", "excess_re", "rayleigh_normalised", "trial_energy_eq"], "Basic.lean", "basic")),
        rec("PH-A-0003", "A", "lean_axioms",
            "trial_energy_le_of_ground: with psi a ground state (E0 ||x||^2 <= re<x,Hx> for all x) and no symmetry hypothesis, the trial state's excess energy is <= f/(N S) (weaker by a factor 2 than PH-A-0002).",
            ["PH-A-0001"], lean_ev(["trial_energy_le_of_ground"], "Basic.lean", "basic")),
        rec("PH-A-0004", "A", "lean_axioms",
            "exists_le_weighted_mean, rayleigh_expansion, sector_eigenvalue_le (Mathlib spectral theorem: eigenvectorBasis, eigenvalues, Parseval): for phi != 0 some eigenvector e_i of symmetric H with <e_i,phi> != 0 has eigenvalue <= re<phi,H phi>/||phi||^2.",
            [], lean_ev(["exists_le_weighted_mean", "rayleigh_expansion", "sector_eigenvalue_le"], "Basic.lean", "basic")),
        rec("PH-A-0005", "A", "lean_axioms",
            "feynman_bijl_bound and feynman_bijl_bound_ground: with the f-sum value <psi,[rho^dagger,[H,rho]] psi> = N hbar^2 k^2/m taken as a HYPOTHESIS, S = ||rho psi||^2/N > 0, and hsym (resp. a ground-state hypothesis instead of hsym), some eigenvector e_i of H with <e_i, rho psi> != 0 has lambda_i - E0 <= hbar^2 k^2/(2 m S) (resp. <= hbar^2 k^2/(m S)).",
            ["PH-A-0002", "PH-A-0003", "PH-A-0004"], lean_ev(["feynman_bijl_bound", "feynman_bijl_bound_ground"], "Basic.lean", "basic")),
        rec("PH-A-0006", "A", "lean_axioms",
            "feynman_bijl_gap: adding that psi is a ground state and that rho psi is orthogonal to every E0-eigenvector (hypothesis), the eigenvalue found satisfies 0 < lambda_i - E0 <= hbar^2 k^2/(2 m S), so it is a genuine excitation and not the E0 level.",
            ["PH-A-0005"], lean_ev(["feynman_bijl_gap"], "Basic.lean", "basic")),
        rec("PH-A-0007", "A", "lean_axioms",
            "Bogoliubov link, re-proved on the pinned stack: epsFree_units (eps0 = hbar^2 k^2/2m for hc = hbar c, ks = 2mc/hbar), feynman_sBog_eq and feynman_sBog_units (the Feynman energy eps0/S_B equals eps_B exactly; S_B = eps0/eps_B by definition), feynman_le_epsBog_iff (for S > 0, eps0/S <= eps_B iff S_B <= S).",
            [], lean_ev(["epsFree_units", "feynman_sBog_eq", "feynman_sBog_units", "feynman_le_epsBog_iff"], "Basic.lean", "basic")),
        rec("PH-A-0008", "A", "lean_axioms",
            "epsBog_pos, sBog_pos, sBog_sq, sBog_le_sqrt: S_B(k)^2 = k^2/(ks^2 + k^2) and S_B(k) <= sqrt(k/(2 ks)) for hc, k, ks > 0 (the H8 bound, re-proved on the pinned stack; the original H8 file was compiled on another stack, QuantumFluids, and independently recompiled by a verifier, results/autoresearch/2026-10-25/H8/verification.md).",
            [], lean_ev(["epsBog_pos", "sBog_pos", "sBog_sq", "sBog_le_sqrt"], "Basic.lean", "basic")),
        rec("PH-A-0009", "A", "lean_axioms",
            "Negative control symmetry_needed, symmetry_needed_fin2 (with ketBra_apply, ketBra_self_symm): H = |e1><e1|, psi = e0, rho = |e1><e0| on orthonormal e0, e1 give double commutator 1 and A(rho) = 1 != 1/2 (A(rho^dagger) = 0), so hsym cannot be dropped from the halving step excess_eq_half. The Lean statements prove only A(rho) != f/2 (with f = 1, A(rho) = 1); they do NOT prove that the conclusion of trial_energy_eq or feynman_bijl_bound fails in this example (that is a hand computation, PH-C-0007).",
            ["PH-A-0001"], lean_ev(["ketBra_apply", "ketBra_self_symm", "symmetry_needed", "symmetry_needed_fin2"], "NegativeControls.lean", "negctl")),
        rec("PH-A-0010", "A", "lean_axioms",
            "Positive control gap_witness, gap_witness_applies, orthonormal_pair_fin2: on a two-level instance (H = |e1><e1|, psi = e0, Hermitian rho = |e1><e0| + |e0><e1|, N = hbar = k = 1, m = 1/2) every hypothesis of feynman_bijl_gap holds, its conclusion is reached, and H(rho psi) = 1 * rho psi with 1 = hbar^2 k^2/(2 m S), so the bound is attained. The witness rho is Hermitian, so hsym holds trivially (rho^dagger = rho); no witness exercises a non-trivial hsym.",
            ["PH-A-0006"], lean_ev(["gap_witness", "gap_witness_applies", "orthonormal_pair_fin2"], "PositiveControls.lean", "posctl")),
        rec("PH-A-0011", "A", "lean_axioms",
            "Planted controls (separate file Controls.lean, never imported) are caught by #print axioms: ctl_sorry depends on sorryAx and ctl_axiom on the planted axiom ctl_cheat. Each claims the false strengthening A(rho) = f. The file compiles with rc 0, so exit status is not the gate.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axiom_lines(["ProgFeynmanBijl.ctl_sorry", "ProgFeynmanBijl.ctl_axiom"], "controls"),
                 "raw_output": json.loads(CJ["controls"].read_text())["output"], "rc": json.loads(CJ["controls"].read_text())["rc"],
                 "allowlist": ["propext", "Classical.choice", "Quot.sound"], "expected": "both controls OUTSIDE the allowlist",
                 "sources": [file_ref(LEAN / "Controls.lean"), file_ref(CJ["controls"])], "status": STATUS,
                 "statement_adequacy": "control rows; not audited by a human", "independent_recompile": audit_ref()}),
        rec("PH-L-0001", "L", "citation",
            "Stamper-Kurn et al. (arXiv:cond-mat/9906035v2): S(q) is the ratio of Bragg line strengths of the trapped to the expanded (free-particle, S = 1) cloud; Bogoliubov S(q) = omega0_q/omega_B_q (Eq. 3); the trapped line strength in the Thomas-Fermi local density approximation tends to 15 pi/32 (hbar omega0_q/2 mu)^(1/2) in the phonon regime; Fig. 3a plots S(q) against mu with a fixed q.",
            [], cite(["sk_ratio", "sk_fig3", "sk_bog_eq3", "sk_lda"])),
        rec("PH-L-0002", "L", "citation",
            "Steinhauer et al. (arXiv:cond-mat/0111438v1): the f-sum rule yields Feynman's relation S(k) = (hbar k^2/2m)/omega(k) (Eq. 2; their ref. [11] is Feynman, Phys. Rev. 94, 262 (1954), not read by us); the plotted closed circles of Fig. 4 are the measured S(k) multiplied by 2.3 'giving rough agreement' with LDA Bogoliubov theory; the open circles are computed from Eq. 2 and the measured omega(k).",
            [], cite(["st_feynman", "st_2p3"])),
        rec("PH-L-0003", "L", "citation",
            "Godfrin et al. (arXiv:2012.09067v1): c = 238.3 +- 0.1 m/s for 4He at saturated vapour pressure (ultrasound) and m4 = 4.0026032 g/mol.",
            [], cite(["godfrin_c", "godfrin_m"], fulltext=file_ref(HERE / "sources/godfrin_2012.09067_fulltext.txt"))),
        rec("PH-L-0004", "L", "citation",
            "Donnelly-Barenghi web edition, chapter 14: Table 14.1 'Adopted database used for structure factor of liquid 4He' with keys 1 (Robkoff-Hallock X-ray, 0.213 <= Q <= 5.129) and 2 (Svensson et al. neutron, 0.79 <= Q <= 6.66), S(0) = 0.051 adopted from theory, no uncertainties printed, no temperatures printed, and the note that the authors of the two sets 'are unable to explain the discrepancy ... in the region of the peak'. Secondary compilation; the page is assumed, not checked, to reproduce Table 14.1 of J. Phys. Chem. Ref. Data 27, 1217 (1998); the primary PRB tables were not seen.",
            [], cite(["donnelly_keys", "donnelly_discrepancy", "donnelly_rows"], page_text=file_ref(HERE / "sources/donnelly_barenghi_vapor15.txt"))),
        rec("PH-L-0005", "L", "citation",
            "Morresi-Garberoglio (arXiv:2501.08730v1) give the reference Svensson, Sears, Woods, Martel, Phys. Rev. B 21, 3638-3651 (1980) (the compilation prints the year 1989) and use it as the experimental pair distribution at T = 2 K; the temperature of the Svensson S(Q) points in the compilation is not verified.",
            [], cite(["mg_svensson", "mg_T2K"])),
        rec("PH-C-0001", "C", "argument",
            "f-sum rule: for N bosons with H = sum p_j^2/2m + V(r) and rho_k = sum_j exp(-i k.r_j), [rho_k^dagger,[H,rho_k]] = N hbar^2 k^2/m as an operator identity (only the kinetic term fails to commute with rho_k; [p^2, e^{-ik.r}] = -hbar (k.p e^{-ik.r} + e^{-ik.r} k.p), then [e^{ik.r}, k.p] = -hbar k^2 e^{ik.r}). It has no finite-dimensional representation, so PH-A-0005 takes its value as a hypothesis.",
            [], {"kind": "argument", "text_file": file_ref(P6 / "FEYNMAN_BIJL.md"), "paper_section": "Human demonstration, Step 6"}),
        rec("PH-C-0002", "C", "argument",
            "Physical reading of PH-A-0005/PH-A-0006: if the density operator, the f-sum value and the k <-> -k symmetry of the physical ground state are as in PH-C-0001, then the lowest excitation in the density channel at wavevector k obeys eps(k) <= hbar^2 k^2/(2 m S(k)) (Feynman, Bijl). Reading a measured S(k) this way needs the T = 0 ground-state S, the exact f-sum rule, the symmetry, and (for the gap form) momentum conservation, none of which is formalised. No novelty is claimed: this is the textbook Feynman-Bijl argument.",
            ["PH-A-0005", "PH-A-0006", "PH-C-0001", "PH-L-0002"], {"kind": "argument", "text": "Tier A attaches to the Lean statement about an abstract finite-dimensional H; this is its physical gloss."}),
        rec("PH-C-0003", "C", "argument",
            "Diffraction test: for every k > 0 the Bogoliubov structure factor with sound speed c satisfies S_B(k) <= sqrt(k/2k*), k* = 2mc/hbar (PH-A-0008). Hence a structure factor S(k) > sqrt(k/2k*) at some k cannot be S_B of a homogeneous Bogoliubov gas of that c; and since S > S_B gives eps0/S < eps_B (PH-A-0007), PH-C-0002 puts the lowest density-channel excitation of that system below eps_B(k). A point S <= sqrt(k/2k*) does not confirm Bogoliubov: the bound is an upper envelope. This is the same test as in doi:10.5281/zenodo.23646117; here it is applied to tabulated data.",
            ["PH-A-0007", "PH-A-0008", "PH-C-0002"], {"kind": "argument", "text": "Composition of PH-A-0007, PH-A-0008 with the physical reading PH-C-0002."}),
        rec("PH-C-0004", "C", "argument",
            "Physical gloss of the He-4 result (conditional): 4He is not a weakly interacting Bose gas (the textbook fact that k a << 1 fails), and the tabulated S(Q) of PH-L-0004 exceeding sqrt(Q/2k*) with k* = 2 m4 c/hbar from PH-L-0003 from the roton region outward is consistent with that. Hand check at the peak, from the L rows only: PH-L-0004 gives S = 1.458 at Q = 2.058 per A (X-ray; and 1.376 at Q = 2.070, neutron), PH-L-0003 gives k* = 3.00379 per A, so sqrt(Q/2k*) = sqrt(2.058/6.00758) = 0.5853 (resp. 0.5870), and 1.458 > 0.5853 + 0.082 (resp. 1.376 > 0.5870 + 0.082). It is conditional on (i) the data being secondary and at 1.4-4 K rather than T = 0, with the temperature dependence of the peak not quantified here, (ii) the post hoc 0.082 threshold, which is not in the preregistration, and (iii) the Tier C reading PH-C-0003. It does not refute Bogoliubov theory in its range of validity, and it does not use the Bijl-Feynman bound to bound anything about He-4.",
            ["PH-A-0008", "PH-C-0003", "PH-L-0003", "PH-L-0004", "PH-L-0005"], {"kind": "argument", "text": "Gloss of PH-X-0001; the arithmetic is Tier X and is therefore not a dependency (closure rule)."}),
        rec("PH-C-0005", "C", "argument",
            "Trapped-gas comparator: for a Thomas-Fermi cloud in the local density approximation S_LDA(q) = <S_B(q; n)> over atoms with weight w(x) = (15/4) x sqrt(1-x), x = n/n0, k*(x) = k*_peak sqrt(x). Applying PH-A-0008 pointwise gives S_LDA(q) <= B_LDA(q) = <sqrt(q/(2 k*(x)))>. A bound built from one k* (peak c, c_eff or mean-density c) is NOT implied; whether it fails is checked numerically (PH-X-0004). Homogeneous-gas Lean statements say nothing about the trap beyond this averaging argument.",
            ["PH-A-0008", "PH-L-0001"], {"kind": "argument", "text": "Average of the pointwise bound over the LDA weight; the weight is the Thomas-Fermi one quoted in PH-L-0001."}),
        rec("PH-C-0006", "C", "argument",
            "Scope: the Feynman-Bijl formalisation is a textbook argument (no novelty claimed); the data analysis tests a bound already published as a diffraction test in doi:10.5281/zenodo.23646117, now applied to 99 tabulated points, with controls and a trapped-gas comparator. No rusty-SUNDIALS or LeanFlow change was made in lane P6; the numerics are Python/numpy at Tier X.",
            [], {"kind": "argument", "text": "Scope statement; see the paper's Sections 1 and 6."}),
        rec("PH-C-0007", "C", "argument",
            "Hand computation for the counterexample of PH-A-0009 (not a Lean statement): with H = |e1><e1|, psi = e0, rho = |e1><e0| and N = hbar = k = 1, m = 1 (so that the f-sum value f = N hbar^2 k^2/m = 1 equals the double-commutator value of PH-A-0001/PH-A-0009), rho psi = e1, S = ||rho psi||^2/N = 1, the only eigenvector of H overlapping rho psi has eigenvalue 1 = lambda - E0, and the bound of feynman_bijl_bound without hsym would read lambda - E0 <= hbar^2 k^2/(2 m S) = 1/2; 1 > 1/2, so the final bound itself fails in this example when hsym is dropped. Kernel-checked is only the halving step (PH-A-0009).",
            ["PH-A-0009", "PH-A-0005"], {"kind": "argument", "text": "Two-level hand computation; the Lean file proves A(rho) = 1 != 1/2 = f/2 only."}),
        rec("PH-X-0001", "X", "numeric",
            f"He-4 test on Table 14.1 (Q > 0): {HE['n_points']} points ({HE['n_xray']} X-ray, {HE['n_neutron']} neutron), k* = {HE['kstar_inv_A']:.5f} per A. Verdicts: {vc['CONSISTENT']} CONSISTENT, {vc['UNDECIDED']} UNDECIDED, {vc['REFUTED']} REFUTED (REFUTED means S - sqrt(Q/2k*) > Delta_ds = {HE['peak']['delta_ds']:.3f}, the gap between the two datasets' peak maxima; Delta_ds is a post hoc proxy defined in the work stage, not in the preregistration). Onset in ({on['last_consistent_below']['Q']}, {on['first_nominal_exceed']['Q']}] per A; strict refuted run {HE['strict_refuted_runs_Q'][0][0]} to {HE['strict_refuted_runs_Q'][0][1]} per A; roton/peak region 1.7-2.4 per A: {rr['n']} points, all REFUTED, S/bound {rr['min_ratio']:.2f}-{rr['max_ratio']:.2f}. Sensitivity (revision_checks.json): Delta_ds in 0.07-0.10 moves REFUTED between 60 and 64, refuted above Q = 2.4 between 36 and 40, X-ray refuted between 30 and 32; the 29 CONSISTENT and the 21 roton refutations are unchanged (smallest roton margin 0.328, about 4.0 Delta_ds). Donnelly-Barenghi's recommended subset (X-ray Q < 1, neutron Q > 1; 60 points): 23 CONSISTENT, 6 UNDECIDED, 31 REFUTED; 10 neutron roton points all REFUTED (S/bound 1.62-2.38, min margin 0.328, refuted even at Delta_ds = 0).",
            ["PH-L-0003", "PH-L-0004", "PH-A-0008"], num([P6 / "data/test_he4.csv", P6 / "data/he4_Sk_donnelly_table14_1.csv", P6 / "results.json", P6 / "scripts/analysis.py", P6 / "DATA.md", PAPER / "revision_checks.py", PAPER / "revision_checks.json"])),
        rec("PH-X-0002", "X", "numeric",
            f"He-4 controls: homogeneous Bogoliubov S_B at the {HE['controls']['positive_bogoliubov_homog']['n']} abscissae gives {HE['controls']['positive_bogoliubov_homog']['violations_nominal']} violations (max S/bound {HE['controls']['positive_bogoliubov_homog']['max_S_over_bound']:.7f}); with Gaussian noise sigma 0.01/0.02/0.04 the fraction of 2000 trials with any REFUTED point is {pn[0.01]:g}/{pn[0.02]:g}/{pn[0.04]:.2f} (data scatter about the Donnelly spline: rms {HE['peak']['rms_resid_all']:.3f}); S = 1 exceeds the bound at {HE['controls']['negative_free_S_equals_1']['nominal_violations']} points (exactly those with Q < 2k*); planted 1.5 S_B is caught at {HE['controls']['planted_1p5_times_Bogoliubov']['nominal_violations']}; two independent parses of the HTML agree on all 300 + 266 numbers.",
            ["PH-X-0001"], num([P6 / "results.json", P6 / "raw/parsed.json", P6 / "scripts/parse_donnelly.py"])),
        rec("PH-X-0003", "X", "numeric",
            f"Feynman self-check of the data: S <= eps0/eps with Godfrin's eps(k) (conservative eps - err), {HE['feynman_check']['n']} points with 0.05 <= Q <= 3.6: {HE['feynman_check']['n_exceed']} exceed it, Q = {HE['feynman_check']['exceed_Q'][0]} and {HE['feynman_check']['exceed_Q'][1]}, both X-ray, consistent with (not proof of) thermal S at T >= 1.38 K. Reported, not dropped.",
            ["PH-X-0001", "PH-L-0003"], num([P6 / "data/test_he4.csv", P6 / "results.json"])),
        rec("PH-X-0004", "X", "numeric",
            f"Trapped-gas positive control on {cf['n_curve_points']} values of mu/h (0.5-12 kHz) at the Stamper-Kurn q: the trapped Bogoliubov model S_LDA exceeds a single-k* bound at {cf['bound_peak']}/{cf['n_curve_points']} (peak c), {cf['bound_c_eff']}/{cf['n_curve_points']} (c_eff) and {cf['bound_mean_density']}/{cf['n_curve_points']} (mean-density c) points and at {cf['bound_lda_average']}/{cf['n_curve_points']} for the LDA-averaged bound; grid control (6 mu x 7 q, Rb): {BEC['controls']['lda_bogoliubov_violations']} violations of S_LDA <= B_LDA of {BEC['controls']['grid_points']}, S = 1 exceeds B_LDA at {BEC['controls']['free_S1_exceeds_bound_count']}; the LDA model reproduces the solid curve of Fig. 3a at six columns to |diff| <= {max(abs(d['diff']) for d in BEC['solid_curve_control']):.4f}.",
            ["PH-C-0005", "PH-L-0001"], num([P6 / "results.json", P6 / "data/bec_model_curve_stamper_kurn_q.csv", P6 / "scripts/analysis.py"])),
        rec("PH-X-0005", "X", "numeric",
            "Stamper-Kurn Fig. 3a (Na, q = 2.506 per um, values read from the figure): S = 0.541, 0.379, 0.293 at mu/h = 3.08, 6.72, 9.30 kHz with sigma 0.129, 0.091, 0.071 against B_LDA = 0.583, 0.480, 0.442: z = -0.33, -1.10, -2.09; all three below the bound, the model sits at 0.82-0.95 of the bound. No refutation, low test power; 'BEC consistent' is not claimed.",
            ["PH-X-0004", "PH-L-0001"], num(sk + [P6 / "raw/sk_fig3a_digitized.json", P6 / "scripts/digitize_sk.py"])),
        rec("PH-X-0006", "X", "numeric",
            f"Steinhauer Fig. 4 (87Rb, mu/h = 1.91 kHz, values read from the figure): the closed circles are multiplied by 2.3 to fit the Bogoliubov-LDA curve, so a test on them is circular; {BEC['steinhauer_closed_summary']['n_exceeds_bound_nominal']} of {BEC['steinhauer_closed_summary']['n']} exceed B_LDA nominally (max z = {BEC['steinhauer_closed_summary']['max_z']:.2f}), none un-rescaled; the open circles are eps0/omega from the measured dispersion (rms difference to the LDA model {BEC['steinhauer_open_vs_lda']['rms_diff']:.3f}), not diffraction values. Not decisive in either direction.",
            ["PH-X-0004", "PH-L-0002"], num([P6 / "data/bec_steinhauer_fig4_tierX.csv", P6 / "raw/fig4_digitized.json", P6 / "scripts/digitize_steinhauer.py", P6 / "results.json"])),
        rec("PH-X-0007", "X", "numeric",
            "Float cross-check of the Lean statements (200 random 12x12 instances, seed 20261025): double-commutator identity max relative residual 1.7e-15; Hermitian rho: A = f/2 within 6.7e-16, trial-energy equality within 1.1e-16, sector bound 200/200; Bogoliubov eps0/S_B = eps_B within 1.8e-16 and the H8 bound at 2000/2000 grid points; negative controls: the 2x2 case gives A = 1, A^dagger = 0, f = 1; non-symmetric rho |A - f/2|/|f| has min 0.0019 and median 0.079; the planted claim A = f is caught 200/200. Supports no claim.",
            ["PH-A-0001"], num([P6 / "lean/feynman_bijl_numeric.json", P6 / "scripts/feynman_bijl_numeric.py"])),
        rec("PH-X-0008", "X", "numeric",
            "Paper-stage rerun by the same AI pipeline (not itself an independent check; the independent recompile is documented in AUDIT.md, see the independent_recompile field of the Tier A rows): the four Lean files recompiled with lean_pinned.py (Basic.lean re-elaborated from source without writing an olean; the other three import the stage-1 olean), all rc 0, identical #print axioms lines to the stage-1 transcripts; file sha256 values match those recorded in FEYNMAN_BIJL.md.",
            ["PH-A-0001"], num([p for p in [PAPER / "rerun/compile_basic.json", PAPER / "rerun/compile_negctl.json", PAPER / "rerun/compile_posctl.json", PAPER / "rerun/compile_controls.json", PAPER / "rerun/summary.json"] if p.exists()],
                              lean_sha256={p.name: sha(p.read_bytes()) for p in LEAN.glob("*.lean")})),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": claims}, indent=1, ensure_ascii=False))
    tiers = {t: sum(1 for c in claims if c["tier"] == t) for t in "ALCX"}
    (HERE / "tier_counts.json").write_text(json.dumps({"total": len(claims), **tiers}))
    print(f"claims {len(claims)} {tiers}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
