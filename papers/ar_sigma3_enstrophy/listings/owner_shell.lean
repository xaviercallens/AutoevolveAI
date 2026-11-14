-- QuantumFluidsShell.lean  sha256 8da44064789a2489f51993ff8b30c70ebc2a2c679e6a7824992d8f7be71a731f
-- lines 42-45
noncomputable def shellBc (k : ℕ → ℝ) : ℕ → (ℕ → ℂ) → ℂ
  | 0,     v => -((k 0 : ℂ) * (starRingEnd ℂ) (v 0) * v 1)
  | m + 1, v => (k m : ℂ) * (v m * v m)
                  - (k (m + 1) : ℂ) * (starRingEnd ℂ) (v (m + 1)) * v (m + 2)
