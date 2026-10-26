import Programmes.SandierSerfaty.Chain

/-! Added after the independent audit (AUDIT.md, N4). New file; no locked file is modified.
Links the stage-8 literals `slopeC` and `flC` of `Asserts.lean` to the L1 outputs: they are recomputed from
`piC`, `bconsC`, `lambdaC`, `muC`, `CalcK.kl` and the table value `f0lC`.
`flC` is conditional on `f0lC` (a table value, stage 3 not ported). -/

namespace ProgSandierSerfaty.Cert.ChainLink

open ProgSandierSerfaty.Cert ProgSandierSerfaty.Cert.IV

/-- slope = -pi * B(l) - lambda / 2, recomputed from the L1 outputs. -/
theorem slope_eq : sub (mul (neg piC) bconsC) (div lambdaC (ofInt 2)) = slopeC := by
  decide +kernel

/-- f(l) = f0(l) - lambda * l * l / 2 - mu, recomputed from the L1 outputs and the table value f0lC. -/
theorem fl_eq :
    sub (sub f0lC (div (mul (mul lambdaC CalcK.kl) CalcK.kl) (ofInt 2))) muC = flC := by
  decide +kernel

end ProgSandierSerfaty.Cert.ChainLink

#print axioms ProgSandierSerfaty.Cert.ChainLink.slope_eq
#print axioms ProgSandierSerfaty.Cert.ChainLink.fl_eq
