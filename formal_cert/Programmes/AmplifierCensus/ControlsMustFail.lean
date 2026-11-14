import Programmes.AmplifierCensus.Controls

/-!
# Must-fail control (nothing imports this file): this file is EXPECTED NOT TO COMPILE.

The kernel is asked to accept the perturbed vector `tauBad` as a solution of eq. (5) on `GR11`.
`decide +kernel` must report that the proposition evaluates to `false`; a successful compile of this
file would mean the checker accepts a wrong certificate.
-/

namespace AmplifierCensusMustFail

open AmplifierCensus AmplifierCensusControls

theorem planted_wrong_certificate : Eq5 GR11 tauBad := by
  unfold Eq5; decide +kernel

end AmplifierCensusMustFail
