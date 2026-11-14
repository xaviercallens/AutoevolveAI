import Lean
/-!
A2 kernel replay (same mechanism as the toolchain's `leanchecker`, `Lean.Replay`, but with
ONE base environment): read every declaration stored in the .olean files of the listed corpus
modules (all olean levels, the last one subsumes the others), import only the non-corpus
dependencies (Mathlib etc.), and replay all corpus declarations through the kernel into that
base environment. Any declaration that was added without kernel checking (e.g. under
`debug.skipKernelTC`, or forged by a metaprogram) makes the replay throw.

usage: lean --run A2Replay.lean <corpus_modules.txt> <external_imports.txt>
-/
open Lean

unsafe def main (args : List String) : IO UInt32 := do
  initSearchPath (← findSysroot)
  let corpus := ((← IO.FS.lines args[0]!).filter (· ≠ "")).map String.toName
  let ext := ((← IO.FS.lines args[1]!).filter (· ≠ "")).map String.toName
  let mut newConstants : Std.HashMap Name ConstantInfo := {}
  for m in corpus do
    let mFile ← findOLean m
    unless (← mFile.pathExists) do
      throw <| IO.userError s!"object file '{mFile}' of module {m} does not exist"
    let mut fnames := #[mFile]
    let sFile := OLeanLevel.server.adjustFileName mFile
    if (← sFile.pathExists) then
      fnames := fnames.push sFile
      let pFile := OLeanLevel.private.adjustFileName mFile
      if (← pFile.pathExists) then
        fnames := fnames.push pFile
    let parts ← readModuleDataParts fnames
    if h : parts.size = 0 then throw <| IO.userError s!"failed to read module data of {m}" else
    let last : ModuleData := parts[parts.size - 1].1
    for name in last.constNames, ci in last.constants do
      newConstants := newConstants.insert name ci
  IO.println s!"corpus modules={corpus.size} corpus constants={newConstants.size}"
  let imports : Array Import := ext.map fun m => { module := m }
  let (_, s) ← importModulesCore imports |>.run
  let env ← finalizeImport s imports {} 0 false false (isModule := true)
  IO.println s!"base environment constants={env.constants.fold (fun n _ _ => n + 1) 0} (imports={imports.size})"
  let clash := newConstants.fold (fun acc n _ => if env.contains n then acc.push n else acc) #[]
  IO.println s!"corpus constants already present in base env={clash.size}: {clash}"
  if args.length > 2 && args[2]! == "--clashes-only" then
    for n in clash do
      let a := (env.find? n).map (·.type.hash)
      let b := (newConstants.get? n).map (·.type.hash)
      let mi := (env.getModuleIdxFor? n).map fun i => env.header.moduleNames[i.toNat]!
      IO.println s!"  clash {n}: base module={mi} base type hash={a} corpus type hash={b}"
    return 0
  let t0 ← IO.monoMsNow
  discard <| env.toKernelEnv.replay newConstants
  let t1 ← IO.monoMsNow
  IO.println s!"REPLAY OK: {newConstants.size} declarations kernel-checked in {t1 - t0} ms"
  return 0
