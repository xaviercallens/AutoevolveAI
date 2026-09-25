theorem problem_8_fermats_little_theorem
    (p : ℕ) [Fact p.Prime] (a : ZMod p) (ha : a ≠ 0) :
    a ^ (p - 1) = 1 := by
  exact ZMod.pow_card_sub_one_eq_one ha