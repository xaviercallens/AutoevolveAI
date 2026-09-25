theorem problem_65_brst_charge_nilpotency
    {V : Type*} [AddCommGroup V] (s : V →+ V) (h_nil : ∀ x, s (s x) = 0) (x : V) :
    s (s x) = 0 :=
  h_nil x