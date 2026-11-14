import Lean
import NavierStokes.ComparatorSolution
open Lean Meta Elab Command

namespace A2Audit

/-- Direct dependencies used for the *statement* closure: types always, values of
definitions/opaques, constructor/inductive links; theorem proofs are skipped. -/
def stmtDeps (ci : ConstantInfo) : Array Name :=
  let t := ci.type.getUsedConstants
  match ci with
  | .defnInfo d => t ++ d.value.getUsedConstants
  | .opaqueInfo o => t ++ o.value.getUsedConstants
  | .inductInfo i => t ++ i.ctors.toArray ++ i.all.toArray
  | .ctorInfo c => t.push c.induct
  | .recInfo r => t ++ r.all.toArray
  | .quotInfo _ => t
  | _ => t

/-- Dependencies including theorem proofs (full proof closure). -/
def fullDeps (ci : ConstantInfo) : Array Name :=
  match ci with
  | .thmInfo th => ci.type.getUsedConstants ++ th.value.getUsedConstants
  | _ => stmtDeps ci

def closure (env : Environment) (roots : Array Name) (deps : ConstantInfo → Array Name) :
    Array Name := Id.run do
  let mut seen : NameSet := {}
  let mut out : Array Name := #[]
  let mut stack : Array Name := roots
  for _ in [0:100000000] do
    match stack.back? with
    | none => break
    | some n =>
      stack := stack.pop
      if seen.contains n then continue
      seen := seen.insert n
      out := out.push n
      match env.find? n with
      | none => pure ()
      | some ci => stack := stack ++ deps ci
  return out

def kindOf : ConstantInfo → String
  | .axiomInfo _ => "axiom" | .defnInfo _ => "def" | .thmInfo _ => "thm"
  | .opaqueInfo _ => "opaque" | .quotInfo _ => "quot" | .inductInfo _ => "induct"
  | .ctorInfo _ => "ctor" | .recInfo _ => "rec"

def modOf (env : Environment) (n : Name) : String :=
  match env.getModuleIdxFor? n with
  | some i => toString (env.header.moduleNames[i.toNat]!)
  | none => "<current>"

def isCorpusMod (m : String) : Bool :=
  m.startsWith "NavierStokes" || m.startsWith "Euler" || m.startsWith "ComparatorChallenges"
    || m == "<current>"

/-- One line per constant of the statement closure: name, kind, levels, type hash, value hash;
for corpus constants also the raw `Expr` text of type and value. -/
def dumpStatement (roots : Array Name) (path : String) : CommandElabM Unit := do
  let env ← getEnv
  let names := (closure env roots stmtDeps).qsort (fun a b => a.toString < b.toString)
  let mut lines : Array String := #[]
  for n in names do
    match env.find? n with
    | none => lines := lines.push s!"{n}\tMISSING"
    | some ci =>
      let vh := match ci with
        | .defnInfo d => toString d.value.hash
        | .opaqueInfo o => toString o.value.hash
        | .thmInfo _ => "proof-skipped"
        | .inductInfo i => s!"params={i.numParams} idx={i.numIndices} ctors={i.ctors} rec={i.isRec} unsafe={i.isUnsafe}"
        | .ctorInfo c => s!"cidx={c.cidx} nf={c.numFields}"
        | _ => "-"
      let m := modOf env n
      let corpus := isCorpusMod m
      let body := if corpus then
          match ci with
          | .defnInfo d => s!"\tTYPE={ci.type}\tVALUE={d.value}"
          | _ => s!"\tTYPE={ci.type}"
        else ""
      lines := lines.push s!"{n}\t{kindOf ci}\t{ci.levelParams}\t{ci.type.hash}\t{vh}\tcorpus={corpus}{body}"
  IO.FS.writeFile path (String.intercalate "\n" lines.toList ++ "\n")
  logInfo m!"A2 statement closure: {names.size} constants written to {path}"

/-- Soundness flags over the full proof closure of the roots. -/
def soundnessScan (roots : Array Name) (path : String) : CommandElabM Unit := do
  let env ← getEnv
  let names := closure env roots fullDeps
  let bad : Array Name := #[``Lean.ofReduceBool, ``Lean.ofReduceNat, ``Lean.trustCompiler, ``sorryAx]
  let mut lines : Array String := #[]
  let mut nCorpus := 0
  let mut mods : NameSet := {}
  for n in names do
    match env.find? n with
    | none => lines := lines.push s!"MISSING\t{n}"
    | some ci =>
      let m := modOf env n
      if isCorpusMod m then
        nCorpus := nCorpus + 1
        mods := mods.insert m.toName
      if bad.contains n then lines := lines.push s!"BAD_CONST_IN_CLOSURE\t{n}\t{m}"
      if ci.isUnsafe then lines := lines.push s!"UNSAFE\t{n}\t{m}"
      if ci.isPartial then lines := lines.push s!"PARTIAL\t{n}\t{m}"
      match ci with
      | .axiomInfo _ => lines := lines.push s!"AXIOM\t{n}\t{m}"
      | .opaqueInfo _ => lines := lines.push s!"OPAQUE\t{n}\t{m}"
      | _ => pure ()
      if (Lean.Compiler.getImplementedBy? env n).isSome then
        lines := lines.push s!"IMPLEMENTED_BY\t{n}\t{m}"
      if Lean.isExtern env n then lines := lines.push s!"EXTERN\t{n}\t{m}"
  -- every axiom anywhere in the imported environment, and every corpus-module
  -- constant with an unsafe/partial/implemented_by/extern flag (whole env, not just closure)
  let mut envAxioms : Array String := #[]
  let mut corpusFlags : Array String := #[]
  let mut nCorpusEnv := 0
  for (n, ci) in env.constants.toList do
    if let .axiomInfo _ := ci then envAxioms := envAxioms.push s!"{n}\t{modOf env n}"
    let m := modOf env n
    if isCorpusMod m && !((`A2Audit).isPrefixOf n) then
      nCorpusEnv := nCorpusEnv + 1
      if ci.isUnsafe || ci.isPartial || (Lean.Compiler.getImplementedBy? env n).isSome
          || Lean.isExtern env n then
        corpusFlags := corpusFlags.push s!"{n}\t{m}\tunsafe={ci.isUnsafe} partial={ci.isPartial}"
      match ci with
      | .axiomInfo _ => corpusFlags := corpusFlags.push s!"{n}\t{m}\tAXIOM"
      | .opaqueInfo _ => corpusFlags := corpusFlags.push s!"{n}\t{m}\tOPAQUE"
      | _ => pure ()
  let header := s!"closure_constants={names.size} corpus_constants_in_closure={nCorpus} corpus_modules_in_closure={mods.size} corpus_constants_in_env={nCorpusEnv} env_axioms={envAxioms.size}"
  let txt := header ++ "\n## closure flags\n" ++ String.intercalate "\n" lines.toList
    ++ "\n## all axioms in environment\n" ++ String.intercalate "\n" (envAxioms.qsort (· < ·)).toList
    ++ "\n## corpus-module flagged constants (whole env)\n" ++ String.intercalate "\n" corpusFlags.toList ++ "\n"
  IO.FS.writeFile path txt
  logInfo m!"A2 soundness: {header}; closure flags={lines.size}; corpus flags={corpusFlags.size}"

end A2Audit


run_cmd A2Audit.dumpStatement #[`NavierStokes.Comparator.navier_stokes_breakdown_R3, `NavierStokes.Comparator.navier_stokes_breakdown_periodic] "/home/callensxavier_gmail_com/proposal2/A2/audit/stmt_solution_ns.tsv"
run_cmd A2Audit.soundnessScan #[`NavierStokes.Comparator.navier_stokes_breakdown_R3, `NavierStokes.Comparator.navier_stokes_breakdown_periodic] "/home/callensxavier_gmail_com/proposal2/A2/audit/sound_ns.txt"
#print axioms NavierStokes.Comparator.navier_stokes_breakdown_R3
#print axioms NavierStokes.Comparator.navier_stokes_breakdown_periodic
