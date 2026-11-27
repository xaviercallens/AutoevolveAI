import Programmes.AmplifierCensus.DataR11
import Programmes.AmplifierCensus.DataP11

/-!
# Richter's N = 11 death-Birth amplifier of weak selection, kernel-checked (C1, proposal 4)

`GR11` is the quartic graph on 11 vertices of Richter (arXiv 2008.01446, Fig. 1a), identified among
all 265 connected quartic graphs (nauty `geng -c -d4 -D4 11`) as the unique one whose argmax-remeeting
vertex yields `N_eff > N`, with one edge at that vertex removed (all four removals are isomorphic).
`GP11` is the parent quartic graph.

* `R11_amplifier`: every rational solution of Allen eq. (5) on `GR11` has
  `N_eff = 2668552698098 / 242579025123 > 11` (≈ 11.000756; Richter prints 11.0008).
* `P11_isothermal`: on the 4-regular parent every solution has `N_eff = 11` (weak-selection
  isothermal theorem, positive control).

Scope: these are statements about the linear system (Allen eqs. 5, 6, 9) on these adjacencies. The
link "N_eff > N ⇒ amplifier of weak selection" is Allen et al. eq. (8) (Tier L), not formalised here.
-/

namespace AmplifierCensus

theorem GR11_symm : ∀ i j : Fin 11, GR11 i j = GR11 j i := by decide +kernel
theorem GR11_loopless : ∀ i : Fin 11, GR11 i i = false := by decide +kernel
theorem GR11_deg : ∀ i : Fin 11, deg GR11 i = if i = 0 ∨ i = 9 then 3 else 4 := by decide +kernel

theorem tauR11_eq5 : Eq5 GR11 tauR11 := by
  unfold Eq5; decide +kernel

theorem tauR11_pos : ∀ i j : Fin 11, i ≠ j → 0 < tauR11 i j := by decide +kernel

theorem neff_tauR11 : neff GR11 tauR11 = 2668552698098 / 242579025123 := by
  unfold neff remeet; decide +kernel

/-- **Richter's N = 11 graph is an amplifier of weak selection (Allen's criterion `N_eff > N`).** -/
theorem R11_amplifier (τ : Fin 11 → Fin 11 → ℚ) (hτ : Eq5 GR11 τ) :
    neff GR11 τ = 2668552698098 / 242579025123 ∧ (11 : ℚ) < neff GR11 τ := by
  rw [neff_of_cert GR11 tauR11 tauR11_eq5 tauR11_pos τ hτ, neff_tauR11]
  exact ⟨rfl, by norm_num⟩

theorem GP11_symm : ∀ i j : Fin 11, GP11 i j = GP11 j i := by decide +kernel
theorem GP11_loopless : ∀ i : Fin 11, GP11 i i = false := by decide +kernel
theorem GP11_regular : ∀ i : Fin 11, deg GP11 i = 4 := by decide +kernel

theorem tauP11_eq5 : Eq5 GP11 tauP11 := by
  unfold Eq5; decide +kernel

theorem tauP11_pos : ∀ i j : Fin 11, i ≠ j → 0 < tauP11 i j := by decide +kernel

/-- Positive control: the quartic parent has `N_eff = 11` exactly (not an amplifier). -/
theorem P11_isothermal (τ : Fin 11 → Fin 11 → ℚ) (hτ : Eq5 GP11 τ) : neff GP11 τ = 11 := by
  rw [neff_of_cert GP11 tauP11 tauP11_eq5 tauP11_pos τ hτ]
  unfold neff remeet; decide +kernel

end AmplifierCensus

#print axioms AmplifierCensus.R11_amplifier
#print axioms AmplifierCensus.P11_isothermal
#print axioms AmplifierCensus.eq5_unique
