theorem problem_1_lagrange_index_multiplicativity
    {G : Type*} [Group G] [Finite G] (H : Subgroup G) :
    Nat.card H * H.index = Nat.card G := by
  exact Subgroup.card_mul_index H