import Mathlib
open ContDiff Set InnerProductSpace MeasureTheory
open scoped Laplacian

local notation "ℝ³" => EuclideanSpace ℝ (Fin 3)

-- Which Laplacian instance fires for vector fields ℝ³ → ℝ³, and its unfolding
set_option pp.explicit true in
#check fun (w : ℝ³ → ℝ³) (x : ℝ³) => Δ w x
example (w : ℝ³ → ℝ³) (x : ℝ³) :
    Δ w x = ∑ i, iteratedFDeriv ℝ 2 w x ![EuclideanSpace.single i 1, EuclideanSpace.single i 1] := by
  rw [InnerProductSpace.laplacian_eq_iteratedFDeriv_orthonormalBasis w (EuclideanSpace.basisFun (Fin 3) ℝ)]
  simp
#check @InnerProductSpace.laplacian_eq_iteratedFDeriv_orthonormalBasis
