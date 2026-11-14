/-
Annexe C, exemple 6 : une contrefaçon que `#print axioms` ne voit pas, et que le rejeu du noyau refuse.
On ajoute directement au noyau (addDecl) une « preuve » de False dont le terme est True.intro, en lui
demandant de ne pas vérifier les types (debug.skipKernelTC). Le compilateur accepte ; `#print axioms`
n'affiche que la liste blanche ; seul `leanchecker`, qui rejoue chaque déclaration, la refuse.
NE JAMAIS utiliser cette option dans un vrai développement : c'est un témoin négatif.
-/
import Lean
open Lean Elab Command

set_option debug.skipKernelTC true in
run_cmd liftCoreM <| addDecl (.thmDecl
  { name := `contrefacon, levelParams := [], type := mkConst ``False,
    value := mkConst ``True.intro })

theorem un_egale_deux : 1 = 2 := contrefacon.elim

#print axioms contrefacon
#print axioms un_egale_deux
