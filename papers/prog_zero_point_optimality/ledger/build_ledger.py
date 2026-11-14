"""Build the Elenchus claim ledger for the zero-point-energy preprint (papers/prog_zero_point_optimality).

Modelled on papers/ar_dipolar_exciton/ledger/build_ledger.py. Every claim gets a content-addressed evidence blob
(evidence/<sha256>.json): verbatim #print axioms lines plus source hashes (Tier A), verbatim quotations with the
Elenchus citation-gate verdict (Tier L), the argument text (Tier C), result files with claim_licence false (Tier X).
Tier discipline (tools/ledger.py, LEDGER_TIER_INVERSION): a claim may not be filed above the tier of anything in its
depends_on, so everything that rests on a floating-point result is filed at X, and Tier C rows rest only on A, L or C rows.
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
DATA = PAPER / "data"
RES = W / "results/programmes/2026-10-25/P2"
LEANDIR = W / "formal_cert/Programmes/ZeroPoint"
BASIC = LEANDIR / "Basic.lean"
CTL = LEANDIR / "Controls.lean"
TOOLCHAIN = "Lean 4.34.1, pinned openai/math fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb toolchain and Mathlib d13f23b723b8a846827a245b89c10fc7d3f11612 (Basic.lean imports Mathlib only)"
RUSTY_WT = "/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-p2"
RUSTY_SHA = "6ad3cf7e5e171479d1481e5fd17e7d432aae21d1"
STATUS = ("producer-checked by the P2 lane (results/programmes/2026-10-25/P2/g2/lean_basic.json) and re-run once at paper stage by the "
          "same AI pipeline (data/rerun_basic.json, identical axiom output); recompiled by a separate AI auditor with its own planted controls "
          "(data/audit/audit_basic_orig.json, AUDIT.md, ZP-X-0013); no human audit")
LB = json.loads((DATA / "lean_basic.json").read_text())
LC = json.loads((DATA / "lean_controls.json").read_text())


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


def axiom_lines(names: list[str], j: dict) -> list[str]:
    out = j["output"].replace(str(W) + "/", "")
    lines = [l.strip() for l in out.split("\n") if any(f"'ProgZeroPoint.{n}'" in l for n in names)]
    if len(lines) != len(names):
        raise SystemExit(f"axiom lines missing for {names}: {lines}")
    return lines


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict) -> dict:
    return {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
            "depends_on": depends, "evidence": blob(ev), "audit": None}


def lean_ev(names: list[str]) -> dict:
    return {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output": axiom_lines(names, LB),
            "allowlist": ["propext", "Classical.choice", "Quot.sound"], "compile_transcript": file_ref(DATA / "lean_basic.json"),
            "paper_stage_rerun": file_ref(DATA / "rerun_basic.json"), "sources": [file_ref(BASIC)], "status": STATUS,
            "statement_adequacy": "not audited by a human"}


def cite(claim_file: str, check_key: str) -> dict:
    claim = json.loads((DATA / claim_file).read_text())
    chk = json.loads((DATA / "citation_check.json").read_text())[check_key]
    return {"kind": "citation", "claim": claim, "citation_gate": {"rc": chk["rc"], "stdout": chk["stdout"]},
            "note": "quotation copied programmatically from pdftotext output of the arXiv PDF; the gate certifies fidelity of the quote, "
                    "statement_match is the lane agent's judgement; tier ceiling L",
            "claim_file": file_ref(DATA / claim_file)}


def arg(text: str, **kw: object) -> dict:
    return {"kind": "argument", "text": text, "source_note": file_ref(RES / "PROOF.md"), **kw}


def num(files: list[Path], **kw: object) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True,
            "instrument": f"rusty-SUNDIALS crates/qf-yukawa-crystal (phonon.rs, phonon_spectral.rs) at {RUSTY_SHA} on branch "
                          "physics/p2-zero-point-optimality-2026-10-25 (not pushed), plus numpy/scipy/sympy scripts",
            "files": [file_ref(p) for p in files], **kw}


def main() -> int:
    for old in EV.glob("*.json"):  # rebuild the blob store from scratch so no stale blob survives
        old.unlink()
    d = DATA
    claims = [
        # ------------------------------------------------------------------ Tier A
        rec("ZP-A-0001", "A", "lean_axioms",
            "ProgZeroPoint.hasDerivAt_Q_x, hasDerivAt_Q_y, hasDerivAt_Qx_x, hasDerivAt_Qy_y: for Q m n x y = ((m + n x)^2 + n^2 y^2)/y "
            "the four partial derivatives as HasDerivAt facts (y != 0 where needed).",
            [], lean_ev(["hasDerivAt_Q_x", "hasDerivAt_Q_y", "hasDerivAt_Qx_x", "hasDerivAt_Qy_y"])),
        rec("ZP-A-0002", "A", "lean_axioms",
            "ProgZeroPoint.lap_Q and grad_Q: for y != 0, y^2 (Q_xx + Q_yy) = 2 Q and y^2 (Q_x^2 + Q_y^2) = Q^2 (with the partials written out explicitly).",
            [], lean_ev(["lap_Q", "grad_Q"])),
        rec("ZP-A-0003", "A", "lean_axioms",
            "ProgZeroPoint.lap_comp: for reals f1, f2 and y != 0, y^2 [f2 (Q_x^2 + Q_y^2) + f1 (Q_xx + Q_yy)] = Q^2 f2 + 2 Q f1 (pure algebra; "
            "that the left side is the hyperbolic Laplacian of f(Q) when f1 = f'(Q), f2 = f''(Q) is the chain rule and is NOT formalised).",
            ["ZP-A-0002"], lean_ev(["lap_comp"])),
        rec("ZP-A-0004", "A", "lean_axioms",
            "ProgZeroPoint.gauss_f', gauss_h, m2_f', m2_h: HasDerivAt facts giving, for f(u) = exp(-pi a u), h(u) = (u^2 f')' = (-2 pi a u + pi^2 a^2 u^2) exp(-pi a u), "
            "and for the second-moment density m2f(u) = (-4 pi a + 4 pi^2 a^2 u) exp(-pi a u), h(u) = (16 pi^2 a^2 u - 20 pi^3 a^3 u^2 + 4 pi^4 a^4 u^3) exp(-pi a u).",
            [], lean_ev(["gauss_f'", "gauss_h", "m2_f'", "m2_h"])),
        rec("ZP-A-0005", "A", "lean_axioms",
            "ProgZeroPoint.sqrt3_half_sq, rho_sq, gamma_fixes_rho, rho_sq_mul_rot, hasDerivAt_gamma: for rho = 1/2 + i sqrt3/2: rho^2 = rho - 1, "
            "gamma(tau) = (tau - 1)/tau fixes rho, rho^2 (-1/2 - i sqrt3/2) = 1, and gamma has complex derivative 1/rho^2 at rho (the rotation by -120 degrees).",
            [], lean_ev(["sqrt3_half_sq", "rho_sq", "gamma_fixes_rho", "rho_sq_mul_rot", "hasDerivAt_gamma"])),
        rec("ZP-A-0006", "A", "lean_axioms",
            "ProgZeroPoint.rot120_comm_symm and rot120_fixed_vec: a symmetric 2x2 real matrix commuting with the rotation by 120 degrees is scalar "
            "(q = 0, r = p), and a vector fixed by that rotation is zero.",
            [], lean_ev(["rot120_comm_symm", "rot120_fixed_vec"])),
        rec("ZP-A-0007", "A", "lean_axioms",
            "ProgZeroPoint.deriv_at_one_of_inversion: if f(1/alpha) = alpha f(alpha) for all alpha > 0 and f has derivative d at 1, then d = -f(1)/2.",
            [], lean_ev(["deriv_at_one_of_inversion"])),
        rec("ZP-A-0008", "A", "lean_axioms",
            "Planted controls (separate file Controls.lean importing the built module) are caught by #print axioms: ctl_sorry depends on sorryAx and "
            "ctl_axiom on the planted axiom ctl_cheat; the file compiles with rc 0, so the exit code is not the gate. lap_wrong_false proves the planted "
            "false identity is false (axioms within the allowlist).",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axiom_lines(["ctl_sorry", "ctl_axiom", "lap_wrong_false"], LC),
                 "raw_output": LC["output"].replace(str(W) + "/", ""), "rc": LC["rc"],
                 "allowlist": ["propext", "Classical.choice", "Quot.sound"], "expected": "ctl_sorry and ctl_axiom OUTSIDE the allowlist",
                 "sources": [file_ref(CTL), file_ref(DATA / "lean_controls.json")], "paper_stage_rerun": file_ref(DATA / "rerun_controls.json"),
                 "statement_adequacy": "control rows; not audited by a human"}),
        # ------------------------------------------------------------------ Tier L
        rec("ZP-L-0001", "L", "citation",
            "Luo-Wei (arXiv:2302.05042v1), p. 3, Corollary 1.1: for any alpha >= 1, min over unit-density lattices L of sum_{P in L} |P|^2 exp(-pi alpha |P|^2) "
            "is achieved at the hexagonal lattice.",
            [], cite("claim_luowei_cor_1_1.json", "luowei_cor_1_1")),
        rec("ZP-L-0002", "L", "citation",
            "Luo-Wei (arXiv:2302.05042v1), p. 12, Lemma 3.5: W_{1/(2 pi)}(1; z) = 0 for z in the upper half plane, i.e. S(1; L) = theta(1; L)/(2 pi) "
            "(as read by the lane agent; statement_match is a judgement).",
            [], cite("claim_luowei_lemma_3_5.json", "luowei_lemma_3_5")),
        rec("ZP-L-0003", "L", "citation",
            "Montgomery (Glasgow Math. J. 30 (1988) 75-85) as restated in Deng-Luo (arXiv:2411.17199v1), p. 3, Theorem A: for all alpha > 0, "
            "theta(alpha; z) is minimised over the upper half plane (up to rotations and translations) at e^{i pi/3}. Secondary source; the original was not opened.",
            [], cite("claim_montgomery_via_dengluo.json", "montgomery_via_dengluo")),
        # ------------------------------------------------------------------ Tier C (rest only on A, L, C)
        rec("ZP-C-0001", "C", "argument",
            "Model: a planar Bravais lattice L of covolume 1 with pair potential V(r) = g(r^2), hbar = m = 1, harmonic approximation. D(k) = sum_{R != 0} "
            "(1 - cos k.R) Hess V(R) (2x2), omega_j(k) = sqrt(lambda_j(D(k))), E_zp(L) = (1/2) <sum_j omega_j>_BZ. Conjecture QU-1: for every completely "
            "monotone g the triangular lattice minimises E_zp over unit-covolume planar Bravais lattices. A counterexample needs a lattice that is dynamically "
            "stable and has lower E_zp.",
            [], arg("Definition of the functional and of the conjecture (docs/proposals/NEXT_STEPS_PROPOSAL_2026-10-25.md; preregistration P2).")),
        rec("ZP-C-0002", "C", "argument",
            "Symmetry at the triangular point: E_zp depends on the lattice only up to rotation, hence E_zp(gamma tau) = E_zp(tau) for gamma in SL2(Z); "
            "gamma(tau) = (tau - 1)/tau fixes rho (ZP-A-0005) with derivative the -120 degree rotation J. For a C^2 invariant function the chain rule gives "
            "J^T grad E = grad E and J^T H J = H, so grad E(rho) = 0 and H is scalar (ZP-A-0006): E(tau) - E(rho) = (Lap E/4)|tau - rho|^2/y^2 + O(|tau - rho|^3) "
            "with Lap = y^2 (d_xx + d_yy). The invariance, the C^2 smoothness and the chain-rule step are not formalised.",
            ["ZP-A-0005", "ZP-A-0006", "ZP-C-0001"], arg("PROOF.md section 3.1.")),
        rec("ZP-C-0003", "C", "argument",
            "Curvature of a pair energy: for F(tau) = sum_{R != 0} f(|R|^2), Lap F = sum_{R != 0} h(|R|^2) with h(u) = (u^2 f'(u))' = u^2 f''(u) + 2 u f'(u). "
            "The algebra is ZP-A-0001..0003; the chain rule and termwise differentiation of an absolutely convergent sum are not formalised.",
            ["ZP-A-0001", "ZP-A-0002", "ZP-A-0003", "ZP-A-0004"], arg("PROOF.md section 3.2.")),
        rec("ZP-C-0004", "C", "argument",
            "Poisson form of the Gaussian dynamical matrix: for V = exp(-pi a r^2), kappa = k/(2 pi), L* the dual lattice, D(k) = (4 pi^2/a) sum_{xi in L*} "
            "[(xi + kappa)(xi + kappa)^T exp(-pi |xi + kappa|^2/a) - xi xi^T exp(-pi |xi|^2/a)] (Poisson summation; the R = 0 term may be included because 1 - cos 0 = 0).",
            ["ZP-C-0001"], arg("PROOF.md section 1, method.")),
        rec("ZP-C-0005", "C", "argument",
            "Sum rule: averaging tr D over the zone kills every cos k.R with R != 0, so <tr D>_BZ = sum_{R != 0} Lap V(R) = 4 pi a - (4 pi^2/a) S(1/a; L), "
            "S(alpha; L) = sum_{P in L} |P|^2 exp(-pi alpha |P|^2) (Poisson summation; the dual of a unit-covolume planar lattice is a rotation of it). "
            "Lap V for the Gaussian is the second-moment density of ZP-A-0004.",
            ["ZP-C-0004", "ZP-A-0004"], arg("PROOF.md section 3.3.")),
        rec("ZP-C-0006", "C", "argument",
            "At a = 1: with theta_L(1/alpha) = alpha theta_L(alpha) (Jacobi, classical, not formalised), ZP-A-0007 gives theta'(1) = -theta(1)/2, hence S(1) = theta(1)/(2 pi) "
            "(this is also Luo-Wei Lemma 3.5, ZP-L-0002) and <tr D> = 4 pi - 2 pi theta_L(1). With Montgomery (ZP-L-0003) the triangular lattice is the unique maximiser of <tr D> at a = 1.",
            ["ZP-C-0005", "ZP-A-0007", "ZP-L-0002", "ZP-L-0003"], arg("PROOF.md section 3.3, consequence 2.")),
        rec("ZP-C-0007", "C", "argument",
            "For a <= 1 the triangular lattice is a global maximiser of the mean-square phonon frequency <tr D> among unit-covolume lattices (and hence of the Einstein bound): "
            "the identity of ZP-C-0005 turns Luo-Wei's minimum of S(alpha; L) for alpha = 1/a >= 1 (ZP-L-0001) into a maximum of <tr D>.",
            ["ZP-C-0005", "ZP-L-0001"], arg("PROOF.md section 3.3, consequence 1.")),
        rec("ZP-C-0008", "C", "argument",
            "Einstein bound: by Cauchy-Schwarz, E_zp <= sqrt(<tr D>/2), with equality only for a flat spectrum.",
            ["ZP-C-0001"], arg("PROOF.md section 3.3.")),
        rec("ZP-C-0009", "C", "argument",
            "Concavity decomposition: with Phi(D) = tr D^{1/2} at fixed reduced k, Lap E_zp = Lin + Conc, Lin = (1/2)<y^2 sum_i tr(Phi'(D) d_i^2 D)>, "
            "Conc = (1/2)<y^2 sum_i Phi''(D)[d_i D, d_i D]>, and Conc <= 0 by operator concavity of the square root (Daleckii-Krein form with a per-branch and a branch-mixing part). "
            "The sign of Lin is not controlled by the sum rule.",
            ["ZP-C-0001", "ZP-C-0002"], arg("PROOF.md section 3.5.")),
        rec("ZP-C-0010", "C", "argument",
            "Structural reason QU-1 can fail: E_zp is not a pair sum (it is a trace of a square root of a lattice sum), so the Bernstein-mixture argument that transfers "
            "Montgomery's Gaussian theorem to every completely monotone potential is linear in V and does not apply to E_zp.",
            ["ZP-C-0003", "ZP-C-0009"], arg("PROOF.md section 3.6, interpretation 4.")),
        rec("ZP-C-0011", "C", "argument",
            "Logic and scope: if a dynamically stable lattice has E_zp below the triangular value for some completely monotone g, QU-1 is false as stated. The competitor lattices are held "
            "in shape by an imposed constraint, not stress-free: the triangular lattice has the lower static energy, so a statement about E_static + Lambda E_zp at its own equilibrium shape is a "
            "different statement and is untested. Only Bravais lattices, the harmonic approximation, and Gaussian/Yukawa/dipolar-exciton/Riesz (s > 2) potentials; Coulomb and Keldysh are excluded.",
            ["ZP-C-0001"], arg("GATE.md caveats; PROOF.md section 8.")),
        rec("ZP-C-0012", "C", "argument",
            "Conditionality: no result in this preprint rests on openai/math (AI-generated, not peer reviewed). The refutation needs only that exp(-pi a r^2) is completely monotone in r^2, "
            "which is elementary; the static positive control uses Montgomery (ZP-L-0003) plus Bernstein mixtures. The pinned toolchain is the only openai/math dependence.",
            [], arg("PROOF.md section 0.")),
        rec("ZP-C-0013", "C", "argument",
            "Novelty: one alphaXiv search (keywords zero-point energy, triangular lattice, lattice energy minimization, phonon, theta function) found no paper on lattice-shape optimality "
            "of the harmonic zero-point energy. This is absence by one search, not a novelty claim.",
            [], arg("PROOF.md section 6, prior art.")),
        # ------------------------------------------------------------------ Tier X
        rec("ZP-X-0001", "X", "numeric",
            "Headline counterexample (Poisson dynamical matrix + Duffy-Gauss rule, N = 128): gauss:1, tau = 0.5 + 0.966025 i: E_zp = 1.4902783183 against 1.5033523522 for the triangular lattice, "
            "dE_zp = -1.3074e-2; quadrature error about 4e-15 (N = 96 vs 128); stable (min lambda/|k|^2 = 0.03493 over the zone at |k| >= 3e-3, exact long-wave 0.10466; triangular 0.03222 and 0.23826). "
            "Reproduced by Rust at n = 768 (G1 code) to 2.6e-9, and by a third minimal numpy implementation (human_check.py: Poisson form, half-shifted grids n = 128 and 256, Richardson) to 4e-12 in dE_zp.",
            ["ZP-C-0001", "ZP-C-0004"], num([d / "poisson_check.json", d / "elastic_check.json", d / "human_check.json", d / "rust_curv/rust_fine_c1.csv", d / "rust_curv/rust_fine_tri.csv"])),
        rec("ZP-X-0002", "X", "numeric",
            "Gate G1 (real-space folded sum, uniform k-grids, n^-3 extrapolation): 12 completely monotone potentials, 567 shapes each; k-grid exponent 3.00-3.01; n = 96 error at the triangular point between 2.6e-8 and 6.5e-6; "
            "an independent numpy implementation agrees to about 1e-6.",
            ["ZP-C-0001"], num([d / "scan_summary_cm.json", d / "independent_check.json", d / "gauss_1__coarse.csv", d / "gauss_1__random.csv", d / "gauss_1__patch_rho.csv"])),
        rec("ZP-X-0003", "X", "numeric",
            "Refuted for 8 of 12 tested potentials (dipolar 0.1 and 0.5, gauss 0.5 and 1, riesz 3 and 4, yukawa 1 and 2) by a lattice stable on n = 96, 192, 384 with lower E_zp; not refuted "
            "for gauss 0.25, 2, 4 and riesz 6 on a 567-point scan plus dense 0.005-step edge scans (a sample, not an exhaustive search). The riesz:4 refutation rests on one competitor "
            "(0.3 + 0.954 i) whose exact long-wave eigenvalue is 0.08 % of the triangular value; for the other seven a second competitor at 0.5 + 0.966 i also lies below.",
            ["ZP-C-0001"], num([d / "edge_check.json", d / "scan_summary_cm.json", d / "elastic_check.json"])),
        rec("ZP-X-0004", "X", "numeric",
            "Correction: the largest-margin point gauss:1, 0.295 + 0.9555 i (dE_zp = -5.12e-2, E_zp confirmed by Duffy, n = 768 and Richardson to about 1e-10) is only marginally stable "
            "(exact long-wave eigenvalue 1.317e-4, 0.06 % of the triangular value) and is not the headline. A first independent run flagged it unstable because of round-off at |k| about 5e-7; "
            "the optimiser was then restricted to |k| >= 3e-3 and the exact elastic tensor used for the long-wave limit (both result files kept).",
            ["ZP-X-0001"], num([d / "poisson_check.json", d / "poisson_check_v1_unbounded_optimizer.json", d / "elastic_check.json"])),
        rec("ZP-X-0005", "X", "numeric",
            "Curvature of E_zp at rho for exp(-pi a r^2): isotropic for a >= 0.5 (d_xx = d_yy to 1.5e-6 relative, |d_xy| <= 2e-8, |grad| <= 1.5e-6 over the four Gaussians with a >= 0.5 of the mechanism study (a = 0.5, 1, 2, 4); at a = 0.25 the relative difference is 4.3e-4 and the gradient about 1e-5); c(a) = Lap E_zp/4 is numerically < 0 (triangular is a strict local maximum of E_zp) on (0.37668, 1.58148) "
            "(23-point scan of a in [0.1, 8] followed by bisection of the sign changes; roots robust to node count and stencil; sign changes between scan points are not excluded; c = 0 at the roots, where the second-order test is inconclusive); positive for a in (0.15, 0.37668) and (1.58148, 4]. Rust real-space code at n = 768 confirms both sign changes. For a <= 0.123 the triangular lattice is marginal "
            "(shear eigenvalue <= 1.5e-9) and c changes sign again; a = 6, 8 are precision-flagged.",
            ["ZP-C-0002"], num([d / "mechanism.json", d / "smalla_check.json", d / "rust_curv/gauss_0.35.csv", d / "rust_curv/gauss_0.40.csv", d / "rust_curv/gauss_1.50.csv", d / "rust_curv/gauss_1.65.csv"])),
        rec("ZP-X-0006", "X", "numeric",
            "Sum-rule and pair-sum checks: Poisson D vs explicit real-space sum agrees to <= 1.4e-14 relative at 200 random k in 12 cases; exact sum rule vs Duffy <tr D> to <= 2.7e-14; the stencil Laplacian of E_static and of <tr D> "
            "agrees with the exact lattice sum of h (ZP-A-0004) to <= 2.5e-10 relative for a >= 0.5; <tr D> = 4 pi - 2 pi theta(1) checked at five shapes to <= 5.1e-16; "
            "Lap <tr D>(rho) < 0 for a < 1.09361 (consistent with Luo-Wei and with Betermin's remark that hexagonal optimality of S cannot hold for all alpha).",
            ["ZP-C-0003", "ZP-C-0005", "ZP-C-0006", "ZP-A-0004"], num([d / "poisson_check.json", d / "mechanism.json", d / "sumrule_identity.json"])),
        rec("ZP-X-0007", "X", "numeric",
            "Mechanism (finite differences, shell-resolved): at a = 1, Lap E_zp = -3.848 = Lin (-0.799) + Conc (-3.048), 63 % from the zone-boundary shell. For the headline competitor the loss is a softening of the lower branch "
            "near the zone boundary (-1.497e-2 of -1.751e-2); <tr D> falls by 2.03e-2, which moves the Einstein bound by only -3.13e-3 (24 % of the gain), the other 76 % is the wider spread of the spectrum (Jensen gap). "
            "Negative control gauss:2 at the same shape: <tr D> rises, total +4.53e-3.",
            ["ZP-C-0008", "ZP-C-0009"], num([d / "mechanism.json"])),
        rec("ZP-X-0008", "X", "numeric",
            "Positive controls: frozen-phonon second difference of an independent pair-sum energy vs (1/2) e^T D e, max relative difference 2.14e-7 over 33 cases; Riesz statics vs Epstein closed forms and dipolar statics vs Ewald to <= 3.9e-7; "
            "cutoff rc 400 -> 800 changes E_zp by <= 2.2e-13; modular invariance of E_zp to <= 2.1e-13 at the same k-set; the static minimiser is the triangular lattice for all 12 potentials (Montgomery, ZP-L-0003).",
            ["ZP-C-0001", "ZP-L-0003"], num([d / "controls.json", d / "scan_summary_cm.json"])),
        rec("ZP-X-0009", "X", "numeric",
            "Negative controls: dropping the -xi xi^T term breaks the Poisson-vs-real-space match by a relative 0.027 to 17.7; swapping a <-> 1/a is invisible at the self-dual a = 1 (1.1e-15) but breaks it by 0.9 to 9.4 elsewhere; "
            "the square lattice is flagged unstable (min lambda/|k|^2 = -0.1475 for gauss:1); gauss:2, which survived G1, has no stable lower lattice at the gauss:1 competitor shapes (+4.53e-3, or unstable); "
            "non-completely-monotone 'wells' potentials show a stable lower-E_zp lattice (-3.03 and -2.04) so the search can detect a lower-E_zp stable lattice when one exists (detection power, not a false-positive control; morse:3;1.0 also has a stable lower-E_zp competitor at 0.5 + 0.966 i).",
            ["ZP-C-0001"], num([d / "poisson_check.json", d / "scan_summary_neg.json", d / "neg_search.json", d / "elastic_check.json"])),
        rec("ZP-X-0010", "X", "numeric",
            "Functional E_static + Lambda E_zp (V -> eps V, Lambda proportional to eps^-1/2; harmonic approximation fails for large Lambda, so this is a statement about the functional only): "
            "for each refuted potential the minimum over the stable sample leaves the triangular lattice at some Lambda between 0.1 and 10 (riesz:4 only at Lambda = 10); the survivors keep it at all five Lambda tested.",
            ["ZP-C-0011"], num([d / "scan_summary_cm.json"])),
        rec("ZP-X-0011", "X", "numeric",
            "Restricted conjecture QU-1' (suggested by the table, not proved): for exp(-pi a r^2) with 0.15 <= a <= 4 the triangular lattice is a strict local minimiser of E_zp among unit-covolume Bravais lattices if a < 0.37668 or a > 1.58148, and a strict local maximiser for 0.37668 < a < 1.58148 (numerical c); at the bisected numerical roots c = 0 and nothing is stated. "
            "At a = 0.15 the triangular lattice is barely stable (min lambda/|k|^2 = 1.7e-7). The global version is open and not claimed.",
            ["ZP-X-0005", "ZP-C-0002"], num([d / "mechanism.json", d / "smalla_check.json"])),
        rec("ZP-X-0012", "X", "numeric",
            "Paper-stage reruns by the same AI pipeline (not independent verification): Lean recompile of Basic.lean rc 0 in 7.9 s and of Controls.lean rc 0, axiom output identical to the lane's; sha256 of both files equal "
            "the recorded values; cargo test -p qf-yukawa-crystal at the branch HEAD: 59 passed, 0 failed, 1 ignored; cargo clippy --workspace --features experimental -- -D warnings: no warnings or errors; cargo fmt --check: exit 0; lattice_phonon duffy reproduces E_zp = 1.490278318280 (headline) and 1.503352352207 (triangular), curv gives c = -0.961984.",
            ["ZP-A-0001"], num([d / "rerun_basic.json", d / "rerun_controls.json", d / "rerun_cargo_test.txt", d / "rerun_clippy.txt", d / "rerun_fmt.txt", d / "rerun_duffy_headline.txt", d / "rerun_duffy_tri.txt", d / "rerun_curv.txt"])),
        rec("ZP-X-0013", "X", "numeric",
            "Separate AI audit (a different Claude agent; no human audit; scope in AUDIT.md): recompiled Basic.lean and Controls.lean with the pinned Lean 4.34.1 (19 printed declarations within the allowlist; its own planted sorry and planted axiom caught by #print axioms); "
            "an independent real-space numpy code reproduces E_zp(gauss:1) = 1.5033523522067 at rho and 1.4902783182775 at 0.5+0.966025i (dE = -1.30740e-2), E_zp at -1/tau identical, the sign and size of c at a = 1 and 2, and dE = -1.4583e-2 for gauss:0.5 at (0.5, 1.016); "
            "regenerated all macros and tables byte-identically from data/. Not recomputed by the auditor: the dipolar, Riesz and Yukawa refutations, the long-wave elastic tensor, Lin/Conc, Result 5, c(a) beyond a = 1, 2, phonon.rs.",
            ["ZP-X-0001", "ZP-A-0001"], num([d / "audit/audit_basic.json", d / "audit/audit_basic_orig.json", d / "audit/audit_controls.json", d / "audit/audit_realspace.json", d / "audit/audit_elenchus_g05.json", PAPER / "AUDIT.md"],
                                            instrument="independent auditor scripts (not in this directory; outputs in data/audit/) and the pinned Lean 4.34.1 toolchain")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": claims}, indent=1, ensure_ascii=False))
    print(f"claims {len(claims)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
