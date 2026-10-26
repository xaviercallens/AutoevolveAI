import Lean
/-! A2 negative control for the kernel-replay checker: a proof of `False` whose
declaration is added to the environment WITHOUT kernel type checking. -/
open Lean Elab Command

set_option debug.skipKernelTC true in
run_cmd liftCoreM <| addDecl (.thmDecl
  { name := `A2Forged.forged_false, levelParams := [], type := mkConst ``False,
    value := mkConst ``True.intro })

theorem A2Forged.uses_forged : False := A2Forged.forged_false

#print axioms A2Forged.uses_forged
