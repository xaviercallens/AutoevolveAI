import Programmes.LonelyRunnerInd.ScalarInputs

/-! Must-fail controls (nothing imports this file). The kernel must REJECT `ctl_wrong_length` and
`ctl_drop_467`, so this file must NOT compile; this shows the `decide` checks are not vacuous. -/

namespace LonelyRunnerInd

theorem ctl_wrong_length : P10.length = 60 := by decide

theorem ctl_drop_467 : 55 ^ 90 ≤ 10 ^ 10 * (P10.prod / 467) := by decide

end LonelyRunnerInd
