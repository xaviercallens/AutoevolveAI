"""M1: write formal_cert/Programmes/ZeroPointDipolar/Basic.lean from the certified run JSONs (no hand transcription).

usage: python -I m1_lean_gen.py M1_DIR OUT.lean
Only runs with certified_not_local_min = true get a certificate theorem; the rationals are copied verbatim.
"""
from __future__ import annotations

import json
import os
import sys

RUNS = [("riesz3", "riesz3", "Riesz `V = r⁻³`", "riesz3.json"),
        ("dip01", "dipolar01", "bilayer point dipole `V = 2(1/r - 1/√(r² + d²))/d²`, d = 1/10", "dipolar_d0.1.json"),
        ("dip05", "dipolar05", "bilayer point dipole, d = 1/2", "dipolar_d0.5.json"),
        ("dipA006", "dipolarA006", "bilayer point dipole, d = 129/2000 (d/a ≈ 0.0600)", "dipolar_da0.06.json"),
        ("dipA009", "dipolarA009", "bilayer point dipole, d = 967/10000 (d/a ≈ 0.0900)", "dipolar_da0.09.json"),
        ("dipA01", "dipolarA01", "bilayer point dipole, d = 1075/10000 (d/a ≈ 0.1000)", "dipolar_da0.1.json"),
        ("dipA05", "dipolarA05", "bilayer point dipole, d = 5373/10000 (d/a ≈ 0.5000)", "dipolar_da0.5.json")]

HEAD = """import Programmes.ZeroPointPhys.Basic
import Mathlib.Tactic

/-!
# M1 (proposal 4, 2026-10-27): the triangular lattice is not a local minimum of the harmonic zero-point energy
# for the r⁻³ potentials (Riesz s = 3, bilayer point dipole), with Ewald-split tails

Same setting, logic and hypotheses as N2 (`Programmes.ZeroPointPhys.Basic`): `E(t)` is the harmonic zero-point energy
per particle (ħ = m = 1) of the unit-covolume lattice `P_t L_ρ`, `P_t = [[1, t], [t, 1 + t²]]`, for the stated radial
pair potential; `U` is N2's t-dependent comparison majorant. This file adds only the rational certificates produced by
`results/proposal4/2026-10-27/M1/code/m1_certify.py` (N2's certifier with an Ewald / Gaussian-mixture split of the
r⁻³ tail: short part in real space, long part in reciprocal space), and assembles them with N2's
`not_localMin_of_deriv_cert`.

The kernel checks the logic and the signs of the rational endpoints. The hypotheses of each final theorem are exactly
the inputs that are NOT kernel-checked: the Arb enclosure `U₂'' ≤ M ≤ M_hi` on the window (lattice sums, Poisson
summation of the long part, reciprocal-space bounds, tails, BZ integral: Tier C-ball and C-human), `E ≤ U` on the window
(positivity checks, Tier C-ball), `U(0) = E(0)`, the differentiability of `U` on the window, and the mirror symmetry.
A statement about the harmonic zero-point energy of a model crystal, not about any physical exciton system.
-/

namespace ProgZeroPointDipolar

open ProgZeroPointCert ProgZeroPointPhys
"""


def main() -> None:
    m1, out = sys.argv[1], sys.argv[2]
    body, prints = [], []
    for short, name, desc, fn in RUNS:
        p = os.path.join(m1, "data", fn)
        if not os.path.exists(p):
            continue
        rec = json.load(open(p))
        if not rec.get("certified_not_local_min"):
            continue
        cr = rec["cert_rationals"]
        body.append(f"""
/-! ## {desc}: `results/proposal4/2026-10-27/M1/data/{fn}`
(QMAX {rec['qmax']}, Ewald split alpha = {rec['alpha']}, N {rec['N']}, depth {rec['max_depth']}, tol {rec['refine_tol']};
M ∈ [{rec['M_window_curvature_bound']['lo_float']:.5f}, {rec['M_window_curvature_bound']['hi_float']:.5f}]) -/

noncomputable def {short}_M_hi : ℝ := {cr['M_hi'].replace('/', ' / ')}
noncomputable def {short}_lmin_lo : ℝ := {cr['lmin_lo'].replace('/', ' / ')}
noncomputable def {short}_lminu_lo : ℝ := {cr['lminu_lo'].replace('/', ' / ')}
noncomputable def {short}_qpd_lo : ℝ := {cr['qpd_lo'].replace('/', ' / ')}

theorem {short}_cert : {short}_M_hi < 0 ∧ 0 < {short}_lmin_lo ∧ 0 < {short}_lminu_lo ∧ 0 < {short}_qpd_lo := by
  refine ⟨?_, ?_, ?_, ?_⟩ <;> norm_num [{short}_M_hi, {short}_lmin_lo, {short}_lminu_lo, {short}_qpd_lo]

theorem {name}_not_localMin_of_certificate (E U U1 U2pp : ℝ → ℝ) (M : ℝ)
    (hEU : ∀ t, |t| ≤ t0 → E t ≤ U t) (h0 : U 0 = E 0)
    (hd1 : ∀ u, |u| ≤ t0 → HasDerivAt U (U1 u) u) (hd2 : ∀ u, |u| ≤ t0 → HasDerivAt U1 (U2pp u) u)
    (hK : ∀ u, |u| ≤ t0 → U2pp u ≤ M) (hM : M ≤ {short}_M_hi)
    (hsym : ∀ t, E (-t) = E t) :
    ¬ IsLocalMin E 0 ∧ ∀ t, 0 < t → t ≤ t0 → E t < E 0 :=
  not_localMin_of_deriv_cert E U U1 U2pp t0 M {short}_M_hi t0_pos {short}_cert.1 hM hEU h0 hd1 hd2 hK hsym
""")
        prints += [f"#print axioms ProgZeroPointDipolar.{short}_cert",
                   f"#print axioms ProgZeroPointDipolar.{name}_not_localMin_of_certificate"]
    txt = HEAD + "".join(body) + "\nend ProgZeroPointDipolar\n\n" + "\n".join(prints) + "\n"
    with open(out, "w") as fh:
        fh.write(txt)
    print(f"wrote {out}: {len(prints) // 2} certificates")


if __name__ == "__main__":
    main()
