theorem problem_15_cantors_theorem {α : Type*} (f : α → Set α) : ¬ Function.Surjective f := by
  intro h
  let s : Set α := {x | x ∉ f x}
  obtain ⟨x, hx⟩ := h s
  by_cases hxs : x ∈ s
  · have hx_not : x ∉ f x := hxs; rw [hx] at hx_not; exact hx_not hxs
  · have hx_in : x ∈ f x := by { by_contra hc; exact hxs hc }; rw [hx] at hx_in; exact hxs hx_in