noncomputable def bdP (N : ℕ) (p q : ℕ → ℝ) (i j : Fin (N + 1)) : ℝ :=
  (if (j : ℕ) = (i : ℕ) + 1 then p i else 0) + (if (j : ℕ) + 1 = (i : ℕ) then q i else 0) +
    (if (j : ℕ) = (i : ℕ) then 1 - p i - q i else 0)

noncomputable def moranUp (N : ℕ) (r : ℝ) (i : ℕ) : ℝ :=
  r * i / (r * i + ((N : ℝ) - i)) * (((N : ℝ) - i) / N)

noncomputable def moranDown (N : ℕ) (r : ℝ) (i : ℕ) : ℝ :=
  ((N : ℝ) - i) / (r * i + ((N : ℝ) - i)) * ((i : ℝ) / N)

noncomputable def moranP (N : ℕ) (r : ℝ) : Fin (N + 1) → Fin (N + 1) → ℝ :=
  bdP N (moranUp N r) (moranDown N r)

noncomputable def geomS (r : ℝ) (n : ℕ) : ℝ := ∑ k ∈ range n, r⁻¹ ^ k

noncomputable def moranFix (N : ℕ) (r : ℝ) (i : ℕ) : ℝ := geomS r i / geomS r N
