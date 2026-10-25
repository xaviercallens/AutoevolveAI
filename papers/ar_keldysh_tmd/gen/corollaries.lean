theorem triangular_keldysh_optimal {r0 : ℝ} (hr0 : 0 < r0) (C : Set Plane) (hC : LocallyFinite C)
    (hdens : DensityOne C) : latticeEnergy (keldysh r0) ≤ energy (keldysh r0) C := -- proof elided

theorem keldyshReg_admissible {r0 ε : ℝ} (hr0 : 0 < r0) (hε : 0 ≤ ε) :
    AdmissiblePotential (keldyshReg r0 ε) := -- proof elided

theorem triangular_keldyshReg_optimal {r0 ε : ℝ} (hr0 : 0 < r0) (hε : 0 ≤ ε) (C : Set Plane)
    (hC : LocallyFinite C) (hdens : DensityOne C) :
    latticeEnergy (keldyshReg r0 ε) ≤ energy (keldyshReg r0 ε) C := -- proof elided
