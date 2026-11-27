# MA-1 prior-art screen (2026-11-11): FCC vs BCC, Yukawa and Gaussian, 3D

## VERDICT: NOT NEW. Item ends with this record (kill criterion of MA-1 met). No PREREG_DRAFT.md.

The statement MA-1 proposed to certify was published 3 weeks before this screen, with computer-assisted
interval arithmetic and a proof of uniqueness among ALL 3D Bravais lattices.

## Evidence (READ = I read the passage in the full text via alphaXiv; SECONDARY = snippet/abstract only)

1. READ. Luo and Wei, "On exact solutions to three-dimensional Yukawa lattice model and BCC to FCC phase
   transitions", arXiv:2610.31456 (math.AP, 22 Oct 2026, v1, not yet refereed).
   - Theorem 1.1: unit covolume, E_kappa(L) = (1/2) sum_{v != 0} e^{-kappa|v|}/|v|. There is a unique
     kappa* in (0, sqrt(pi)) with E(L_B) = E(L_F). BCC is the unique minimiser among ALL lattices for
     kappa < kappa*, FCC the unique minimiser for kappa > kappa*, exactly these two at kappa*.
     Density rho: transition at kappa = rho^{1/3} kappa* (their eq. 1.6).
   - kappa* = 1.71792186846990 (abstract/Thm 1.1); appendix (A.9): 1.717921868469903 < kappa* < 1.717921868469904.
     Units: unit covolume (NOT Wigner-Seitz). Convert: a_ws = (3/(4 pi))^{1/3}, so kappa_ws = kappa* a_ws = 1.7179219 * 0.62035 = 1.0657, i.e. the
     published "Madelung crossover 1.066" (see 4). The "1.72" in the task prompt is the unit-covolume value, not the Wigner-Seitz one.
   - Method: Gaussian (Laplace) representation + Poisson/Ewald split; kappa* is the root of eq. (1.4), an integral
     of (Theta_B - Theta_F) against an explicit kernel; local-global argument (Bernstein-coefficient bounds on shape
     rectangles, 1000 FCC / 25 BCC intervals), outward interval enclosures at 128/256/512 bits (MPFR). Certificate
     "accompanies the manuscript" (not checked by me). Corollary 1.1 recovers Muratov-Novaga BCC optimality at kappa -> 0.
   - This covers the "among all lattices" question (the 5-dim shape space) rigorously, not only FCC vs BCC.
2. READ. Luo and Wei, "On Sarnak-Stromberggson conjecture", arXiv:2609.17356 (math.NT, 15 Sep 2026, v1).
   Gaussian: Theta(alpha, L) = sum e^{-pi alpha |v|^2}, covolume 1: argmin = FCC for alpha > 1, BCC for alpha < 1,
   FCC or BCC at alpha = 1; Epstein zeta argmin = FCC for all s > 3/2. This proves the Sarnak-Stromberggson
   conjecture (SS, Invent. Math. 165 (2006) 115-151, inequalities (43)-(44), Sec. 5; SECONDARY for the SS paper itself).
   The Gaussian crossover is EXACT, not a number to enclose: Theta_B(t) = t^{-3/2} Theta_F(1/t) by Poisson
   summation (L_B = L_F^*), so the two coincide at t = 1 (trivial arithmetic, no compute needed).
3. READ (open problem only). Deng and Luo, arXiv:2610.35437 (26 Oct 2026): Open Problem 1.1 asks for the 3D phase
   diagram of theta(alpha) - b theta(beta) (two competing Gaussians) among 3D lattices; it is stated as OPEN there.
   Cohn-Kumar-Schurmann (numerical Gaussian core ground states, formal duality) and Cohn-de Courcy-Ireland
   (Duke 2018, high-dimensional bounds) are cited there (SECONDARY).
4. SECONDARY (snippets). Hamaguchi-Farouki-Dubin, Phys. Rev. E 56, 4671 (1997) "Triple point of Yukawa systems" and
   PRE/JCP 1996: at T = 0 the BCC Madelung energy is below FCC for kappa_ws < 1.066 (Wigner-Seitz units); Hoy-Robbins,
   PRE 69, 056103 (2004), arXiv:cond-mat/0401045: strain method, ~1% uncertainty. Robbins-Kremer-Grest, J. Chem. Phys.
   88, 3286 (1988). No rigorous bounds there (physics numerics). Gaussian core: Prestipino-Saija-Giaquinta (PRE 71,
   050102 (2005), arXiv:cond-mat/0506012) and Stillinger 1976: FCC at low density, BCC at higher density, at finite T
   and T = 0 (FCC-BCC lines start at rho* ~ 0.1794/0.1798 at T* = 0; exponent/units of their model, not converted). SECONDARY.
5. SECONDARY. Muratov-Novaga arXiv:2610.29732 (21 Oct 2026): BCC uniquely minimises renormalised 3D Coulomb energy
   among Bravais lattices (kappa -> 0 limit). Already cited in our B3 paper (papers/p2_3d_feasibility/main.tex, cid L-0001/L-0003).
   Betermin 2D completely-monotone extension (hexagonal) cited in item 3.

## What is and is not covered

- Covered rigorously (computer-assisted, preprint): Yukawa FCC/BCC crossover to 15 digits and global optimality over all 3D
  Bravais lattices, single crossing. Gaussian: exact, analytic crossover, global minimiser over all lattices.
- Not covered anywhere (open): non-lattice (point-set) optimality in 3D; universal optimality is unknown in 3D
  (only E8 and Leech: Cohn-Kumar-Miller-Radchenko-Viazovska); two-Gaussian 3D diagram (Open Problem 1.1 above).
  A certified computation over lattices can only claim Bravais-lattice statements, never "among all configurations".

## Residual value (small; owner decides, NOT recommended as MA-1)

(a) Independent re-verification of Luo-Wei's Yukawa certificate (producer != verifier): confirm kappa* digits with python-flint
    (flint 0.9.0 is importable in system python3; NOT in .venv) in minutes of CPU. Value = audit note, not a discovery.
(b) A Lean statement of E_B < E_F for fixed kappa < kappa* (and >), tier A, would be new as a formalisation but needs the
    Gaussian theta ordering (the hard part of their paper, Sec. 4-5) and is far beyond a one-day item; the cheap fixed-parameter
    comparison needs rigorous infinite-sum tails in Lean. Low priority.
(c) Genuinely open and adjacent: Open Problem 1.1 (2-Gaussian 3D phase diagram) or a Lennard-Jones/other non-CM family; would be a new MA item
    requiring its own screen (the same authors are active, scooping risk high).

Caveat: the Luo-Wei papers are single-version arXiv preprints, unrefereed, and I did not run their certificates.
alphaXiv excerpts were saved as files; only abstract, intro, theorem statements and appendix A.9 lines were read, not the full proofs.
