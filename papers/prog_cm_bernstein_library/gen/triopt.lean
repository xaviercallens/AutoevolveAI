/-- Upstream's universal optimality, restated for completely monotone potentials (conditional on
`OAI.AtomicTriangular.universal_energy_minimum`, AI-generated, not peer reviewed). -/
theorem triangular_optimal {g : ℝ → ℝ} (hg : IsCompletelyMonotoneOn g) (C : Set OAI.AtomicTriangular.Plane)
    (hC : OAI.AtomicTriangular.LocallyFinite C) (hd : OAI.AtomicTriangular.DensityOne C) :
    OAI.AtomicTriangular.latticeEnergy g ≤ OAI.AtomicTriangular.energy g C :=
  (OAI.AtomicTriangular.universal_energy_minimum g C hg.admissible hC hd).1
