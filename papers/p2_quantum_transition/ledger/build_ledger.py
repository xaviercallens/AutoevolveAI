"""Build the Elenchus claim ledger for the B1 paper (papers/p2_quantum_transition). Modelled on papers/prog_zero_point_optimality/ledger/build_ledger.py.

Tier discipline (tools/ledger.py): a claim may not be filed above the tier of anything it depends on. There is no Tier A row (no Lean here) and no Tier L row:
the citation gate admits only theorem-like quotations, and the real gate verdict for every literature quotation is REFUSED (kind). Those quotations are filed at
Tier C with the gate's verbatim-fidelity result as evidence. Everything resting on floating point is Tier X; Tier C rows depend only on Tier C rows.
Run:  /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I build_ledger.py ; then run_gate.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
EV = HERE / "evidence"
DATA = PAPER / "data"
CIT = HERE / "citations"
RUSTY_SHA = "9e85e15b23be0c74a665b6a5b74ec02b0bbffc5f"
RUSTY_WT = "/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-p2"
SCHA_RS_SHA = "35c65007c97c9f43e2a66e8092940909b29beeefe4e7aa166091a77dc578e98a"
PAPER_TEX = "papers/p2_quantum_transition/main.tex"

NUM = json.loads((DATA / "result_numbers.json").read_text())
EXTRA = json.loads((DATA / "extra_checks.json").read_text())
EXT = json.loads((DATA / "scha_extend.json").read_text())
CHK = json.loads((CIT / "citation_check.json").read_text())
TAB = {r["a"]: r for r in NUM["hbar_star_table"]}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def blob(obj: dict) -> str:
    raw = json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False).encode()
    d = sha(raw)
    EV.mkdir(parents=True, exist_ok=True)
    (EV / f"{d}.json").write_bytes(raw)
    return f"sha256:{d}"


def file_ref(p: Path) -> dict:
    return {"path": str(p.relative_to(PAPER.parents[1])), "sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict, short: str) -> dict:
    r = {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind, "depends_on": depends, "evidence": blob(ev), "audit": dict(AUDIT)}
    SHORT[cid] = short
    return r


SHORT: dict[str, str] = {}
AUDIT: dict[str, object] = {
    "auditor": "a separate Claude agent (not the producer or the paper writer)", "date": "2026-10-26",
    "verdict": "ACCEPT_WITH_CORRECTIONS", "report": "papers/p2_quantum_transition/AUDIT.md",
    "human_audit": False, "note": "independent AI audit; corrections B1-B4 and N1-N11 applied in the revision (REVISION.md); no human audit",
}


def arg(text: str, **kw: object) -> dict:
    return {"kind": "argument", "text": text, "derivation": f"{PAPER_TEX}, Section 3 (step-by-step derivation)", "source_note": file_ref(DATA / "TRANSITION.md"),
            "status": "human-style argument written by an AI agent; independent AI audit AUDIT.md (ACCEPT_WITH_CORRECTIONS); no human audit", **kw}


def lit(key: str, statement_short: str) -> tuple[str, dict]:
    c = CHK[key]
    ev = {"kind": "argument", "text": "Literature statement quoted verbatim from the fetched source text. Tier L (citation gate) is not available: the gate admits only theorem-like kinds "
          "and refuses this kind. Filed at Tier C with the gate's verbatim-fidelity result.",
          "claim": c["claim"], "real_gate": {"rc": c["rc"], "stdout": c["stdout"]}, "verbatim_only_check": c["verbatim_only_check"],
          "claim_file": file_ref(CIT / f"claim_{key}.json"), "source_pdf_sha256": c["claim"]["pdf_sha256"], "source_text_sha256": c["claim"]["source_sha256"],
          "source_manifest": file_ref(HERE / "sources" / "MANIFEST.md"), "status": "quote verified against producer-fetched text; statement_match is the producer's judgement"}
    return statement_short, ev


def num(files: list[Path], **kw: object) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True,
            "instrument": "Python/numpy producer code results/proposal2/2026-10-26/B1/code (b1_lib.py etc.), rusty-SUNDIALS crates/qf-yukawa-crystal "
                          f"at {RUSTY_SHA} (not pushed), and the paper-stage scripts in papers/p2_quantum_transition",
            "files": [file_ref(p) for p in files], "status": "floating-point result; independent AI audit AUDIT.md reproduced the headline numbers; no human audit", **kw}


LIT_SHORT = {
    "B1-C-0101": "quote, Astrakharchik et al. p.3: Lindemann ratio 0.230(6) at 2D dipole melting; others 0.235(15), 0.24(1), 0.279",
    "B1-C-0102": "quote, Prestipino et al. p.11: Gaussian (n = 2) is a marginal case, no evidence of a cluster crystal in 2D or 3D",
    "B1-C-0103": "quote, Prestipino et al. p.15: for n = 2 crystallization is swept away at T = 0 (mean field)",
    "B1-C-0104": "quote, Prestipino et al. p.25: freezing completely washed out for n = 2 (mean field)",
    "B1-C-0105": "quote, Prestipino et al. p.25: mean field realistic for weak interparticle forces",
    "B1-C-0106": "quote, Henkel et al. p.2: dressed potential C6/(r^6 + Rc^6)",
    "B1-C-0107": "quote, Henkel et al. p.2: negative components of the momentum-space potential near 2 pi/Rc",
    "B1-C-0108": "quote, Henkel et al. p.4 note 26: C6 M/(hbar^2 Rc^4) < 1e-2 for their Fig. 3c",
    "B1-C-0109": "quote, Zeiher et al. p.2: U_ij = U0/(1 + (R/Rc)^6)",
    "B1-C-0110": "quote, Zeiher et al. p.3: U0/2 pi about 1.8 kHz",
    "B1-C-0111": "quote, Zeiher et al. p.7: Rc/a_lat = 2.02",
    "B1-C-0112": "quote, Zeiher et al. p.3: a_lat = 532 nm",
    "B1-C-0113": "quote, Zeiher et al. p.3: rubidium-87",
    "B1-C-0114": "quote, Zeiher et al. p.5: dressed-atom loss time 130(20) us vs 2.2 ms expected",
    "B1-C-0115": "quote, Zeiher et al. p.3: bare Rydberg state lifetime about 27 us",
    "B1-C-0116": "quote, Astrakharchik et al. p.3: a_L^-1 = (sqrt(3) n/2)^(1/2), i.e. a_L = nearest-neighbour distance",
}


def tex_escape(s: str) -> str:
    """Escape a plain-text label for a LaTeX table cell."""
    bs = chr(92)
    for ch, rep in (("&", "and"), ("%", bs + "%"), ("_", bs + "_"), ("#", bs + "#"), ("~", "$" + bs + "sim$"), (">=", "$" + bs + "ge$"), ("<", "$<$"), ("^", bs + "^{}"), ("hbar*", "hbar$^*$")):
        s = s.replace(ch, rep)
    return s


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    d = DATA
    a1 = TAB[1.0]
    ex = EXTRA
    claims: list[dict] = []
    # ---------------------------------------------------------------- Tier C: definitions and arguments
    claims.append(rec("B1-C-0001", "C", "argument",
                      "Model and units: planar Bravais lattice of shape tau, one particle per cell, V = eps exp(-pi a r^2/l^2); hbar_eff = hbar/sqrt(m eps l^2); harmonic energy per particle "
                      "E = E_st + hbar_eff E_zp, E_st = (1/2) sum_{R != 0} exp(-pi a |R|^2), E_zp = (1/2) <sqrt(lam_1(D)) + sqrt(lam_2(D))>_BZ with "
                      "D(k) = sum_{R != 0} (1 - cos k.R) Hess V(R); GCM units rho sigma^2 = 1/(pi a), hbar/sqrt(m eps sigma^2) = hbar_eff sqrt(pi a).",
                      [], arg("Definition."), "model, units, E = E_st + hbar E_zp"))
    claims.append(rec("B1-C-0002", "C", "argument",
                      "Curvature balance: E depends on the lattice only up to rotation, so E(gamma tau) = E(tau) on SL2(Z); gamma(tau) = (tau - 1)/tau fixes rho with derivative the -120 degree rotation "
                      "(machine-checked in the prior paper P2, not re-proved here); hence grad E(rho) = 0, the Hessian is scalar and E(tau) - E(rho) = c |tau - rho|^2/y_rho^2 + O(r^3), "
                      "c = Lap E(rho)/4. With c(h) = c_st + h c_zp, c_st > 0 and c_zp < 0: c > 0 iff h < h* = -c_st/c_zp. Invariance, smoothness and the chain rule are not formalised.",
                      ["B1-C-0001"], arg("Symmetry and curvature balance."), "isotropic curvature; spinodal hbar* = -c_st/c_zp"))
    claims.append(rec("B1-C-0003", "C", "argument",
                      "First order: in the disk coordinate w = (tau - rho)/(tau - conj rho) the stabiliser of rho is D3 (w -> omega w, omega^3 = 1, plus a reflection), whose only cubic invariant is Re w^3. "
                      "With Delta E_st = s2 r^2 + s3 r^3 cos 3 theta and Delta E_zp = z2 r^2 + z3 r^3 cos 3 theta, the tie coupling T = Delta E_st/(-Delta E_zp) = h* + kappa r cos 3 theta + O(r^2), "
                      "kappa = (s3 + h* z3)/|z2|. If kappa != 0 a lower shape exists for some h < h*, so the transition is first order (a Landau cubic term); the two mirror rays Re tau = 1/2 and |tau| = 1 "
                      "differ by 60 degrees, so cos 3 theta = +-1 on them and the slopes of T in |w| are equal and opposite. Lambda_1 = min over dynamically stable shapes of T.",
                      ["B1-C-0002"], arg("Symmetry argument (Landau)."), "D3 cubic invariant: first order; equal and opposite ray slopes"))
    claims.append(rec("B1-C-0004", "C", "argument",
                      "Lindemann scaling: harmonic <|u|^2>/l^2 = h U(a), U = (1/2)<tr D^{-1/2}>_BZ; gamma = sqrt(<|u|^2>)/a_nn with a_nn^2 = 2/sqrt3; Lambda_L(gamma_c) = gamma_c^2 a_nn^2/U(a), so "
                      "Lambda_L is proportional to gamma_c^2 (0.9 gamma_c -> 0.81, 1.1 gamma_c -> 1.21) and Lambda_1/Lambda_L = (gamma(Lambda_1)/gamma_c)^2. For the Coulomb crystal gamma^2 ~ r_s^{-1/2} so r_s* ~ gamma_c^{-4}. "
                      "Lindemann is a heuristic.",
                      ["B1-C-0001"], arg("Algebra."), "Lindemann: Lambda_L ~ gamma_c^2; ratio identity"))
    claims.append(rec("B1-C-0005", "C", "argument",
                      "SCHA for Gaussians in closed form: with w_R Gaussian of covariance C_R = h <(1 - cos k.R) D_eff^{-1/2}>, <exp(-b|R + w|^2)> = det(I + 2bC)^{-1/2} exp(-b R^T (I + 2bC)^{-1} R) (b = pi a); "
                      "E_SCHA = (h/4)<tr D_eff^{1/2}> + (1/2) sum_{R != 0} <V(R + w_R)>, stationary at D_eff = sum_R (1 - cos k.R)<Hess V(R + w_R)> (standard condition, verified numerically not re-derived); "
                      "for h -> 0, E_SCHA = E_st + h E_zp + O(h^2).",
                      ["B1-C-0001"], arg("Gaussian integral and expansion."), "SCHA closed form; small-hbar limit"))
    claims.append(rec("B1-C-0006", "C", "argument",
                      "Scope of SCHA: for each shape the T = 0 SCHA energy is a variational (Rayleigh-Ritz) upper bound on the true ground-state energy, and differences of upper bounds do not order the true energies; "
                      "its O(h^2) energy contains the quartic anharmonicity at first order but not the second-order cubic term; it has no exchange. 'SCHA removes the transition' is a statement about the approximate landscape.",
                      ["B1-C-0005"], arg("Limitation."), "SCHA scope: upper bound, no 2nd-order cubic, no exchange"))
    claims.append(rec("B1-C-0007", "C", "argument",
                      "The 2D Fourier transform of exp(-pi a r^2) is a^{-1} exp(-pi k^2/a) > 0 for all k (closed form): the Gaussian has no negative Fourier component.",
                      [], arg("Closed-form Fourier transform."), "Gaussian Fourier transform is positive"))
    claims.append(rec("B1-C-0011", "C", "argument",
                      "Reading of the QMC Lindemann anchor: in Astrakharchik et al. gamma = sqrt<(r - r_c)^2>/a_L with a_L 'the lattice length'; the same page defines the inverse lattice site length "
                      "a_L^-1 = (sqrt(3) n/2)^(1/2), i.e. a_L = a_nn (quotation B1-C-0116); we read <(r - r_c)^2> as the total 2D displacement (r is a 2D position). This displacement reading is ours, not a quoted definition.",
                      ["B1-C-0101", "B1-C-0116"], arg("Assumption flagged."), "reading: <(r - r_c)^2> is the total 2D displacement (a_L = a_nn is quoted, B1-C-0116)"))
    # literature quotations (Tier C with verbatim check)
    LIT = [("B1-C-0101", "astra_lindemann", "Astrakharchik et al. (cond-mat/0608246v2 p.3): Lindemann ratio at the 2D dipole quantum melting gamma = 0.230(6); hard disks 0.279; Yukawa bosons 0.235(15); Coulomb bosons 0.24(1)."),
           ("B1-C-0116", "astra_aL", "Astrakharchik et al. (cond-mat/0608246v2 p.3): in the solid phase the static structure factor has a delta-function peak at the inverse lattice site length a_L^-1 = (sqrt(3) n/2)^(1/2) = 0.93... n^(1/2), i.e. a_L is the nearest-neighbour distance of the triangular lattice at density n."),
           ("B1-C-0102", "prest_marginal", "Prestipino et al. (1809.07515v1 p.11): the Gaussian repulsion (n = 2) is a marginal case, no evidence of a cluster crystal in 2D or 3D (the authors' summary of the classical Gaussian-core-model literature, refs [37,38], not their mean-field result)."),
           ("B1-C-0103", "prest_swept", "Prestipino et al. (p.15): for n = 2 (u~(k) everywhere positive) crystallization is swept away at zero temperature (mean field)."),
           ("B1-C-0104", "prest_washed", "Prestipino et al. (p.25): freezing is completely washed out in the Gaussian n = 2 case (mean field)."),
           ("B1-C-0105", "prest_mf", "Prestipino et al. (p.25): the mean-field state is realistic for weak interparticle forces."),
           ("B1-C-0106", "henkel_pot", "Henkel et al. (1001.3250v2 p.2): dressed potential U(r) = C6~/(r^6 + Rc^6)."),
           ("B1-C-0107", "henkel_neg", "Henkel et al. (p.2): the momentum space potential U~ has negative attractive contributions around k_rot ~ 2 pi/Rc."),
           ("B1-C-0108", "henkel_weak", "Henkel et al. (p.4, note 26): C6~ M/(hbar^2 Rc^4) < 1e-2 for the parameters of Fig. 3c."),
           ("B1-C-0109", "zeiher_form", "Zeiher et al. (1602.06313v3 p.2): U_ij = U0/(1 + (R/Rc)^6)."),
           ("B1-C-0110", "zeiher_u0", "Zeiher et al. (p.3): U0/2pi ~ 1.8 kHz."),
           ("B1-C-0111", "zeiher_rc", "Zeiher et al. (p.7): cut-off radius Rc/a_lat = 2.02 for the 31P1/2 state."),
           ("B1-C-0112", "zeiher_lat", "Zeiher et al. (p.3): optical lattice spacing a_lat = 532 nm."),
           ("B1-C-0113", "zeiher_rb", "Zeiher et al. (p.3): the atoms are rubidium-87."),
           ("B1-C-0114", "zeiher_loss", "Zeiher et al. (p.5): extracted loss time 130(20) microseconds against the anticipated tau_r/beta^2 = 2.2 ms."),
           ("B1-C-0115", "zeiher_tau", "Zeiher et al. (p.3): the 31PJ state has a lifetime of approximately 27 microseconds.")]
    for cid, key, st in LIT:
        s, ev = lit(key, st)
        claims.append(rec(cid, "C", "argument", s + " [quotation verified verbatim against the fetched text; the real citation gate verdict is REFUSED because the kind is not theorem-like, so Tier L is not claimed]", [], ev, LIT_SHORT[cid]))
    claims.append(rec("B1-C-0008", "C", "argument",
                      "No cluster or supersolid preemption for a pure Gaussian: its Fourier transform has no negative component (B1-C-0007) and Prestipino et al. call it the marginal case with no evidence of a cluster crystal in 2D or 3D (B1-C-0102; their summary of the classical Gaussian-core-model literature). "
                      "The sub-agent-read sources that state the negative-Fourier-component criterion are not in this ledger.",
                      ["B1-C-0007", "B1-C-0102"], arg("Combination of a closed form and one verbatim quotation."), "no cluster preemption for a pure Gaussian"))
    claims.append(rec("B1-C-0009", "C", "argument",
                      "Rydberg dressing realises a soft-shoulder potential (U0/(1 + (R/Rc)^6) or C6/(r^6 + Rc^6)) whose momentum-space form has negative components (Henkel et al., B1-C-0107); it is not a Gaussian. It therefore has the negative Fourier component that the cluster criterion requires "
                      "(that criterion is attributed to sub-agent-read sources only, not in this ledger), and Henkel et al. (re-read) find roton softening and supersolid formation for it. Its quantum parameter hbar/sqrt(m U0 Rc^2) (in units of Rc) cannot be mapped onto the Gaussian hbar_eff window. A true Gaussian interaction was not found in cold-atom platforms (sub-agent search, not in the ledger).",
                      ["B1-C-0106", "B1-C-0107", "B1-C-0109"], arg("Combination of quotations."), "Rydberg dressing: soft shoulder, not Gaussian"))
    # ---------------------------------------------------------------- Tier X
    claims.append(rec("B1-X-0001", "X", "numeric",
                      f"B1a: for a in (0.37668, 1.58148) the harmonic spinodal hbar*(a) = -c_st/c_zp exists (a = 0.4 ... 1.5 tested): minimum {min(r['hbar_star'] for r in TAB.values() if r['hbar_star']):.4f} at a = 0.5, "
                      f"{a1['hbar_star']:.4f} at a = 1, diverging at both ends; negative controls a = 0.3 (c_zp = +{TAB[0.3]['c_zp']:.3f}) and a = 2.0 have c_zp > 0, no hbar* and no stable shape with Delta E_zp < 0.",
                      ["B1-C-0001", "B1-C-0002"], num([d / "result_numbers.json", d / "b1a_curvature.json", d / "summary.json", d / "scan_a0.3.json", d / "scan_a2.json"]), "B1a: hbar*(a) table; negative controls a = 0.3, 2"))
    claims.append(rec("B1-X-0002", "X", "numeric",
                      f"First order: a stable oblique lattice reaches the triangular energy at Lambda_1 < hbar* (a = 1: {a1['Lam_1_edge']['Lam1']:.4f} against {a1['hbar_star']:.4f}); Lambda_1/hbar* = 0.75-0.78 for a in [0.45, 1.2]; "
                      "the argmin over the stable sample jumps from the triangular neighbour to 0.30 + 0.96 i between hbar = 0.09 and 0.10 at a = 1; winners are oblique (a <= 1.2) or near-centred-rectangular (a >= 1.3) and lie on the harmonic stability "
                      "edge (margin 2.3e-5 to 2.4e-3 against 0.034 for the triangular lattice at a = 1); margin >= 0.01 moves Lambda_1 by 3-11 %. "
                      "Meaning of 'first order': a finite-distortion dynamically stable lattice ties with rho before c(hbar) vanishes; the competitor minimises E over the harmonically stable sample and sits on its boundary, it is not an interior local minimum.",
                      ["B1-C-0003"], num([d / "result_numbers.json", d / "scan_a1.json", d / "scan_a0.5.json", d / "summary.json"]), "first order: Lambda_1 < hbar*; stability-edge winners"))
    claims.append(rec("B1-X-0003", "X", "numeric",
                      "Symmetry test: the slopes of the tie coupling against |w| on the rays Re tau = 1/2 and |tau| = 1 are equal and opposite: slope ratio "
                      + ", ".join(f"{v['slope_ratio_up_over_arc']:.2f} (a = {k})" for k, v in ex["ray_slopes"].items()) + " (prediction -1; both signs are reversed at a = 1.2, so kappa changes sign between a = 1 and 1.2 and the local cubic argument is silent there; the first-order claim rests on Lambda_1 < hbar* in B1-X-0002, not on the cubic term alone).",
                      ["B1-C-0003"], num([d / "extra_checks.json", d / "scan_a1.json", d / "scan_a0.5.json", d / "scan_a0.7.json", d / "scan_a0.8.json", d / "scan_a1.2.json", PAPER / "checks.py"]), "ray slopes equal and opposite (ratio -1.0)"))
    claims.append(rec("B1-X-0004", "X", "numeric",
                      f"B1b: harmonic Lindemann ratio at hbar*: >= {ex['bands']['min_gamma_hbar_star']:.4f} for all a tested (minimum at a = 0.7), rising towards both ends; at Lambda_1: {ex['bands']['min_gamma_Lam1']:.3f}-{a1['gamma_at_Lam_1_edge']:.3f} (a = 0.5-1) inside [0.23, 0.28] for a = "
                      f"{', '.join(f'{x:g}' for x in ex['bands']['a_inside_023_028'])} and inside [0.23, 0.30] for a = {', '.join(f'{x:g}' for x in ex['bands']['a_inside_023_030'])}; Lambda_1 > Lambda_L(0.23) for every a. "
                      f"The spinodal gamma(hbar*) is >= 0.28 (to rounding; 0.2798 at a = 0.7) only against the band gamma_c <= 0.28; against the harmonic value gamma_c = 0.30 it is "
                      f"{min(r['gamma_at_hbar_star'] for r in TAB.values() if r['hbar_star'] and r['a'] >= 0.45 and r['gamma_at_hbar_star'] < 0.30):.3f}-{max(r['gamma_at_hbar_star'] for r in TAB.values() if r['hbar_star'] and r['a'] >= 0.45 and r['gamma_at_hbar_star'] < 0.30):.3f} for a = 0.5-0.9, i.e. the spinodal precedes the 0.30 Lindemann point. "
                      "Inconclusive-to-adverse for 'before melting'. Where Lambda_1 is inside the band the negative verdict on the first-order point rests on SCHA alone. QMC gamma_c anchors are true-<u^2> values, the table gamma is harmonic.",
                      ["B1-C-0004", "B1-C-0101", "B1-C-0011", "B1-C-0116"], num([d / "result_numbers.json", d / "extra_checks.json", d / "summary.json"]), "B1b: gamma at hbar* and Lambda_1 vs band"))
    s = NUM["scha"]
    claims.append(rec("B1-X-0005", "X", "numeric",
                      f"B1c: in the T = 0 SCHA the triangular lattice is a local minimum far beyond the harmonic hbar*: at a = 1, Lap E_SCHA = +{s['1']['lap_ladder'][5]['lap']:.3f} at hbar = 0.15 (harmonic -0.101) and +{s['1']['lap_ladder'][-1]['lap']:.3f} at 0.30; SCHA spinodals "
                      f"{s['0.5']['lam_star_scha']:.4f} (a = 0.5), {s['0.7']['lam_star_scha']:.4f} (0.7), {s['1.3']['lam_star_scha']:.4f} (1.3), in (0.30, 0.3347) at a = 1; gamma_SCHA there 0.60-0.87.",
                      ["B1-C-0005", "B1-C-0006"], num([d / "scha.json", d / "result_numbers.json"]), "B1c: SCHA keeps triangular a local minimum to hbar ~ 0.27-0.33"))
    claims.append(rec("B1-X-0006", "X", "numeric",
                      "SCHA competitors: at the harmonic Lambda_1 every sampled stable competitor lies above the triangular lattice (min Delta E "
                      f"{min(s[a]['profiles_min_dE_stable'][0][2] for a in s):+.1e} to {max(s[a]['profiles_min_dE_stable'][0][2] for a in s):+.1e}); continuation-seeded SCHA over 150 shapes per case "
                      f"(a = 1 and 0.5; hbar = Lambda_1, hbar*, 0.2): {min(e['n_scha_stable'] for e in EXT)}-{max(e['n_scha_stable'] for e in EXT)} SCHA-stable, "
                      f"{min(e['n_scha_stable_but_harmonically_unstable'] for e in EXT)}-{max(e['n_scha_stable_but_harmonically_unstable'] for e in EXT)} of them harmonically unstable, {sum(e['n_below_triangular'] for e in EXT)} below the triangular energy.",
                      ["B1-C-0005", "B1-C-0006"], num([d / "scha.json", d / "scha_extend.json"]), "SCHA competitors incl. beyond the harmonic edge: none below"))
    claims.append(rec("B1-X-0007", "X", "numeric",
                      "SCHA controls: hbar -> 0 gives the harmonic energy with remainder 0.177 hbar^2 (ratio 3.84 on doubling); converged D_eff is a variational minimum (E rises 1.3e-5 to 1.2e-4 under perturbation); N = 24/32/48 agree to 3e-11; "
                      "small-hbar slope extrapolates to -3.843 (least-squares line through hbar = 0.0025, 0.005, 0.01; two-point extrapolation -3.846, quadratic -3.848) against the harmonic 4 c_zp = -3.848 (Lap E_SCHA, a = 1); the quadratic fit has hbar^2 coefficient 16.5 and a cubic-in-hbar term comparable to it at hbar = 0.1 (3-point interpolation, not controlled); Python and Rust agree to 8.9e-16 on 5 shapes; square lattice flagged unstable. "
                      "The 0.177, 3.84, 1.3e-5, 1.2e-4 and 3e-11 values are quoted from the producer's TRANSITION.md (t_scha.py output not re-run); the slope and the cross-check were recomputed at paper stage.",
                      ["B1-C-0005"], num([d / "scha_slope_control.json", d / "crosscheck.json", d / "TRANSITION.md"]), "SCHA controls: limit, variational minimum, slope, py = rust"))
    claims.append(rec("B1-X-0008", "X", "numeric",
                      "Harmonic controls: frozen-phonon second difference vs (1/2) e^T D e in 12 cases, max relative difference 6.3e-6, planted bug (dropped Gamma-subtraction term) 0.52; P2 reference values reproduced "
                      "(E_zp(a = 1, rho) = 1.5033523522, c_zp(1) = -0.96198); Lindemann quadrature Duffy N = 16-128 converged to 1e-13, uniform grids order 1.000.",
                      ["B1-C-0001"], num([d / "controls.json", d / "result_numbers.json"]), "harmonic positive and negative controls"))
    claims.append(rec("B1-X-0009", "X", "numeric",
                      "PIMC BLOCKED (not run): fixed commensurate box imposes the shape (no cell-shape moves); at a = 1, hbar = 0.10, competitor 0.30 + 0.96 i the thermodynamic-limit Delta E = -2.86e-4 per particle, finite-size shift -2.0e-4 (M = 8) and -2.0e-5 (M = 12); "
                      "N |Delta E| = 0.018 (N = 64) to 0.041 (N = 144); hbar omega_min = 0.027 at M = 12 (beta >~ 250).",
                      ["B1-C-0004"], num([d / "pimc_feasibility.json"]), "PIMC blocked: feasibility numbers"))
    claims.append(rec("B1-X-0010", "X", "numeric",
                      f"The 2D Hankel transform of 1/(1 + (r/Rc)^6) has minimum {ex['shoulder_ft']['shoulder_min_value']/ex['shoulder_ft']['shoulder_value_at_k0']:.4f} u~(0) at k Rc = {ex['shoulder_ft']['shoulder_min_k']:.2f}, first negative at k Rc = {ex['shoulder_ft']['first_zero_crossing_k']:.2f}; "
                      f"two cutoffs agree to {ex['shoulder_ft']['shoulder_two_cutoffs_max_abs_diff']:.1e}; positive control: the same code reproduces pi exp(-k^2/4) for exp(-r^2) to {ex['shoulder_ft']['gaussian_positive_control_max_abs_error']:.1e}; k = 0 value matches the closed form.",
                      [], num([d / "extra_checks.json", PAPER / "checks.py"]), "soft-shoulder Fourier transform negative; Gaussian control"))
    claims.append(rec("B1-X-0011", "X", "numeric",
                      f"Rydberg arithmetic (Rb-87 mass, quoted U0/2pi = 1.8 kHz, Rc = 2.02 x 532 nm): hbar^2/(m Rc^2)/h = {ex['rydberg']['E_Rc_over_h_Hz']:.1f} Hz, U0/(hbar^2/m Rc^2) = {ex['rydberg']['U0_over_E_Rc']:.1f}, hbar/sqrt(m U0 Rc^2) = {ex['rydberg']['hbar_over_sqrt_m_U0_Rc2']:.3f}.",
                      ["B1-C-0110", "B1-C-0111", "B1-C-0112", "B1-C-0113"], num([d / "extra_checks.json", PAPER / "checks.py"]), "Rydberg parameter hbar/sqrt(m U0 Rc^2) = 0.237 (arithmetic)"))
    claims.append(rec("B1-X-0012", "X", "numeric",
                      f"Rust SCHA module scha.rs (307 lines, sha256 {SCHA_RS_SHA}) at rusty-SUNDIALS commit {RUSTY_SHA} (branch physics/p2-zero-point-optimality-2026-10-25, not pushed; the blob hash was read from the git object database): "
                      "paper-stage rerun cargo test --offline --locked --release -p qf-yukawa-crystal: 63 passed, 0 failed, 1 ignored; Python and Rust SCHA agree to 8.9e-16 on 5 shapes. "
                      "The Rust module is its own implementation of the same Duffy-Gauss zone rule as the Python code (only the real-space dynamical matrix differs), so the 1e-16 agreement tests the code, not the quadrature. Clippy and fmt not rerun.",
                      ["B1-C-0005"], num([HERE / "rust_test.log", d / "crosscheck.json"]), "Rust SCHA module: commit, tests, cross-check"))
    claims.append(rec("B1-X-0013", "X", "numeric",
                      "Preregistered kill criterion ('if the transition lies beyond melting or disappears beyond harmonic, report that (negative result)') is met: the transition disappears in the T = 0 SCHA (B1-X-0005, B1-X-0006) "
                      "and the harmonic spinodal lies at or beyond the Lindemann band for gamma_c <= 0.28 (B1-X-0004; for gamma_c = 0.30 it precedes the Lindemann point for a = 0.5-0.9); the first-order point precedes melting only for gamma_c >= gamma(Lambda_1) and a ~ 0.5-1. "
                      "Where Lambda_1 is inside the Lindemann band (a = 0.5-1 for gamma_c <= 0.28, a = 0.45-1.1 for gamma_c = 0.30) the negative verdict rests on SCHA alone. Priors: B1a 0.85 confirmed, "
                      "B1b 0.4 not supported, B1c 0.25 refuted within SCHA. Holds within SCHA (no second-order cubic O(hbar^2) term, no exchange), PIMC not run, Bravais lattices only; independent AI audit AUDIT.md (ACCEPT_WITH_CORRECTIONS), no human audit.",
                      ["B1-X-0001", "B1-X-0002", "B1-X-0004", "B1-X-0005", "B1-X-0006", "B1-C-0006"], num([d / "result.json", d / "result_numbers.json"]), "net verdict: kill criterion met (negative result)"))
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": claims}, indent=1, ensure_ascii=False))
    rows = []
    for c in sorted(claims, key=lambda c: (c["tier"] != "C", c["id"])):
        rows.append("\\texttt{" + c["id"] + "} & " + c["tier"] + " & " + tex_escape(SHORT[c["id"]]) + " \\\\")
    (PAPER / "gen" / "tab_ledger.tex").write_text("\n".join(rows) + "\n")
    print(f"claims {len(claims)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
