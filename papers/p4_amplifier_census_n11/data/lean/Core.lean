import Mathlib.Tactic
import Mathlib.Algebra.BigOperators.Fin

/-!
# Weak-selection effective population size for death-Birth updating (C1, proposal 4)

Allen et al., arXiv 1906.01036v1 (PLoS Comput. Biol. 16(1): e1007529, 2020), for an unweighted
graph with Boolean adjacency `A` on `Fin n`:

* step probabilities `p i k = [A i k] / deg i`;
* eq. (5): `τ i i = 0` and, for `i ≠ j`, `τ i j = 1 + ½ ∑ₖ (p i k τ j k + p j k τ i k)`;
* eq. (6): remeeting time `τᵢ = 1 + ∑ⱼ p i j τ i j`;
* eq. (9): `N_eff = ∑ᵢ πᵢ τᵢ`, `πᵢ = deg i / ∑ⱼ deg j`;
* Definition p. 8: amplifier of weak selection iff `N_eff > N`. The link between `N_eff` and the
  fixation probability (Allen eq. (8)) is literature (Tier L), NOT formalised here.

`eq5_unique`: if `v` solves eq. (5) and is positive off the diagonal, every rational solution equals
`v` (maximum principle). This lets a single kernel-checked rational solution certify `N_eff` for *all*
solutions of the system, so the statement is not about a guessed vector.
-/

namespace AmplifierCensus

open Finset

variable {n : ℕ}

/-- Degree of `i`. -/
def deg (A : Fin n → Fin n → Bool) (i : Fin n) : ℕ := (univ.filter fun k => A i k = true).card

/-- Step probability of the ancestral random walk, `p i k = [A i k] / deg i`. -/
def p (A : Fin n → Fin n → Bool) (i k : Fin n) : ℚ := if A i k then 1 / (deg A i : ℚ) else 0

/-- Allen et al. eq. (5), coalescence times. -/
def Eq5 (A : Fin n → Fin n → Bool) (τ : Fin n → Fin n → ℚ) : Prop :=
  (∀ i, τ i i = 0) ∧
    ∀ i j, i ≠ j → τ i j = 1 + (1 / 2) * ∑ k, (p A i k * τ j k + p A j k * τ i k)

/-- Allen et al. eq. (6), remeeting time. -/
def remeet (A : Fin n → Fin n → Bool) (τ : Fin n → Fin n → ℚ) (i : Fin n) : ℚ :=
  1 + ∑ j, p A i j * τ i j

/-- Allen et al. eq. (9), effective population size. -/
def neff (A : Fin n → Fin n → Bool) (τ : Fin n → Fin n → ℚ) : ℚ :=
  ∑ i, ((deg A i : ℚ) / ∑ j, (deg A j : ℚ)) * remeet A τ i

theorem p_nonneg (A : Fin n → Fin n → Bool) (i k : Fin n) : 0 ≤ p A i k := by
  unfold p; split_ifs <;> positivity

/-- One-sided maximum principle: a difference `δ` of two solutions is `≤ 0` everywhere. -/
theorem diff_nonpos (A : Fin n → Fin n → Bool) (v δ : Fin n → Fin n → ℚ) (hv : Eq5 A v)
    (hpos : ∀ i j, i ≠ j → 0 < v i j) (hd0 : ∀ i, δ i i = 0)
    (hd : ∀ i j, i ≠ j → δ i j = (1 / 2) * ∑ k, (p A i k * δ j k + p A j k * δ i k)) :
    ∀ i j, δ i j ≤ 0 := by
  by_contra hcon
  push_neg at hcon
  obtain ⟨i0, j0, h0⟩ := hcon
  have hij0 : i0 ≠ j0 := by rintro rfl; rw [hd0] at h0; exact lt_irrefl _ h0
  set S : Finset (Fin n × Fin n) := univ.filter fun x => x.1 ≠ x.2 with hS
  have hmem0 : (i0, j0) ∈ S := by simp [hS, hij0]
  obtain ⟨⟨i, j⟩, hmem, hmax⟩ :=
    S.exists_max_image (fun x => δ x.1 x.2 / v x.1 x.2) ⟨_, hmem0⟩
  have hij : i ≠ j := by simpa [hS] using hmem
  set c := δ i j / v i j with hc
  have hvij := hpos i j hij
  have hc0 : 0 < c := by
    have h1 : 0 < δ i0 j0 / v i0 j0 := div_pos h0 (hpos i0 j0 hij0)
    exact lt_of_lt_of_le h1 (hmax _ hmem0)
  have hle : ∀ k l, δ k l ≤ c * v k l := by
    intro k l
    by_cases hkl : k = l
    · subst hkl; rw [hd0, hv.1]; simp
    · have hm : (k, l) ∈ S := by simp [hS, hkl]
      have h1 := hmax _ hm
      have hvkl := hpos k l hkl
      simp only at h1
      rw [div_le_iff₀ hvkl] at h1
      linarith
  have hsum : ∑ k, (p A i k * δ j k + p A j k * δ i k)
      ≤ c * ∑ k, (p A i k * v j k + p A j k * v i k) := by
    rw [mul_sum]
    apply sum_le_sum
    intro k _
    have a1 := mul_le_mul_of_nonneg_left (hle j k) (p_nonneg A i k)
    have a2 := mul_le_mul_of_nonneg_left (hle i k) (p_nonneg A j k)
    nlinarith
  have hvq := hv.2 i j hij
  have hdq := hd i j hij
  have hδ : δ i j = c * v i j := by rw [hc]; field_simp
  nlinarith

/-- Uniqueness of the solution of eq. (5), given one solution positive off the diagonal. -/
theorem eq5_unique (A : Fin n → Fin n → Bool) (v τ : Fin n → Fin n → ℚ) (hv : Eq5 A v)
    (hpos : ∀ i j, i ≠ j → 0 < v i j) (hτ : Eq5 A τ) : τ = v := by
  have key : ∀ (a b : Fin n → Fin n → ℚ), Eq5 A a → Eq5 A b → ∀ i j, i ≠ j →
      a i j - b i j = (1 / 2) * ∑ k, (p A i k * (a j k - b j k) + p A j k * (a i k - b i k)) := by
    intro a b ha hb i j hij
    have hs : ∑ k, (p A i k * (a j k - b j k) + p A j k * (a i k - b i k))
        = ∑ k, (p A i k * a j k + p A j k * a i k) - ∑ k, (p A i k * b j k + p A j k * b i k) := by
      rw [← sum_sub_distrib]
      exact sum_congr rfl (fun k _ => by ring)
    rw [hs, ha.2 i j hij, hb.2 i j hij]
    ring
  have h1 := diff_nonpos A v (fun i j => τ i j - v i j) hv hpos (by intro i; simp [hτ.1, hv.1])
    (fun i j hij => key τ v hτ hv i j hij)
  have h2 := diff_nonpos A v (fun i j => v i j - τ i j) hv hpos (by intro i; simp [hτ.1, hv.1])
    (fun i j hij => key v τ hv hτ i j hij)
  funext i j
  have a1 : τ i j - v i j ≤ 0 := h1 i j
  have a2 : v i j - τ i j ≤ 0 := h2 i j
  linarith

/-- Certificate lifting: if a rational `v` positive off the diagonal solves eq. (5), then every
solution has `N_eff = neff A v`. -/
theorem neff_of_cert (A : Fin n → Fin n → Bool) (v : Fin n → Fin n → ℚ) (hv : Eq5 A v)
    (hpos : ∀ i j, i ≠ j → 0 < v i j) (τ : Fin n → Fin n → ℚ) (hτ : Eq5 A τ) :
    neff A τ = neff A v := by
  rw [eq5_unique A v τ hv hpos hτ]

end AmplifierCensus
