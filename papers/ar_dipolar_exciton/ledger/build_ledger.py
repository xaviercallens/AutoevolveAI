"""Build the Elenchus claim ledger for the bilayer dipolar-exciton preprint (papers/ar_dipolar_exciton).

Modelled on results/discovery/ledger/build_ledger.py. Every claim gets a content-addressed evidence blob
(evidence/<sha256>.json): verbatim #print axioms lines plus source hashes (Tier A), verbatim primary-source excerpts
(Tier L, from sources/excerpts.json), the argument text (Tier C), result files with claim_licence false (Tier X).
Gate: python3 <elenchus>/tools/ledger.py ledger.json --evidence-dir evidence
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
H1 = W / "results/autoresearch/2026-10-25/H1"
C1 = H1 / "contribution"
DATA = PAPER / "data"
RUSTY = Path("/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h1/crates/qf-yukawa-crystal")
HF = Path("/home/callensxavier_gmail_com/hf-data/dipolar_exciton")
UP = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/openai_math_pinned/lean/OAI/Analysis/Triangular/Energy")
EXC = json.loads((HERE / "sources/excerpts.json").read_text())
TOOLCHAIN = "Lean 4.34.1, Mathlib d13f23b723b8a846827a245b89c10fc7d3f11612, openai/math fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb (pinned copy)"
RUSTY_SHA = "272a09e62c1b9b36eabc167cdafaa2845fbe9198"
AX = C1 / "compile_controls.json"   # stage-1 transcript that prints every claimed theorem plus both planted controls
PRIOR = W / "formal_cert/Autoresearch/DipolarExciton.lean"
MULTI = W / "formal_cert/Autoresearch/DipolarExcitonMultipolar.lean"
CTL = W / "formal_cert/Autoresearch/DipolarExcitonMultipolarControls.lean"
ANYD = W / "formal_cert/Triangular/AnyDensity.lean"
PRIOR_STATUS = ("prior round: independently re-compiled by a separate AI agent, verdict ACCEPT_WITH_CORRECTIONS "
                "(results/autoresearch/2026-10-25/H1/verification.md); no human audit")
MULTI_STATUS = ("stage 1 producer compile (contribution/FORMAL.md); re-elaborated from source by a separate AI auditor at stage 4 "
                "(papers/ar_dipolar_exciton/audit/recompile_multipolar_src.json: rc 0, axioms within the allowlist; planted sorry and "
                "planted axiom caught in audit/audit_controls.json; AUDIT.md); no human audit")
STEP1 = W / "formal_cert/Autoresearch/DipolarExcitonStep1.lean"
STEP1_CTL = W / "formal_cert/Autoresearch/DipolarExcitonStep1Controls.lean"
AX_STEP1 = C1 / "compile_step1_controls.json"
STEP1_STATUS = ("stage 5 (revision, audit correction C8): producer-checked only; the g_sqrt proof is the stage-4 auditor probe "
                "audit_g_sqrt moved unchanged; g_inplane and g_inplane_pos are new and not independently re-checked; no human audit")


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


def axiom_lines(names: list[str], ax: Path = AX) -> list[str]:
    out = json.loads(ax.read_text())["output"].replace("\n ", " ")
    lines = [l.strip() for l in out.split("\n") if any(f"'{n}'" in l for n in names)]
    if len(lines) != len(names):
        raise SystemExit(f"axiom lines missing for {names}: {lines}")
    return lines


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict) -> dict:
    return {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
            "depends_on": depends, "evidence": blob(ev), "audit": None}


def lean_ev(names: list[str], srcs: list[Path], status: str, ax: Path = AX) -> dict:
    return {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output": axiom_lines(names, ax),
            "allowlist": ["propext", "Classical.choice", "Quot.sound"], "compile_transcript": file_ref(ax),
            "sources": [file_ref(p) for p in srcs], "status": status,
            "statement_adequacy": "not audited by a human"}


def cite(keys: list[str], **kw: object) -> dict:
    return {"kind": "citation", "excerpts": {k: EXC[k] for k in keys}, "excerpt_file": file_ref(HERE / "sources/excerpts.json"), **kw}


def num(files: list[Path], **kw: object) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True,
            "instrument": f"rusty-SUNDIALS crates/qf-yukawa-crystal (dipolar.rs, dipolar_ewald.rs, CVODE BDF) at {RUSTY_SHA} on branch physics/ar-dipolar-exciton-2026-10-25 (not pushed), plus numpy/scipy scripts",
            "files": [file_ref(p) for p in files], **kw}


def main() -> int:
    for old in EV.glob("*.json"):  # rebuild the blob store from scratch so no stale blob survives
        old.unlink()
    P ="AutoresearchDipolar."
    M = "AutoresearchDipolarMultipolar."
    pri = [PRIOR]
    mul = [PRIOR, MULTI, ANYD]
    claims = [
        rec("DX-A-0001", "A", "lean_axioms",
            "Upstream OAI.AtomicTriangular.universal_energy_minimum (openai/math, AI-generated, not peer reviewed): for every g with AdmissiblePotential g and every C with LocallyFinite C and DensityOne C, latticeEnergy g <= energy g C and latticeEnergy g = energy g A (energies in [0, infinity], energy = liminf of disk averages over ordered pairs). Certifies the statement about upstream's definitions only.",
            [], dict(lean_ev(["OAI.AtomicTriangular.universal_energy_minimum"], [UP / "Universal.lean", UP / "Basic.lean"], "upstream theorem, AI-generated, not peer reviewed"),
                     statement_adequacy="AI-audited only (results/discovery/statement_fidelity.md); no human audit")),
        rec("DX-A-0002", "A", "lean_axioms",
            "TriangularDensity.triangular_optimal_any_density (D2, 2026-10-10, imported unchanged): for rho > 0 and admissible h, (sqrt rho)^-1 A is locally finite with DensityRho rho and its h-energy is <= that of every locally finite DensityRho-rho configuration.",
            ["DX-A-0001"], lean_ev(["TriangularDensity.triangular_optimal_any_density"], [ANYD], "D2 (2026-10-10), part of the work published as doi:10.5281/zenodo.23285631; AI-verified only, no human audit")),
        rec("DX-A-0003", "A", "lean_axioms",
            "AutoresearchDipolar.dipolar_admissible: for d > 0 (hypothesis unused), g d = fun t => 2 (t^(-1/2) - (t + d^2)^(-1/2)) is AdmissiblePotential (C^infinity on (0, infinity), nonnegative, (-1)^r g^(r) >= 0).",
            [], lean_ev([P + "dipolar_admissible"], pri, PRIOR_STATUS)),
        rec("DX-A-0004", "A", "lean_axioms",
            "AutoresearchDipolar.triangular_dipolar_optimal: for d > 0 and every locally finite density-one C, latticeEnergy (g d) <= energy (g d) C.",
            ["DX-A-0001", "DX-A-0003"], lean_ev([P + "triangular_dipolar_optimal"], pri, PRIOR_STATUS)),
        rec("DX-A-0005", "A", "lean_axioms",
            "AutoresearchDipolar.latticeEnergy_dipolar_lt_top: for every real d, latticeEnergy (g d) < top (via g d t <= d^2 t^(-3/2) and finiteness of the Riesz-3 lattice sum, TriangularRiesz.latticeEnergy_riesz_lt_top).",
            [], lean_ev([P + "latticeEnergy_dipolar_lt_top"], pri + [W / "formal_cert/Triangular/RieszFinite.lean"], PRIOR_STATUS)),
        rec("DX-A-0006", "A", "lean_axioms",
            "Negative control AutoresearchDipolar.h_not_admissible: for d > 0, h d t = t^(-1/2) - 2 (t + d^2)^(-1/2) is not AdmissiblePotential (h d (d^2) < 0).",
            [], lean_ev([P + "h_not_admissible"], pri, PRIOR_STATUS)),
        rec("DX-A-0007", "A", "lean_axioms",
            "shiftDiff_admissible, admissible_const_mul, g_eq_shiftDiff, dipolar_admissible_all: for s > 0 and c >= 0, shiftDiff s c t = t^(-s/2) - (t + c)^(-s/2) is admissible; nonnegative multiples of admissible functions are admissible; g d = 2 shiftDiff 1 (d^2); hence g d is admissible for every real d.",
            [], lean_ev([M + n for n in ["shiftDiff_admissible", "admissible_const_mul", "g_eq_shiftDiff", "dipolar_admissible_all"]], mul, MULTI_STATUS)),
        rec("DX-A-0008", "A", "lean_axioms",
            "Negative control for the family: shiftDiff_neg_of_neg and shiftDiff_not_admissible_of_neg: for s > 0 and c < 0, shiftDiff s c (-2c) < 0, so shiftDiff s c is not admissible (the sign of c is load-bearing).",
            [], lean_ev([M + "shiftDiff_neg_of_neg", M + "shiftDiff_not_admissible_of_neg"], mul, MULTI_STATUS)),
        rec("DX-A-0009", "A", "lean_axioms",
            "triangular_shiftDiff_optimal and triangular_shiftDiff_optimal_any_density: for s > 0, c >= 0 the triangular-lattice inequalities of DX-A-0001/DX-A-0002 hold for shiftDiff s c (at density one, and at every density rho > 0 for (sqrt rho)^-1 A). For s != 1 a mathematical generalisation only. No finiteness (non-vacuity) theorem is proved for this family; at c = 0 shiftDiff s 0 is identically 0, so the statement is then trivially 0 <= energy. Non-vacuity is proved for g d only (DX-A-0005, DX-A-0011).",
            ["DX-A-0001", "DX-A-0002", "DX-A-0007"], lean_ev([M + "triangular_shiftDiff_optimal", M + "triangular_shiftDiff_optimal_any_density"], mul, MULTI_STATUS)),
        rec("DX-A-0010", "A", "lean_axioms",
            "triangular_dipolar_optimal_any_density: for d > 0 and rho > 0, (sqrt rho)^-1 A is locally finite, has DensityRho rho, and energy (g d) ((sqrt rho)^-1 A) <= energy (g d) C for every locally finite DensityRho-rho configuration C.",
            ["DX-A-0002", "DX-A-0003"], lean_ev([M + "triangular_dipolar_optimal_any_density"], mul, MULTI_STATUS)),
        rec("DX-A-0011", "A", "lean_axioms",
            "Non-vacuity at every density: g_scaled_le (g d (t/rho) <= d^2 rho^(3/2) t^(-3/2)), latticeEnergy_dipolar_scaled_lt_top and energy_dipolar_any_density_lt_top: for d > 0, rho > 0, energy (g d) ((sqrt rho)^-1 A) < top, so DX-A-0010 is not top <= top.",
            ["DX-A-0002", "DX-A-0003", "DX-A-0005"], lean_ev([M + n for n in ["g_scaled_le", "latticeEnergy_dipolar_scaled_lt_top", "energy_dipolar_any_density_lt_top"]], mul, MULTI_STATUS)),
        rec("DX-A-0012", "A", "lean_axioms",
            "Planted controls (separate file DipolarExcitonMultipolarControls.lean, importing the built module) are caught by #print axioms: ctl_sorry depends on sorryAx and ctl_axiom on the planted axiom ctl_cheat; the file compiles with rc 0, so exit status is not the gate.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axiom_lines(["AutoresearchDipolarMultipolarControls.ctl_sorry", "AutoresearchDipolarMultipolarControls.ctl_axiom"]),
                 "raw_output": json.loads(AX.read_text())["output"], "rc": json.loads(AX.read_text())["rc"],
                 "allowlist": ["propext", "Classical.choice", "Quot.sound"], "expected": "both controls OUTSIDE the allowlist",
                 "sources": [file_ref(CTL), file_ref(AX)], "statement_adequacy": "control rows; not audited by a human"}),
        rec("DX-A-0013", "A", "lean_axioms",
            "AutoresearchDipolarStep1.g_sqrt, g_inplane, g_inplane_pos: for t > 0, g d t = 2 (1/sqrt t - 1/sqrt (t + d^2)); for r > 0, g d (r^2) = 2 (1/r - 1/sqrt (r^2 + d^2)); for d != 0 and r > 0, g d (r^2) > 0. Algebra of Step 1 only; the physical pair counting is DX-C-0001.",
            [], lean_ev(["AutoresearchDipolarStep1." + n for n in ["g_sqrt", "g_inplane", "g_inplane_pos"]], [PRIOR, STEP1, STEP1_CTL], STEP1_STATUS, AX_STEP1)),
        rec("DX-A-0014", "A", "lean_axioms",
            "Planted controls for the Step-1 module (separate file DipolarExcitonStep1Controls.lean): ctl1_sorry depends on sorryAx and ctl1_axiom on the planted axiom ctl1_cheat; ctl1_wrong_sign_false proves that the wrong-sign in-plane form is false at r = d = 1; the file compiles with rc 0.",
            ["DX-A-0013"], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axiom_lines(["AutoresearchDipolarStep1Controls.ctl1_sorry", "AutoresearchDipolarStep1Controls.ctl1_axiom", "AutoresearchDipolarStep1Controls.ctl1_wrong_sign_false"], AX_STEP1),
                 "raw_output": json.loads(AX_STEP1.read_text())["output"], "rc": json.loads(AX_STEP1.read_text())["rc"],
                 "allowlist": ["propext", "Classical.choice", "Quot.sound"], "expected": "ctl1_sorry and ctl1_axiom OUTSIDE the allowlist",
                 "sources": [file_ref(STEP1_CTL), file_ref(AX_STEP1)], "statement_adequacy": "control rows; not audited by a human"}),
        rec("DX-L-0001", "L", "citation",
            "Petrache-Serfaty (arXiv:1908.09714v3): the Cohn-Kumar conjecture (universal minimality of the triangular lattice in dimension 2 among density-1 configurations for completely monotone functions of squared distance) 'remains open in dimension 2'; the lower energy is the liminf of ball averages (1.1); Riesz potentials are Gaussian superpositions (1.2).",
            [], cite(["ps_conjecture", "ps_energy", "ps_riesz"])),
        rec("DX-L-0002", "L", "citation",
            "Wang et al. (arXiv:2001.03812v5), MoSe2/WSe2 heterobilayers (h-BN encapsulated, 4 K): free interlayer-exciton gas only in the narrow density range around 1e11 ~ 1e12 cm^-2; trap-to-gas transition at n ~ 1-5e11 cm^-2; Mott transition at n_Mott = 1.6-3e12 cm^-2; moire potential wells of depth 10s-100 meV.",
            [], cite(["wang_title", "wang_mott", "wang_hbn", "wang_trap_depth", "wang_trap_gas", "wang_window"])),
        rec("DX-L-0003", "L", "citation",
            "Choudhary et al. (JARVIS, arXiv:2007.01831v2; publication doi:10.1038/s41524-020-00440-1): JARVIS-DFT uses the vdW-DF-OptB88 functional (VASP) consistently, shown to give accurate lattice parameters for vdW-bonded materials.",
            [], cite(["jarvis_optb88"])),
        rec("DX-L-0004", "L", "citation",
            "HuggingFace colabfit/JARVIS_DFT_3D_12_12_2022 at revision f4de0085edcf92885870c67459363d2c7080c90b: card license 'unknown'; cites ColabFit doi:10.60732/e9e65ccd and publication doi:10.1038/s41524-020-00440-1; original data doi:10.6084/m9.figshare.6815699.",
            [], cite(["colabfit_readme"], readme=file_ref(HF / "colabfit__JARVIS_DFT_3D_12_12_2022/README.md"),
                     provenance=file_ref(HF / "provenance.json"))),
        rec("DX-C-0001", "C", "argument",
            "Physics model: two rigid vertical dipoles (electron above hole, layer separation d) at in-plane distance r interact by e-e + h-h = 2/r and two cross pairs -2/sqrt(r^2 + d^2), in units e^2/(4 pi eps); in t = r^2 this is g d. For r > 0, g d (r^2) = 2 (1/r - 1/sqrt(r^2 + d^2)). The algebraic identity is now kernel-checked (DX-A-0013); the pair counting (which charges, which distances, dropping the intra-exciton binding) is the physical reading and stays an argument.",
            ["DX-A-0013"], {"kind": "argument", "text_file": file_ref(H1 / "verification.md"), "paper_section": "Physics; Human demonstration Step 1"}),
        rec("DX-C-0002", "C", "argument",
            "Gloss of DX-A-0004/DX-A-0010: within the classical, zero-temperature, rigid-dipole, unscreened model of DX-C-0001, no locally finite configuration of the given density has lower (liminf) energy than the triangular lattice, conditional on upstream DX-A-0001 and on definition fidelity. It says nothing about uniqueness, quantum excitons, screening, moire potentials, separate e/h crystals or the e-h plasma.",
            ["DX-A-0004", "DX-A-0010", "DX-C-0001"], {"kind": "argument", "text": "Tier A attaches to the Lean statement; this is its physical gloss."}),
        rec("DX-C-0003", "C", "argument",
            "Novelty: complete monotonicity of t^(-1/2) - (t + c)^(-1/2) is elementary (Bernstein: it equals the integral of e^(-ut)(1 - e^(-uc)) u^(-1/2)/sqrt(pi) du); given upstream the optimality corollary is immediate. A literature search (alphaXiv, 2026-10-25; absence by search, not proof) found no explicit statement for the bilayer potential; the only new item is the explicit kernel-checked corollary.",
            ["DX-L-0001"], {"kind": "argument", "text_file": file_ref(H1 / "verification.md"), "note_file": file_ref(H1 / "NOTE.md")}),
        rec("DX-C-0004", "C", "argument",
            "Scaling identity g_d(t/rho) = sqrt(rho) g_{d sqrt(rho)}(t): density rho at separation d is density one at separation d sqrt(rho), with energies multiplied by sqrt(rho). Not kernel-checked (DX-A-0010 does not need it); used to define d_tilde = d sqrt(n) in the numerics.",
            [], {"kind": "argument", "text": "g_d(t/rho) = 2((t/rho)^(-1/2) - (t/rho + d^2)^(-1/2)) = 2 sqrt(rho)(t^(-1/2) - (t + rho d^2)^(-1/2))."}),
        rec("DX-C-0005", "C", "argument",
            "Proxy assumption: the electron-hole separation d of a MoSe2/WSe2 interlayer exciton is approximated by the adjacent metal-plane spacing of MoSe2 and WSe2 homo-stacks computed with OptB88vdW; real carrier centroids, stacking and heterostructure relaxation differ.",
            ["DX-L-0003"], {"kind": "argument", "text_file": file_ref(C1 / "NUMERICS.md"), "topic": "HF caveats 1-2: homo-stack metal-plane spacing used as dipole length"}),
        rec("DX-C-0006", "C", "argument",
            "Normalisation: the Rust per-particle energy e is (1/2) sum over nonzero lattice vectors of U = V/d^2 at density one, so latticeEnergy (g d) (ordered-pair convention, sum over all nonzero lattice points) equals 2 d^2 e_tri in the same length units.",
            ["DX-C-0001"], {"kind": "argument", "text_file": file_ref(C1 / "NUMERICS.md"), "topic": "per-particle energy e = (1/2) sum' U versus Lean latticeEnergy (sum over all nonzero lattice points)"}),
        rec("DX-C-0007", "C", "argument",
            "Regime: with d = 0.66 nm, n = 1e11 cm^-2 lies at the lower edge of the free-gas window and below or at the trap-to-gas transition (moire-trapped regime), n = 1e12 inside the window, n = 3e12 at or above n_Mott; the samples are h-BN encapsulated, so the eps_r = 1 energy scales are upper bounds (divide by the effective eps_r), and moire depths of 10s-100 meV dominate the sub-meV lattice gaps.",
            ["DX-L-0002", "DX-C-0005"], {"kind": "argument", "text": "Comparison of DX-L-0002 densities with the d_tilde grid."}),
        rec("DX-X-0001", "X", "numeric",
            "Exact (Ewald) energies: Rust Ewald vs independent Python Ewald (scipy quad, eta = 1.0) agree to <= 1.9e-13 relative (tri and square, five d); Python direct sums R = 100..400 plus exact tail agree to <= 1.9e-5 (oscillating lattice-minus-continuum residual); dropping the tail (negative control) gives 3.14e-2; Rust e_tri at eta 0.6/0.8/1.2 agree to <= 1.3e-13 relative (1.32e-13; an earlier note said 1.5e-13) and to <= 4.8e-13 over the 41-point grid d in [0.01, 3]; 288-particle box vs primitive cell <= 2.6e-14.",
            ["DX-C-0001"], num([DATA / "independent_check.json", DATA / "references.jsonl", DATA / "lattice_gaps.jsonl",
                                 RUSTY / "src/dipolar_ewald.rs", RUSTY / "src/dipolar.rs", RUSTY / "scripts/dipolar_independent_check.py"])),
        rec("DX-X-0002", "X", "numeric",
            "Lattice gaps (exact): e_sq/e_tri - 1 falls from 1.58e-2 (d_tilde = 0.01) to 1.36e-3 (d_tilde = 3) and e_hc/e_tri - 1 from 9.53e-2 to 8.75e-3 on the 41-point grid; both positive everywhere sampled. Two competitor lattices only.",
            ["DX-C-0001"], num([DATA / "lattice_gaps.jsonl", DATA / "references.jsonl"])),
        rec("DX-X-0003", "X", "numeric",
            "Controls at all five d (0.0209, 0.066, 0.114, 0.3, 1): perfect and noisy triangular lattices relax back (|rel gap| <= 2.6e-14, 0 defects, 0 negative Hessian modes); the square lattice is a saddle of the dynamics potential (64-72 negative modes) and square+noise relaxes to a distorted state with rel gap 1.73e-3..4.77e-3; incommensurate boxes (d = 0.066) stay defected (rel gaps 2.0e-3, 7.9e-4).",
            ["DX-X-0001"], num([DATA / "controls.jsonl", DATA / "summary.json", DATA / "run_table.md", DATA / "preregistration.json"])),
        rec("DX-X-0004", "X", "numeric",
            "Preregistered P1 (DIP-TRI-1): 0 of 21 relaxed competitors (12 T=0 quenches, 2 anneals, 2 incommensurate boxes, 5 square+noise; d = 0.0209, 0.066, 1 for the quenches) lies below the exact triangular energy by more than 1e-9 relative; most negative competitor rel gap -2.3e-14; smallest gap among states not at the lattice 1.54e-4; |gap_exact - gap_sf| <= 1.6e-5. 3/12 quenches (all from seed 501) and 1/2 anneals reach the lattice. Of the 21, only 14 (12 quenches + 2 anneals) are open searches; the 2 incommensurate boxes and 5 square+noise relaxations are designed negative controls. anneal_01 and uniform_04 (d = 0.066, different seeds) end in the same state (e_exact 4.43936745573261, psi6 0.998112), so independent outcomes are fewer than 21. Deviations from DIP-TRI-1: reduced run counts at d = 0.0209 and 1, none at 0.114 and 0.3; first attempts at d = 0.0209 and d = 1 were killed after about 34 min (budget) and their finished jobs were never printed (driver kept them in memory; fix 916fc88); reported energies are Ewald energies, not the preregistered image sum plus tail (reported_potential), because the truncated residual is non-monotone (DX-X-0005).",
            ["DX-X-0001", "DX-X-0003"], num([DATA / "main_d0.0209.jsonl", DATA / "main_d0.066.jsonl", DATA / "main_d1.jsonl", DATA / "summary.json", DATA / "preregistration.json",
                                              C1 / "NUMERICS.md"])),
        rec("DX-X-0005", "X", "numeric",
            "Truncation residual: at d = 0.066, |e_tri(R) - e_tri^Ewald| with exact uniform tail is 1.7e-3 (R = 8), 7.9e-5 (16), 6.6e-7 (32), 4.0e-5 (64), 7.6e-7 (128), 2.5e-7 (256), not monotone; reported gaps are therefore Ewald gaps.",
            ["DX-X-0001"], num([DATA / "references.jsonl", DATA / "fig_truncation_residual.pdf"])),
        rec("DX-X-0006", "X", "numeric",
            "HuggingFace illustration: from colabfit/JARVIS_DFT_3D_12_12_2022 (rev f4de0085edcf92885870c67459363d2c7080c90b, co/co_0.parquet) the adjacent metal-plane spacings of semiconducting TMD homo-stacks are MoSe2 6.5827 A (3 slabs, 6 spacings), WSe2 6.6151 A (1 slab), MoS2 6.2371 A (bulk-like cell); proxy d = 6.599 A gives d_tilde = 0.0209 / 0.0660 / 0.1143 at n = 1e11 / 1e12 / 3e12 cm^-2. 26 Hub queries found no heterobilayer or interlayer-separation dataset.",
            ["DX-L-0003", "DX-L-0004", "DX-C-0005", "DX-C-0004"], num([DATA / "physical_d.json", DATA / "hf_provenance.json", HF / "provenance.json",
                                                                      RUSTY / "results/dipolar/hf_search.json", RUSTY / "scripts/dipolar_physical_d.py", RUSTY / "scripts/dipolar_tmd_extract.py"])),
        rec("DX-X-0007", "X", "numeric",
            "Physical scale (unscreened, eps_r = 1): square-minus-triangular gap per exciton 0.0014 / 0.044 / 0.223 meV at n = 1e11 / 1e12 / 3e12 cm^-2 (physical d_tilde^2 times the gap evaluated at the simulated d_tilde 0.0209 / 0.066 / 0.114; the stage-4 auditor, evaluating at the physical d_tilde 0.1143, gets 0.224 meV at 3e12), about 1.5 to 5 orders of magnitude below moire depths of 10s-100 meV; divide by eps_r.",
            ["DX-X-0002", "DX-X-0006", "DX-C-0007"], num([DATA / "summary.json", DATA / "physical_d.json"])),
        rec("DX-X-0008", "X", "numeric",
            "Paper-stage reruns by the same agent pipeline (not independent human verification): cargo test -p qf-yukawa-crystal at the branch HEAD: 28 passed, 0 failed, 1 ignored; Lean source sha256 values match those recorded in FORMAL.md; Lean recompile of the controls file (imports the stage-1 oleans): rc 0 in 755.4 s, axiom output identical to stage 1; Lean recompile of the Multipolar source without writing oleans (imports the prior-round DipolarExciton olean): rc 0 in 660.7 s, axiom output identical to compile_attempt1.json. Same AI pipeline; not producer != verifier.",
            [], num([p for p in [C1 / "rerun_cargo_test_paper_stage.txt", C1 / "recompile_controls_paper_stage.json", C1 / "recompile_multipolar_paper_stage.json"] if p.exists()],
                    lean_sha256={p.name: sha(p.read_bytes()) for p in [PRIOR, MULTI, CTL, ANYD]})),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": claims}, indent=1, ensure_ascii=False))
    print(f"claims {len(claims)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
