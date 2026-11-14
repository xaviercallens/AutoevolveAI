/-
Annexe C, exemple 5 : témoins négatifs de la porte d'axiomes.
Ce fichier compile avec le code de retour 0 ; ce sont les lignes `#print axioms` qui révèlent la triche.
-/

theorem vrai_controle_positif (n : Nat) : n + 0 = n := rfl

theorem faux_par_sorry : 1 = 2 := by sorry

axiom triche : False
theorem faux_par_axiome : 1 = 2 := triche.elim

#print axioms vrai_controle_positif
#print axioms faux_par_sorry
#print axioms faux_par_axiome
