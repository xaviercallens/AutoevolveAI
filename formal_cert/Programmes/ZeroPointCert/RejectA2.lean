import Programmes.ZeroPointCert.Basic

/-!
# B2 negative control: the a = 2 certificate must be REJECTED by the kernel (this file must fail to compile)

Endpoints copied verbatim from `results/proposal2/2026-10-26/B2/run_a2_shear_negctl.json` (`cert_rationals`).
At a = 2 the triangular lattice is a local minimum (P2, Tier X), and the linear-response bound is positive, so the
claimed inequality is false and `norm_num` must fail. Expected: rc != 0.
-/

namespace ProgZeroPointCert

theorem a2_cert_claim :
    (3189252546719 / 250000000000 : ℝ) + (966174495059 / 200000000000) * (1018658311 / 62500000000) < 0 := by
  norm_num

end ProgZeroPointCert
