import Programmes.SandierSerfaty.CalcKS0
import Programmes.SandierSerfaty.CalcKF0

/-!
# calcK chunk controls: this file MUST FAIL to compile (planted 1-ulp perturbations of chunk results)

`rej_S0_ulp`, `rej_F0_ulp`: the chunk theorems with the expected lower endpoint moved by one unit (`2^-144`); the
kernel must reject both. `pos_S0_again`, `pos_F0_again` re-prove the genuine chunks in the same file (profiled), so a
rejection is not an artefact of the file. `ctl_S0_ulp_ne`, `ctl_F0_ulp_ne`: honest kernel proofs that the perturbed
statements are false.
-/

namespace ProgSandierSerfaty.Cert.CalcK

open ProgSandierSerfaty.Cert ProgSandierSerfaty.Cert.IV

set_option profiler true

set_option maxRecDepth 100000 in
theorem pos_S0_again : chunkS S0_nodes S0_cells 0 32 S0_val = true := by decide +kernel

set_option maxRecDepth 100000 in
theorem pos_F0_again : chunkF F0_nodes F0_cells 0 8 F0_val = true := by decide +kernel

set_option maxRecDepth 100000 in
theorem ctl_S0_ulp_ne : chunkS S0_nodes S0_cells 0 32 ⟨S0_val.u + 1, S0_val.v⟩ = false := by decide +kernel

set_option maxRecDepth 100000 in
theorem ctl_F0_ulp_ne : chunkF F0_nodes F0_cells 0 8 ⟨F0_val.u - 1, F0_val.v⟩ = false := by decide +kernel

set_option maxRecDepth 100000 in
theorem rej_S0_ulp : chunkS S0_nodes S0_cells 0 32 ⟨S0_val.u + 1, S0_val.v⟩ = true := by decide +kernel

set_option maxRecDepth 100000 in
theorem rej_F0_ulp : chunkF F0_nodes F0_cells 0 8 ⟨F0_val.u - 1, F0_val.v⟩ = true := by decide +kernel

end ProgSandierSerfaty.Cert.CalcK
