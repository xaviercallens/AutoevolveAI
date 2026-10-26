/-
Annexe C, exemple 2 : calcul dans les réels avec Mathlib.
Tactiques : ring, linarith, nlinarith, norm_num, positivity.
Imports épinglés sur des modules construits (jamais `import Mathlib` en entier).
-/
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Positivity

-- ring : identité de polynômes, dans tout anneau commutatif.
theorem carre_somme (a b : ℝ) : (a + b) ^ 2 = a ^ 2 + 2 * a * b + b ^ 2 := by
  ring

-- linarith : combinaison linéaire d'hypothèses (inégalités linéaires).
theorem moyenne_entre (x y : ℝ) (h : x ≤ y) : x ≤ (x + y) / 2 := by
  linarith

-- nlinarith : on lui fournit le carré positif qui sert d'indice.
theorem am_gm_deux (a b : ℝ) : 2 * a * b ≤ a ^ 2 + b ^ 2 := by
  nlinarith [sq_nonneg (a - b)]

-- norm_num : arithmétique exacte sur des littéraux (ici, des rationnels).
theorem quatre_septiemes : (4 : ℝ) / 7 - 1 / 3 = 5 / 21 := by
  norm_num

-- positivity : prouve 0 < e ou 0 ≤ e à partir de la forme de l'expression.
theorem positif (x : ℝ) : 0 < x ^ 2 + 1 := by
  positivity

#print axioms carre_somme
#print axioms moyenne_entre
#print axioms am_gm_deux
#print axioms quatre_septiemes
#print axioms positif
