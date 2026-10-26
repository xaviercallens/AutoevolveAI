# P1 S2: adversarial audit of the reduction in "Triangular minimality for planar Coulomb renormalized energy"

Date 2026-10-25. Subject: the openai/math preprint `Triangular-minimality-for-planar-Coulomb-renormalized-energy-September-23-2026` (AI-generated, not peer reviewed), which says it proves the Sandier-Serfaty conjecture (SS2012 Conjecture 1) and, through Betermin-Sandier, the d=2 case of Brauchart-Hardin-Saff Conjecture 4.

**What this file is.** It is an agent audit, tier C: a human-style argument check done by an agent, not machine-checked. The constant checks in the scripts below are X-exact (exact rational arithmetic that we ran). The float cross-checks are tier X. The S1 certificate reproduction (WORK1) is an exact-integer interval computation that we re-ran. None of this is tier A.

**What this file does not say.** It does not say the conjecture is proved or refuted. Every statement here is conditional on:

- the openai/math manuscript;
- the cited results (SS2012, BS2018), whose statements we checked but whose proofs we take as cited (tier L);
- the C++ certificate behaving as its source reads under a conforming toolchain.

## 0. Sources audited (SHA-256)

| File | SHA-256 (prefix) |
|---|---|
| `build/main.tex` | `6147d866be2c` |
| `sections/01-introduction.tex` | `6326c2926659` |
| `sections/history.tex` | `9e7c10c45c4e` |
| `sections/02-reduction.tex` | `ef5f5ea21cbb` |
| `sections/03-geometry.tex` | `1b8446c6849e` |
| `sections/04-calibration.tex` | `3a432cdeffb3` (= record) |
| `sections/05-tails.tex` | `d9793ed1ece3` (= record) |
| `sections/06-computation.tex` | `fa15ff08f64c` (= record) |
| `sections/07-conclusion.tex` | `8ec26728f5f2` |
| `sections/08-scientific-support.tex` | `adf0f7905596` (= record) |
| `verification/certificate.cpp`, `core.hpp`, `grids.hpp` | `53d46bba38d6`, `c7f76596cde6`, `4640e0a32eb2` (= record) |

"= record" means the hash equals the one bound in `verification/data/certificate-record.txt`. The corpus root is `/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/SocrateAI-Scientific-Agora-LeanMaster/lean4basesource/openai-math/preprints/Triangular-minimality-for-planar-Coulomb-renormalized-energy-September-23-2026/`.

## 1. Verdict

**At the depth of this audit we found no GAP in Sections 2-5.** Every step of the reduction is classified CONFIRMED, except one context citation that is CONFIRMED_WITH_MINOR_FIX (a numbering pin only). The finite certificate stages match the inequalities that Sections 4-6 require, constant for constant (Section 4 of this file).

Three things remain CANNOT_ASSESS (Section 6):

- an exhaustive line-by-line equivalence between the C++ and the formulas;
- trust in the runtime (compiler, Boost, OpenMP, hardware);
- the internal proofs of the cited SS2012 and BS2018 results.

The argument chain we checked is:

1. **Square tori to the plane (Section 2).** For every n≥2 and every configuration, W_n(h) ≥ nC implies W(E) ≥ C for every E in A_1. The only cited inputs are SS2012 Theorem 1(1),(3),(4), Lemma 4.7 and Proposition 4.9. We verified each statement on the arXiv v2 pages cited below.
2. **Minimizers and Voronoi sectors (Section 3).** A square-torus minimizer exists and has separation r_*=1/√π. Its Voronoi cells give at most 6n sectors with d ≥ 1/(2√π). Separation is used only for the minimizer.
3. **Dual identity (Section 3).** W = Σ_S J(S) + ½∫|∇(h−H)|² holds for the glued trial potential H. We re-derived it, including the role of the zero constant term.
4. **Sector reduction (Section 4).** The sector reduction J − λA − μθ = g_d(d tanα) + g_d(d tanβ) is exact. With the signed-endpoint lemma it reduces everything to three scalar inequalities (cal:scalar-bounds). The exact calibration gives W(E_tri) = 6K + λ + 2πμ.
5. **Tails (Section 5).** Analytic tail bounds connect the 39 retained modes to the infinite series. The error is below 1e-11, with about 2.4e-13 actually used.
6. **Certificate (Section 6).** The finite certificate checks the three scalar inequalities on the compact rectangle. The exterior is handled by an exact formula.

**Thinnest point (not a gap).** The thinnest quantitative point is the negative-part assertion (comp:negative-assertion). Its Lipschitz allowance er_drop ≤ 5343e-7 is spent against a slack of 4585e-7 (WORK1: break-even about ×1.86). We re-derived both terms of that allowance (Section 4 of this file, row `global_grid` (negative part)) and found them correct, and sufficient as stated, not loose.

**Strongest independent checks.**

- **Calibration identity.** It can be tested without the C++. The certificate's printed λ, μ, K give 6K + λ + 2πμ ∈ [−4.15042142, −4.15040429]. This interval contains the closed-form W(E_tri) = −4.1504128077 from BS2018 §7.3 (p.26), which our Ewald evaluation reproduces to 2e-50. The square lattice (−4.1171606) and two mis-normalized values fall outside the interval. This combination does not depend on λ and μ (Section 5, check 1).
- **λ, μ, K individually.** We re-implemented them from the TeX formulas alone (mpmath, tier X): λ = −6.7300292886, μ = 0.4138833846, K = −0.0034815867. Each lies inside the certificate's printed interval. The negative controls fall outside: no angular term e, and mode m=1 dropped (which even makes K > 0). Section 5, check 4.

## 2. Cited results: verified statements (load-bearing vs context)

| Citation in manuscript | Used for | Load-bearing? | What we verified (source, version, page) | Verdict |
|---|---|---|---|---|
| SS2012 Def. 1.1-1.2, (1.3)-(1.5), Remark 7 / (1.9),(1.12) | class A_m, W(j,χ), ball cutoffs, scaling | yes | arXiv:1011.4617v2 pp.2-4. A_m: curl j=ν−m, div j=0, ν=2πΣδ_p over a discrete Λ, ν(B_R)/\|B_R\| bounded. Cutoffs: (1.3) \|∇χ\|≤C, supp⊂U_R, χ=1 at distance ≥1 from the complement. (1.4)-(1.5) match the manuscript's transcription, including θ<2. Scaling: W(j)=m(W(j′)−¼log m). | CONFIRMED |
| SS2012 Theorem 1(1),(3),(4) | cutoff independence; min W_U over A_1 achieved, finite and independent of U; periodic minimizing sequence | yes | arXiv v2 pp.4-5. Item 1: W_U(j) is independent of χ under (1.4)-(1.5). Item 3: "min_{A_1} W_U is achieved and finite, and it is independent of the choice of U". Item 4: "a minimizing sequence ... periodic (with respect to a square lattice of sidelength √(2πn))". Corollary 4.4 (p.35) and its proof (p.57) give axis-aligned square periods. | CONFIRMED |
| SS2012 Lemma 4.7 | local L^r bound (red:local-Lr) | yes | arXiv v2 p.38. The statement reads ∫_U χ^{p/2}\|j\|^p ≤ C(\|U\|+C_p)^{1−p/2}(W(j,χ)+n(log n+‖m‖_∞)‖χ‖_∞+n‖∇χ‖_∞)^{p/2}, with Û={d(x,U)<1} and n=#Λ in Û. The final display of the proof (p.39) has **2W(j,χ)**. The manuscript notes this factor-2 difference, and its (W)_+ / n log(2+n) weakening covers both forms, since ‖∇ξ‖ is bounded. Struwe's dyadic argument is credited on p.38. | CONFIRMED |
| SS2012 Proposition 4.9 | mass displacement (red:mass-displacement) with one g_U for two cutoffs | yes | arXiv v2 p.41. "There exists a measure g supported on Û such that g ≥ −C(‖m‖²+1) ... For any function χ compactly supported in U, \|W(j,χ)−∫χ dg\| ≤ Cn(log n+‖m‖_∞)‖∇χ‖_∞, n=#{p: B(p,C)∩Supp∇χ≠∅}". The quantifier order (one g, then every χ) is what the manuscript needs. At m=1 the manuscript's Cn(log(2+n)+1)‖∇ξ‖ is a weakening. SS use the same device in Cor. 4.12 (pp.45-46) and Lemma 4.14 (pp.55-57). | CONFIRMED |
| SS2012 Conjecture 1, Theorem 2 | statement of the target | context/target | arXiv v2 p.5. Conjecture 1: W(Λ_m)=min_{A_m} W. Remark 1.5: W ≈ −0.2011 (triangular), −0.1958 (square). | CONFIRMED (statement) |
| BS2018 Def. 2.1-2.4, Remark 2.5 eq.(2.4) | class A^BS_m (div E=2π(ν−m)), ball W, scaling min_{A_m}W=m(min_{A_1}W−(π/2)log m) | yes (Corollary only) | arXiv:1404.4485v5 pp.4-5. With A^BS_{1/(2π)} ↔ C_1 under F=(j_2,−j_1), (2.4) gives min_{A^BS_1}W=2π(M−¼log2π). This is the manuscript's (eq:bhs-minimum-normalization). We re-derived it. | CONFIRMED |
| BS2018 Theorem 1.5 and §7.3 | C=(1/π)min_{A_1}W+½logπ+log2; C≤C_BHS, with equality iff the density-one triangular lattice attains the min | yes (Corollary only) | arXiv v5 p.3 (Thm 1.5) and pp.25-26 (W(Λ_1)≈−4.1504128, C_BHS≈−0.0556053). The unit-sphere passage includes −n(n−1)log2 (p.23), as the manuscript says. | CONFIRMED |
| BHS2012 Conjecture 4 | target constant | statement only | arXiv:1202.4037v1 p.13: C_log,2 = 2log2+½log(2/3)+3log(√π/Γ(1/3)) = −0.05560530494... Energy over ordered pairs j≠k (eq.(1), p.1). V_log(S²)=½−log2 (eq.(3)). | CONFIRMED (statement) |
| Lieb-Rougerie-Yngvason 2018 "Lemma 3 and Appendix A" | related screening/exclusion precedent | context only (Lemma geo:separation is self-contained) | arXiv:1701.09064v3. The content matches: the single-nucleus screening radius 1/√π is eq.(3.53), p.20, and exclusion by superharmonicity is Proposition 4.2, p.21. arXiv v3 has no "Lemma 3" or "Appendix A" with that content. The numbering presumably refers to another version; we did not check one. | CONFIRMED_WITH_MINOR_FIX (re-pin the citation) |
| Gruber 1999, Bourne-Peletier-Theil 2014 Lemma 12, Petrache-Serfaty 2020, Montgomery 1988, Rankin/Cassels/Ennola/Diananda, Revol-Rouillier 2005, BBH 1994 | history and analogies | context only | not verified (not premises) | not a gap |

## 3. Step-by-step check of the reduction

Column "Our check" gives the tier of *our* verification: C = re-derived by hand; L = statement read in the source; X-exact = exact-rational script; X = float script.

### 3.1 Section 2: from square tori to the full plane

| ID | Claim | Hypotheses / inputs | Follows? What we did | Our check | Verdict |
|---|---|---|---|---|---|
| R1 | Lemma red:local: E smooth off Λ, E = (x−p)/\|x−p\|² + smooth near p, E ∈ L^q_loc (q<2), W(E,ξ) finite | div E=2π(Σδ−1), curl E=0, Λ simple and locally finite | Re-derived. E_p^0=∇log\|x−p\|−π(x−p) has div 2πδ_p−2π and curl 0. ΔV_1=∂_1divV−∂_2curlV and the companion identity hold. Weyl's lemma applies. ½\|E\|²−1/(2\|x−p\|²) ∈ L¹ and the (ξ(x)−ξ(p))/\|x−p\|² term is integrable. | C | CONFIRMED |
| R2 | Normalization bridge: C_b, j=(−E_2,E_1) ∈ C_{2π}, j′=m^{-1/2}j(·/√m) ∈ C_1 | Def. 1.1 of SS2012 | Re-derived: div j = −curl E = 0; curl j = div E; δ(y/√m) = mδ_{√m v}, so curl j′ = 2πΣδ_{√m v} − 1. | C+L | CONFIRMED |
| R3 | (red:exact-scaling) W(E,χ_R) = W(j′,ξ_t) − (π/2)log m Σ ξ_t(v), with no area factor | change of variables y=√m x | Re-derived: the puncture radius η′ = √m η produces +π log√m per charge. | C | CONFIRMED |
| R4 | (red:bulk-Lr) ∫_{Q_{t+A}}\|j′\|^r ≤ C t²(log t)^{r/2} | SS Lemma 4.7 applied to ξ_{t+D} with D > A+√m+2 in U = Q_{t+D+1}; W(j′,ξ) ≤ Ct² (limsup bound plus charge growth); n = O(t²) | Re-derived the exponent: t^{2−r}(t² log t)^{r/2} = t²(log t)^{r/2}. ξ_{t+D}=1 on Q_{t+A} because D−√m>A. | C+L | CONFIRMED |
| R5 | (red:density), (red:strip): ρ′(Q_t)=\|Q_t\|+o(t²); strip count ≤ C(t+t^{1+1/r}(log t)^{1/2}) = o(t²/log t) | coarea for ‖y‖_∞, Stokes on charge-free boundaries, Hölder | Re-derived: \|∂Q\|^{1−1/r}(t²(log t)^{r/2})^{1/r} = t^{1+1/r}(log t)^{1/2}. **It is o(t²/log t), not just o(t²)**, since 1+1/r<2 gives t^{1+1/r}(log t)^{3/2}=o(t²). That is exactly what makes the (4.12) error n log n = o(t²) in R6. | C | CONFIRMED |
| R6 | (red:cutoff-comparison) W(j′,ξ_t) ≥ W(j′,ζ_{Q_{t−L}}) − o(t²) | SS Prop 4.9 with one g_U (U=Q_{t+1}) for both cutoffs; g ≥ −C dx; 0≤ζ≤ξ_t≤1 with difference supported in a width-(L+1) strip | Re-derived. Both errors are C·n(log(2+n)+1)·O(1), with n ≤ the strip count of R5 (A=L+1+C), so they are o(t²). ∫(ξ_t−ζ)dg ≥ −C\|Q_t∖Q_{t−L−1}\| = −O(t). | C+L | CONFIRMED |
| R7 | Lemma red:plane-bound: W(E) ≥ 2π(M−¼log2π), so W(E) ≠ −∞ | R3-R6, SS Thm 1(3) (W_Q(j′) ≥ M), \|Q_{t−L}\|/\|Q_t\|→1, Σξ_t(v)=\|Q_t\|/(2π)+o(t²) | Re-derived the limit: W(E)=m(limsup W(j′,ξ_t)/\|Q_t\| − ¼log m), since (π/2)log m·(1/2π) = ¼log m. The case W(E)=+∞ is trivial. The provisional −∞ case is excluded by the same chain. The limsups are over real t, so the shift t→t−L is harmless. | C | CONFIRMED |
| R8 | Lemma red:periodic-average: periodic fields have energy per area = E_P(F)/A for ball or square cutoffs | F_ρ ∈ L¹(P) (from R1); R_ξ = O(R) boundary charges; O(R) boundary cells | Re-derived the decomposition W(F,ξ) = ∫ξF_ρ + π log ρ Σξ(v) + R_ξ. | C | CONFIRMED |
| R9 | (red:harmonic) E_{T_n}(E) = W_n(h) + (n/2)\|c\|² | E−(−∇h) harmonic on the torus, so constant; ∫∇h = 0 | Re-derived. The cross term −2c·∫∇h → 0. | C | CONFIRMED |
| R10 | Prop red:reduction: torus bound nC ⇒ W(E) ≥ C on A_1; the infimum equals W(E_tri) when C = W(E_tri) | SS Thm 1(4) square-periodic j_k with W_ball(j_k)→M; area 2πN_k (integrate curl); N_k=1 fixed by doubling the period; rescaling E_k(x)=√m(j_2,−j_1)(√m x) on T_{N_k} | Re-derived: div E_k = m·curl j_k(√m·) = 2πΣδ − m = 2π(Σδ−1) at m=2π; curl E_k = 0. E_T(E_k)/N_k = mW_ball(j_k) − (π/2)log m = m(W_ball − ¼log m). The SS squares are axis-aligned (Cor. 4.4), so the rotation remark is not needed. | C+L | CONFIRMED |

### 3.2 Section 3: finite tori, separation, Voronoi sectors, dual identity

| ID | Claim | Hypotheses / inputs | Follows? What we did | Our check | Verdict |
|---|---|---|---|---|---|
| G1 | Lemma geo:existence: W_n = πnR_n + πΣ_{i≠j}G_n(v_i−v_j); a minimizer with distinct points exists | Green function on T_n; Δh=2π off the sites | Re-derived the Green identity: the boundary term gives 2π(−log η + a_i) per site. Lower semicontinuity on the compact T_n^n, with G bounded below, gives existence. | C | CONFIRMED |
| G2 | Lemma geo:separation: a minimizer has torus separation ≥ r_* = 1/√π, also between lifts | Φ=Σ_{p≠q}G_n(·−p) is minimized at q (symmetry of G); φ(x) = −log(\|x\|/r_*) + (π/2)(\|x\|²−r_*²) on the disk | Re-derived: −Δφ = 2π(δ − 1_B), φ(r_*)=φ′(r_*)=0, φ>0 inside, and the disk area is 1. Ψ ∈ W^{2,∞}. On Ω, −ΔΨ ≥ 2π − 2π(n−1)/n = 2π/n > 0. \|Ω\| ≤ n−1 < n, so every component D has ∂D ≠ ∅. On ∂D every φ vanishes, so Ψ = Φ. Φ(q) > Ψ(q) uses φ>0 inside the disk. Ψ(q) > min_{∂D}Ψ is the standard strong minimum principle for W^{2,2}_loc strong supersolutions. The manuscript does not cite it, and we did not verify a reference for it. Injectivity radius √n/2 > r_* for n≥2. **Separation is used only for the minimizer**, and the lower bound then passes to every configuration by minimality. | C | CONFIRMED |
| G3 | Lemma geo:voronoi: at most 6n face-edge incidences; each gives a sector S(d,α,β) with d ≥ r_*/2; total area n, total angle 2πn; signed endpoints allowed | separated periodic lift | Re-derived. Interiors of distinct lift cells are disjoint, so the open faces are disks. Open edges are embedded (bounded, and a translate cannot coincide with the edge). Vertex degree ≥3 counted with multiplicity. V−E+n=0 and 3V≤2E give E≤3n and 2E≤6n. Loops, self-adjacent cells and repeated neighbours (possible at n=2,3) are counted with multiplicity, which Euler's formula permits. An edge shared with a translate p+γ of the same site has d=\|γ\|/2 ≥ √n/2 > r_*/2. C_p ⊂ p+[−L/2,L/2]². | C | CONFIRMED |
| G4 | Lemma dual:gluing: H is continuous off the sites, in H¹(Ω_η), with H=−log r+O(r²) and ∇H=−e_r/r+O(r) | radial data (dual:radial-origin)-(dual:radial-sum), k_i ≥ 6, d ≥ d_0 | Re-derived. Edge trace B(t)+ΣD_i(t) depends only on the common distance. Vertex-ray trace B(r)+Σ(r/r_v)^{k_i}D_i(r_v) is the same from both adjacent sectors. The series and their first derivatives converge uniformly by (dual:radial-sum). For r≤d_0/2, (r/t)^k ≤ (r/d_0)^6 2^{6−k} gives the O(r^6) and O(r^5) corrections. | C | CONFIRMED |
| G5 | Prop dual:identity: W_T(h) = Σ_S J(S) + ½∫\|∇(h−H)\|² ≥ Σ_S J(S) | \|T\| = N; G4 | Re-derived. ½\|∇h\|² = ½\|∇(h−H)\|² + ∇h·∇H − ½\|∇H\|². Green's identity, used in the form ∫H∂_n h with Δh=2π and ∂_n h = 1/η+O(1), gives ∫∇h·∇H = −2π∫H − 2πN log η + o(1). **Only H's zero constant term enters the hole boundary term; the constant a_i of h never appears.** Sanity check: H = h−a (all a_i=a) reproduces W = πNa. Σθ(S) = 2πN matches the counterterms. | C | CONFIRMED |
| G6 | Lemma dual:signed-endpoints | G(d,·) even, 2g_d ≥ K on x≥0, ∫max(0,−G) ≤ −K | Re-derived. If α<0, the sum is g_d(v)−g_d(u) = ∫_u^v G ≥ −∫max(0,−G) ≥ K. Both endpoints cannot be negative. | C | CONFIRMED |
| G7 | Prop dual:assembly: N(6K+λ+2πμ) on compatible tori; the same bound for every configuration on T_n when d_0 ≤ d_* | G3, G5, G6, K≤0, M_0≤6N | Re-derived: Σ J ≥ M_0 K + λN + 2πμN ≥ N(6K+λ+2πμ), using K≤0. The minimizer-to-all-configurations step is valid. | C | CONFIRMED |

### 3.3 Section 4: calibration on the triangular cell

| ID | Claim | Hypotheses / inputs | Follows? What we did | Our check | Verdict |
|---|---|---|---|---|---|
| K1 | Lemma cal:green-expansion: h_tri = −log\|z\| + C_tri + π\|z\|²/2 + Σ c_m Re z^{6m} on 0<\|z\|<a | 2∂_z²h_tri is elliptic with double poles; ℘ for the hexagonal lattice | Re-derived. The constant difference is killed by ω^{−2}-equivariance. j+2 ≡ 0 mod 6. k(k−1)c_m = (k−1)Σλ^{−k}. The residual is a real affine harmonic function and rotation kills its linear part. The coefficients are real by reflection. | C | CONFIRMED |
| K2 | Edge polynomial V_m and mode recovery: (−1)^m c_m r^k + (r/t)^k(V_m(t)−(−1)^m c_m t^k) = c_m r^k cos kφ | t = p secφ; nearest neighbour on the positive real axis | Re-derived: Re(p+i√(t²−p²))^k = t^k cos kφ, and kπ/6 = mπ on the vertex rays. | C | CONFIRMED |
| K3 | Continuations: S, P, Q, the inner b_m, U_m, τ, u_m, D_m are C², B constant and D_i=0 beyond l | knot matching | Exact check: S(0)=S′(0)=S″(0)=0 and S(1)=1, S′(1)=S″(1)=0. (P,P′,P″)(0)=(0,1,0), (Q,Q′,Q″)(0)=(0,0,1), and all six vanish at h_s (`tail_constants.py`: PQ_matching). By hand: T_0m=V_m(p), T_1m=V_m′(p), 2T_2m=V_m″(p). | X-exact + C | CONFIRMED |
| K4 | (cal:angle-density) J = ∫(f_0(d secφ) − tan²φ e(d secφ))dφ, with f_0 and e as in (cal:f0-e) | H_r and H_φ formulas | Re-derived every term: source S_1 + t²ΣD_i/(k_i+2); radial square log t + S_2 − 2ΣD_i + 2Σk_iD_iH_{k_i} + Σk_ik_jD_iD_j/(k_i+k_j); angular tan²φΣQ_iQ_j/(k_i+k_j) = 2tan²φ·e. e ≥ 0 by the kernel ∫_0^1 v^{k_i+k_j−1}dv. | C | CONFIRMED |
| K5 | (cal:sector-primitive) J − λA − μθ = g_d(d tanα) + g_d(d tanβ) | s = d tanφ, dφ = (d/t²)ds | Re-derived. λA and μθ become ∫(d/t²)(λt²/2 + μ)ds. Oddness of g_d handles signed endpoints. | C | CONFIRMED |
| K6 | Lemma cal:stationarity: ∇g = 0 at (p, x_0) for the constants (cal:constants) | integration by parts with V(s) = O(s²) | Re-derived both integrations by parts. The fixed-angle derivative equals λx_0 minus the area derivative λx_0. G(p,x_0)=0 by the definition of μ, since x_0²/p² = 1/3. | C | CONFIRMED |
| K7 | Lemma cal:energy-identity: W(E_tri) = 6K + λ + 2πμ (exact) | G5 on R²/Λ_tri with N=1 and d_0=p; H = h_tri − C_tri in each regular sector (R_0 < a); the square term is 0 | Re-derived: u_0=γ, u_m=(−1)^m c_m r^k for r ≤ R_0 (τ=0 and the U-cutoff off), b_m=V_m on [p,R_0], D_0=0. **Independent numeric tests:**<br>(a) The certificate's printed λ, μ, K give [−4.15042142, −4.15040429], which contains W(E_tri) = −4.1504128077 (BS2018 closed form and our Ewald). The negative controls fall outside.<br>(b) Our own re-implementation of f_0 and e satisfies the identity to 1e-25.<br>(c) Its λ, μ and K each lie inside the printed intervals (Section 5, checks 1 and 4). | C + X | CONFIRMED |
| K8 | Prop cal:scalar-to-torus: (cal:scalar-bounds) ⇒ W_T ≥ N·W(E_tri) on compatible tori with d_0 = b | K5, G6, G7, K7 | Logic re-derived. | C | CONFIRMED |

### 3.4 Section 5: infinite-mode truncation

| ID | Claim | Inputs | What we did | Our check | Verdict |
|---|---|---|---|---|---|
| T1 | (tail:coefficient-square), (tail:coefficient-uniform): \|c_m\| ≤ 7/(d a^d) for d ≥ 12; the square-tail bound 8(4/3)^{d/2}D^{2−d}/(d−2) | \|w\|² ≥ ¾max(\|n\|,\|q\|)²; 8v points per shell | Re-derived the shell count and the norm bound. Bracket = 6+50/729 = 4424/729 < 7. Negative control "< 6.05" fails as it should. The code's `cs()` adds exactly this tail. | C + X-exact | CONFIRMED |
| T2 | (tail:mode-derivative-bound): \|u_m^{(j)}\|, \|D_m^{(j)}\| ≤ w_k for j≤3, k≥234 | Leibniz bounds on U_m, the inner b_m, V_m near p, V_m on [p+.01,R_0], the extension, and τ | Every hand constant recomputed exactly: S-derivatives (1, 15/8, 10√3/3, 60); 25.4446 < 25.445 (control "< 25.43" fails); orders 0-2: 5.5e-7, 1.96e-4, 0.07057; inner b‴: 8405.5 k³ < 8500 k³; X ≤ 1.2p; 596.30 < 597; \|z′\|,\|z″\|,\|z‴\| = 6.12, 266.9, 47540 within 7/300/60000; 19977 < 20000; P,Q derivative suprema 6400 and 120 within 2e5/4000; τ bounds 1, 25, 1066.7, 142222.2 within 1/27/1067/142223; Leibniz factor 145506; 6.12e11 < 7e11. | X-exact | CONFIRMED |
| T3 | (tail:weighted-sum): 𝔞 < 2e-21 | ratio test at k=234 | ρ_i(234) = 0.0878, 0.0186, 0.0586, 0.0434, all < 1/10. T_0 = 1.5511e-21 < 1.56e-21 (control "< 1.0e-21" fails). Independent exact partial sum P_600 + R_606 = 1.6503e-21 < 2e-21. | X-exact | CONFIRMED |
| T4 | (tail:finite-core-premise) is a finite premise; \|B̃_1\|_{2,t} < 10 on [0,b] | \|c_1\|<1; Σ_{k≥12}7k²(2/7)^{k−3} < .014 | Sum = 0.012805 (exact partial sum plus geometric tail). \|c_1\| = 0.63469 (independent mpmath). The premise itself is certificate stage `core_test`. | X-exact + X | CONFIRMED |
| T5 | (tail:f-estimate), (tail:e-estimate), (tail:uniform-error): errors < 1e-11 for f_0, e and their first two derivatives on [b,l] | H_k identities, submultiplicative norms | Re-derived H_k″ = B_1′ − kB_1/t + k(k+1)H_k/t², hence \|H_k″\| ≤ \|B_1′\| + 2k‖B_1‖/t, and the 6(k+1) factor. Re-derived the split of the mixed term and the Q_i norm coefficients. F(A,4A) = A(56264180 + 104A) holds as an exact identity. 2F(A_0,4A_0) = 2.2506e-13 < 2.4e-13; e″: 1.28e-13 < 1.3e-13. | C + X-exact | CONFIRMED |
| T6 | (tail:exterior-formula) for t ≥ l: e=0, f_0(t) = f_0(l) − πB(l)(t²−l²); \|ΔB(l)\| < 6.075e-58 | D_i=0 and B constant beyond l | Re-derived: S_1′ = tB(l), and the derivatives of log t + S_2 cancel because B_1 = 1/t. ΔB bound = 6.0744e-58. **Independent B(l)** = 1.04646435626, inside the printed bcon (1.0464643, 1.0464644). Controls: dropping m=1 gives 1.0827, and the wrong lattice scale gives 1.0278; both fall outside. | C + X-exact + X | CONFIRMED |

## 4. Does the finite certificate check what the analysis needs? (stage ↔ inequality, with constants)

We read `certificate.cpp`, `core.hpp` and `grids.hpp`. Printed values are the outward-rounded 1e-7 pairs from `certificate-record.txt`, which equal our S1 run (WORK1). Assertions use uncoarsened 2^-144 endpoints.

| Stage (code) | Manuscript inequality it must certify | Code ↔ formula correspondence checked | Printed result | Verdict |
|---|---|---|---|---|
| `init_constants` | enclosures of log 2 and π (comp:logarithm), (comp:pi); p, R_0, a | log: 200-term atanh series on [1/4,1] plus [−1,1]/Q. The remainder 2(3/5)^401/(401·16/25) = 8.5e-92 < 2^-144 (exact check in `tail_constants.py`: log_remainder). The π remainders v^-301/301 for v=5 and 239 are also < 2^-144 (pi_remainder). π: Machin formula, 150 terms each, plus [−2,2]/Q. Interval `IV` ops: all nine sign cases of `operator*`, floor_q/ceil_q, `inv`, `sqrt` with +1, `rat`. | — | CONFIRMED |
| `cs()` + `init_after_co` | c_m enclosures (comp:coefficient-summand), (supp:real-recurrence), half-square doubling, tail (tail:coefficient-square); \|c_1\| < 1 | re6 = A⁶−45A⁴q²+135A²q⁴−27q⁶, im6 = s_1, and the complex-pair recurrence; denominator (64N⁶)^m; tail 8(4/3)^{3m}B^{2−6m}/(6m−2), then ·a^{−6m}/(6m). The \|c_1\| < 1 check is present. | (not printed); our independent c_1 = 0.63469 | CONFIRMED |
| `basis()`, `fh()`, `ss0()`, `table()` | B̃, D̃_i on each spline piece (cal:radial-data); f̃_0, ẽ jets (cal:f0-e); initial integrals (comp:initial-integrals); propagation (comp:propagation); midpoint (comp:midpoint); cell enclosures (comp:cell-integrals); ODE jets (comp:jet-ode); exact inner formula (comp:inner-exact); node separation (comp:node-separation) | Segment logic checked piece by piece: seg0 D=−U, D_0=0; seg1 S·(T_0+T_1h+T_2h²); seg2 edge polynomial in t²−p²; seg3-4 Hγ, HV_m with P,Q scaled by h_s and α=V′(R_0)=2R·dV/dw, β=V″(R_0)=4R²V_ww+2V_w; seg5 constants with τ; seg6 the constant B. `integ` uses H³\|A[2]\|/12 where A[2]=Y″/2, **so it equals the manuscript's (u−v)³ sup\|Y″\|/24 (no factor-2 discrepancy)**. ss0 coefficients match (comp:initial-integrals). The seg-0 exact formula (πt²−½)log t − 3π²t⁴/8 was re-derived. The strict node-separation throw is present. | — | CONFIRMED (spot-checked; see 6.1) |
| `core_test` | finite-core premise (tail:finite-core-premise): \|B̃_1\|_{2,t} < 6000 and Σ(k_i+1)³\|D̃_i\|_{3,t} < 2e6 on [b,l] | The jet norm uses A[q] = F^{(q)}/q!, so Σ\|A[q]\| = \|F\|_{j,t}. B_1 = B.der() + 1/t through order 2. The throw is on failure. The mesh (.00022) affects only tightness. | passes (no throw) | CONFIRMED |
| `lookup()`, `tail()` | (comp:lookup), (comp:radial-interpolation), (comp:tail-tuple) | Value queries interpolate f̃_0 and ẽ linearly, then add (H²/8)·\|cell f̃_0″\| and the ε = 1e-11 truncation. **This decomposition is valid**: \|f_0 − L(f̃_0)\| ≤ \|f̃_0 − L(f̃_0)\| + \|f_0 − f̃_0\|. Derivative queries take cell hulls plus ε. The exterior tuple applies when T.v ≥ l.u. The cell selection uses lower/upper-endpoint binary searches as argued in manuscript §6.3 (comp:lookup). | — | CONFIRMED |
| `calcLam` | λ, μ from (cal:constants) via (comp:lambda-origin), (comp:lambda-derivatives); 45000-step midpoint sums | cf = s_0/2 − s_0³/(24p²) + [0, s_0⁵/(80p⁴)]; coefficient [p/(t(s_0)+p)², 1/(4p)]·s_0³/6; f_0″ range on [p,t(s_0)]. We re-derived the second-derivative bound C′/p + 8C/s_0² for pV/s² (using t ≥ p, \|V\| ≤ Cs²/(2p), \|V′\| ≤ Cs/p) and E′/p + E/p². Error L h²/24 · sup. | λ (−67300312, −67300275), μ (4138830, 4138838); our independent λ = −6.7300292886 and μ = 0.4138833846 lie inside | CONFIRMED |
| `calcK` | K = 2∫_0^{x_0}G(p,s)ds by (comp:K-quadrature) | midpoint h ≤ .0001; G_ss hull on the .0002 mesh; error h²(R/2)\|G_ss\|/24, then ×2 | K (−34823, −34809); our independent K = −0.0034815867 lies inside | CONFIRMED |
| asserts after `calcK` | (comp:tail-signs): −6.731 < λ < −6.729, K < 0, f(l) > 0, −πB(l) − λ/2 > 0 ⇒ (comp:positive-tail) | f(l) = f̃_0(l) + ε − λl²/2 − μ; bcons = −log R + πR²/2 + ΣV_m(R) + ε | f(l) (44755, 44772); slope (774490, 774509) | CONFIRMED |
| `bdsup` | (comp:global-derivative-bounds): L_1 ≥ ‖G_d‖, L_2 ≥ ‖G_s‖, L_3 ≥ ‖G_dd‖, L_4 ≥ ‖G_ss‖ on 𝒟 = [b,.697]×[0,.65] | (comp:rational-derivatives) and (comp:G-derivatives) re-derived: A_dd = 2d(d²−3s²)/t⁶, A_ss = −2d/t⁴ + 8ds²/t⁶, Z = A − 1/d, the f″r_v² + f′(1−r_v²)/t terms. The cells cover 𝒟 (the last cell's upper endpoint exceeds .697 by outward rounding). The hulls use the full derivative lookup. | L_1 ≤ 7.4636170, L_2 ≤ 2.5091315, L_3 ≤ 143.7890461, L_4 ≤ 315.1489689 | CONFIRMED |
| `global_grid` (outer) | (comp:outer-assertion) m_* − E_0 − E_I > 0 on 𝒟 ∖ int 𝒟_0 | er0 = 2·.65·S_h²·L_4/24 = E_0; eri = 2(D_h²·.65·L_3 + S_h²L_2)/8 = E_I. S_h and D_h are outward maxima of the actual node gaps. Nodes are partitioned at the sides of 𝒟_0. `needall` tests every x-node on d-nodes at or outside the d-sides; interior d-nodes are tested only for x ≤ .29420 or ≥ .32621. The x=0 value −K is tested. **Bilinear error without a mixed derivative**: successive 1-D interpolation, first in d (\|F_dd\| ≤ 2·.65·L_3) and then in x at the two d-corners (\|F_xx\| = 2\|G_s\| ≤ 2L_2). The errors add. Every cell outside int 𝒟_0 has all four corners tested. | gmin (134,162); factor (0,15); gmin−factor (120,162) ⇒ m_* − E_0 − E_I ≥ 1.20e-5 | CONFIRMED |
| `global_grid` (negative part) | (comp:negative-assertion) N_* + K + .65(S_hL_2/4 + D_hL_1/2) < 0 for b ≤ d ≤ .697 | max(0,−y) is 1-Lipschitz and \|∂_sG\| ≤ L_2, so the midpoint error per cell is ∫L_2\|s−s_mid\| = L_2h²/4. The sum is ≤ .65·S_hL_2/4. A shift to the nearest d-node is ≤ D_h/2, costing ≤ .65·L_1·D_h/2. The code's `er_drop = Smax*(H/4*Gs + Dh/2*Gd)` matches exactly. Every d-node, including those inside 𝒟_0, is included. The integrand vanishes for s ≥ .65 because √(b²+.65²) = .7086 > l. **This is the thinnest margin** (WORK1: allowance 5343e-7 against slack 4585e-7). We found no error in it, and the constants are not loose. | drneg (24879, 24882); er_drop (0, 5343); drneg + er_drop + K (−9944, −4585) | CONFIRMED |
| `inside_hess` | (comp:hessian-assertions) on 𝒟_0; ⇒ (comp:inner-conclusion) by convexity plus exact stationarity (K6) | A_j = Σ_{i<j}\|S_i\|F_1 + [0,\|S_j\|]F_1 (direct integration from s=0); B_j = G_d; C_j = G_s; det per cell. Tested on cells with upper end ≥ .29420. W^{2,∞}, mollification and convexity give the conclusion. (p, x_0) = (0.537285, 0.310202) is interior to 𝒟_0 (exact check). | g_dd ≥ 1.0529222, g_xx ≥ .0128335, det ≥ .0086252 | CONFIRMED. No negative control has exercised this stage yet (WORK1). |
| Theorem comp:scalar | (cal:scalar-bounds) for all d ≥ b, x ≥ 0 | d ≥ .697 ⇒ t ≥ d > l ⇒ G > 0. For x > .65 the primitive increases. 𝒟 = outer region ∪ 𝒟_0. The negative part vanishes outside 𝒟. | — | CONFIRMED |
| Thm torus (Section 7) | b < d_* = 1/(2√π) | 4b²·3.1416 = 0.9999684 < 1 (exact). The control b′ = 0.282095 gives 1.0000006 > 1, so it fails as it should. | — | CONFIRMED |

## 5. Independent numeric checks (scripts in `P1/s2_audit/`)

All were run with `taskset -c 4-7 .venv/bin/python -I`. Each output JSON sits next to its script.

1. **`calibration_check.py`** (exact Fractions for the interval; 50-digit mpmath values; tier X for the values). It tests the exact identity of K7.
   - Result: 6K + λ + 2πμ ∈ [−4.15042141551, −4.15040428896] (width 1.71e-5).
   - BS2018 closed form, expanded as π logπ − (π/2)log3 − 3π logΓ(1/3) + (3/2)π log2: −4.1504128076789633794.
   - Ewald heat-kernel split of πR_tri: the same value, at both s_0 = 1/(4π) and 1/(2π).
   - Positive controls:
     - Ewald and the closed form differ by 2.1e-50.
     - In SS normalization, Ewald gives −0.20108945 (triangular) and −0.1957972 (square), matching SS2012 Remark 1.5 (−0.2011, −0.1958).
     - C from BS Theorem 1.5 equals C_BHS = −0.0556053049433925 (difference 4e-51).
   - Negative controls, all outside the interval:
     - square lattice: −4.11716061233;
     - SS normalization without the 2π scaling: −0.20108944761;
     - ¼log2π shift dropped: −1.26348226266.
   - A first run used a mistyped compact form of the BS closed form (our own transcription error, not an error in BS2018 or the manuscript). It failed, and was corrected to the expanded form printed on BS2018 p.26.
   - **Scope of this check.** The combination 6K + λ + 2πμ does not depend on λ or μ. Each of the six regular sectors has area 1/6 = p·x_0 and angle π/3 (the half-sector has area p·x_0/2 = 1/12 and angle π/6 = arctan(x_0/p)) [corrected at REVISE, audit N1: the first version mixed the full and the half sector], so the λ and μ terms in K cancel exactly, and quadrature only adds an error. The check therefore tests 12∫_0^{x_0} G⁰(p,s)ds = 6J(regular sector) = W(E_tri). That covers the f_0/e formulas, the lookup and the K quadrature on [p,R_0], but it cannot detect an error in the λ or μ formulas. Check 4 covers λ and μ individually. Our own re-implementation demonstrated this blindness directly: its first run had a wrong λ (about 5e5) but still satisfied the identity to 3e-20.
2. **`bl_check.py`** (30-digit mpmath; tier X). It tests T6 and the coefficient sums independently of the C++.
   - B(l) = 1.04646435626088, inside the printed pair (1.0464643, 1.0464644).
   - c_1 = 0.63469179871, so \|c_1\| < 1. The D=400 positive control agrees to 1.8e-12, within the paper's D=256 tail bound.
   - Negative controls, both outside the pair: dropping m=1 gives 1.0827; a=1 instead of √(2/√3) gives 1.0278.
3. **`tail_constants.py`** (exact Fractions and sympy; tier X-exact). Every hand constant of Section 5, the Appendix rational propagation, and the domain facts of Sections 6-7 pass. The four tightened negative controls fail as designed.
4. **`constants_reimpl.py`** (mpmath at 25-45 digits; tier X). It re-implements f_0, e, G, λ, μ and K from the TeX only: (cal:f0-e), (cal:primitive), (cal:constants).
   - Method: on [p,R_0], B is exactly γ + Σa_m r^{6m}, so S_1, S_2 and H_k use the monomial formulas. D_m = c_m t^k cos(kφ) − a_m t^k with cos φ = p/t, and D_0 = 0. The coefficients c_m come from float64 lattice sums.
   - Result: λ = −6.73002928856, μ = 0.413883384579, K = −0.00348158666. Each is inside the printed pairs (−6.7300312, −6.7300275), (.4138830, .4138838), (−.0034823, −.0034809).
   - Positive controls: G(p,x_0) = 1e-53, and 6K + λ + 2πμ − W(E_tri) = −1.0e-25.
   - Negative controls: no angular term gives λ = −6.75295 and K = −0.0039749; dropping m=1 gives λ = −6.76510 and K = +0.000526. All are outside.
   - An earlier run used tanh-sinh at 25 digits for ∫(f_0(t(s))−f_0(p))/s² ds. It sampled s ~ 1e-12, cancelled catastrophically, and returned λ ≈ 5.5e5. That is a defect of our script, not of the certificate. Re-run with 45-digit Gauss-Legendre it gives the values above. The failed run still satisfied the identity to 3e-20, which shows directly that check 1 cannot see λ.
   - This is evidence that the C++ evaluates the manuscript's formulas on [p,R_0]. It is not a proof, and it does not cover the spline pieces below p or above R_0, nor the grid assertions.

## 6. CANNOT_ASSESS (stated limits of this audit)

- **6.1 Exhaustive code ↔ formula equivalence.**
  - Checked: the `IV` arithmetic primitives, `log`, π, `cs`, `init_after_co` (α, β, T_0-T_2, edge coefficients), the `basis` segment logic, `ss0`, `fh`, `integ`, `table` propagation and cell states, `core_test`, `lookup`, `tail`, `calcLam`, `calcK`, both `G` overloads, `bdsup`, `global_grid`, `inside_hess`, and the stage order in `run_certificate`.
  - Not checked line by line: the jet `pow` binomial shortcut, `J::log`, `J::sqrt`, `solve` beyond its recurrence, `cpol`'s Taylor shift (an exact identity, (comp:polynomial-shift)), `hor`, and the OpenMP reduction order. For OpenMP, the source comment says endpoint addition is exact, so the order cannot change results.
  - The independent B(l), calibration and λ/μ/K re-implementation checks agree with the C++ outputs. That is evidence, not proof, of correspondence on [p,R_0]. No independent check covers the spline pieces on [b,p) and (R_0,l] (inner S-cutoff, the P/Q extension, τ blending) or the grid-stage values (gmin, drneg, the L_1-L_4 hulls, the Hessian hulls). There we rely on the code reading in Section 4.
- **6.2 Runtime trust.** This covers the compiler, Boost.Multiprecision `cpp_int`, OpenMP, the OS and the hardware. Our S1 used a different toolchain from the record (g++ 11.4, Boost 1_74) and reproduced all 22 pairs. This is not a formal guarantee.
- **6.3 Proofs inside the cited results.** We verified the statements of SS2012 Theorem 1, Lemma 4.7 and Proposition 4.9, and of BS2018 Theorem 1.5 and (2.4). We did not re-verify their proofs (tier L). The whole-plane theorem inherits them.
- **6.4 Negative-control coverage.** No negative control (WORK1) exercised `inside_hess`, `calcLam` or `core_test` failure paths. A planted Hessian-breaking edit would close this.
- **6.5 Statement-level formalization.** Nothing here is tier A. S3 (Lean statement) is a separate stage.

## 7. Minor remarks (no effect on the argument)

- **Citation pin.** The LRY2018 "Lemma 3 and Appendix A" does not match the arXiv v3 numbering (Prop. 4.2 and eq. (3.53)). It is context only.
- **Uncited standard tool.** Lemma geo:separation uses the strict minimum principle for W^{2,s} supersolutions (here Ψ ∈ W^{2,∞}). It is standard, but the manuscript gives no reference and we did not verify one.
- **Redundant remark.** The rotation remark in Prop red:reduction is not needed: SS2012 Cor. 4.4 already gives axis-aligned square periods.

## 8. Bottom line

Within this audit's scope, we see no missing step between the cited inputs and the main theorems:

- SS2012 Theorem 1, Lemma 4.7 and Proposition 4.9;
- BS2018 Theorem 1.5 (for the corollary only);
- the finite certificate, whose stages certify exactly the scalar inequalities (cal:scalar-bounds) and the finite-core premise.

The calibration identity, λ, μ, K, B(l) and every Section 5 constant hold up under independent recomputation with positive and negative controls. The grid-stage values are covered only by the code reading. This is an agent audit (tier C), not a proof. Any claim that the Sandier-Serfaty conjecture holds rests on the openai/math manuscript (AI-generated, not peer reviewed), on the cited literature, and on the certificate run. It should be stated that way, and only after independent expert review.
