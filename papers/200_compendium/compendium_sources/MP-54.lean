theorem problem_54_hodge_star_dual_involution
    {E : Type*} [AddCommGroup E] (star : E →+ E)
    (h_invol : ∀ x, star (star x) = x) (w : E) :
    star (star w) - w = 0 := by
  rw [h_invol w, sub_self]