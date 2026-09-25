theorem problem_14_baire_category {X : Type*} [TopologicalSpace X] [BaireSpace X] 
    (s : ℕ → Set X) (ho : ∀ n, IsOpen (s n)) (hd : ∀ n, Dense (s n)) : 
    Dense (⋂ n, s n) :=
  BaireSpace.baire_property s ho hd