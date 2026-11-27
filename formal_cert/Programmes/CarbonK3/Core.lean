import Programmes.CompletelyMonotone.Basic

/-!
# Proposal 4, K3 (2026-10-31): post-cessation monotonicity of a linear carbon-cycle impulse response

Statements about a stylised LINEAR impulse-response model, NOT about the Earth system.

The IRF is `h(t) = a0 + sum_i a_i exp(-r_i t)` with `a0, a_i, r_i >= 0` (Joos et al. 2013 mean IRF: `r_i = 1/tau_i`).
A DISCRETE emission measure `sum_j w_j delta_{z_j}` with `w_j >= 0` and `z_j <= T` gives the excess concentration
`excess(t) = sum_j w_j h(t - z_j)` for `t > T`.

* `irf_cm`: `h` is completely monotone on `(0, inf)` (reuses `ProgCM`).
* `excess_cm_after`: `s -> excess (s + T)` is completely monotone on `(0, inf)`, i.e. `excess` is CM on `(T, inf)`.
* `excess_antitone`, `excess_convexOn`: non-increasing and convex on `(T, inf)`.
* `excess_tendsto`: if every `r_i > 0` the limit is `a0 * sum_j w_j` (the `a0 * int m` of the continuous case).
* `neg_ctl_not_cm`: with one NEGATIVE coefficient (`h = 1 - exp(-t)`) the conclusion fails, so the nonnegativity
  hypotheses of `irf_cm` cannot be dropped.
Continuous emission paths `m` are NOT covered by this file (paper proof only, Tier C).
-/

namespace CarbonK3

open ProgCM Set Filter Topology

/-- Sum-of-exponentials impulse response, rates `r i = 1/tau_i`. -/
noncomputable def irf {n : ℕ} (a0 : ℝ) (a r : Fin n → ℝ) (t : ℝ) : ℝ :=
  a0 + ∑ i, a i * Real.exp (-(r i * t))

/-- Excess concentration after a discrete nonnegative emission measure. -/
noncomputable def excess {k n : ℕ} (w z : Fin k → ℝ) (a0 : ℝ) (a r : Fin n → ℝ) (t : ℝ) : ℝ :=
  ∑ j, w j * irf a0 a r (t - z j)

theorem irf_cm {n : ℕ} {a0 : ℝ} {a r : Fin n → ℝ} (ha0 : 0 ≤ a0) (ha : ∀ i, 0 ≤ a i) (hr : ∀ i, 0 ≤ r i) :
    IsCompletelyMonotoneOn (irf a0 a r) := by
  have h1 : IsCompletelyMonotoneOn (fun _ : ℝ => a0) := ProgCM.const ha0
  have h2 : IsCompletelyMonotoneOn (fun t : ℝ => ∑ i, a i * Real.exp (-(r i * t))) :=
    ProgCM.sum Finset.univ a (fun i t => Real.exp (-(r i * t))) (fun i _ => ha i)
      (fun i _ => ProgCM.exp_neg_mul (hr i))
  exact (h1.add h2).congr' fun t _ => rfl

theorem excess_cm_after {k n : ℕ} {w z : Fin k → ℝ} {a0 : ℝ} {a r : Fin n → ℝ} {T : ℝ}
    (hw : ∀ j, 0 ≤ w j) (hz : ∀ j, z j ≤ T) (ha0 : 0 ≤ a0) (ha : ∀ i, 0 ≤ a i) (hr : ∀ i, 0 ≤ r i) :
    IsCompletelyMonotoneOn (fun s => excess w z a0 a r (s + T)) := by
  have hF : ∀ j ∈ (Finset.univ : Finset (Fin k)),
      IsCompletelyMonotoneOn (fun s => irf a0 a r (s + (T - z j))) :=
    fun j _ => (irf_cm ha0 ha hr).comp_add_const (sub_nonneg.2 (hz j))
  have hS := ProgCM.sum Finset.univ w (fun j s => irf a0 a r (s + (T - z j)))
    (fun j _ => hw j) hF
  refine hS.congr' fun s _ => ?_
  simp only [excess]
  refine Finset.sum_congr rfl fun j _ => ?_
  congr 2
  ring

theorem excess_antitone {k n : ℕ} {w z : Fin k → ℝ} {a0 : ℝ} {a r : Fin n → ℝ} {T : ℝ}
    (hw : ∀ j, 0 ≤ w j) (hz : ∀ j, z j ≤ T) (ha0 : 0 ≤ a0) (ha : ∀ i, 0 ≤ a i) (hr : ∀ i, 0 ≤ r i) :
    AntitoneOn (fun s => excess w z a0 a r (s + T)) (Ioi 0) := by
  have := (excess_cm_after hw hz ha0 ha hr).antitoneOn_sign 0
  simpa using this

theorem cm_convexOn {f : ℝ → ℝ} (hf : IsCompletelyMonotoneOn f) : ConvexOn ℝ (Ioi 0) f := by
  have hanti := hf.antitoneOn_sign 1
  have hmono : MonotoneOn (deriv f) (interior (Ioi (0 : ℝ))) := by
    rw [interior_Ioi]
    intro x hx y hy hxy
    have := hanti hx hy hxy
    simp only [pow_one, neg_mul, one_mul, iteratedDeriv_one] at this
    linarith
  refine MonotoneOn.convexOn_of_deriv (convex_Ioi 0) ?_ ?_ hmono
  · exact fun t ht => (hf.differentiableAt ht).continuousAt.continuousWithinAt
  · rw [interior_Ioi]
    exact fun t ht => (hf.differentiableAt ht).differentiableWithinAt

theorem excess_convexOn {k n : ℕ} {w z : Fin k → ℝ} {a0 : ℝ} {a r : Fin n → ℝ} {T : ℝ}
    (hw : ∀ j, 0 ≤ w j) (hz : ∀ j, z j ≤ T) (ha0 : 0 ≤ a0) (ha : ∀ i, 0 ≤ a i) (hr : ∀ i, 0 ≤ r i) :
    ConvexOn ℝ (Ioi 0) (fun s => excess w z a0 a r (s + T)) :=
  cm_convexOn (excess_cm_after hw hz ha0 ha hr)

theorem excess_tendsto {k n : ℕ} (w z : Fin k → ℝ) (a0 : ℝ) (a r : Fin n → ℝ) (T : ℝ)
    (hr : ∀ i, 0 < r i) :
    Tendsto (fun s => excess w z a0 a r (s + T)) atTop (nhds (a0 * ∑ j, w j)) := by
  have hexp : ∀ (i : Fin n) (c : ℝ), Tendsto (fun s : ℝ => Real.exp (-(r i * (s + T - c)))) atTop (nhds 0) := by
    intro i c
    have h0 : Tendsto (fun s : ℝ => s + (T - c)) atTop atTop :=
      tendsto_atTop_add_const_right atTop (T - c) tendsto_id
    have h1 : Tendsto (fun s : ℝ => r i * (s + T - c)) atTop atTop :=
      (h0.const_mul_atTop (hr i)).congr fun s => by ring
    exact Real.tendsto_exp_neg_atTop_nhds_zero.comp h1
  have hirf : ∀ j, Tendsto (fun s : ℝ => irf a0 a r (s + T - z j)) atTop (nhds a0) := by
    intro j
    have : Tendsto (fun s : ℝ => a0 + ∑ i, a i * Real.exp (-(r i * (s + T - z j)))) atTop
        (nhds (a0 + ∑ i : Fin n, a i * 0)) := by
      refine tendsto_const_nhds.add (tendsto_finsetSum _ fun i _ => ?_)
      exact (hexp i (z j)).const_mul _
    simpa [irf] using this
  have := tendsto_finsetSum (Finset.univ : Finset (Fin k)) fun j _ => (hirf j).const_mul (w j)
  have e : a0 * ∑ j, w j = ∑ j, w j * a0 := by rw [Finset.mul_sum]; exact Finset.sum_congr rfl fun j _ => mul_comm _ _
  rw [e]
  refine this.congr fun s => ?_
  simp only [excess]

/-- NEGATIVE CONTROL: one negative coefficient (`h(t) = 1 + (-1) exp(-t)`) is not completely monotone. -/
theorem neg_ctl_not_cm : ¬ IsCompletelyMonotoneOn (irf (n := 1) 1 (fun _ => -1) (fun _ => 1)) := by
  intro h
  have hanti := h.antitoneOn_sign 0
  have h12 : (1 : ℝ) ≤ 2 := by norm_num
  have := hanti (show (1 : ℝ) ∈ Ioi 0 by simp) (show (2 : ℝ) ∈ Ioi 0 by simp) h12
  simp only [irf, pow_zero, one_mul, iteratedDeriv_zero, Finset.univ_unique, Fin.default_eq_zero,
    Finset.sum_singleton] at this
  have hlt : Real.exp (-2) < Real.exp (-1) := Real.exp_lt_exp.2 (by norm_num)
  linarith

end CarbonK3

#print axioms CarbonK3.irf_cm
#print axioms CarbonK3.excess_cm_after
#print axioms CarbonK3.excess_antitone
#print axioms CarbonK3.excess_convexOn
#print axioms CarbonK3.excess_tendsto
#print axioms CarbonK3.neg_ctl_not_cm
