# B1: quantum triangular → rhombic transition in the 2D Gaussian-core crystal

Proposal 2, item B1. The preregistration is `../preregistration.json` (B1; priors: B1a 0.85, B1b_before_melting 0.4,
B1c_survives 0.25; kill condition: "if the transition lies beyond melting or disappears beyond harmonic, report that").
Date 2026-10-26. B1a–B1c are Tier X (floating-point numerics, nothing here is a proof). B1d is Tier L (literature).

## Verdict

1. **B1a (harmonic): CONFIRMED, with a correction to the picture.** In the harmonic theory,
   E(τ) = E_static(τ) + ħ_eff E_zp(τ). For every a in the tested range 0.378–1.58, the triangular lattice stops being a
   local minimum at the spinodal ħ*(a) = −c_static/c_zp.
   - ħ*(a) has a minimum of 0.0877 at a = 0.5 and is 0.124 at a = 1. It diverges at both ends of the interval
     (a1, a2) = (0.37668, 1.58148).
   - The transition is **not continuous; it is first order.** The stabiliser of ρ has a D3 symmetry, which allows a cubic
     invariant. The "tie coupling" ΔE_static/(−ΔE_zp) therefore falls linearly with distance along the arc |τ| = 1
     towards the square lattice, and rises at first along Re τ = 1/2.
   - A dynamically stable distorted lattice reaches the triangular energy at Λ_1(a) < ħ*(a), with Λ_1/ħ* ≈ 0.75–0.78
     for a between 0.45 and 1.2. At a = 1, Λ_1 = 0.0942 and ħ* = 0.124. The winner is an *oblique* lattice near
     τ ≈ 0.30 + 0.96i, not a rhombic one, except for a ≥ 1.3, where the winner is a centred-rectangular lattice near
     Re τ = 1/2, y ≈ 1.03.
   - That lattice sits **at the edge of harmonic dynamical stability**. Its stability margin is 2e-5 to 2e-3, against
     0.034 for the triangular lattice at a = 1. Over the sampled stable set, the harmonic energy has no interior
     minimum other than the triangular one.
   - Restricting to shapes with margin ≥ 0.01 (well inside the stable set) moves Λ_1 by only 3–11 % (a = 1: 0.0973). So
     "first order, with Λ_1 well below ħ*" is robust. *Which* phase lies beyond is not determined by harmonic Bravais
     theory.
2. **B1b (Lindemann): the transition does not clearly precede melting (prior 0.4 → not supported).**
   - We use the harmonic Lindemann ratio γ = √⟨|u|²⟩/a_nn at the triangular lattice, with total 2D rms displacement and
     the nearest-neighbour distance a_nn. This is the convention of the QMC values we cite.
   - At the spinodal ħ*, γ ranges from 0.280 (a = 0.6–0.7) to 0.51 (a = 0.4, 1.4) and 0.74 (a = 1.5).
   - At the first-order point Λ_1, γ = 0.245–0.298 for a in [0.45, 1.1], and up to 0.44 outside that range.
   - Verified QMC Lindemann ratios at quantum melting of 2D boson crystals are 0.230(6) (dipoles), 0.235(15) (Yukawa),
     0.24(1) (Coulomb bosons) and 0.279 (hard disks) (section B1d).
   - Only for a ≈ 0.5–1.0 does the harmonic Λ_1 sit *inside* the γ_c band 0.23–0.28. Everywhere else the harmonic
     transition lies at or beyond the Lindemann point.
   - Because ⟨u²⟩ ∝ ħ_eff, the melting coupling Λ_L scales like γ_c². A 10 % uncertainty in γ_c is a 21 % uncertainty
     in Λ_L. The textbook's Coulomb case has r_s* ∝ γ_c⁻⁴, which is a different exponent.
3. **B1c (anharmonic, SCHA): the transition DISAPPEARS before melting (prior "survives" 0.25 → refuted). This is the
   preregistered kill condition, so the result is negative.**
   - In the T = 0 self-consistent harmonic approximation, the triangular lattice is a local minimum, Lap E_SCHA(ρ) > 0,
     far beyond the harmonic ħ*. At a = 1, Lap E_SCHA = +0.117 at ħ_eff = 0.15, where the harmonic value is −0.101, and
     +0.008 at ħ_eff = 0.30.
   - The SCHA spinodal is 0.274 at a = 0.5, 0.308 at a = 0.7 and 0.294 at a = 1.3. At a = 1 it lies in (0.30, 0.335):
     Lap E_SCHA = +0.008 at 0.30, and at 0.335 both mirror paths give ΔE < 0 at the smallest r.
   - The triangular lattice also stays the lowest of every sampled stable competitor at ħ_eff up to the SCHA spinodal.
     This includes the harmonic Λ_1 winner, which is 2.6e-5 *above* triangular at a = 1, ħ_eff = Λ_1. The first
     sampled ħ_eff with a lower stable competitor is the SCHA spinodal itself (0.27–0.31; 0.33 at a = 1).
   - There the SCHA Lindemann ratio is 0.60–0.87, more than twice γ_c. The crystal has long melted by any Lindemann
     estimate.
   - A continuation-seeded SCHA run reaches 103–114 shapes beyond the harmonic stability edge (a = 1 and 0.5;
     ħ_eff = Λ_1, ħ*, 0.2). None of them lies below triangular.
   - This holds *within SCHA*, which omits the second-order cubic O(ħ²) term. The negative net verdict also rests on
     B1b: the harmonic ħ* is at or beyond the Lindemann point for every a.
   - Path-integral Monte Carlo was **not run (BLOCKED)**; the reasons are in section B1c.
4. **B1d (literature): no cluster/supersolid preemption for the Gaussian itself; preemption by ordinary quantum melting
   is what the numbers show.**
   - Cluster crystals and supersolid droplet crystals need a negative Fourier component of V. The Gaussian has none: it
     is the marginal GEM-2 case, with no cluster crystal in 2D or 3D.
   - Rydberg-dressed atoms realise a soft-shoulder potential U₀/(1+(r/R_c)⁶) whose Fourier transform does have negative
     parts. That platform is therefore governed by cluster/supersolid physics, not by this Gaussian-model transition.
   - No QMC study of the quantum Gaussian-core model was found, so no ab-initio melting line is available.

**Net result (negative):** the harmonic theory predicts a first-order triangular → oblique/rhombic instability at
Λ_1 ≈ 0.07–0.13 (spinodal ħ* ≈ 0.09–0.18) for a ≈ 0.45–1.3. It is an artefact of the harmonic approximation:
- it sits at or beyond the Lindemann melting estimate;
- the self-consistent anharmonic theory removes it up to ħ_eff ≈ 0.27–0.31 or more, where γ_SCHA ≈ 0.6–0.75.

The P2 result, that the triangular lattice is a local maximum of E_zp, stands as a statement about the harmonic
functional. It does not translate into a structural transition of the quantum crystal.

## Units and setup

- **Potential and parameter.** g(r²) = ε exp(−π a r²) at unit density (l² = 1/ρ), mass m, and
  ħ_eff = ħ/√(m ε l²).
- **Energy per particle (harmonic).** E = E_static + ħ_eff E_zp, with:
  - E_static = ½ Σ_{R≠0} e^{−π a|R|²};
  - E_zp = ½ ⟨√λ₁ + √λ₂⟩_BZ;
  - D(k) = Σ_{R≠0} (1 − cos k·R) Hess V(R), the same normalisation as P2;
  - ⟨|u|²⟩/l² = (ħ_eff/2) ⟨tr D^{−1/2}⟩_BZ;
  - a_nn = √(2/√3) = 1.0746.
- **Conversion to GCM units.** In the units V = ε e^{−r²/σ²} of the Gaussian-core-model literature, ρσ² = 1/(πa) and
  ħ/√(mεσ²) = ħ_eff √(πa).
- **Shape.** τ = x + iy with basis a1 = (1/√y, 0), a2 = (x/√y, √y). D(k) is taken from the reciprocal-space (Poisson)
  form, and BZ integrals use the Duffy–Gauss rule: four triangles with apex at Γ, which removes the |k| singularity of
  E_zp and the 1/|k| singularity of ⟨u²⟩.
- **Acoustic k → 0.** In 2D at T = 0, ⟨u²⟩ = ∫ d²k/ω ∝ ∫ dk is finite. The Duffy Jacobian ∝ s cancels the 1/|k|; see
  control 2 for the quadrature.
- **Curvature.** c = Lap F/4, with Lap = y²(∂xx + ∂yy) at ρ, so that F(τ) − F(ρ) = c |τ−ρ|²/y_ρ² + O(r³). The curvature
  is isotropic by the order-3 stabiliser (P2 PROOF.md 3.1); the stencil isotropy check gives f_xx = f_yy to 1.3e-6.
- **Where c comes from.**
  - c_static is the exact pair sum of h(u) = (u² f′)′ (P2's Lean-checked `gauss_h`).
  - c_zp comes from a Richardson five-point stencil on E_zp with Duffy N = 48. The N = 64 values agree to 1e-6.

## B1a: ħ*(a) and Λ_1(a) (harmonic)

The table is generated by `code/b1_summary.py`; the data are in `data/b1a_curvature.json`, `data/scan_a*.json`/`.csv`
and `data/summary.json`. Column definitions:

- **margin** is min over the zone of λ_lo(D)/|k|². The triangular lattice has margin 0.034 at a = 1.
- **Λ_1 edge** is the smallest tie coupling over the 0.005 grid of shapes in 0.15 ≤ x ≤ 0.5,
  max(√(1−x²), 0.8) ≤ y ≤ 1.15. Stability is screened on a 48² grid plus long-wave directions. The 12 best shapes were
  re-verified with the P2 optimiser (n = 192 seeds, Nelder–Mead, long-wave rows), with E_zp at Duffy N = 64.
- **Λ_1 margin ≥ 0.01** keeps only shapes with screened margin ≥ 0.01.
- **γ** is the harmonic Lindemann ratio at the triangular lattice.
- **Λ_L(γ_c)** = γ_c² a_nn² / (⟨u²⟩/ħ_eff) is the harmonic Lindemann melting coupling.

| a | rho sigma^2 | c_static | c_zp | hbar* | gamma(hbar*) | Lam_1 edge (tau) | Lam_1 margin>=0.01 | gamma(Lam_1 edge) | Lam_L(0.23) | Lam_L(0.28) | SCHA Lam* |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.3 | 1.061 | 0.00171 | +0.17814 | none (c_zp>0) | - | none | none | - | 0.0167 | 0.0247 | - |
| 0.4 | 0.796 | 0.01385 | -0.07992 | 0.1732 | 0.505 | 0.1307 (0.500, 1.000) | none | 0.438 | 0.0360 | 0.0533 | - |
| 0.45 | 0.707 | 0.02569 | -0.26876 | 0.0956 | 0.337 | 0.0746 (0.305, 0.955) | 0.0826 (0.355, 0.935) | 0.298 | 0.0445 | 0.0660 | - |
| 0.5 | 0.637 | 0.04041 | -0.46052 | 0.0877 | 0.299 | 0.0683 (0.305, 0.955) | 0.0725 (0.335, 0.945) | 0.264 | 0.0518 | 0.0767 | 0.2745 |
| 0.6 | 0.531 | 0.07239 | -0.78641 | 0.0921 | 0.280 | 0.0714 (0.305, 0.955) | 0.0737 (0.320, 0.950) | 0.247 | 0.0621 | 0.0921 | - |
| 0.7 | 0.455 | 0.09926 | -0.99008 | 0.1003 | 0.280 | 0.0769 (0.300, 0.955) | 0.0793 (0.315, 0.955) | 0.245 | 0.0677 | 0.1004 | 0.3076 |
| 0.8 | 0.398 | 0.11582 | -1.07073 | 0.1082 | 0.286 | 0.0826 (0.300, 0.960) | 0.0848 (0.310, 0.955) | 0.250 | 0.0697 | 0.1034 | - |
| 0.9 | 0.354 | 0.12174 | -1.05214 | 0.1157 | 0.298 | 0.0883 (0.300, 0.960) | 0.0908 (0.310, 0.955) | 0.260 | 0.0692 | 0.1025 | - |
| 1 | 0.318 | 0.11913 | -0.96198 | 0.1238 | 0.313 | 0.0942 (0.300, 0.960) | 0.0973 (0.310, 0.955) | 0.273 | 0.0668 | 0.0990 | - |
| 1.1 | 0.289 | 0.11074 | -0.82467 | 0.1343 | 0.335 | 0.1023 (0.300, 0.955) | 0.1071 (0.315, 0.955) | 0.292 | 0.0632 | 0.0937 | - |
| 1.2 | 0.265 | 0.09908 | -0.65980 | 0.1502 | 0.367 | 0.1131 (0.300, 0.955) | 0.1207 (0.315, 0.950) | 0.319 | 0.0590 | 0.0874 | - |
| 1.3 | 0.245 | 0.08609 | -0.48237 | 0.1785 | 0.417 | 0.1313 (0.460, 1.040) | 0.1358 (0.465, 1.030) | 0.357 | 0.0544 | 0.0806 | 0.2943 |
| 1.4 | 0.227 | 0.07307 | -0.30355 | 0.2407 | 0.506 | 0.1426 (0.485, 1.040) | 0.1524 (0.500, 1.025) | 0.390 | 0.0496 | 0.0736 | - |
| 1.5 | 0.212 | 0.06088 | -0.13140 | 0.4633 | 0.738 | 0.1672 (0.500, 1.035) | 0.1849 (0.500, 1.020) | 0.443 | 0.0450 | 0.0667 | - |
| 2 | 0.159 | 0.02020 | +0.49451 | none (c_zp>0) | - | none | none | - | 0.0253 | 0.0375 | - |

Further results:

- **Isotropy check.** The two mirror-line paths at a = 1 (`fig_b1_hbar_star.png`, right) both start at
  ħ* = 0.1238 as r → 0, which checks that the curvature is isotropic.
- **Arc |τ| = 1 towards i.** The tie coupling decreases monotonically: 0.1237 at r = 0.003, 0.1172 at r = 0.10 and
  0.1019 at r = 0.22. Every point on this path is stable, with margin 0.028–0.061.
- **Line Re τ = 1/2 upwards.** The tie coupling rises to 0.1248 at r ≈ 0.06, then decreases. These are the opposite
  signs of the cubic term on the two inequivalent mirror rays.
- **First order (Landau, D3 cubic invariant).** At a = 1 and ħ_eff = 0.10 < ħ* = 0.124, the triangular lattice is a
  strict local minimum. Yet the stable oblique lattice 0.30 + 0.96i lies 2.9e-4 lower per particle (`ladder` in
  `scan_a1.json`). Above Λ_1 the argmin over the stable sample jumps from τ = ρ to that edge region, with no
  continuous growth of the distortion.
- **Negative controls.**
  - a = 0.30 has c_zp = +0.178 and a = 2.0 has c_zp = +0.495, so neither has an ħ*.
  - In both, no stable sampled shape has a lower harmonic E at any ħ_eff in the ladder 0.02–0.3; in fact no stable
    shape has ΔE_zp < 0 at all.
  - a = 0.378, just inside a1, gives c_zp = −0.0043 and ħ* = 2.29, consistent with the sign change at a1 = 0.37668.

## B1b: Lindemann comparison

- **Literature anchors (verified, B1d).**
  - Astrakharchik, Boronat, Kurbakov and Lozovik, arXiv:cond-mat/0608246 (PRL 2007), p. 3: "We estimate the
    thermodynamic Lindemann ratio γ = √⟨(r − r_c)²⟩/a_L, (a_L is the lattice length), at the transition density as
    γ = 0.230(6). Comparing to other two-dimensional systems we find that this value is smaller than the one of a
    hard-disks γ = 0.279, while is similar to more long-ranged potentials, like γ = 0.235(15) for Yukawa bosons and
    γ = 0.24(1) for Coulomb bosons." These are QMC values of the *true* ⟨u²⟩: total 2D, absolute, over the
    nearest-neighbour spacing. That is our convention: the same page gives a_L⁻¹ = (√3n/2)^{1/2}, i.e.
    a_L = a_nn = 1.0746 at n = 1.
  - The textbook section (`papers/textbook_universal_optimality/sec_quantum_melting.tex`, facts_qm.md) gives the
    *harmonic* γ at the QMC Wigner-crystal transition (r_s = 31(1), Drummond–Needs): 0.301. That is about 1.3 times
    the QMC-measured boson values. Our reading of this gap (Tier C, untested) is that it is the difference between the
    harmonic and the true ⟨u²⟩; it also compares a Coulomb (fermion) system with bosons.
- **Comparison band.** We therefore compare the harmonic γ with the band 0.23–0.30.
- **Results.**
  - At ħ*, γ ≥ 0.28 everywhere: 0.28 at a = 0.6–0.7, rising to 0.3–0.74 towards both ends.
  - At Λ_1, γ is 0.245–0.273 for a = 0.5–1.0, inside the band, and 0.29–0.44 elsewhere.
  - **Verdict:** the spinodal lies beyond melting. The first-order point is at best marginal, and only for a ≈ 0.5–1.0,
    and only within harmonic theory.
- **Anharmonic ⟨u²⟩ is larger.** The SCHA ⟨u²⟩ at the same ħ_eff exceeds the harmonic one: at a = 1, Λ_1 = 0.0942,
  γ_SCHA = 0.287 against γ_harm = 0.273. This pushes the comparison further towards "melted first".
- **Sensitivity.** Λ_L = γ_c² a_nn²/(⟨u²⟩/ħ_eff), so γ_c → 0.9 γ_c multiplies Λ_L by 0.81 and γ_c → 1.1 γ_c by 1.21.
  The textbook's Coulomb case has r_s* ∝ γ_c⁻⁴ (0.9⁻⁴ = 1.52); here the dependence is quadratic, because ⟨u²⟩ is
  linear in ħ_eff at fixed a. It is a heuristic in both cases: Lindemann is a rule of thumb, not a theorem.

## B1c: anharmonic check

### SCHA (T = 0)

- **Method.**
  - The trial state is the ground state of a harmonic crystal with an effective dynamical matrix D_eff.
  - The pair-displacement covariance is C_R = ħ_eff ⟨(1 − cos k·R) D_eff^{−1/2}⟩.
  - For the Gaussian, both averages are closed form:
    - ⟨V(R+w)⟩ = det(I + 2πaC)^{−1/2} exp(−πa Rᵀ(I + 2πaC)^{−1}R);
    - ⟨Hess V(R+w)⟩ is the Hessian of that function.
  - The energy is E_SCHA = (ħ_eff/4)⟨tr D_eff^{1/2}⟩ + ½ Σ_R ⟨V(R + w_R)⟩, made stationary by
    D_eff = Σ(1 − cos k·R)⟨Hess V⟩ and solved by mixing iteration to |ΔE| < 1e-14.
  - The SCHA curvature is taken **from the SCHA energy of each shape** (stencil). This is the true curvature of the
    SCHA energy surface, not the auxiliary D_eff, so the "bubble" term of the SCHA free-energy Hessian is included
    implicitly.
- **Code.** `code/b1_lib.py` (class `SCHA`) and `code/b1c_scha.py`, with an independent second implementation in Rust:
  `rusty-SUNDIALS-wt-p2`, `crates/qf-yukawa-crystal/src/scha.rs`, commit `9e85e15b23be0c74a665b6a5b74ec02b0bbffc5f`
  (not pushed).
- **Controls (`code/t_scha.py`, Rust tests).**
  - ħ_eff → 0 gives the harmonic energy, with remainder 0.177 ħ_eff² (doubling ħ_eff multiplies the remainder by
    3.84).
  - The converged D_eff is a variational minimum: scaling it by 0.97 or 1.03, or interpolating towards the bare D,
    raises E by 1.3e-5 to 1.2e-4.
  - N = 24/32/48 nodes agree to 3e-11, and a wider R cutoff changes nothing.
  - The small-ħ_eff slope of the SCHA curvature matches the harmonic one (`code/t_scha_slope.py`,
    `data/scha_slope_control.json`). At a = 1, (Lap E_SCHA − Lap E_static)/ħ_eff = −3.807, −3.769 and −3.697 at
    ħ_eff = 0.0025, 0.005 and 0.01. Linear extrapolation gives −3.846, against the harmonic 4 c_zp = −3.848. The SCHA
    curvature is therefore consistent with harmonic theory at leading order, and the stiffening is an
    O(ħ_eff²) effect, coefficient ≈ +15 at a = 1.
  - Python and Rust agree to 2e-16: E_SCHA(a = 1, ρ, 0.1) = 0.226749898820164 in both.
  - Negative controls: the square lattice has no SCHA solution at ħ_eff = 1e-3 when the iteration is started from the
    bare D (this is a seeding statement, not a statement about large ħ_eff), and the iteration loses positive
    definiteness above a breakdown ħ_eff.

| a | harmonic hbar* | harmonic Lam_1 | Lap E_SCHA(rho) at hbar_eff = 0.05 / 0.10 / 0.15 / 0.20 / 0.30 (harmonic Lap at 0.10) | SCHA spinodal Lam*_SCHA | gamma_SCHA at Lam*_SCHA | SCHA: gamma at harmonic Lam_1; min dE of stable sampled competitors there | first sampled Lam with a stable competitor below triangular (gamma_SCHA) | SCHA breakdown at rho |
|---|---|---|---|---|---|---|---|---|
| 0.5 | 0.0877 | 0.0683 | +0.103 / +0.077 / +0.058 / +0.037 / -0.013 (-0.023) | 0.2745 | 0.60 | 0.267; +1.17e-05 | 0.2745 (0.60) | 0.617 |
| 0.7 | 0.1003 | 0.0769 | +0.238 / +0.146 / +0.099 / +0.069 / +0.006 (+0.001) | 0.3076 | 0.67 | 0.261; +2.29e-05 | 0.3076 (0.67) | 0.518 |
| 1 | 0.1238 | 0.0942 | +0.313 / +0.193 / +0.117 / +0.078 / +0.008 (+0.092) | in (0.30, 0.335) (Lap = +0.008 at 0.30; ΔE < 0 at the smallest r on both paths at 0.3347) | 0.67–0.87 | 0.287; +2.58e-05 | 0.3347 (0.87) | 0.427 |
| 1.3 | 0.1785 | 0.1313 | +0.259 / +0.174 / +0.105 / +0.068 / -0.008 (+0.151) | 0.2943 | 0.75 | 0.358; +1.60e-05 | 0.2943 (0.75) | 0.370 |

- **Reading of the table.**
  - At every a, anharmonic stiffening of the shear response makes Lap E_SCHA(ρ) fall far more slowly with ħ_eff than
    the harmonic 4(c_static + ħ_eff c_zp).
  - At the harmonic Λ_1, every sampled stable competitor lies *above* the triangular lattice in SCHA. These are the
    arc and line paths out to r = 0.22 plus the harmonic edge winners.
  - Competitors below triangular appear only at ħ_eff ≥ 0.27–0.33, where γ_SCHA ≥ 0.6.
- **Beyond the harmonic stability edge (continuation, `code/b1c_scha_extend.py`, `data/scha_extend.json`).** The plain
  solve starts from the bare D, so it rejects every harmonically unstable shape by construction. This run seeds each
  shape with the converged D_eff of its neighbour instead.
  - Shapes covered: the arc |τ| = 1 from ρ all the way to i (step 0.01 in angle); Re τ = ½ from ρ up to y = 1.30; and
    a strip x ∈ [0.15, 0.30], y from the arc to 1.12. That is 150 shapes per case.
  - Cases: a = 1 and 0.5, at ħ_eff = harmonic Λ_1, harmonic ħ* and 0.2.
  - 144–150 shapes are SCHA-stable (converged, stability_eff > 0). Of these, 103–114 are harmonically **unstable**:
    anharmonicity stabilises them.
  - **In all six cases no SCHA-stable shape lies below the triangular lattice** (n_below_triangular = 0). The lowest
    competitor is always the arc point nearest ρ, with ΔE = +1.2e-6 to +6.6e-6.
  - The lowest shape beyond the harmonic edge lies +3.0e-4 to +1.7e-3 above triangular. For example, at a = 1 and
    ħ_eff = Λ_1 the shape 0.289 + 0.957i is +1.7e-3 above.
  - So the SCHA verdict is not an artefact of seeding at the harmonic edge.
- **Near the SCHA breakdown** the results are not reliable and no claim is made there:
  - at a = 1, ħ_eff ≥ 0.33, the sign of ΔE fluctuates between neighbouring ħ_eff values (`data/scha.json`);
  - at a = 0.5, Lap E_SCHA is −0.013 at 0.30 but +0.003 at 0.50 (breakdown 0.617), an apparent re-entrance;
  - this regime has γ_SCHA > 0.6, outside any crystal description.
- **Limits of SCHA (Tier C caveats).**
  - The SCHA is a Gaussian variational approximation. Its O(ħ_eff²) energy contains the quartic anharmonicity at first
    order but not the second-order cubic term, so it is not an exact anharmonic expansion.
  - It does not describe exchange or melting itself.
  - The stiffening is itself an O(ħ_eff²) effect (slope control: coefficient ≈ +15 at a = 1), which is exactly the order
    at which SCHA is incomplete. So B1c holds *within SCHA*. The negative net verdict does not rest on SCHA alone: B1b
    already puts the harmonic spinodal ħ* at or beyond the Lindemann point (γ ≥ 0.28) for every a.

### Path-integral Monte Carlo: BLOCKED (not run)

`code/b1c_pimc_feasibility.py` and `data/pimc_feasibility.json` quantify why a 1–2 point PIMC within a few hours on 2
cores cannot decide the question:

1. **A fixed periodic box commensurate with the triangular lattice imposes the shape.** Seeing a distortion requires
   cell-shape moves at fixed area, i.e. sampling τ. That move set is not implemented.
2. **Finite size.** An M×M cell sees only the Γ-centred M×M k-grid. At a = 1, ħ_eff = 0.10, for the competitor
   0.30 + 0.96i:
   - the thermodynamic-limit gap is ΔE = −2.86e-4 per particle;
   - the finite-size shift of ΔE is −2.0e-4 at M = 8 (N = 64) and −2.0e-5 at M = 12 (N = 144).
3. **Thermal smearing of the shape.** N|ΔE| is 0.018 at N = 64 and 0.041 at N = 144. So k_BT ≪ 0.04 ε would be needed
   for a clear shape preference. Meanwhile ground-state conditions require k_BT ≪ ħω_min ≈ 0.027 at M = 12, which
   implies β ≳ 250 and roughly 200+ time slices × 144 particles.
4. **No PIMC was needed for the verdict.** The SCHA already shows the instability is absent up to γ ≈ 0.6. At the
   harmonic Λ_1 a PIMC would be probing a crystal whose harmonic γ (0.27) is at the Lindemann threshold. Exchange of
   bosons, which the SCHA does not have, matters there too.

## B1d: literature (Tier L)

All quotes were obtained through alphaXiv (`answer_pdf_queries`). Two of them I re-read myself:
arXiv:1809.07515 (Sec. II, p. 11; Sec. III, p. 15; Conclusions, p. 25) and arXiv:cond-mat/0608246 (p. 3, quoted
above). The rest come from a literature subagent's alphaXiv reading and are marked [sub].

- **Quantum Gaussian-core model.** No QMC or PIMC study of bosons with a Gaussian pair potential was found in three
  targeted searches [sub]. That is "not found", not "does not exist". The only quantum result is mean-field,
  Prestipino, Sergi and Bruno, arXiv:1809.07515 (Gross–Pitaevskii plus Gaussian variational, weak-coupling regime):
  - p. 11: "The Gaussian repulsion (n = 2) is a marginal case: despite there is no evidence of a cluster crystal in
    two or three dimensions, clear hints of clusterization are detected in one dimension."
  - p. 15: "for n = 2 (where ũ(k) is everywhere positive) crystallization is swept away at zero temperature."
  - p. 25: "freezing is completely washed out in the Gaussian, n = 2 case."
  - Those are statements about mean-field (cluster) crystallization at high density and weak coupling. Our crystal is
    the opposite regime: one particle per site, ħ_eff → 0. The paper says the mean-field is "realistic for weak
    interparticle forces".
- **Cluster crystals and supersolid droplet crystals.**
  - Cinti, Boninsegni and Pohl, arXiv:1402.0840: the droplet crystal needs "the presence of a negative Fourier
    component" [sub].
  - Boninsegni review, arXiv:1201.0980, Sec. 2.3: a necessary condition for supersolidity "may be that the Fourier
    transform of the two-body potential go negative" [sub].
  - Mendoza-Coto et al., arXiv:2010.04631, Sec. III.B: the GCM "is a bounded potential for which the Likos' criterion
    predicts no cluster-crystal phases at high density … α = 2 corresponds exactly to the boundary of the
    cluster-forming ability" [sub].
  - Likos et al., PRE 2001, could not be opened.
  - **Verdict:** cluster or supersolid phases do not preempt the single-occupancy Gaussian crystal. What preempts the
    harmonic transition is ordinary quantum melting, per the Lindemann estimate and SCHA above.
- **Classical 2D GCM.**
  - Prestipino, Saija and Giaquinta, arXiv:1107.0828, p. 2: "the most stable state of the GCM at zero temperature is a
    triangular crystal for any pressure P", with "a maximum melting temperature T_m of about 0.0115" (ε/k_B) [sub].
    This is consistent with our static control: triangular is the Montgomery minimiser.
  - Melting temperatures fall to about 0.004 ε at ρσ² ≈ 0.7 (a ≈ 0.45) [sub, arXiv:2209.02802 and 2307.09327, read
    from figures and reduced units; not precise].
- **Rydberg dressing.**
  - Henkel, Nath and Pohl, arXiv:1001.3250: "the momentum space potential Ũ has negative attractive contributions
    around k_rot ∼ 2π/R_c", so the potential is not Gaussian-like in the sense that matters (Q±) [sub].
  - Their parameters give m U₀ R_c²/ħ² < 10⁻², i.e. ħ/√(mU₀R_c²) > 10: deep mean-field.
  - Zeiher et al., arXiv:1602.06313: U₀/2π ≈ 1.8 kHz and R_c ≈ 2.02 × 532 nm for ⁸⁷Rb [sub]. This gives
    ħ/√(mU₀R_c²) ≈ 0.24 (arithmetic: ħ²/(mR_c²)/h ≈ 100.5 Hz, 1800/100.5 = 17.9). The atoms were pinned in a lattice,
    and the dressed-state lifetime (~27 µs) is far shorter than motional time scales.
  - **Verdict:** Rydberg-dressed gases do not realise the Gaussian. Their soft shoulder belongs to the cluster/supersolid
    class. The reachable ħ/√(mU₀R_c²) (in units of the soft-core radius R_c, not of l) spans about 0.2 (pinned,
    short-lived) to more than 10 (condensates). The soft shoulder has no Gaussian width a, so these numbers cannot be
    compared directly with our ħ_eff window (0.07–0.18 at a ≈ 0.45–1.3); none of them is a demonstrated itinerant
    realisation of that window. No cold-atom or molecular realisation of a true Gaussian interaction was found [sub].

## Controls (`code/b1_controls.py`, `data/controls.json`, `code/t_smoke.py`)

- **Positive control 1: harmonic phonons against finite-difference forces (frozen phonon).** We take the second
  difference of the explicit supercell pair-sum energy (6×6 cells, all images, values of V only) with u = ε e cos(k·R),
  ε = 1e-3. It equals ½ eᵀD(k)e from the Poisson D. The test covers 12 cases: a = 0.5, 1, 1.4; triangular, the edge
  competitor 0.30 + 0.96i and an oblique shape; 3 (k, e) each. Maximum relative difference: 6.3e-6 (the O(eps^2) quartic remainder at eps = 1e-3). The planted bug
  (dropped Γ-subtraction term of D) gives 0.52, so the control can fail.
- **Positive control 2: P2 reference values reproduced.**
  - E_zp(a = 1, ρ) = 1.5033523522;
  - E_zp(0.5 + 0.966i) = 1.4902783183;
  - Lap E_static(1) = 0.4765235167, exact and stencil within 2e-10;
  - c_zp(1) = −0.96198;
  - the c(a) table matches P2 PROOF.md 3.4, e.g. −0.4605 at a = 0.5 and +0.4945 at a = 2.
- **Positive control 3: Lindemann quadrature.** ⟨tr D^{−1/2}⟩ by Duffy N = 16/32/64/128 is converged to 1e-13. Uniform
  half-shifted grids n = 64…1024 converge to the Duffy value with observed order 1.000 (a = 0.5 and 1.0), the n⁻¹ expected from the
  1/|k| singularity. So the acoustic k → 0 region is handled.
- **Negative controls.** a = 0.30 and a = 2.0 (outside (a1, a2)) give c_zp > 0, no ħ* and no lower stable competitor
  (B1a). The square lattice is flagged unstable in both the harmonic and the SCHA code.

## Figures (code-generated, `code/b1_summary.py`)

- `figures/fig_b1_hbar_star.png`:
  - left: ħ*(a), Λ_1(a) (edge, and margin ≥ 0.01), the harmonic Lindemann band (γ_c 0.23–0.28) and SCHA spinodals;
  - right: tie coupling along the two mirror lines at a = 1.
- `figures/fig_b1_scha_curvature.png`: Lap E(ρ) against ħ_eff, SCHA (solid) versus harmonic (dashed), with the harmonic
  Lindemann γ_c = 0.23 coupling (dotted).

## What is not claimed

- No Lean statement: everything in B1a–B1c is Tier X.
- Only Bravais lattices, one particle per cell. Non-Bravais, striped, cluster or liquid phases are not part of the
  energy comparison, except through the Lindemann and literature arguments.
- The harmonic Λ_1 winners sit on the harmonic stability boundary. The phase that would follow in an exact treatment is
  undetermined.
- The SCHA is an approximation (see its caveats). PIMC was not run.
- The Lindemann criterion is a heuristic, and γ_c carries the uncertainty stated in B1b.
- Literature items marked [sub] were read through alphaXiv by a subagent and not re-read by me.

## Commands (cores 6,7, ≤ 2 threads)

```
PY=/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I ; B=results/proposal2/2026-10-26/B1
taskset -c 6,7 $PY $B/code/t_smoke.py ; taskset -c 6,7 $PY $B/code/t_scha.py ; taskset -c 6,7 $PY $B/code/t_scha2.py
taskset -c 6,7 $PY $B/code/b1a_curvature.py $B/data/b1a_curvature.json               # 1 min
taskset -c 6,7 $PY $B/code/b1a_scan.py $B/data 1.0 0.3 0.4 0.45 0.5 0.6 0.7 0.8 0.9 1.1 1.2 1.3 1.4 1.5 2.0   # ~12 min
bash $B/code/run_stage2.sh                                                            # controls + SCHA, ~70 min
taskset -c 6,7 $PY $B/code/t_scha_slope.py $B/data/scha_slope_control.json ; taskset -c 6,7 $PY $B/code/b1c_scha_extend.py $B/data/scha_extend.json
$PY $B/code/t_scan_domain.py $B/data                                                  # no stable scan point on the domain boundary
taskset -c 6,7 $PY $B/code/b1c_pimc_feasibility.py $B/data/pimc_feasibility.json
taskset -c 6,7 $PY $B/code/b1_summary.py $B                                          # tables, figures, result_numbers.json
bash $B/code/rust_check.sh ; bash $B/code/rust_clippy.sh                             # 63 tests pass; clippy exit 0
/home/callensxavier_gmail_com/rusty-target-ar/release/lattice_phonon scha 1 0.5 0.8660254037844386 0.1 32
```
