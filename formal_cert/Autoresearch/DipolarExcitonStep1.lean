import Autoresearch.DipolarExciton

/-! H1 stage 5 (revision, correction C8 of the stage-4 audit). The Step-1 algebraic identity of the paper: the
`rpow` form of the bilayer dipolar-exciton potential `g d` equals the square-root form, and, at `t = r ^ 2` with
`r > 0`, the in-plane form `2 (1/r - 1/sqrt(r^2 + d^2))`. The first proof is the stage-4 auditor's probe
`audit_g_sqrt` (DipolarExcitonAuditH1Controls.lean), moved here unchanged so that it is a claimed declaration.
The physical reading (four Coulomb pairs) stays an argument; only the algebra is checked here. -/

namespace AutoresearchDipolarStep1

/-- Square-root form of `g d` on `(0, ∞)`. -/
theorem g_sqrt (d t : ℝ) (ht : 0 < t) :
    AutoresearchDipolar.g d t = 2 * (1 / Real.sqrt t - 1 / Real.sqrt (t + d ^ 2)) := by
  have h2 : 0 ≤ t + d ^ 2 := by positivity
  simp only [AutoresearchDipolar.g, Real.sqrt_eq_rpow, one_div, Real.rpow_neg ht.le, Real.rpow_neg h2]

/-- In-plane form: for `r > 0`, `g d (r ^ 2) = 2 (1/r - 1/sqrt(r^2 + d^2))`. -/
theorem g_inplane (d r : ℝ) (hr : 0 < r) :
    AutoresearchDipolar.g d (r ^ 2) = 2 * (1 / r - 1 / Real.sqrt (r ^ 2 + d ^ 2)) := by
  rw [g_sqrt d (r ^ 2) (by positivity), Real.sqrt_sq hr.le]

/-- The in-plane potential is positive for `d ≠ 0`, `r > 0` (the cross pairs are farther apart). -/
theorem g_inplane_pos (d r : ℝ) (hd : d ≠ 0) (hr : 0 < r) : 0 < AutoresearchDipolar.g d (r ^ 2) := by
  rw [g_inplane d r hr]
  have hd2 : 0 < d ^ 2 := by positivity
  have hlt : r < Real.sqrt (r ^ 2 + d ^ 2) := (Real.lt_sqrt hr.le).2 (by linarith)
  have : 1 / Real.sqrt (r ^ 2 + d ^ 2) < 1 / r := one_div_lt_one_div_of_lt hr hlt
  linarith

end AutoresearchDipolarStep1
