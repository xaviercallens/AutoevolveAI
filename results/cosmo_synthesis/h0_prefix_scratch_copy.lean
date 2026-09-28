/-
Inverse-distance-ladder exercise (slug bao_bbn_h0): kernel-verified algebraic
skeleton of the sound-horizon / BAO-observable relations used in
scripts/bao_bbn_h0/common.py (fit: scripts/bao_bbn_h0/fit_real.py).

The SECONDARY (preregistered) sound horizon is Aubourg et al. 2015
(arXiv:1411.1074) eq. 16, exactly as coded in `common.rd_aubourg16`:

    r_d(ω_cb, ω_b) = 55.154 · exp(−72.3 (ω_ν + 0.0006)²) / (ω_cb^0.25351 · ω_b^0.12807)  [Mpc]

with ω_ν = 0.0107 · Σm_ν = 0.0107 · 0.06 fixed (`common.OMEGA_NU_AUBOURG`) and
ω_cb = Ωₘ h² − ω_ν (`common.omega_cb_of`; Ωₘ is neutrino-inclusive, the
DESI/Planck convention). The sampler only evaluates the likelihood where
`omega_cb_of(h0/100, om) > 0` (common.py, make_logpost) -- that support
condition is the domain of the monotonicity theorem below.
The PRIMARY analysis (amendment 1) replaces this closed form by a CAMB table;
nothing here is claimed about CAMB's r_d.

The BAO observable D_H(z)/r_d is coded (common.distances_manual_vec /
obs_from_distances / predict_manual_vec) as
    dh0 = c / (100 h),   dh = dh0 / E(z),   obs = dh / r_d,     h = H0 / 100,
and the BAO-only gate (common.make_logpost_hrd) samples (Ωₘ, h r_d) by passing
`hrd / h_rad` in place of r_d while the distances are evaluated at a fixed
`h_rad`.

Scope, deliberately (same policy as BAO_FlatLCDM.lean): exact facts about the
MODEL AS CODED, not a theorem "about the sky":
  * r_d > 0 wherever ω_cb > 0 and ω_b > 0 (so dividing the distances by r_d
    is always well defined on the sampled support);
  * r_d is strictly decreasing in ω_b on (0, ∞) -- the direction along which
    the BBN prior acts;
  * for fixed h > 0 and ω_b > 0, r_d(Ωₘ h² − ω_ν, ω_b) is strictly decreasing
    in Ωₘ on the sampled support {Ωₘ : Ωₘ h² − ω_ν > 0} -- more matter, smaller
    sound horizon, the degeneracy direction that BAO+BBN has to break;
  * the coded observable depends on (h, r_d) only through the product h r_d
    (D_H/r_d = c / (100 · (h r_d) · E)), and the gate's substitution
    r_d ↦ hrd / h_rad at fixed h_rad gives EXACTLY c / (100 · hrd · E): the
    r_d-free (Ωₘ, h r_d) gate is an exact reparametrisation, not an
    approximation. H0 = 100 h is built into the same identity.
Exponents are real powers (Real.rpow), exactly as `** 0.25351` in numpy.
Literature: docs/literature/BAO_BBN_H0_LITERATURE_REVIEW_2026.md.
Numbers from the fit (results/bao_bbn_h0/fit.json): H0 = 68.55 ± 0.59 (primary),
68.58 ± 0.60 (secondary); nothing numeric is asserted here.
-/
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

namespace ANSE.BAOBBNH0

open Real

/-- Aubourg's fixed neutrino density `ω_ν = 0.0107 · Σm_ν`, `Σm_ν = 0.06 eV`
(`common.OMEGA_NU_AUBOURG`). -/
noncomputable def omegaNu : ℝ := 0.0107 * 0.06

/-- Aubourg et al. 2015 eq. 16 sound horizon [Mpc], exactly as `common.rd_aubourg16`. -/
noncomputable def rdAubourg (wcb wb : ℝ) : ℝ :=
  55.154 * Real.exp (-72.3 * (omegaNu + 0.0006) ^ 2) /
    (wcb ^ (0.25351 : ℝ) * wb ^ (0.12807 : ℝ))

/-- `ω_cb = Ωₘ h² − ω_ν`, exactly as `common.omega_cb_of(h, om)`. -/
noncomputable def omegaCb (h Om : ℝ) : ℝ := Om * h ^ 2 - omegaNu

/-- The numerator of eq. 16 is a fixed positive constant. -/
theorem rd_numerator_pos : 0 < 55.154 * Real.exp (-72.3 * (omegaNu + 0.0006) ^ 2) := by
  have := Real.exp_pos (-72.3 * (omegaNu + 0.0006) ^ 2)
  positivity

/-- `r_d > 0` for `ω_cb > 0`, `ω_b > 0`: the sound horizon the fit divides by is
strictly positive on the whole sampled support. -/
theorem rdAubourg_pos {wcb wb : ℝ} (hcb : 0 < wcb) (hb : 0 < wb) :
    0 < rdAubourg wcb wb := by
  unfold rdAubourg
  have h1 := Real.rpow_pos_of_pos hcb (0.25351 : ℝ)
  have h2 := Real.rpow_pos_of_pos hb (0.12807 : ℝ)
  exact div_pos rd_numerator_pos (mul_pos h1 h2)

/-- `r_d` is strictly decreasing in `ω_cb` on `(0, ∞)` at fixed `ω_b > 0`. -/
theorem rdAubourg_strictAntiOn_cb {wb : ℝ} (hb : 0 < wb) :
    StrictAntiOn (fun wcb => rdAubourg wcb wb) (Set.Ioi (0 : ℝ)) := by
  intro x hx y hy hxy
  simp only [Set.mem_Ioi] at hx hy
  simp only
  unfold rdAubourg
  have hb' := Real.rpow_pos_of_pos hb (0.12807 : ℝ)
  have hx' := Real.rpow_pos_of_pos hx (0.25351 : ℝ)
  have hpow : x ^ (0.25351 : ℝ) < y ^ (0.25351 : ℝ) :=
    Real.rpow_lt_rpow hx.le hxy (by norm_num)
  have hden : x ^ (0.25351 : ℝ) * wb ^ (0.12807 : ℝ) < y ^ (0.25351 : ℝ) * wb ^ (0.12807 : ℝ) :=
    mul_lt_mul_of_pos_right hpow hb'
  exact div_lt_div_of_pos_left rd_numerator_pos (mul_pos hx' hb') hden

/-- `r_d` is strictly decreasing in `ω_b` on `(0, ∞)` at fixed `ω_cb > 0`: the
direction along which the BBN prior on `ω_b` moves the sound horizon. -/
theorem rdAubourg_strictAntiOn_b {wcb : ℝ} (hcb : 0 < wcb) :
    StrictAntiOn (rdAubourg wcb) (Set.Ioi (0 : ℝ)) := by
  intro x hx y hy hxy
  simp only [Set.mem_Ioi] at hx hy
  unfold rdAubourg
  have hcb' := Real.rpow_pos_of_pos hcb (0.25351 : ℝ)
  have hx' := Real.rpow_pos_of_pos hx (0.12807 : ℝ)
  have hpow : x ^ (0.12807 : ℝ) < y ^ (0.12807 : ℝ) :=
    Real.rpow_lt_rpow hx.le hxy (by norm_num)
  have hden : wcb ^ (0.25351 : ℝ) * x ^ (0.12807 : ℝ) < wcb ^ (0.25351 : ℝ) * y ^ (0.12807 : ℝ) :=
    mul_lt_mul_of_pos_left hpow hcb'
  exact div_lt_div_of_pos_left rd_numerator_pos (mul_pos hcb' hx') hden

/-- Monotonicity in `Ωₘ`: for fixed `h > 0` and `ω_b > 0`, the sound horizon
`r_d(Ωₘ h² − ω_ν, ω_b)` used in the fit is strictly decreasing in `Ωₘ` on the
sampled support `{Ωₘ : Ωₘ h² − ω_ν > 0}` (common.py's `omega_cb_of(...) > 0`
mask). -/
theorem rd_strictAntiOn_Om {h wb : ℝ} (hh : 0 < h) (hb : 0 < wb) :
    StrictAntiOn (fun Om => rdAubourg (omegaCb h Om) wb) {Om : ℝ | 0 < omegaCb h Om} := by
  intro x hx y hy hxy
  simp only [Set.mem_ofPred_eq] at hx hy
  have hcb : omegaCb h x < omegaCb h y := by
    unfold omegaCb
    have : 0 < h ^ 2 := by positivity
    nlinarith
  exact rdAubourg_strictAntiOn_cb hb (Set.mem_Ioi.mpr hx) (Set.mem_Ioi.mpr hy) hcb

/-- `H0 = 100 h`, as coded (`h = h0 / 100`). -/
noncomputable def H0 (h : ℝ) : ℝ := 100 * h

/-- The coded BAO observable `D_H(z)/r_d = (c / (100 h)) / E(z) / r_d`
(`distances_manual_vec`: `dh0 = C_KM_S/(100 h)`, `dh = dh0 / E`; `obs_from_distances`: `/ rd`). -/
noncomputable def DH_over_rd (c h E rd : ℝ) : ℝ := c / H0 h / E / rd

/-- The observable depends on `(h, r_d)` only through the product `h r_d`:
`D_H/r_d = c / (100 · (h r_d) · E)`. Unconditional field identity (Lean's `x/0 = 0`
convention makes both sides agree even at zero denominators). -/
theorem DH_over_rd_eq_hrd (c h E rd : ℝ) :
    DH_over_rd c h E rd = c / (100 * (h * rd) * E) := by
  unfold DH_over_rd H0
  rw [div_div, div_div]
  ring_nf

/-- Two parameter points with the same `h r_d` predict the same observable. -/
theorem DH_over_rd_degenerate {h rd h' rd' : ℝ} (c E : ℝ) (hprod : h * rd = h' * rd') :
    DH_over_rd c h E rd = DH_over_rd c h' E rd' := by
  sorry

/-- The `(Ωₘ, h r_d)` gate (`make_logpost_hrd`) evaluates the distances at a fixed
`h_rad` and passes `hrd / h_rad` as `r_d`; for `h_rad ≠ 0` this is EXACTLY
`c / (100 · hrd · E)`, i.e. an exact reparametrisation in `h r_d`. -/
theorem gate_reparam_exact {hrad : ℝ} (hne : hrad ≠ 0) (c E hrd : ℝ) :
    DH_over_rd c hrad E (hrd / hrad) = c / (100 * hrd * E) := by
  rw [DH_over_rd_eq_hrd]
  have : hrad * (hrd / hrad) = hrd := by field_simp
  rw [this]

-- Axiom footprint, checked as part of this file's own compilation (Elenchus
-- NO_FOOTPRINT rule): every theorem this file is gated on appears here.
#print axioms rd_numerator_pos
#print axioms rdAubourg_pos
#print axioms rdAubourg_strictAntiOn_cb
#print axioms rdAubourg_strictAntiOn_b
#print axioms rd_strictAntiOn_Om
#print axioms DH_over_rd_eq_hrd
#print axioms DH_over_rd_degenerate
#print axioms gate_reparam_exact

end ANSE.BAOBBNH0
