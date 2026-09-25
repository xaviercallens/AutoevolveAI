theorem problem_22_stokes_divergence {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E] [CompleteSpace E] {n : ℕ} 
    (I : Box (Fin (n + 1)))
    (f : (Fin (n + 1) → ℝ) → Fin (n + 1) → E)
    (f' : (Fin (n + 1) → ℝ) → (Fin (n + 1) → ℝ) →L[ℝ] (Fin (n + 1) → E))
    (s : Set (Fin (n + 1) → ℝ)) (hs : s.Countable)
    (Hs : ∀ x ∈ s, ContinuousWithinAt f (Box.Icc I) x)
    (Hd : ∀ x ∈ (Box.Icc I) \ s, HasFDerivWithinAt f (f' x) (Box.Icc I) x) :
    HasIntegral I GP (fun x => ∑ i, f' x (Pi.single i 1) i) BoxAdditiveMap.volume
      (∑ i, (integral (I.face i) GP (fun x => f (i.insertNth (I.upper i) x) i) BoxAdditiveMap.volume -
             integral (I.face i) GP (fun x => f (i.insertNth (I.lower i) x) i) BoxAdditiveMap.volume)) :=
  hasIntegral_GP_divergence_of_forall_hasDerivWithinAt I f f' s hs Hs Hd