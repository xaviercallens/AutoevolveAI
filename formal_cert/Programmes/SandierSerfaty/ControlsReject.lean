import Programmes.SandierSerfaty.Asserts
import Programmes.SandierSerfaty.Constants
import Programmes.SandierSerfaty.Controls

/-!
# Planted FALSE stages stated as theorems: this file MUST FAIL to compile

Each theorem below is a planted false stage (a perturbed constant or endpoint) asserted with `decide +kernel`, exactly
as the genuine stage theorems are. The kernel must reject every one of them ("Tactic `decide` proved that the
proposition ... is false"); the compile log is recorded in `results/proposal2/2026-10-26/A1/logs/`.
-/

namespace ProgSandierSerfaty.Cert.Reject

open ProgSandierSerfaty.Cert ProgSandierSerfaty.Cert.IV ProgSandierSerfaty.Cert.Controls

theorem rej_pi_shift :
    (((piC.u + 2 ^ 100 : Int) : ℚ) / (Q : ℚ)) ≤ 16 * (atS (1 / 5) 150 - e5) - 4 * (atS (1 / 239) 150 + e239) := by
  decide +kernel

set_option maxRecDepth 100000 in
theorem rej_ln2_199 : add (mul (ofInt 2) (ln2Loop 199 0 (div oneI (ofInt 3)) zeroI)) ⟨-1, 1⟩ = ln2C := by
  decide +kernel

theorem rej_pair : coarse gmfC = (121, 162) := by decide +kernel

theorem rej_gmf_121 : 121 * Q ≤ 10000000 * gmfC.u := by decide +kernel

theorem rej_erdrop_x2 : (add (add drnegC (mul (ofInt 2) erdropC)) KC).v < 0 := by decide +kernel

theorem rej_det : 87 * Q ≤ 10000 * detC.u := by decide +kernel

set_option maxRecDepth 100000 in
theorem rej_G_eight_to_four :
    Gs4 pilot_lam pilot_mu pilot_eps pilot_p (calcK_s 0) calcK_G0_cells = some calcK_G0_expected := by
  decide +kernel

end ProgSandierSerfaty.Cert.Reject
