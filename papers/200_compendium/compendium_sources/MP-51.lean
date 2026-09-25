theorem problem_51_yang_mills_bianchi_identity
    {R : Type*} [CommRing R] {M : Type*} [AddCommGroup M] [Module R M] (v : M) :
    ExteriorAlgebra.ι R v * (ExteriorAlgebra.ι R v * ExteriorAlgebra.ι R v) = 0 := by
  rw [ExteriorAlgebra.ι_sq_zero v, mul_zero]