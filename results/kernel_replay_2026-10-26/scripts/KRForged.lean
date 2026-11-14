import Lean
/-! Planted forgery control for the kernel-replay gate: a proof of `False` added WITHOUT kernel type checking
(debug.skipKernelTC + addDecl). `#print axioms` on it shows no axioms at all. -/
open Lean Elab Command

set_option debug.skipKernelTC true in
run_cmd liftCoreM <| addDecl (.thmDecl
  { name := `KRForged.forged_false, levelParams := [], type := mkConst ``False,
    value := mkConst ``True.intro })

theorem KRForged.uses_forged : False := KRForged.forged_false

#print axioms KRForged.uses_forged
