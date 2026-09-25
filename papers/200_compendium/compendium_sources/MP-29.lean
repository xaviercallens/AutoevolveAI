theorem problem_29_maxwell_bianchi_identity
    {R : Type*} [CommRing R] {M : Type*} [AddCommGroup M] [Module R M] (v : M) :
    ExteriorAlgebra.ι R v * ExteriorAlgebra.ι R v = 0 :=
  ExteriorAlgebra.ι_sq_zero v