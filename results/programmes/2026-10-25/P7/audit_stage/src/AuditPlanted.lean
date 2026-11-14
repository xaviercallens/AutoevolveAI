import Programmes.PopGen.MoranFixation
import Programmes.PopGen.Price

/-! Auditor's own planted controls (P7 audit). Must be CAUGHT by #print axioms. -/

namespace P7AuditPlanted

open ProgPopGen ProgPopGen.Price Filter Topology

/-- Planted sorry on a FALSE claim (neutral limit under selection). -/
theorem audit_sorry :
    Tendsto (fun n => kPow (moranP 10 (3 / 2)) n 1 (Fin.last 10)) atTop (𝓝 (1 / 10)) := by
  sorry

/-- Planted axiom on a FALSE Price claim. -/
axiom audit_cheat : ∀ (n w : Fin 2 → ℚ), wbarNext Finset.univ n w - wmean Finset.univ n w = wvar Finset.univ n w

theorem audit_axiom :
    wbarNext (Finset.univ : Finset (Fin 2)) ![1, 1] ![1, 2] - wmean Finset.univ ![1, 1] ![1, 2]
      = wvar (Finset.univ : Finset (Fin 2)) ![1, 1] (![1, 2] : Fin 2 → ℚ) := audit_cheat _ _

/-- Sorry hidden inside a lemma used by an otherwise honest-looking theorem. -/
theorem audit_hidden_lemma : moranFix 3 2 1 = 4 / 7 := by sorry

theorem audit_uses_hidden : moranFix 3 2 1 + 0 = 4 / 7 := by rw [add_zero]; exact audit_hidden_lemma

end P7AuditPlanted

#print axioms P7AuditPlanted.audit_sorry
#print axioms P7AuditPlanted.audit_axiom
#print axioms P7AuditPlanted.audit_uses_hidden
