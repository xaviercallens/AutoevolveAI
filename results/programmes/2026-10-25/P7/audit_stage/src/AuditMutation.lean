import Programmes.PopGen.MoranFixation

/-! Auditor's mutation test (P7 audit): a FALSE value must make the kernel REJECT (rc != 0). -/

namespace P7AuditMutation

open ProgPopGen

/-- Mutated positive control: the true value is 4/7; 1/3 must fail to check. -/
theorem audit_wrong_value : moranFix 3 2 1 = 1 / 3 := by
  norm_num [moranFix, geomS, Finset.sum_range_succ]

end P7AuditMutation
