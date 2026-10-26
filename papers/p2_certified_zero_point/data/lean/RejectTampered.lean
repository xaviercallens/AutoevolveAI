import Programmes.ZeroPointCert.Basic

/-!
# B2 control: a tampered certificate must be REJECTED by the kernel (this file must fail to compile)

The upper end `Upp0_hi` of the U''(0) enclosure is replaced by its negative (sign flip, the kind of error a broken
emitter would make). The certificate inequality is then false, and `norm_num` must fail. Expected: rc != 0.
-/

namespace ProgZeroPointCert

theorem tampered_cert : (475041875131 / 250000000000 : ℝ) + trW_hi * esum_hi < 0 := by
  norm_num [trW_hi, esum_hi]

end ProgZeroPointCert
