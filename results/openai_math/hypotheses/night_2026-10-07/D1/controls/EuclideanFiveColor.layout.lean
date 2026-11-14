/- header /- nested -/ comment -/
import Mathlib

namespace OAI

namespace EuclideanFiveColor

def ProperColoring (colorCount : ℕ) (coloring : ℂ → Fin colorCount) : Prop :=
    ∀ point otherPoint : ℂ, ‖point - otherPoint‖ = 1 → coloring point ≠ coloring otherPoint  -- control comment

theorem no_proper_five_coloring : ¬ ∃ coloring : ℂ → Fin 5, ProperColoring 5 coloring := by
    sorry  -- control comment

end EuclideanFiveColor

end OAI
