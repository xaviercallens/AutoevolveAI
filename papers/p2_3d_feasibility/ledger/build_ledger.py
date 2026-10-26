"""Build the Elenchus claim ledger for the B3 feasibility preprint (papers/p2_3d_feasibility).

Modelled on papers/prog_zero_point_optimality/ledger/build_ledger.py. Every claim gets a content-addressed evidence blob
(evidence/<sha256>.json): verbatim quotations with the Elenchus citation-gate verdict (Tier L), the argument text with a hash of the
source note (Tier C), result files with claim_licence false (Tier X).

Re-tiering note. The feasibility note results/proposal2/2026-10-26/B3/FEASIBILITY.md used the letter A for "elementary inequality with a
proof sketch". In the Elenchus ledger A means kernel-checked, and the gate caps kind 'argument' at C. Nothing in this paper is
kernel-checked, so there is NO Tier A row: those inequalities are filed at C (human demonstration, not machine-checked). Everything that
depends on a floating-point result is filed at X (tier closure, LEDGER_TIER_INVERSION).
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
EV = HERE / "evidence"
DATA = PAPER / "data"
CODE = PAPER / "code"
CIT = json.loads((DATA / "citation_check.json").read_text())
GATE_NOTE = ("quotation copied programmatically from pdftotext output of the arXiv PDF; the gate certifies fidelity of the quote, "
             "statement_match is the writing agent's judgement; tier ceiling L")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def blob(obj: dict) -> str:
    raw = json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False).encode()
    d = sha(raw)
    EV.mkdir(parents=True, exist_ok=True)
    (EV / f"{d}.json").write_bytes(raw)
    return f"sha256:{d}"


def file_ref(p: Path) -> dict:
    return {"path": str(p.relative_to(PAPER)), "sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict) -> dict:
    return {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
            "depends_on": depends, "evidence": blob({**ev, "for_claim": cid}), "audit": None}


def cite(key: str) -> dict:
    c = CIT[key]
    return {"kind": "citation", "claim": c["claim"], "citation_gate": {"rc": c["rc"], "stdout": c["stdout"]}, "note": GATE_NOTE,
            "gate_tool": "SocrateAI-Scientific-Elenchus/tools/citation_check.py"}


def remark(keys: list[str], what: str) -> dict:
    return {"kind": "argument", "text": what,
            "quotations": [{"key": k, "verbatim_in_source": CIT[k]["verbatim_in_source"], "source_id": CIT[k]["source_id"],
                            "source_sha256": CIT[k]["source_sha256"], "quote": CIT[k]["quote"]} for k in keys],
            "note": "remark/status sentences are not theorem-like, so the citation gate (theorem, lemma, proposition, corollary only) "
                    "cannot admit them to Tier L; the quotation is verified verbatim and the claim is filed at C"}


def arg(text: str, **kw: object) -> dict:
    return {"kind": "argument", "text": text, "source_note": file_ref(DATA / "FEASIBILITY.md"),
            "status": "human-style demonstration written by an AI agent; not machine-checked; no human has checked it", **kw}


def num(files: list[Path], **kw: object) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True,
            "instrument": "numpy/scipy Ewald summation and Sobol quasi-Monte Carlo (code/ewald3d.py, n1/n2/n3/n3b scripts), floating point",
            "files": [file_ref(p) for p in files], **kw}


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    n1, n2, n3, n3b = (CODE / f for f in ("n1_energies.json", "n2_voronoi.json", "n3_green_obstruction.json", "n3b_cubic.json"))
    scripts = [CODE / f for f in ("ewald3d.py", "n1_energies.py", "n2_voronoi.py", "n3_green_obstruction.py", "n3b_cubic.py")]
    claims = [
        # ----------------------------------------------------------------------------- Tier L (citation gate ACCEPTED)
        rec("B3-L-0001", "L", "citation",
            "Muratov-Novaga (arXiv:2610.29732v1), p. 4, Theorem 1: among Bravais lattices of covolume one the BCC lattice is the unique minimiser of the Born Coulombic energy E(L) = E(L, 1/2). "
            "Lattice-restricted; the non-periodic problem is not covered.", [], cite("mn_thm1")),
        rec("B3-L-0002", "L", "citation",
            "Muratov-Novaga (arXiv:2610.29732v1), p. 13, Proposition 6: the bisection terminates and covers the parameter rectangle by 46 414 closed boxes, each verified by one of four tests (R), (C), (B), (E).",
            [], cite("mn_prop6")),
        rec("B3-L-0003", "L", "citation",
            "Luo-Wei (arXiv:2610.31456v1), p. 2, Theorem 1.1 item (2): for the 3D Yukawa energy among lattices of covolume one and 0 < kappa < kappa_*, the BCC lattice is the unique minimiser. Lattice-only.",
            [], cite("lw_thm11")),
        rec("B3-L-0004", "L", "citation",
            "Rougerie-Serfaty (arXiv:1307.2805v5), p. 12, Theorem 1: for every dimension d >= 2 the infimum of the renormalized energy over A_1 is achieved and finite, with a periodic minimising sequence (for the energy W of their (2.16)-(2.17)).",
            [], cite("rs_thm1")),
        # ----------------------------------------------------------------------------- Tier C: literature remarks (verbatim, not gateable)
        rec("B3-C-0001", "C", "argument",
            "Blanc-Lewin (arXiv:1504.01153v2), section 2.6, p. 19: for d = 3 numerical simulations indicate BCC is the global minimiser of the Coulomb lattice energy as conjectured by Wigner, 'Proving this fact is still an open problem'; "
            "BCC -1.44423 and FCC -1.44415 (times rho^{1/3}); Lieb-Narnhofer prove e_Jell(rho) >= -1.4508 rho^{1/3}, an argument that 'is still an open problem' to close to BCC (quotation).",
            [], remark(["bl_open", "bl_ln"], "Status of the 3D Wigner crystallization problem, as reported by Blanc-Lewin (a survey).")),
        rec("B3-C-0002", "C", "argument",
            "Lewin (arXiv:2202.09240v2), Remark 19, p. 22: in d = 3 the Onsager-type constant is c1 = (3/5)(9 pi/2)^{1/3} ~ 1.4508, close to the conjectured best value 1.4442. The original Lieb-Narnhofer paper was not opened.",
            [], remark(["lewin_c1"], "The constant of the Lieb-Narnhofer / Sari-Merlini lower bound, as restated in Lewin's survey.")),
        rec("B3-C-0003", "C", "argument",
            "Aydin-Iacobelli (arXiv:2610.28547v1), p. 4: lattice results on the quantization problem do not settle Gersho's conjecture, 'which remains open for d >= 3'. The Kelvin/Weaire-Phelan, Barnes-Sloane, Choksi-Lu and HS26 statements "
            "are taken from that paper's text (p. 4-6) and are second-hand here.",
            [], remark(["ai_gersho"], "Gersho's conjecture is open in 3D, as stated by Aydin-Iacobelli.")),
        rec("B3-C-0004", "C", "argument",
            "Rougerie-Serfaty (arXiv:1307.2805v5), Remark B.2, p. 67: for d >= 3 the cutoff-based renormalized energy W of (2.16)-(2.17) 'may depend on the choice of cutoff', unlike d = 2; so the 2D statement 'for every field in A_1' has no verified 3D counterpart "
            "(the statement about the minimum transfers through Theorem 1, B3-L-0004).",
            [], remark(["rs_remark_b2"], "Caveat on step G1 (reduction to periodic configurations) in d >= 3.")),
        rec("B3-C-0005", "C", "argument",
            "Muratov-Novaga (arXiv:2610.29732v1): the relative BCC-FCC energy gap is 6.2e-5 (p. 3); Section 7 (p. 14) calls the non-periodic BCC problem 'a substantially harder three-dimensional crystallization problem'.",
            [], remark(["mn_gap", "mn_harder"], "Scale of the BCC-FCC gap and status of the non-periodic problem.")),
        rec("B3-C-0006", "C", "argument",
            "Hales-McLaughlin (arXiv:math/9811079v3), abstract only: the volume of a Voronoi polyhedron in a unit-ball packing is at least that of a regular dodecahedron of unit inradius. The dodecahedron is not a tiling cell, "
            "so this per-cell bound is not sharp at the optimal packing (our inference; ABSTRACT AND FIRST PAGE ONLY were read).",
            [], remark(["hm_abstract"], "Precedent for non-sharp per-cell bounds in 3D.")),
        # ----------------------------------------------------------------------------- Tier C: our arguments
        rec("B3-C-0010", "C", "argument",
            "Dual identity (3D transcription). Let h solve -Delta h = 4 pi (sum_p delta_p - 1) on a periodic configuration, W(h) = (1/8 pi) int^ren |grad h|^2 (unit density, per-particle units). For any trial H with the same 1/r singularities at the sites, u = h - H: "
            "int|grad h|^2 = int|grad u|^2 + 2 int grad h . grad H - int|grad H|^2, and int grad h . grad H = 4 pi (H_reg(0) - int H) by the equation for h. Hence W(h) = F(H) + (1/8 pi) int|grad(h - H)|^2 with "
            "F(H) = sum_cells [ -int H - (1/8 pi) int^ren |grad H|^2 ] (constant term of the singular expansion normalised to zero). F(H) <= W(h) for every admissible H, with equality iff H = h. "
            "The renormalisation bookkeeping at the sites is inherited from the 2D proof and is not re-derived here.",
            [], arg("Section 4.1 of the paper; FEASIBILITY.md G6.")),
        rec("B3-C-0011", "C", "argument",
            "Slack lemma. (i) Pointwise: if grad H(x) lies in a linear subspace N(x) for every H in the class, then |grad(h - H)|^2 >= |P_{N(x)^perp} grad h|^2 (Pythagoras; a linear subspace is all that is used); for H = H(r) this is the tangential gradient, for axial H(r, angle to n) it is (e_psi . grad h)^2. "
            "(ii) Isometry: if R is an isometry of a piece preserving the Dirichlet form and the singular part, and H = H o R, then (1 - R)(h - H) = (1 - R) h, and since ||(1 - R)/2|| <= 1 in the Dirichlet norm, "
            "||grad(h - H)|| >= ||grad (h - h o R)/2||. (iii) Squared Dirichlet distances add over pieces with disjoint interiors, and the maximum of two valid lower bounds is valid.",
            [], arg("Section 4.2; FEASIBILITY.md section 3, 'Lower-bound principle'.")),
        rec("B3-C-0012", "C", "argument",
            "Ceiling lemma. Suppose a method certifies, for every configuration to which the method applies (in the planar architecture: separated configurations, G13), F(H_conf) >= C N for trial potentials H_conf in a class K (so that the certified constant is C). Applied to the BCC torus, "
            "C <= F(H_bcc)/N = W_bcc - (1/8 pi) int|grad(h_bcc - H_bcc)|^2 <= W_bcc - inf_{H in K} slack(H). This does not use that BCC is the minimiser. BCC is separated (nearest-neighbour distance (sqrt(3)/2) 2^{1/3} ~ 1.091 > R ~ 0.620), so the lemma applies to it.",
            ["B3-C-0010"], arg("Section 4.3.")),
        rec("B3-C-0013", "C", "argument",
            "Why exact calibration works in 2D and fails for the 3D transcription. 2D: in each Voronoi sector h_tri = gamma(r) + sum_m c_m r^{6m} T_{6m}(d/t) because cos(6 m phi) = T_{6m}(d/t); so h_tri is a function of (r, t) only, lies in the sector ansatz class, and the square term is zero. "
            "3D: the axial ansatz H(r, theta) restricted to a face (r = t) is a function of t = sqrt(d^2 + rho^2) alone, hence constant on every circle of fixed in-face radius rho. If h_bcc is not constant on such a circle, then H != h_bcc and the square term is strictly positive. "
            "The 2D statement is the manuscript identity as audited in the P1 audit; it is not re-checked here.",
            ["B3-C-0019"], arg("Section 4.4.")),
        rec("B3-C-0014", "C", "argument",
            "Cell Euler identity. A convex polyhedron with f faces, e edges, v vertices has v - e + f = 2 and every vertex has degree >= 3, so 3v <= 2e, e <= 3f - 6, sum_F n_F = 2e <= 6f - 12, i.e. sum_F (6 - n_F) >= 12, with equality iff the cell is simple "
            "(every vertex of degree 3). For a simple cell sum_F (6 - n_F) = 12 exactly, whatever f is. (FCC rhombic dodecahedron: f = 12, e = 24, sum (6 - n_F) = 24.)",
            [], arg("Section 6.1; FEASIBILITY.md G4.")),
        rec("B3-C-0015", "C", "argument",
            "Transfer of the 2D incidence count (sketch). Give each in-face sector (face F, edge e) the weight K (3 theta'_e/pi - 1) with theta'_e the signed in-face angle at the foot. A face whose foot is inside sums to K (6 - n_F); a foot outside gives -K n_F >= K (6 - n_F) when K <= 0. "
            "Tiny faces at near-degenerate vertices force K <= 0 (J -> 0 while the weight stays fixed). So the count transfers with K <= 0 and uses only the identity B3-C-0014, after one extra step. Unlike 2D, the Euler inequality sum_F (6 - n_F) >= 12 points in the unfavourable direction for K <= 0 (non-simple cells such as those of fcc and hcp give 24 K). The transfer therefore uses an extra step: configurations with simple Voronoi cells are dense, and W_N is continuous on separated configurations, so it suffices to prove the bound for simple tessellations, on which sum_F (6 - n_F) = 12 exactly; the certificate domain must then include a margin below the separation distance (as the planar proof's b = 0.28209 < d_* does) to cover nearby perturbations. Not carried out in detail.",
            ["B3-C-0014"], arg("Section 6.1; FEASIBILITY.md G4.")),
        rec("B3-C-0016", "C", "argument",
            "Screened potential and separation in 3D. With R = (3/(4 pi))^{1/3} (ball of volume 1) and phi(x) = 1/|x| - 3/(2R) + |x|^2/(2R^3) on B_R: phi(R) = 1/R - 3/(2R) + 1/(2R) = 0, phi'(R) = -1/R^2 + 1/R^2 = 0, "
            "and -Delta phi = 4 pi delta - 3/R^3 = 4 pi (delta - 1_{B_R}) because 3/(4 pi R^3) = 1. By the same strict-minimum-principle argument as in 2D (r_* = 1/sqrt(pi)) this suggests separation >= R ~ 0.6204 and face distance >= R/2 ~ 0.3102 for a minimiser. "
            "The identities are checked by hand; the transfer of the minimum-principle step is asserted, not written out.",
            [], arg("Section 3 (step G3); FEASIBILITY.md G3.")),
        rec("B3-C-0017", "C", "argument",
            "Additive invariants of a simple cell. From v = 2f - 4 and sum n_F = 6f - 12: a f + b sum n_F + c v = (a + 6 b + 2 c) f - 12 b - 4 c, which is the same for all simple cells iff a + 6 b + 2 c = 0. So, besides volume and total solid angle, "
            "there is a one-parameter family of count weights (one free constant), i.e. three multipliers (lambda, mu, K) in total.",
            [], arg("Section 6.2; FEASIBILITY.md G9.")),
        rec("B3-C-0018", "C", "argument",
            "Calibration count (heuristic, NOT a theorem; it is the only argument against classes whose data are not invariant under the 60-degree rotation of the hexagonal pyramids, whatever their number of parameters). The truncated octahedron has 144 flags and the group O_h has order 48, so 3 flag orbits (assuming the action on flags is free); each in-face sector (face, edge) pairs two mirror flags, so there are 3 sector types: "
            "(square face, hex-square edge), (hex face, hex-square edge), (hex face, hex-hex edge). Piece-intrinsic data see 2 types (square, hex); neighbour data split the hex type in two. A per-piece affine bound tight at the optimum imposes, per type, three stationarity conditions "
            "and one equality, i.e. about 8 conditions (2 types) or 12 (3 types), against 3 multipliers. In 2D: 1 sector type, 2 stationarity conditions and 1 equality = 3 against 3. Hidden identities from the stationarity of W at BCC are not excluded.",
            ["B3-C-0017"], arg("Section 6.2; FEASIBILITY.md G9.")),
        rec("B3-C-0019", "C", "argument",
            "2D baseline as described by the openai/math preprint 'Triangular minimality for planar Coulomb renormalized energy' (AI-generated, not peer reviewed) and by our independent reproduction and audit (doi:10.5281/zenodo.23653827): "
            "reduction to square tori (SS2012), existence of a torus minimiser with separation, glued sector trial potential and dual identity, exact calibration at the triangular lattice, stationarity of two multipliers, a finite certificate. "
            "This paper takes the 2D proof as given (the audit found no gap in Sections 2-5) and did not re-read the manuscript ourselves at paper stage; the step descriptions follow FEASIBILITY.md section 2. An independent AI audit of this preprint re-read 04-calibration.tex (Lemmas cal:stationarity, cal:energy-identity, eq. cal:trial-potential) and found the description of G5-G9 accurate.",
            [], arg("Section 3; results/programmes/2026-10-25/P1/REDUCTION_AUDIT.md (not copied into this bundle).")),
        rec("B3-C-0020", "C", "argument",
            "Residual plan (a weaker target, not optimality). Prove by computer assistance a 3D jellium lower bound W >= W_bcc - delta* with delta* as small as the ceiling of B3-C-0012 allows, using the 3D dual identity with the axial ansatz. First lemma: the 3D torus pipeline "
            "(separation R, axial dual identity on flat tori of volume N, in-face signed-sector reduction to a three-variable primitive Gamma_{d,s}(x)). Falsification test, to run first: (1) optimise the axial radial data B, D_k to maximise the calibrated constant 12 K + lambda + 4 pi mu; "
            "(2) sample random in-face sectors (d >= 0.31, s and x arbitrary) and check that the piece inequality holds; (3) kill the plan if the best feasible constant does not beat the radial-only ceiling, i.e. if the angular modes add nothing. Not run.",
            ["B3-C-0012", "B3-C-0016"], arg("Section 7; FEASIBILITY.md section 6.")),
        rec("B3-C-0021", "C", "argument",
            "Certificate-size estimate under stated assumptions. 2D record: outer mesh about 2184 x 3611 nodes, Hessian mesh about 2.4e6 cells, global-derivative mesh about 4.2e5 rectangles, 72.6 s on 32 threads (about 2.3e3 core-s). "
            "Assumptions: (a) best case, exact axial pieces with a primitive in 3 variables; (b) margins scale with the relative gap of the nearest competitor, 8.0e-3 in 2D against 6.2e-5 in 3D (factor 129); (c) interpolation error proportional to h^2, so 11.4 times finer per dimension; "
            "(d) the same cost per node. Under (a)-(d): uniform mesh (2808 x 11.4)^3 ~ 3.2e13 nodes ~ 2e2 core-years; five parameters: ~ 3e22 nodes. Adaptive boxes (cf. 46 414 boxes in Muratov-Novaga) make 1e5-1e8 plausible IF a sharp piece inequality existed.",
            ["B3-C-0005"], arg("Section 8; FEASIBILITY.md section 5; 2D record from the manuscript's verification/data/certificate-record.txt as quoted in FEASIBILITY.md.")),
        # ----------------------------------------------------------------------------- Tier X
        rec("B3-X-0001", "X", "numeric",
            "Ewald jellium energies per particle at unit density (1/r Coulomb, uniform background; fcc-bcc gap computed from these energies, 8.969202e-5, and 2 x gap = 1.793840e-4 matches Muratov-Novaga's 1.7938403e-4): bcc -1.4442307515, fcc -1.4441410595 (gap 8.969e-5), hcp -1.4440838423 (gap 1.469e-4), sc -1.4186487397, A15 -1.4408630487, C15 -1.4284766566. "
            "Positive controls: independence of the Ewald splitting parameter to <= 9e-16; literature Madelung constants (Wigner-Seitz units) reproduced to 2.8e-13 (bcc, fcc, hcp) and 2.1e-9 (sc). Negative control: dropping the background term makes the result depend on the splitting parameter (spread 0.44).",
            [], num([n1] + scripts)),
        rec("B3-X-0002", "X", "numeric",
            "Periodic Voronoi statistics over 32 configurations (lattices, A15, C15, perturbed bcc/fcc/hcp, two Poisson samples): mean faces bcc 14, fcc 12, hcp 12, A15 13.5, C15 13.33, sc 6, perturbed fcc about 14, Poisson 15.5. "
            "Mean sum_F (6 - n_F) = 12 in 29 of the 32; fcc and hcp (non-simple cells) give 24 (negative control for the 'simple cell' hypothesis); one perturbed hcp run gave 11.9375, which is impossible for convex cells and is attributed (by us, not independently verified) to a near-degenerate-vertex merge at the 1e-7 tolerance. "
            "Second moment G: bcc 0.0785433 < A15 0.0787354 < fcc 0.0787451 = hcp < C15 0.0793381 < sc 0.0833333.",
            [], num([n2, CODE / "n2_voronoi.log"] + scripts)),
        rec("B3-X-0003", "X", "numeric",
            "Sanity checks on the bcc Green function h used in the slack bounds: finite-difference Laplacian off the sites 12.5656 against 4 pi = 12.5664; gradient against central differences, max deviation 9.0e-9; "
            "cubic-harmonic fit near the site gives regular constant C = -2.88847 against 2 x Madelung = -2.88846 (positive control), and the degree-4 coefficient c4 = -2.77 (bcc), -1.55 (fcc), +7.60 (sc).",
            [], num([n3, n3b] + scripts)),
        rec("B3-X-0004", "X", "numeric",
            "Face traces of h_bcc on circles of fixed in-face radius (rho/inradius = 0.3, 0.6, 0.9, i.e. fixed t): hexagonal face max-min = 8.9e-6, 5.7e-4, 6.6e-3, only azimuthal mode cos 6 psi (amplitude 3.3e-3 at 0.9), all other modes up to 8 below 7e-17; "
            "square face only cos 4 psi (5.9e-3 at 0.9) and cos 8 psi. So the trace is not a function of t alone.",
            [], num([n3] + scripts)),
        rec("B3-X-0005", "X", "numeric",
            "Lower bounds on the square term (1/8 pi) int |grad(h_bcc - H)|^2 per particle by Sobol quasi-Monte Carlo over the BCC cell (two seeds, 11 and 12): radial class 3.091e-3; axial class (max(pair-average bound, azimuthal bound) on hex pyramids plus azimuthal bound on square pyramids) 1.058e-4 (seed 11 1.0586e-4, seed 12 1.0576e-4); "
            "piece-intrinsic hierarchical class on hexagonal pyramids only 8.751e-5 (8.7547e-5, 8.7477e-5), about 300 standard errors from zero. Positive control: replacing h by the exactly radial Wigner-Seitz field gives <= 2.2e-30 for all bounds. "
            "The study's own control does not test the rotation convention of the pair-average bound (a radial field is invariant under any rotation). Independent-auditor result (AUDIT.md, auditor script /tmp/b3audit/ctl.py, not re-run by the writer; paper's own bounds_for_gradient, 2^16 Sobol points, seed 5, one hexagonal pyramid): R-invariant non-radial field (n.x)^3 + rho^4: hierarchical 5.4e-35, axial 3.9e-36 (full Dirichlet 1.28e-3); cos 6 psi: hierarchical 3.0e-37, axial 2.8e-7; cos 3 psi (odd under R): hierarchical 1.29994e-4 = its full Dirichlet energy 1.29994e-4, as predicted; the rotation convention in the code is correct.",
            [], num([n3, CODE / "n3_green_obstruction.log"] + scripts)),
        rec("B3-X-0006", "X", "numeric",
            "Consequence (ceilings, B3-C-0012 evaluated with B3-X-0005): any certified constant from a trial class that is radial, axial or piece-intrinsic hierarchical (hexagonal pyramids) satisfies C <= W_bcc - 3.09e-3 (radial), C <= W_bcc - 1.06e-4 (axial), C <= W_bcc - 8.75e-5 (hierarchical). "
            "Scale: 8.75e-5 is 0.98 x and 1.06e-4 is 1.18 x the fcc-bcc gap (8.969e-5), and 0.72 x the hcp-bcc gap for the axial one; the radial ceiling is 34.5 x the gap. None of these is zero, which is what kills exact calibration. "
            "Square pyramids are not used in the hierarchical bound (a larger bound is expected).",
            ["B3-C-0011", "B3-C-0012", "B3-C-0013", "B3-X-0004", "B3-X-0005"], num([n3] + scripts)),
        rec("B3-X-0007", "X", "numeric",
            "2D reference: the radial-class slack for h_tri (series of the manuscript, 400000 Monte Carlo points) is 1.85e-3, which is 0.056 x the 2D square-minus-triangular gap 0.03325; the 2D sector class has slack 0 by the manuscript identity "
            "(a constant in the script, not a computed value; see B3-C-0019). The 2D lattice energies are typed constants; the 2D reference is plain Monte Carlo with no standard error (MC hexagon area 1.0011).",
            [], num([n3] + scripts)),
        rec("B3-X-0008", "X", "numeric",
            "Residual-plan scale: the radial ceiling W_bcc - 3.09e-3 = -1.4473 is above the Lieb-Narnhofer value -1.4508 by 3.5e-3 (the LN gap to BCC is 6.6e-3), so a radial-class calibration could in principle improve on LN by at most about 3.5e-3, "
            "and the axial class leaves at most 1.06e-4 from BCC; these are ceilings on what the method could deliver, not bounds that we have obtained.",
            ["B3-X-0006", "B3-C-0001"], num([n3, n1])),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": claims}, indent=1, ensure_ascii=False))
    print(f"claims {len(claims)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
