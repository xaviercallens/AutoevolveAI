# N3: literature map for jellium lower bounds and Lieb–Oxford constants

Date 2026-10-26. Preregistered item N3 in `../preregistration.json`, with prior room_for_improvement 0.4. The kill rule is: "no-go if the best known bound already exceeds what B3's residual plan could certify".

This is a literature check only. The only computation is one mpmath evaluation of closed-form constants (tier X, listed in §6).

**Tiers.**
- **L**: read in the primary or secondary source through alphaXiv on 2026-10-26, with the arXiv id and page.
- **L-sec**: the statement is quoted by a secondary source; the original was not read.
- **X**: our own numerics.
- **C**: our own reasoning.
- **UNREAD**: a source that is relevant and could not be accessed.

## 0. Verdict

**Conditional GO, narrowly scoped.** The GO covers running B3's falsification test (B3 §6) and, if that test passes, a certified lower bound on the 3D jellium energy that beats Lieb–Narnhofer.

- It is **not** a GO for anything about the Lieb–Oxford constant. A better jellium lower bound changes neither the LO lower bound 1.4442 nor the LO upper bound 1.5765 (§2).
- The GO is conditional on three unread 1976–79 sources (§5). They must be checked before any claim of novelty.

**Number to beat:** e_Jel ≥ −c_LN, with c_LN = (3/5)(9π/2)^{1/3} = (9/10)(4π/3)^{1/3} = **1.4507927586…**

**Ceiling, i.e. the conjectured true value:** ζ_BCC(1) = **−1.4442307515**, and it is rigorously known that e_Jel ≤ ζ_BCC(1).

**What B3 could at best certify:**
- with the axial ansatz, about −1.44434 (bcc − 1.06e-4);
- with the radial ansatz, about −1.4473.

Both ceilings lie above −1.45079, so the preregistered kill does **not** fire. These are upper limits of the method, not bounds anyone has. The B3 paper states this too (main.tex §plan, l.278 and l.286).

## 1. 3D jellium lower bound: the convention and the best known value

**Convention (checked).** The energy is per particle at unit density ρ = 1, which is the same as per unit volume. The interaction is 1/|x|, with a neutralizing background.

| Value | What it is | Source |
|---|---|---|
| −1.4442307515 | bcc: ζ_BCC(1) = ½·(2·Madelung). Muratov–Novaga's 2·Madelung = −2.888461503, and our B3 Ewald value −1.4442308 | Lewin–Lieb 1408.3358 App. B eq. (B4), p.8: "When L is the BCC lattice, e_Jel(L) ≃ −1.4442". LLS 2203.12473 p.3: "e_UEG ?= ζ_BCC(1) ≃ −1.4442". B3 FEASIBILITY §4 (X) |
| −1.4507927586 | Lieb–Narnhofer / Sari–Merlini bound | see the statements below |

**Lieb–Narnhofer, statement as quoted.**
- **Csirik, arXiv:2610.20910 (2026), Theorem 2.2(i), p.6** (citing [LN75, Appendix]; tier L-sec for LN itself): "For every N ⩾ 1 and every X ∈ (R³)^N, U^{ρ0}_Ω(X) ⩾ −(9/10) N/r_s = −(9/10)(4π/3)^{1/3} ρ0^{1/3} N, r_s = (3/(4πρ0))^{1/3}". With c_LN := (3/5)(9π/2)^{1/3} = (9/10)(4π/3)^{1/3} ≃ 1.4508, this gives e_Jel ⩾ −c_LN.
- This holds for **every finite N, every bounded Ω**, and does not even require neutrality.

**Method and its optimality.** Lewin, arXiv:2202.09240 (J. Math. Phys. 63 (2022) 061101), **Remark 19, p.22**:
- The idea is "to replace V_s by V_s ∗ ν for a radial function ν ⩾ 0 … Newton's theorem implies V_s ∗ ν ⩽ V_s … After optimizing over ν (**the optimum is the uniform measure of a certain ball**), this provides the constant c₁ = (3/5)(9π/2)^{1/3} ≃ 1.4508 which is surprisingly close to the conjectured best value −ζ_BCC(1) ≃ 1.4442".
- p.23: −c₁ "is exactly the Jellium energy of a system composed of points sufficiently far away and a background Ω equal to the union of the balls of volume 1 centered at the points".

**Consequence (C).**
- 1.4508 is the **optimum of the radial-smearing (Onsager/Newton) method**.
- Beating it needs a non-radial, configuration-dependent argument. B3's dual identity with Voronoi/axial pieces is exactly that kind of argument.
- This is the strongest evidence that an improvement would be new and not a routine re-optimization.

**Has anyone improved −1.4508? Nothing found in the sources read.**
- Csirik 2026, Thm 2.2, p.6, still uses c_LN as the stability bound, and "By Theorem 2.2, e_Jel ⩾ −c_LN" (p.6).
- Lewin–Lieb 2015 (1408.3358) p.7: "One thing that is definitely known is that the BCC value must be very close to the true minimum because a rigorous lower bound … was given in [9] and reads E_Jel(N) ⩾ −(1.4508…)N".
- LLS 2022 (2203.12473) p.4: the LO constant "can be replaced by 1.451 when ρ is a characteristic function [LN75, BBL12, LL15]".
- Blanc–Lewin 1504.01153 §2.6, p.19 (read in B3): bcc in 3D "is still an open problem", together with the LN bound.
- Two alphaXiv discovery searches (default and recency) returned no improvement.
- This is **not** exhaustive. See the unread sources in §5.

**Rigorous upper bound on e_Jel (L).**
- e_UEG ⩽ ζ_BCC(1) was "surprisingly hard to prove … achieved only recently in [CP19, LLS19a]" (LLS 2203.12473, p.3, eq. (6)).
- Classical e_Jel = e_UEG holds [LLS19a, CP19]. The quantum version is Csirik 2610.20910, Theorem 3.1, p.8: e^ℏ_Jel(ρ0) = e^ℏ_UEG(ρ0).
- So the rigorous bracket today is **−1.4507928 ⩽ e_Jel ⩽ −1.4442308**: a gap of 6.56e-3, or 0.45 %.

**Lattice-only results, which say nothing about the general minimum (L, read in B3).**
- Muratov–Novaga, arXiv:2610.29732, Thm 1, p.4: bcc is the unique minimizer among Bravais lattices. The proof is computer-assisted.
- Luo–Wei, arXiv:2610.31456: the Yukawa analogue.

**Citation discrepancy.**
- LN is J. Stat. Phys. **12 (1975) 291–310** according to Csirik ref [14] and Lewin ref 341.
- Lewin–Lieb 1408.3358 ref [9] prints "J. Stat. Phys. 12, 465 (1975)".
- We use 291–310 (two sources agree) and flag the discrepancy.

## 2. Lieb–Oxford constant and exactly how jellium enters

**Definition (L).** LLS 2203.12473, Theorem 1, p.9:

c_LO = sup_{ρ⩾0, ∫ρ∈ℕ} (−E_ind[ρ]) / ∫ρ^{4/3}.

Here E_ind[ρ] = inf_P {⟨Σ|x_j − x_k|^{-1}⟩_P − D(ρ,ρ)} over N-particle states P with density ρ (eqs. (2)–(3), p.2).

**3D bounds (L).**

| Bound | Value | Source |
|---|---|---|
| Upper, best | **c_LO ⩽ 1.5765** | LLS 2203.12473 eq. (79), p.28: "we can safely assert that c_LO ⩽ 1.5765". Abstract and eq. (7), p.4: "1.58". Published in Lett. Math. Phys. 112 (2022) 92 (per Rosenzweig ref) |
| Earlier upper bounds | 1.64 (Chan–Handy 1999), 1.68 (Lieb–Oxford 1981), 8.52 (Lieb 1979) | LLS p.2 and p.4 |
| Lower, best | **c_LO ⩾ −e_UEG ⩾ −ζ_BCC(1) ≃ 1.4442** | LLS p.4: "Due to (5) and (6), it is known that the best constant is above 1.44". (5) is the LDA limit [LLS18]; (6) is e_UEG ⩽ ζ_BCC [CP19, LLS19a] |
| Conjecture | c_LO = −e_UEG | LLS p.4: "conjectured in [LP93, OC07, RPCP09]". Rosenzweig 2608.17155 p.2: "the exact value of c_LO(1,3) is unknown: a widely discussed candidate is approximately 1.4442" |
| Fixed N | Λ_1 ≈ 1.0918 < Λ_2 < … strictly; c_LO = sup_N Λ_N, and it is not attained at finite N | Rosenzweig 2608.17155, Thm 1.1, p.3 (AI-assisted, 2026). Perdew–Sun 2206.09974 p.5: C_2 ⩾ 1.234 (or 1.256 per SVGG16) |
| Restricted classes | 1.25 for negatively-correlated states and Hartree–Fock; 1.2090 at constant density | LLS Thm 4, p.11 |
| Gradient-corrected | E_ind ⩾ −(c_LN + α)∫ρ^{4/3} − (0.001206/α³)∫\|∇ρ\| (or − (0.2097/α²)∫\|∇ρ^{1/3}\|²) | Lewin–Lieb 1408.3358, Thm 1, eq. (6), p.1. The leading constant is c_LN = 1.4508 itself (p.2); BBL12 is similar |

**Direction of the jellium–LO link (C, from the L statements above).**

1. An **upper** bound on the jellium/UEG energy, i.e. a trial state, gives a **lower** bound on c_LO. This is how 1.4442 arises: c_LO ⩾ −e_UEG, because by (5) slowly varying densities realize e_UEG ∫ρ^{4/3}.
2. A **lower** bound on jellium, LN-type or an improvement of it, bounds −e_UEG from above. It gives **no** upper bound on c_LO, because c_LO is a supremum over *all* densities, most of them non-uniform. Its value lies in [1.4442, 1.5765], and c_LO = −e_UEG is only conjectured.
3. **Answer: neither.** An improved jellium lower bound changes neither 1.4442 nor 1.5765.
4. The only LO-type constants it touches are **ceilings**:
   - the leading constant of a *gradient-corrected* bound;
   - the constant for constant-density / characteristic-function ρ (1.451, LLS p.4).
   By (5) each of these must be ⩾ −e_UEG. An improvement of *those* inequalities would imply an improved jellium bound, not conversely. A torus/Voronoi certificate does not transfer to general densities.
5. **Historical caveat.** Lewin–Lieb 2015 App. B (pp.7–10) argued that the "jellium-like" indirect energy is −0.9507, not −1.4442. That gap was closed by the floating-crystal-in-fluid construction [LLS19a, CP19]: e_UEG = e_Jel. Perdew–Sun 2206.09974 pp.6–7: "That equivalence was later proved rigorously [20,21,22]".

**2D bounds (1/|x| interaction in d = 2, ρ^{3/2}; L, as of the sources read).**
- Benguria–Gallegos–Tušek, arXiv:1106.5772, **Thm 1.1, p.2**: E(ψ) ⩾ −(1+ε)β∫ρ^{3/2} − (4/(βε))∫|∇ρ^{1/4}|², with β = (4/3)^{3/2}√(5π−1) ≃ 5.9045. This needs a gradient term.
- Without a gradient term the best they cite is C_LSY = 192√(2π) ≃ 481.27 (Lieb–Solovej–Yngvason 1995, Lemma 5.3, eq. (5.24)).
- Numerical proposals are ≃ 1.95 (Räsänen et al., cited on p.2).
- We did not find a 2D analogue of LLS 2022. LLS23 ("Universal functionals", §5.3, cited by Rosenzweig p.1) states the Riesz LO for all (s, d), but we did **not** read it.
- So "481.27 / 5.9045+gradient" is "best as of the sources read", not a verified state of the art.

## 3. Would a certified non-sharp improvement of the 3D jellium bound be new and meaningful?

**New:** probably yes, conditional on §5.
- No rigorous improvement over −1.4508 appears in the 2015–2026 sources read.
- Lewin's Remark 19 shows the classical method is saturated at 1.4508.
- Numerically the answer is believed to be −1.4442308 (bcc), so an improvement would not be "already known numerically" in a way that makes the bound moot. The rigorous lower bound is the open part.

**Meaningful: modestly.**
- *For.* It would be the first improvement of a 1975 constant that is quoted in every review (Blanc–Lewin, Lewin 2022, Csirik 2026). It would shrink the rigorous bracket on e_Jel = e_UEG, classical and, by Csirik Thm 3.1, the classical limit of the quantum energy. It is also the natural 3D shadow of the 2D Sandier–Serfaty theorem (§4).
- *Against.* It does **not** change the Lieb–Oxford constant (§2). It does not prove bcc optimality (B3: the axial ansatz has a forced slack ≥ 1.06e-4, larger than the fcc−bcc gap). DFT practice is unaffected.
- *Size thresholds.* B3's secondary target δ* < 6.6e-4 (10× LN) would be a clear result. Beating LN by only ~1e-4 would still be new, but it is a small numerical improvement.

**Form of the target (C).**
- B3's pipeline is periodic: flat tori of volume N. A torus certificate gives only the thermodynamic-limit statement e_Jel ⩾ −c.
- That is weaker in form than LN, which holds for every finite N and every domain.
- The step "torus minimum per particle → e_Jel" needs a verified 3D Coulomb citation. Candidates:
  - Lewin 2202.09240 §IV.C, "Limit with periodic boundary conditions", p.45ff (section title read; its theorem was not read for d = 3, s = 1);
  - Rougerie–Serfaty, CPAM 69 (2016), Thm 1 and Prop. B.3, which B3 read for the smeared energy.
- B3 G1 records the caveat: Rougerie–Serfaty Remark B.2 says the cutoff-W may depend on the cutoff for d ⩾ 3. The theorem used must be the smeared/periodic one.

## 4. 2D analogue under the Sandier–Serfaty conjecture

**Subject.** The openai/math preprint "Triangular minimality for planar Coulomb renormalized energy" (2026-09-23) claims to prove the SS2012 conjecture: min W over A₁ is attained at the triangular lattice. It is AI-generated and not peer reviewed. Our P1 audit (`results/programmes/2026-10-25/P1/REDUCTION_AUDIT.md`, tier C) found no gap in §§2–5 and reproduced the certificate. It records W(E_tri) = −4.1504128077 (BS2018 §7.3, p.26) and square −4.1171606.

**What follows if it holds.**

1. **2D log-gas (s = 0) jellium energy, exactly.**
   - Lewin Remark 19, p.22: the LN-type bound is c₁ = 3/8 + (1/4)log π ≃ 0.6612 in d = 2. The expected best constant is −ζ′_trg(0) ≃ 0.6606 (his ref. 316, Prop. B.1). Conjecture 35, p.42: e(0) = min_L ζ′_L(0).
   - X: c₁ = 0.6611824715 and ζ′_tri(0) = −0.6605587142, from the Kronecker limit formula −½log(2π√y|η(τ)|²) at τ = e^{iπ/3}. That matches Lewin's 0.6606; the square lattice gives −0.6552665.
   - X: W(E_tri)/(2π) = −0.6605587 and W(E_sq)/(2π) = −0.6552665. Both agree with ζ′_L(0) to 7 digits, so e(0) = min W/(2π) in Lewin's normalization at unit density. This is a one-parameter proportional map fixed a priori, checked on 2 lattices; an affine map was not tested on a third.
   - Under SS: **e_2D-log-Jel = ζ′_tri(0) = −0.6605587**. The 2D LN gap of 6.24e-4 is **closed exactly**, as a sharp theorem.
   - The 2D proof is the sharp version of what B3 tries in 3D. B3 found that its exact-calibration step is genuinely 2D.
2. **The 2D Lieb–Oxford constant for 1/|x| electrons (s = 1, d = 2): nothing follows.** That is a different interaction.
   - The implication "triangular is optimal for all s ∈ [0,2)" is Petrache–Serfaty's, and it runs **from Cohn–Kumar** (Lewin p.43: PS20 show Cohn–Kumar ⇒ Conjecture 35 for max(0, d−2) ⩽ s < d). It does not run from s = 0 to s = 1.
   - The LO framework degenerates as s → 0 (Rosenzweig 2608.17155 §7.2, p.20: "At s = 0, both contributions are of order ε, so this construction no longer forces a strict gain").
   - So BGT 5.9045 (with gradient) and LSY 481.27 are untouched.
   - A log-gas "LO-type" inequality (indirect energy ⩾ −C N − ¼∫ρ log ρ) would inherit the lower bound C ⩾ −ζ′_tri(0) through a 2D jellium = UEG equality. We have **not** verified that such an inequality, or that equality for s = 0, is in the literature, so this is tier C.
3. **Other consequences (L, through the manuscript's own claims, not re-checked here):**
   - via Bétermin–Sandier, the d = 2 case of Brauchart–Hardin–Saff Conjecture 4;
   - via Sandier–Serfaty 2015 (2D Coulomb gases), the leading next-order constant of the 2D Coulomb gas ground state as β → ∞.

## 5. Unread sources (these block an unconditional novelty claim)

| Source | Why it matters | Status |
|---|---|---|
| R. R. Sari, D. Merlini, R. Calinon, "On the ground state of the one-component classical plasma", J. Phys. A 9 (1976) 1539 (Lewin ref 446) | The title is squarely on topic. It could contain a lower bound sharper than LN | UNREAD: not in alphaXiv; web search confirmed only the citation |
| R. Calinon, D. Merlini, R. R. Sari, "H-stability property and energy of Wigner lattices in one-component classical plasma", Comput. Phys. Commun. (1977) | Same group; numerical | UNREAD |
| H. Totsuji, "Lower bounds for thermodynamic quantities of d-dimensional classical one-component plasmas", Phys. Rev. A (1979) | Possibly an ion-sphere bound, which would equal LN at T = 0 | UNREAD |
| Lieb–Narnhofer 1975 original; Sari–Merlini J. Stat. Phys. 14 (1976) 91 | The LN statement is taken from Csirik and Lewin (L-sec) | UNREAD |
| LLS23 "Universal functionals", §5.3 | Riesz LO in all (s, d), relevant to 2D | UNREAD |
| Lewin 2202.09240 §IV.C theorem for d = 3 Coulomb | torus → e_Jel transfer for the target | UNREAD (section located, theorem not read) |

**Action before any attempt:**
- Obtain SMC 1976 and Totsuji 1979, through the IOP/APS pages or a library.
- If either beats 1.4508, the number to beat becomes theirs and the GO must be re-evaluated against B3's ceiling. B3's axial ceiling −1.44434 would still lie above any value consistent with Lewin 2022 calling LN "surprisingly good", but that is reasoning, not evidence.

## 6. Numerics (X)

The script is an inline mpmath one-liner with 30 digits, run with `.venv/bin/python`:
- (3/5)(9π/2)^{1/3} = (9/10)(4π/3)^{1/3} = 1.450792758614823. Both forms agree, which is the positive control.
- 3/8 + log(π)/4 = 0.661182471462350.
- Kronecker limit: tri −0.660558714214019 and square −0.655266462955755. Positive control: Lewin's 0.6606. Negative control: the square lattice is higher.
- bcc −2.888461503/2 = −1.4442307515.

## 7. GO / NO-GO

**Kill rule check.**
- Best known rigorous: −1.4507928.
- B3 axial ceiling: about −1.44434. B3 radial ceiling: about −1.4473.
- Both are above it, so the kill does **not** fire.

**GO, narrow and conditional on §5.**

**Target inequality (tier C to start).** For all N and every flat torus T of volume N,

  min_{x∈T^N} W_T(x)/N ⩾ −c*,  with c* < c_LN = 1.4507927586…,

proved by a computer-assisted dual-identity certificate (B3 §6). By the 3D periodic thermodynamic limit (citation to verify, §3) this gives e_Jel = e_UEG ⩾ −c*.

**Success thresholds.**
- Minimal: any certified c* < 1.45079 with the margin enclosed.
- Clear: c* ⩽ 1.44489, i.e. δ* < 6.6e-4 from bcc.
- Ceiling: 1.44434 for the axial class and 1.4473 for the radial class. These are upper limits, not achieved values.

**First step.** B3's falsification test: optimize the radial or axial data, then sample sector inequalities. Kill the attempt if the best feasible certified constant does not beat −1.4507928.

**Not claimed.** Any effect on the Lieb–Oxford constant: an improvement would move neither 1.4442 nor 1.5765.

**Prior update.** room_for_improvement was 0.4. The method-level evidence (Remark 19) supports novelty, but realizability is untested. We leave it at 0.4 and do not raise it.
