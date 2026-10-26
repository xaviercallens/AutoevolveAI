import Programmes.Famille.Acronymes

/-! Annexe F, exemple 11 : lire et verifier le theoreme ILENE (theoreme isotherme, un mutant).
Compile avec Lean 4.34.1 + Mathlib d13f23b7 (scripts/certified_numerics/lean_pinned.py). -/

open Acronymes

-- 1. L'enonce exact, tel que Lean le connait.
#check @ILENE

-- 2. Les axiomes dont depend la preuve (liste blanche : propext, Classical.choice, Quot.sound).
#print axioms ILENE

-- 3. La valeur limite pour n = 4 et r = 2, celle du cycle de l'exemple 5 : 8/15.
example : (1 - 1 / (2 : Real)) / (1 - (1 / (2 : Real)) ^ 4) = 8 / 15 := by norm_num

-- 4. Temoin negatif plante : une egalite fausse "prouvee" par sorry. Le fichier compile quand meme
--    (avertissement seulement) ; c'est #print axioms qui trahit la fraude.
theorem planted_wrong_value : (1 - 1 / (2 : Real)) / (1 - (1 / (2 : Real)) ^ 4) = 4 / 7 := by sorry

#print axioms planted_wrong_value
