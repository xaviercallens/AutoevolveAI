noncomputable def kPow (P : Fin (N + 1) → Fin (N + 1) → ℝ) : ℕ → Fin (N + 1) → Fin (N + 1) → ℝ
  | 0 => fun i j => if i = j then 1 else 0
  | n + 1 => fun i j => ∑ k, kPow P n i k * P k j

structure AbsorbingChain (P : Fin (N + 1) → Fin (N + 1) → ℝ) : Prop where
  nonneg : ∀ i j, 0 ≤ P i j
  rowSum : ∀ i, ∑ j, P i j = 1
  absorb0 : ∀ j, P 0 j = if j = 0 then 1 else 0
  absorbN : ∀ j, P (Fin.last N) j = if j = Fin.last N then 1 else 0

def InteriorHarmonic (P : Fin (N + 1) → Fin (N + 1) → ℝ) (g : Fin (N + 1) → ℝ) : Prop :=
  ∀ i : Fin (N + 1), 0 < (i : ℕ) → (i : ℕ) < N → ∑ j, P i j * g j = g i
