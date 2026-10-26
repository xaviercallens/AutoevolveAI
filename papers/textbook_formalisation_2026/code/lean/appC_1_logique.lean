/-
Annexe C, exemple 1 : logique propositionnelle et quantificateurs, Lean 4 sans bibliothèque.
Tactiques : intro, exact, apply, constructor, cases (via obtain), rfl.
-/

-- Un terme de preuve : on écrit directement l'objet (une paire).
theorem et_comm_terme (p q : Prop) (h : p ∧ q) : q ∧ p := ⟨h.2, h.1⟩

-- La même chose en mode tactique.
theorem et_comm_tactique (p q : Prop) : p ∧ q → q ∧ p := by
  intro h
  obtain ⟨hp, hq⟩ := h
  constructor
  · exact hq
  · exact hp

-- apply : on raisonne « en arrière » à partir de la conclusion.
theorem modus_ponens_chaine (p q r : Prop) (hpq : p → q) (hqr : q → r) : p → r := by
  intro hp
  apply hqr
  apply hpq
  exact hp

-- Quantificateurs : un « pour tout » est une fonction, un « il existe » une paire (témoin, preuve).
theorem existe_successeur : ∀ n : Nat, ∃ m : Nat, m = n + 1 := by
  intro n
  exact ⟨n + 1, rfl⟩

#print axioms et_comm_terme
#print axioms et_comm_tactique
#print axioms modus_ponens_chaine
#print axioms existe_successeur
