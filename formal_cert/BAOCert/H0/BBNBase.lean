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
  * AT FIXED E, the coded observable depends on (h, r_d) only through the
    product h r_d (D_H/r_d = c / (100 · (h r_d) · E)). E is a free real here;
    in the BBN fits E(z) itself depends on h through the radiation term
    (orad = omega_r_h2 / h²), so for the full BBN likelihood this is exact only
    up to that radiation dependence (~1e-4), and exact for the gate below,
    which evaluates E at a fixed h_rad. The gate's substitution
    r_d ↦ hrd / h_rad at fixed h_rad gives EXACTLY c / (100 · hrd · E): the
    r_d-free (Ωₘ, h r_d) gate is an exact reparametrisation, not an
    approximation. H0 = 100 h is built into the same identity;
  * identifiability of the inverse distance ladder (secondary r_d): at fixed
    Ωₘ > 0 and ω_b > 0, h ↦ h · r_d(Ωₘ h² − ω_ν, ω_b) is STRICTLY INCREASING
    on {h > 0 : ω_ν ≤ (1 − 2a) Ωₘ h²}, a = 0.25351. So once BAO fix (Ωₘ, h r_d)
    and BBN fixes ω_b, at most one h reproduces them. The hypothesis is
    stronger than the preregistered bare "1 − 2a > 0" because ω_ν > 0 is
    subtracted inside the power; it is necessary (below it h·r_d decreases,
    checked numerically in results/bao_bbn_h0/fixround_diagnostics.json). It
    holds wherever Ωₘ h² ≥ 0.0013, which includes the T1 posterior by a wide
    margin (ω_m ≈ 0.14), but NOT the whole secondary prior support: the band
    ω_ν < Ωₘ h² < 0.0013 (e.g. Ωₘ ≈ 0.01, H0 ≈ 25-36) is sampled and there
    h·r_d decreases. The CAMB table's ω_cdm ≥ 0.005 excludes that corner for
    the primary.
Exponents are real powers (Real.rpow), exactly as `** 0.25351` in numpy.
Literature: docs/literature/BAO_BBN_H0_LITERATURE_REVIEW_2026.md.
Numbers from the fit (results/bao_bbn_h0/fit.json): H0 = 68.55 ± 0.59 (primary),
68.58 ± 0.60 (secondary); nothing numeric is asserted here.
-/
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Analysis.Convex.SpecificFunctions.Basic
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

/-- At fixed `E`, the observable depends on `(h, r_d)` only through the product `h r_d`:
`D_H/r_d = c / (100 · (h r_d) · E)`. (`E` is a free real here; in the BBN fits `E(z)`
depends on `h` through radiation, so this is exact there only up to that dependence.) Unconditional field identity (Lean's `x/0 = 0`
convention makes both sides agree even at zero denominators). -/
theorem DH_over_rd_eq_hrd (c h E rd : ℝ) :
    DH_over_rd c h E rd = c / (100 * (h * rd) * E) := by
  unfold DH_over_rd H0
  rw [div_div, div_div]
  ring_nf

/-- At the same `c` and the same `E`, two parameter points with the same `h r_d` predict
the same observable (in the BBN fits `E` itself carries a small `h` dependence via radiation). -/
theorem DH_over_rd_degenerate {h rd h' rd' : ℝ} (c E : ℝ) (hprod : h * rd = h' * rd') :
    DH_over_rd c h E rd = DH_over_rd c h' E rd' := by
  rw [DH_over_rd_eq_hrd, DH_over_rd_eq_hrd, hprod]

/-- The `(Ωₘ, h r_d)` gate (`make_logpost_hrd`) evaluates the distances at a fixed
`h_rad` and passes `hrd / h_rad` as `r_d`; for `h_rad ≠ 0` this is EXACTLY
`c / (100 · hrd · E)`, i.e. an exact reparametrisation in `h r_d`. -/
theorem gate_reparam_exact {hrad : ℝ} (hne : hrad ≠ 0) (c E hrd : ℝ) :
    DH_over_rd c hrad E (hrd / hrad) = c / (100 * hrd * E) := by
  rw [DH_over_rd_eq_hrd]
  have : hrad * (hrd / hrad) = hrd := by field_simp
  rw [this]

/-- Generic identifiability lemma behind the inverse distance ladder. For `0 < a ≤ 1/3`,
`w > 0`, `Ωₘ > 0` and `0 < h₁ < h₂` with `w ≤ (1 − 2a) Ωₘ h₁²`:
`h₁ (Ωₘ h₂² − w)^a < h₂ (Ωₘ h₁² − w)^a`, i.e. `h / (Ωₘ h² − w)^a` strictly increases.
Proof: Bernoulli `(1+s)^e ≤ 1 + e s` with `e = a/(1−2a) ≤ 1`. -/
theorem hrd_mono_generic {a w Om h1 h2 : ℝ} (ha : 0 < a) (ha3 : a ≤ 1 / 3) (hw : 0 < w)
    (hOm : 0 < Om) (hh1 : 0 < h1) (h12 : h1 < h2) (hsupp : w ≤ (1 - 2 * a) * (Om * h1 ^ 2)) :
    h1 * (Om * h2 ^ 2 - w) ^ a < h2 * (Om * h1 ^ 2 - w) ^ a := by
  have hXpos : 0 < Om * h1 ^ 2 := by positivity
  have h2a : 0 < 1 - 2 * a := by linarith
  have hc1 : 0 < Om * h1 ^ 2 - w := by nlinarith
  set X := Om * h1 ^ 2 with hX
  set r := h2 / h1 with hr
  have hr1 : 1 < r := by rw [hr, lt_div_iff₀ hh1]; linarith
  have hr0 : 0 < r := by linarith
  have hh2 : h2 = r * h1 := by rw [hr]; field_simp
  have hc2eq : Om * h2 ^ 2 - w = r ^ 2 * X - w := by rw [hh2, hX]; ring
  have hr2gt : 1 < r ^ 2 := by nlinarith
  have hc2 : 0 < r ^ 2 * X - w := by nlinarith
  set e := a / (1 - 2 * a) with he
  have he0 : 0 < e := div_pos ha h2a
  have he1 : e ≤ 1 := by rw [he, div_le_one h2a]; linarith
  have hea : e * (1 - 2 * a) = a := by rw [he]; exact div_mul_cancel₀ a h2a.ne'
  set s := w * (r ^ 2 - 1) / (r ^ 2 * (X - w)) with hs
  have hs0 : 0 ≤ s := by
    rw [hs]
    apply div_nonneg (mul_nonneg hw.le (by linarith)) (by positivity)
  have hq : (r ^ 2 * X - w) / (X - w) = r ^ 2 * (1 + s) := by
    rw [hs]
    have : X - w ≠ 0 := hc1.ne'
    have : r ≠ 0 := hr0.ne'
    field_simp
    ring
  have h2ew : 2 * e * w ≤ X - w := by
    have k1 : (2 * e * w) * (1 - 2 * a) = 2 * a * w := by
      rw [show (2 * e * w) * (1 - 2 * a) = 2 * w * (e * (1 - 2 * a)) by ring, hea]; ring
    have k2 : (2 * e * w) * (1 - 2 * a) ≤ (X - w) * (1 - 2 * a) := by rw [k1]; nlinarith
    exact le_of_mul_le_mul_right k2 h2a
  have hkey : 1 + e * s < r := by
    have hew : 0 < e * w := mul_pos he0 hw
    have hden : 0 < r ^ 2 * (X - w) := by positivity
    have hes : e * s = e * (w * (r ^ 2 - 1)) / (r ^ 2 * (X - w)) := by rw [hs]; ring
    have hlt : e * (w * (r ^ 2 - 1)) < (r - 1) * (r ^ 2 * (X - w)) := by
      have s1 : e * (w * (r ^ 2 - 1)) = (e * w) * (r - 1) * (r + 1) := by ring
      have s2 : (e * w) * (r - 1) * (r + 1) < (e * w) * (r - 1) * (2 * r ^ 2) :=
        mul_lt_mul_of_pos_left (by nlinarith) (mul_pos hew (by linarith))
      have s3 : (e * w) * (r - 1) * (2 * r ^ 2) = ((r - 1) * r ^ 2) * (2 * e * w) := by ring
      have s4 : ((r - 1) * r ^ 2) * (2 * e * w) ≤ ((r - 1) * r ^ 2) * (X - w) :=
        mul_le_mul_of_nonneg_left h2ew (mul_nonneg (by linarith) (by positivity))
      have s5 : ((r - 1) * r ^ 2) * (X - w) = (r - 1) * (r ^ 2 * (X - w)) := by ring
      linarith
    have : e * s < r - 1 := by rw [hes, div_lt_iff₀ hden]; exact hlt
    linarith
  have hbern : (1 + s) ^ e ≤ 1 + e * s :=
    rpow_one_add_le_one_add_mul_self (by linarith) he0.le he1
  have hqe : (1 + s) ^ e < r := lt_of_le_of_lt hbern hkey
  have hqa : (1 + s) ^ a < r ^ (1 - 2 * a) := by
    have : (1 + s) ^ a = ((1 + s) ^ e) ^ (1 - 2 * a) := by
      rw [← Real.rpow_mul (by linarith), hea]
    rw [this]
    exact Real.rpow_lt_rpow (Real.rpow_nonneg (by linarith) _) hqe h2a
  have hr2 : (r ^ 2) ^ a = r ^ (2 * a) := by
    rw [← Real.rpow_natCast, ← Real.rpow_mul hr0.le]
    norm_num
  have hu : ((r ^ 2 * X - w) / (X - w)) ^ a < r := by
    rw [hq, Real.mul_rpow (by positivity) (by linarith), hr2]
    calc r ^ (2 * a) * (1 + s) ^ a < r ^ (2 * a) * r ^ (1 - 2 * a) :=
          mul_lt_mul_of_pos_left hqa (Real.rpow_pos_of_pos hr0 _)
      _ = r := by rw [← Real.rpow_add hr0]; norm_num
  rw [Real.div_rpow hc2.le hc1.le, div_lt_iff₀ (Real.rpow_pos_of_pos hc1 a)] at hu
  rw [hc2eq, hh2]
  calc h1 * (r ^ 2 * X - w) ^ a < h1 * (r * (X - w) ^ a) := mul_lt_mul_of_pos_left hu hh1
    _ = r * h1 * (X - w) ^ a := by ring

/-- Identifiability of the inverse distance ladder for the SECONDARY (eq. 16) sound horizon:
at fixed `Ωₘ > 0` and `ω_b > 0`, `h ↦ h · r_d(Ωₘ h² − ω_ν, ω_b)` is strictly increasing on
`{h > 0 : ω_ν ≤ (1 − 2 · 0.25351) Ωₘ h²}` (the hypothesis is stronger than bare `1 − 2a > 0`
because `ω_ν > 0` sits inside the power). BAO fix `(Ωₘ, h r_d)`, BBN fixes `ω_b`; at most one
`h` on that set then matches. The set contains the T1 posterior but not the extreme low-`Ωₘ h²`
corner of the secondary prior. Nothing is claimed about the PRIMARY CAMB `r_d`. -/
theorem hrd_strictMonoOn_h {Om wb : ℝ} (hOm : 0 < Om) (hb : 0 < wb) :
    StrictMonoOn (fun h => h * rdAubourg (omegaCb h Om) wb)
      {h : ℝ | 0 < h ∧ omegaNu ≤ (1 - 2 * 0.25351) * (Om * h ^ 2)} := by
  intro x hx y hy hxy
  obtain ⟨hx0, hxs⟩ := hx
  obtain ⟨hy0, hys⟩ := hy
  have hw : (0 : ℝ) < omegaNu := by unfold omegaNu; norm_num
  have key := hrd_mono_generic (a := 0.25351) (by norm_num) (by norm_num) hw hOm hx0 hxy hxs
  have hcx : 0 < Om * x ^ 2 - omegaNu := by nlinarith
  have hcy : 0 < Om * y ^ 2 - omegaNu := by nlinarith
  have hcxa := Real.rpow_pos_of_pos hcx (0.25351 : ℝ)
  have hcya := Real.rpow_pos_of_pos hcy (0.25351 : ℝ)
  have hP := Real.rpow_pos_of_pos hb (0.12807 : ℝ)
  have hN := rd_numerator_pos
  simp only
  unfold rdAubourg omegaCb
  set N := 55.154 * Real.exp (-72.3 * (omegaNu + 0.0006) ^ 2)
  set P := wb ^ (0.12807 : ℝ)
  have ex : ∀ t c : ℝ, 0 < c → t * (N / (c * P)) = (N / P) * (t / c) := by
    intro t c hc
    field_simp
  rw [ex x _ hcxa, ex y _ hcya]
  apply mul_lt_mul_of_pos_left _ (div_pos hN hP)
  rw [div_lt_div_iff₀ hcxa hcya]
  exact key

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
#print axioms hrd_mono_generic
#print axioms hrd_strictMonoOn_h

end ANSE.BAOBBNH0
