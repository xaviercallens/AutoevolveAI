theorem problem_13_zorns_lemma {α : Type*} [PartialOrder α] 
    (h : ∀ (c : Set α), IsChain (· ≤ ·) c → BddAbove c) : 
    ∃ m : α, IsMax m :=
  zorn_le h