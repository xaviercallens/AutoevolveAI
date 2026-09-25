structure ComplexProjectiveManifold where
  dim : Nat
  is_smooth : Prop

structure CohomologyClass (X : ComplexProjectiveManifold) (k : Nat) where
  is_hodge : Prop
  is_algebraic : Prop

def hodge_conjecture : Prop :=
  ∀ (X : ComplexProjectiveManifold) (k : Nat),
    X.is_smooth →
    ∀ (alpha : CohomologyClass X (2 * k)),
      alpha.is_hodge → alpha.is_algebraic
