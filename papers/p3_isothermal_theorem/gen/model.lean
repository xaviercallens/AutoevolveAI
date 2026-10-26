noncomputable def fit (r : ℝ) (S : Finset (Fin n)) (i : Fin n) : ℝ := if i ∈ S then r else 1

noncomputable def ind (S : Finset (Fin n)) (i : Fin n) : ℝ := if i ∈ S then 1 else 0

def upd (S : Finset (Fin n)) (i j : Fin n) : Finset (Fin n) := if i ∈ S then insert j S else S.erase j

noncomputable def totFit (μ : Fin n → ℝ) (r : ℝ) (S : Finset (Fin n)) : ℝ := ∑ k, μ k * fit r S k

noncomputable def coef (μ : Fin n → ℝ) (W : Fin n → Fin n → ℝ) (r : ℝ) (S : Finset (Fin n))
    (i j : Fin n) : ℝ :=
  μ i * fit r S i / totFit μ r S * W i j

noncomputable def bdK (μ : Fin n → ℝ) (W : Fin n → Fin n → ℝ) (r : ℝ) (S T : Finset (Fin n)) : ℝ :=
  ∑ i, ∑ j, coef μ W r S i j * (if upd S i j = T then 1 else 0)

noncomputable def cutOut (μ : Fin n → ℝ) (W : Fin n → Fin n → ℝ) (S : Finset (Fin n)) : ℝ :=
  ∑ i, ∑ j, μ i * W i j * (ind S i * (1 - ind S j))

noncomputable def cutIn (μ : Fin n → ℝ) (W : Fin n → Fin n → ℝ) (S : Finset (Fin n)) : ℝ :=
  ∑ i, ∑ j, μ i * W i j * ((1 - ind S i) * ind S j)

noncomputable def upP (μ : Fin n → ℝ) (W : Fin n → Fin n → ℝ) (r : ℝ) (S : Finset (Fin n)) : ℝ :=
  ∑ T, bdK μ W r S T * (if T.card = S.card + 1 then 1 else 0)

noncomputable def downP (μ : Fin n → ℝ) (W : Fin n → Fin n → ℝ) (r : ℝ) (S : Finset (Fin n)) : ℝ :=
  ∑ T, bdK μ W r S T * (if T.card + 1 = S.card then 1 else 0)

structure RowStochastic (W : Fin n → Fin n → ℝ) : Prop where
  nonneg : ∀ i j, 0 ≤ W i j
  rowSum : ∀ i, ∑ j, W i j = 1

structure Isothermal (W : Fin n → Fin n → ℝ) : Prop extends RowStochastic W where
  colSum : ∀ j, ∑ i, W i j = 1

def StronglyConnected (W : Fin n → Fin n → ℝ) : Prop :=
  ∀ a b, Relation.TransGen (fun x y => 0 < W x y) a b

def CutPositive (μ : Fin n → ℝ) (W : Fin n → Fin n → ℝ) : Prop :=
  ∀ S : Finset (Fin n), S ≠ ∅ → S ≠ univ → ∃ i ∈ S, ∃ j ∉ S, 0 < μ i * W i j
