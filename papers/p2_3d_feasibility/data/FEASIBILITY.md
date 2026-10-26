# B3: can the 2D Sandier–Serfaty proof architecture reach 3D jellium (bcc)?

Date 2026-10-26. Preregistered item B3 (`../preregistration.json`). The priors were credible_plan 0.15 and proof 0.02.

This is a feasibility study, not a proof.

**Tiers.**
- **A**: an elementary inequality, stated with its proof sketch. It is not kernel-checked.
- **L**: literature, read through alphaXiv on 2026-10-26, with the arXiv id and page.
- **C**: our own argument or conjecture, not checked.
- **X**: our floating-point numerics, with positive and negative controls. Scripts and JSON are in `numerics/`.

**Subject.** The openai/math preprint "Triangular minimality for planar Coulomb renormalized energy" (2026-09-23; build/sections 01–08, verification/). It is AI-generated and not peer reviewed. Our P1 audit of it is `results/programmes/2026-10-25/P1/REDUCTION_AUDIT.md`. That audit found no gap in Sections 2–5, and that the certificate reproduces. B3 takes the 2D proof as given and asks only whether its architecture transfers.

## 0. Verdict (short)

**This is a reasoned negative for proving bcc optimality with this architecture.** The decisive step is the **exact calibration (zero square term) with low-dimensional, universally glued pieces**.

- **Why it works in 2D.** In each Voronoi sector the triangular Green function is a function of (r, t) only, by the Chebyshev identity cos(6mφ) = T_6m(d/t). This is what makes ½∫|∇(h−H)|² = 0 at the optimum (manuscript §4.2, Lemma cal:energy-identity).
- **Why it fails in 3D.** A point of a face at fixed t lies on a circle, and h_bcc varies on it. Its trace on the hexagonal face carries a cos 6ψ mode, and on the square face a cos 4ψ mode (X, §3).
- **Axial slack.** The literal 3D transcription of the sector ansatz (axial about each face normal) has a forced square term of at least **δ_axial ≥ 1.059e-4 per particle**. That is **1.18× the fcc−bcc gap** (8.969e-5) and 0.72× the hcp−bcc gap. So the axial architecture cannot even certify W ≥ W_fcc, let alone W ≥ W_bcc.
- **Hierarchical slack.** The richer ansatz, with in-face sectors and piece-intrinsic data only, still has a forced slack of at least **8.75e-5 ≈ 0.98× the gap**, from the hexagonal pyramids alone (X; the lower-bound inequalities are A).
- **Calibration count.** An exact ansatz must carry neighbour data. For it, the per-piece affine calibration is overdetermined at bcc: about 12 conditions (3 piece types) for 3 multipliers, against 3 for 3 in 2D (C).
- **Strength of the negative.** It is rigorous (A inequalities plus X numerics) for every piece-intrinsic ansatz with 4 or fewer parameters. For richer ansätze carrying neighbour data, it rests on the Tier C counting argument G9 and is not a theorem.
- **What remains open in 3D.** The cell-local relatives of the problem are open (Gersho's 3D conjecture) or false (Kelvin's conjecture, refuted by Weaire–Phelan) (L).

**The incidence count is *not* the failing step.** This corrects the naive expectation. 3D has an exact per-cell Euler identity, Σ_F(6 − n_F) = 12 for every simple Voronoi cell (A). We verified it on 33 configurations (X). It provides a usable count weight (§2, step G4).

**Residual credible plan.** Do not aim at optimality. Aim at a 3D analogue of the dual-identity lower bound: a computer-assisted improvement of Lieb–Narnhofer (−1.4508) towards bcc (−1.44423). The ceiling of the axial architecture is W ≥ W_bcc − δ with δ ≥ 1.06e-4. The first lemma and the falsification test are in §6.

Against the priors: the outcome is "no credible plan for a proof, a credible plan for a weaker bound". That is consistent with credible_plan 0.15 for the optimality question, and below it.

## 1. Literature (L, verified 2026-10-26 via alphaXiv)

| Ref | What it actually states (page) | Role here |
|---|---|---|
| Muratov–Novaga, arXiv:2610.29732v1 | Thm 1, p.4: bcc uniquely minimizes E(L) = Z(L,½) **among Bravais lattices** of covolume 1. The proof is computer-assisted (Ewald positivity, a 5D Iwasawa rectangle, a certified Hessian near the fcc dual) with **46 414 boxes** and smallest margin 5.1e-12 (Prop 6, p.13). The relative bcc–fcc gap is 6.2e-5 (p.3). §7, p.14 calls non-periodic bcc optimality "a substantially harder three-dimensional crystallization problem". | Lattice-restricted result. Calibration scale for a certificate. |
| Luo–Wei, arXiv:2610.31456v1 | Thm 1.1: for 3D Yukawa among **Bravais lattices**, bcc is the minimizer for κ < κ* ≈ 1.7179218684699 and fcc for κ > κ*. Cor 1.1 recovers Muratov–Novaga at κ→0. | Lattice-only. |
| Blanc–Lewin, arXiv:1504.01153v2 (EMS Surv. Math. Sci. 2 (2015) 255–306) | §2.6, p.19: proving bcc in 3D "is still an open problem". Lieb–Narnhofer [J. Stat. Phys. 12 (1975) 291] prove e_Jell ≥ −1.4508 ρ^{1/3}, against bcc −1.44423, fcc −1.44415, sc −1.41865. | Status, and the best simple bound. |
| Lewin, arXiv:2202.09240v2 (J. Math. Phys. 63 (2022) 061101) | Remark 19, p.22: Lieb–Narnhofer / Sari–Merlini constant c₁ = (3/5)(9π/2)^{1/3} ≈ 1.4508 in d=3, from Onsager's lemma and Newton's theorem with balls. Rougerie–Serfaty, CPAM 69 (2016) 519–605 is ref. 424; Petrache–Serfaty, JIMJ 16 (2017) 501 is ref. 405. Graf–Schenker are refs 223 and 224 (Lett. Math. Phys. 35 (1995) 75; Commun. Math. Phys. 174 (1995) 215–227, "On the molecular limit of Coulomb gases"). | 3D analogue of the reduction step. We **did not read** the Graf–Schenker text; only the bibliographic data is verified. |
| Aydın–Iacobelli, arXiv:2610.28547v1 | p.1 and p.4: Gersho's conjecture "remains open in dimensions higher than two". Barnes–Sloane (1983) prove bcc optimal among lattice quantizers. The paper itself proves only **local** optimality of bcc under small periodic C¹ perturbations. p.4 cites Choksi–Lu [CL20], a 3D strategy modelled on Gruber's proof of Fejes Tóth, with only partial results. p.5–6: the Kelvin conjecture (bcc foam) was refuted by Weaire–Phelan; Weaire–Phelan is worse than bcc for quantization [KN01, SV02]; the lattice (translative) truncated-octahedron conjecture was proved in 2026 [HS26, arXiv:2609.00997]. | The cell-local analogue of the 2D Fejes Tóth/Gruber step is open in 3D. |
| Hales–McLaughlin, arXiv:math/9811079 | The dodecahedral conjecture: the Voronoi-cell volume in a unit-ball packing is at least the volume of the regular dodecahedron, which is **not** a tiling cell. | Precedent: the per-cell bound is not sharp for the 3D optimum (fcc). Kepler needed Hales' hybrid decomposition. Title and abstract only were read. |

## 2. Step-by-step decomposition of the 2D proof

| # | 2D step (manuscript ref) | Class | 3D status |
|---|---|---|---|
| G1 | Reduction from the plane to square tori: SS2012 Thm 1, Lemma 4.7, Prop 4.9 (§2) | **Needs a 3D analogue (exists for the smeared energy)** | Rougerie–Serfaty, arXiv:1307.2805v5 (CPAM 69 (2016)), Thm 1, p.12: α_d = inf_{A₁} 𝕎 is achieved and finite, with a periodic minimizing sequence. Prop 5.9, p.50 adds hyperrectangle periods. This holds for the *smeared* (Onsager) energy 𝕎 in every d ≥ 2 (L). **Caveat:** their Remark B.2, p.67 says the cutoff-based W, which is what the 2D proof's reduction uses, "may depend on the choice of cutoff" for d ≥ 3, and Prop B.1 (W = 𝕎) is proved only for d = 2. So the 2D statement "for *every* field in A₁" has no verified 3D counterpart. The statement about the minimum transfers through Thm 1 together with Prop B.3, which gives the periodic energy formula in all d. |
| G2 | Existence of a torus minimizer; pair-energy representation (Lemma geo:existence) | Dimension-agnostic | The 3D Green function on T³ is bounded below. The argument is the same. |
| G3 | Separation through a screened potential and the strict minimum principle (Lemma geo:separation, r* = 1/√π) | Dimension-agnostic | φ(x) = 1/\|x\| − 3/(2R) + \|x\|²/(2R³) on B_R with R = (3/4π)^{1/3}, so the ball has volume 1. Value and gradient vanish at R, and −Δφ = 4π(δ − 1_{B_R}). The same proof gives separation ≥ R ≈ 0.6204, hence face distance d ≥ 0.3102 (A, sketch). |
| G4 | Incidence count ≤ 6n sectors (Euler on T², 3V ≤ 2E) times a sector constant K < 0 (Lemma geo:voronoi) | **Needs a 3D analogue (exists, stated here)** | Per *cell*: Euler v − e + f = 2 and 3v ≤ 2e give Σ_F(6 − n_F) ≥ 12, with equality iff the cell is simple (A). Generic configurations are dense and W_n is continuous, so one may restrict to simple tessellations. Then Σ_F(6 − n_F) = 12 exactly per cell. Give each in-face sector (face F, edge e) the weight K(3θ'_e/π − 1), where θ'_e is its signed in-face angle at the foot. A face whose foot is inside sums to K(6 − n_F); a foot outside gives −K·n_F ≥ K(6 − n_F) when K ≤ 0. Tiny faces created near degenerate vertices force K ≤ 0, since J → 0 while the weight stays fixed. So the count transfers with K ≤ 0, as in 2D (C). The face count f itself is unconstrained: in X it is 13.33 (C15), 13.5 (A15), 14 (bcc and small perturbations of fcc and hcp), up to 14.22 (perturbed fcc), and 15.5 (Poisson). That is why the weight must be Euler-type and not a per-face constant. |
| G5 | Gluing of H = B(r) + Σ(r/t)^k D(t) (Lemma dual:gluing) | Dimension-agnostic, for the *axial* ansatz | Ray-wise in 3D, t(ω) = d/(n̂·ω). On a face r = t, and both sites see the same t. On the (site, cell-edge) interfaces both pyramids hit the same edge point, so t agrees. H¹ gluing goes through. |
| G6 | Dual identity W = ΣJ(S) + ½∫\|∇(h−H)\|² (Prop dual:identity) | Dimension-agnostic | Green's identity with 1/r singularities and a zero constant term. Normalization: W = Σ[−∫H − (1/8π)∫^ren\|∇H\|²] + (1/8π)∫\|∇(h−H)\|². |
| G7 | Sector integral → primitive g_d(x) in 2 variables (cal:angle-density, cal:sector-primitive) | **Needs a 3D analogue** | With an axial H, J(pyramid) = ∫_F G₃(d,\|y−m\|) dA over the face polygon. Splitting into in-face sectors and integrating radially gives a 1D primitive Γ_{d,s}(x) in **3** variables (d, s, x), with signed in-face endpoints handled as in Lemma dual:signed-endpoints (C). |
| G8 | **Exact calibration on the optimal cell: H = h_opt, square term zero** (Lemma cal:energy-identity, via cos kφ = T_k(d/t)) | **Genuinely 2D: FAILS** | This is the decisive step (§3). |
| G9 | Stationarity: λ, μ solve the 2 stationarity equations at the single sector type (Lemma cal:stationarity) | **Genuinely 2D (counting)** | The hexagon has 12 flags under D6 (order 12), so 1 flag type. The truncated octahedron has 144 flags under O_h (order 48), so 3 orbits (C). With piece-intrinsic data the parameter points are 2 (square in-face sector, hex in-face sector), each needing ∂_d, ∂_s, ∂_x = 0 plus an equality: 8 conditions. With the neighbour data that exactness requires (§3), the two hex orbits (hex–hex edge vs hex–square edge) become distinct pieces: 3 types, about 12 conditions. The multipliers are λ (volume), μ (solid angle) and K (Euler weight); those are the only additive invariants with fixed per-cell totals (A: any count combination a·f + b·Σn_F + c·v is invariant iff a + 6b + 2c = 0, which leaves one free constant). That is 8–12 vs 3, against 3 vs 3 in 2D. A per-piece affine bound tight at bcc is generically impossible (C: this is a counting heuristic; hidden identities from the stationarity of W at bcc are not excluded). |
| G10 | Hexagon optimality behind the scalar bounds (Fejes Tóth/Gruber pattern, ≤ 6 sides on average) | Genuinely 2D | The 3D cell-local analogues: Gersho's conjecture is open (Aydın–Iacobelli p.4). The Kelvin cell is beaten by Weaire–Phelan. The dodecahedral bound (Hales–McLaughlin) is not sharp at fcc. X: G is lowest at bcc among our tilings (0.0785433, then A15 0.0787354, fcc/hcp 0.0787451, C15 0.0793381), so quantization does not refute bcc, but it is a *different* functional. |
| G11 | Tails / lattice sums (§5) | Needs a 3D analogue (routine) | Cubic harmonics replace z^{6m}. The ℓ = 4 coefficient is nonzero (X: c₄ = −2.77 for bcc, −1.55 for fcc, +7.60 for sc). |
| G12 | Finite certificate on the (d, x) rectangle with a Hessian at the stationary point (§6) | Needs a 3D analogue | Size in §5. It is not the binding constraint. |
| G13 | Separation used only for the minimizer; the bound then extends to all configurations by minimality | Dimension-agnostic | — |

## 3. The decisive step: exact calibration fails (X, with an A-level inequality)

**Lower-bound principle (A).** Let 𝓗 be the class of admissible trial H. Let 𝓥 ⊇ 𝓗 be a closed subspace of H¹(cell minus the site) that is invariant under a group of isometries of each piece, or defined by ∂_ψ H = 0. Then ½∫\|∇(h−H)\|² ≥ ½ dist(h, 𝓥)², computed with an orthogonal projection or a group average. Three classes, at the bcc torus (unit density, per-particle units, 1/r Coulomb):

The classes are nested: radial ⊂ axial ⊂ hierarchical. An axial H is rotation-invariant about n̂, so on a regular-hexagon pyramid it is D6-invariant. A larger class has smaller or equal slack. Squared distances add over disjoint pyramids. Hence:

| Trial class | Valid lower bound used | Forced square term ≥ | / (fcc−bcc = 8.969e-5) |
|---|---|---|---|
| radial H(r) in each cell (Lieb–Narnhofer-like) | tangential gradient | 3.09e-3 (MC s.e. 9e-6) | 34× |
| **axial** H(r, angle to the face normal): the literal 2D ansatz | max(D6 bound 8.75e-5, azimuthal 3.74e-5) on hex pyramids + azimuthal 1.83e-5 on square pyramids | **1.059e-4** | **1.18×** |
| in-face hierarchical, piece-intrinsic data only (6 congruent hex in-face sectors force D6 invariance; h_bcc in the hex pyramid is only C3v) | D6 group average, hex pyramids only | 8.75e-5 (s.e. 2.9e-7) | 0.98× |
| 2D reference: radial H for h_tri, against the 2D square−triangle gap 0.03325 | tangential gradient | 1.85e-3 | 0.056× |
| 2D reference: the sector ansatz | — | 0 exactly (manuscript §4.2) | 0 |

The azimuthal-only bound (ê_ψ·∇h)², summed over all 14 pyramids, is 5.574e-5. It is weaker than the combined bound and is reported for completeness. The numbers are from Sobol replicate seed 11; seed 12 agrees to about 1e-7 (see the JSON).

**Face traces (X).**
- On the hexagonal face, at fixed t, h_bcc varies by 8.9e-6, 5.7e-4 and 6.6e-3 at ρ/inradius = 0.3, 0.6 and 0.9. Its only Fourier content is cos 6ψ (amplitude 3.3e-3 at 0.9). Every other mode up to 8 is below 1e-16.
- The 6-fold symmetry on the face follows from inversion through the face centre combined with C3.
- On the square face the only modes are cos 4ψ (5.9e-3) and cos 8ψ.
- So the trace is not a function of t alone. That kills the axial ansatz.
- The face trace *is* representable by an in-face Chebyshev ansatz. The leftover obstruction for the hierarchical class is the C3v-only interior of the hex pyramid. Removing it needs piece data from the neighbouring faces (hex–hex vs hex–square edges, dihedral angles 109.47° vs 125.26°).

**Consequence (C).**
- Exactness at bcc requires pieces carrying at least (d, s, x, plus adjacent-edge data): 5 or more parameters, against 2 in 2D.
- Even then, the multiplier count G9 is overdetermined.
- An axial 3D transcription can prove at best W ≥ W_bcc − δ with δ ≥ 1.06e-4. That lies below W_fcc, so it can never give bcc optimality, nor even exclude energies between bcc and fcc.

## 4. Per-cell comparisons (X): the Kelvin/Weaire–Phelan warning made concrete

Ewald energies per particle at unit density. Controls passed:
- Positive: α-independence to 1e-15; literature Madelung constants reproduced to 2e-13 (bcc, fcc, hcp) and 2e-9 (sc); Muratov–Novaga's 2·Madelung = −2.888461503 reproduced as the regular part of h.
- Negative: dropping the background term gives an α spread of 0.44.

| Config | e/particle | above bcc | mean faces | ⟨Σ(6−n_F)⟩ | G (2nd moment) |
|---|---|---|---|---|---|
| bcc | −1.4442308 | 0 | 14 | 12 | 0.0785433 |
| fcc | −1.4441411 | 8.97e-5 | 12 (non-simple) | **24** (negative control) | 0.0787451 |
| hcp | −1.4440838 | 1.47e-4 | 12 (non-simple) | 24 | 0.0787451 |
| A15 (Weaire–Phelan) | −1.4408630 | 3.37e-3 | 13.5 | 12 | 0.0787354 |
| C15 | −1.4284767 | 1.58e-2 | 13.33 | 12 | 0.0793381 |
| sc | −1.4186487 | 2.56e-2 | 6 | 12 | 0.0833333 |
| fcc perturbed (rms 0.002) | −1.44412 | 1.1e-4 | 14.0 | 12 | 0.078746 |
| Poisson (N=400) | −0.19 / −0.35 | — | 15.5 | 12 | 0.114–0.116 |

The table shows four things:
1. bcc is not extremal in face count, so no f-based count can be sharp at bcc.
2. The Euler weight is exactly 12 for every simple cell. One run, hcp perturbed at rms 0.002 seed 1, gave 11.94: that is a near-degenerate-vertex merge artifact of the 1e-7 tolerance and is impossible for a convex cell.
3. Weaire–Phelan cells (A15), which win the Kelvin surface-area problem, lose in jellium energy by 3.4e-3 and in quantization by 1.9e-4 in G. So the jellium question does not inherit Kelvin's counterexample.
4. A per-cell functional sharp at bcc must nonetheless separate cells differing by 6e-5 relative. That is the cell-local problem the 2D proof solved with the hexagon/Euler pattern, and it is open in 3D even for the second moment (Gersho).

## 5. Certificate size under the 2D method's scaling (C, explicit assumptions)

**2D record** (verification/data/certificate-record.txt, 06-computation.tex):
- Outer mesh: D_h ≤ 1.9e-4 over d ∈ [0.282, 0.697] and S_h ≤ 1.8e-4 over s ∈ [0, 0.65], about 2184 × 3611 ≈ **7.9e6 nodes**.
- Hessian mesh: about 600 × 4078 ≈ **2.4e6 cells**.
- Global derivative mesh: about 4.2e5 rectangles.
- 39 modes; worst margin 1.2e-5 against \|K\| = 3.5e-3.
- 72.6 s on 32 threads, about 2.3e3 core-s, so about 2e-4 core-s per node.

**Assumptions.**
- (a) Best case: the axial 3D pieces were exact, giving a primitive in 3 variables (d, s, x).
- (b) Margins scale with the relative gap of the nearest competitor: 2D 8.0e-3 (square), 3D 6.2e-5 (fcc), a factor of 129.
- (c) Interpolation error ∝ h², so h ∝ √margin, 11.4× finer per dimension.
- (d) Same per-node cost, which ignores the larger cubic-harmonic channel count.

**Estimates.**
- Uniform mesh: (2808 × 11.4)³ ≈ (3.2e4)³ ≈ **3e13 nodes**, ≈ 7e9 core-s ≈ **200 core-years**.
- An exact ansatz needs 5 or more parameters: (3.2e4)⁵ ≈ **3e22 nodes**, which is infeasible uniformly.
- Adaptive second-order boxes, as in Muratov–Novaga (46 414 boxes in 5D at the same relative gap), suggest 1e5–1e8 boxes is plausible for a 3–5 parameter piece inequality, if such an inequality were true.

So size is **not** the binding constraint. Existence of a sharp piece inequality is (G8, G9).

## 6. Conclusion

**Negative (for bcc optimality).** The architecture "glued low-dimensional sector ansatz + exact calibration + per-piece affine bound + Euler count" fails in 3D at G8.
- No axial or piece-intrinsic H reproduces h_bcc. The forced slack is ≥ 1.06e-4 per particle (axial, 1.18× the fcc−bcc gap) and ≥ 8.75e-5 (in-face hierarchical, 0.98×).
- This part is rigorous, as an A-level inequality plus X numerics, for piece-intrinsic ansätze with 4 or fewer parameters.
- Repairing G8 needs pieces carrying neighbour data: 5 or more parameters, still a piece problem, not yet a whole-cell one.
- For those richer pieces, G9 says the per-piece affine calibration has about 12 conditions for 3 multipliers. That is a Tier C counting argument, not a theorem.
- If the per-piece bound is abandoned entirely, the problem becomes a cell-level comparison. Its closest studied relatives are Gersho's 3D conjecture (open) and Kelvin's (false).

**Residual plan (a weaker target; Tier C).** Use the 3D dual identity with the axial ansatz to prove a computer-assisted lower bound W ≥ −1.4442308 − δ*, with δ* as small as possible.
- The ceiling is δ* ≥ 1.06e-4, against Lieb–Narnhofer's 6.6e-3 gap: up to about 60× sharper than LN, and still far from optimality.
- What the angular machinery adds must be measured against the radial-only ceiling, W_bcc − 3.09e-3 ≈ −1.4473. That ceiling already beats LN, and in principle is reachable without any angular data.

- **First lemma:** the 3D torus pipeline G2 + G3 + G5 + G6 on paper (separation R = (3/4π)^{1/3}; the axial dual identity on arbitrary flat tori with volume = N), plus the in-face signed-sector reduction G7 to Γ_{d,s}(x).
- **Falsification test, run first:**
  1. Optimize the axial radial data B, D_k to maximize the calibrated constant 12K + λ + 4πμ.
  2. Then sample random in-face sectors (d ≥ 0.31; s, x arbitrary) and check that the piece inequality holds.
  3. Kill the plan if the best feasible constant does not beat the radial-only ceiling of about −1.4473, i.e. if the angular modes add nothing.
- Secondary target: δ* < 6.6e-4, which is 10× better than LN.

## 7. Files

- `numerics/ewald3d.py`: Ewald energy, potential and gradient; structures; periodic Voronoi.
- `numerics/n1_energies.py` → `n1_energies.json`: lattice energies and controls.
- `numerics/n2_voronoi.py` → `n2_voronoi.json`, `n2_voronoi.log`: face counts, Euler weight, G, separations, perturbed and Poisson configurations.
- `numerics/n3_green_obstruction.py` → `n3_green_obstruction.json`: radial, axial and hierarchical slack bounds, face traces, Laplacian and gradient checks, 2D reference.
  - The final run (cited above) reproduces c₄ = −2.769 and C = −2.88847 against 2·Madelung = −2.88846.
  - Combined axial bound: 1.0586e-4 (seed 11) and 1.0576e-4 (seed 12). WS radial control: about 1e-30.
  - `n3_run1_pre_signfix.json` is kept as history. It came from an earlier run with an r²-sign error in the cubic fit and the control field, and without the combined axial bound; its slack bounds agree with the final run.
- `numerics/n3b_cubic.py` → `n3b_cubic.json`: cubic-harmonic coefficient c₄ and the regular part, against 2·Madelung.
- Compute: cores 6–7, 2 threads; total about 45 min of wall time.
