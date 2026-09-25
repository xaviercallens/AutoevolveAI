theorem problem_32_dirac_clifford_anticommutation
    {R : Type*} [CommRing R] {M : Type*} [AddCommGroup M] [Module R M]
    (Q : QuadraticForm R M) (a b : M) (h_ortho : Q.IsOrtho a b) :
    CliffordAlgebra.ι Q a * CliffordAlgebra.ι Q b + CliffordAlgebra.ι Q b * CliffordAlgebra.ι Q a = 0 :=
  CliffordAlgebra.ι_mul_ι_add_swap_of_isOrtho h_ortho