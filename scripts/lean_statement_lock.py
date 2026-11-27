#!/usr/bin/env python3
"""Statement lock for the Lean files of this repository (pinned Lean 4.34.1 + Mathlib d13f23b7).

What it does.  For each named declaration (usually a headline theorem) it asks Lean ITSELF for the elaborated type
(`pp.all`, explicit universes, full names, no notation) and for the transitive closure of the definitions, instances,
structures and axioms that this type mentions and that live in the programme's own modules (module name starting with
`Programmes.` by default; Mathlib and core are NOT expanded).  The canonical text and its SHA-256 go into a lock JSON.
`check` recompiles with the pinned toolchain and compares; any difference is a failure with a unified diff.

What it does NOT do.  It does not prove that the statement means what a paper says (a human/auditor fidelity reading is
still needed), it does not look at proofs (changing a proof is invisible, by design), it does not pin Mathlib
definitions (the Mathlib commit is recorded and must match), and it cannot know whether the statement was hard to
prove before the lock was written (see `status`: `post_hoc` or `pre_proof`).

Usage (all compilation is pinned and happens in a scratch olean directory; nothing is built in the main formal/ tree):
    python3 scripts/lean_statement_lock.py update --spec formal_cert/locks/specs/LowDissE3.spec.json
    python3 scripts/lean_statement_lock.py check  --lock formal_cert/locks/LowDissE3.lock.json
    python3 scripts/lean_statement_lock.py check  --all
    python3 scripts/lean_statement_lock.py negctl --lock L --file F.lean --old 'text' --new 'text'
    python3 scripts/lean_statement_lock.py selftest
Spec file: {"programme": str, "status": "post_hoc"|"pre_proof", "module_prefixes": ["Programmes."],
            "entries": [{"file": "formal_cert/Programmes/X/Core.lean", "declarations": ["X.thm", ...]}]}
Exit codes: 0 all locks hold, 1 a lock failed (drift, missing declaration, toolchain mismatch, bad axioms),
2 usage/compilation problem (could not decide).
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts" / "certified_numerics"))
import lean_pinned  # noqa: E402  (pinned toolchain description and LEAN_PATH logic)

LOCK_DIR = REPO / "formal_cert" / "locks"
DEFAULT_ROOT = REPO / "formal_cert"
DEFAULT_SCRATCH = REPO / "formal_cert" / ".olean_out" / "statement_lock"
SCHEMA = 1
AXIOM_WHITELIST = {"propext", "Classical.choice", "Quot.sound"}
LEAN_FLAGS = ["-DautoImplicit=false"]  # same flags as lean_pinned.compile_file
MARK = "\x01"
IMPORT_RE = re.compile(r"^import\s+(\S+)", re.MULTILINE)

PROBE_TEMPLATE = r"""import Lean
@@IMPORTS@@

open Lean Elab Command Meta

namespace StatementLockProbe

def MARK : String := String.singleton (Char.ofNat 1)

def ppOpts (o : Options) : Options :=
  let o := o.setBool `pp.all true
  let o := o.setBool `pp.universes true
  let o := o.setBool `pp.fullNames true
  let o := o.setBool `pp.proofs false
  let o := o.setBool `pp.deepTerms true
  let o := o.set `pp.maxSteps (1000000000 : Nat)
  o.set `format.width (100000000 : Nat)

def ppStr (e : Expr) : MetaM String :=
  withOptions ppOpts do
    let f ← ppExpr e
    return f.pretty 100000000

def kindOf : ConstantInfo → String
  | .axiomInfo _ => "axiom"
  | .defnInfo _ => "def"
  | .thmInfo _ => "theorem"
  | .opaqueInfo _ => "opaque"
  | .quotInfo _ => "quot"
  | .inductInfo _ => "inductive"
  | .ctorInfo _ => "constructor"
  | .recInfo _ => "recursor"

def valueOf? : ConstantInfo → Option Expr
  | .defnInfo v => some v.value
  | .opaqueInfo v => some v.value
  | _ => none

def isThm : ConstantInfo → Bool
  | .thmInfo _ => true
  | _ => false

def refsOf (ci : ConstantInfo) : Array Name :=
  let ts := ci.type.getUsedConstants
  let vs := match valueOf? ci with
    | some v => v.getUsedConstants
    | none => #[]
  let extra : Array Name := match ci with
    | .inductInfo v => v.ctors.toArray
    | _ => #[]
  ts ++ vs ++ extra

def isOwn (env : Environment) (prefixes : List String) (n : Name) : Bool :=
  match env.getModuleIdxFor? n with
  | some idx =>
    match env.header.moduleNames[idx.toNat]? with
    | some m => prefixes.any (fun p => (m.toString).startsWith p)
    | none => false
  | none => false

def closure (env : Environment) (prefixes : List String) (root : Name) : Array Name := Id.run do
  let mut seen : NameSet := {}
  let mut work : Array Name := #[root]
  let mut out : Array Name := #[]
  while !work.isEmpty do
    let n := work.back!
    work := work.pop
    if seen.contains n then continue
    seen := seen.insert n
    match env.find? n with
    | none => continue
    | some ci =>
      if n != root then
        if isThm ci then continue
        out := out.push n
      for c in refsOf ci do
        if !seen.contains c && isOwn env prefixes c then
          work := work.push c
  return out

def flagsOf (env : Environment) (n : Name) (ci : ConstantInfo) : String :=
  let red := match ci with
    | .defnInfo _ =>
      toString (repr (getReducibilityStatusCore env n))
    | _ => "-"
  let inst := if Meta.isInstanceCore env n then "instance" else "-"
  s!"{red},{inst}"

def render (tag : String) (env : Environment) (n : Name) (ci : ConstantInfo) (axs : String) (deps : String)
    (withValue : Bool) : MetaM String := do
  let ty ← ppStr ci.type
  let ups := ",".intercalate (ci.levelParams.map toString)
  let mut s := s!"{MARK}{tag}\t{n}\t{kindOf ci}\t{ups}\t{flagsOf env n ci}\t{axs}\t{deps}\n{MARK}T\n{ty}\n"
  if withValue then
    match valueOf? ci with
    | some v => s := s ++ s!"{MARK}V\n{← ppStr v}\n"
    | none => pure ()
  return s

syntax (name := lockdump) "#lockdump " str str str+ : command

@[command_elab lockdump] def elabLockdump : CommandElab := fun stx => do
  let some path := stx[1].isStrLit? | throwUnsupportedSyntax
  let some pfx := stx[2].isStrLit? | throwUnsupportedSyntax
  let prefixes := pfx.splitOn ","
  let mut roots : Array Name := #[]
  for s in stx[3].getArgs do
    let some t := s.isStrLit? | throwUnsupportedSyntax
    roots := roots.push t.toName
  let env ← getEnv
  let mut out := ""
  let mut table : NameSet := {}
  let mut tableOrder : Array Name := #[]
  for r in roots do
    let some ci := env.find? r | throwError "declaration not found: {r}"
    let axs ← collectAxioms r
    let deps := closure env prefixes r
    out := out ++ (← liftTermElabM (render "R" env r ci (",".intercalate (axs.toList.map toString))
      (" ".intercalate (deps.toList.map toString)) false))
    for d in deps do
      if !table.contains d then
        table := table.insert d
        tableOrder := tableOrder.push d
  for d in tableOrder do
    let some ci := env.find? d | continue
    out := out ++ (← liftTermElabM (render "E" env d ci "" "" true))
  IO.FS.writeFile path out

end StatementLockProbe

open StatementLockProbe in
#lockdump "@@OUT@@" "@@PREFIXES@@" @@DECLS@@
"""


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_text(s: str) -> str:
    return sha256_bytes(s.encode("utf-8"))


def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes())


def canon(text: str) -> str:
    """Whitespace-canonical form: line breaks plus indentation collapse to one space."""
    return re.sub(r"\s*\n\s*", " ", text.strip())


def toolchain_info() -> dict[str, str]:
    env = dict(os.environ, PATH=f"{lean_pinned.TOOLCHAIN_BIN}:{os.environ.get('PATH', '')}")
    ver = subprocess.run([str(lean_pinned.TOOLCHAIN_BIN / "lean"), "--version"], env=env, capture_output=True, text=True,
                         check=True).stdout.strip()
    manifest = json.loads((lean_pinned.PINNED / "lake-manifest.json").read_text())
    rev = next(p["rev"] for p in manifest["packages"] if p["name"] == "mathlib")
    return {"lean_version": ver, "mathlib_rev": rev, "lean_flags": " ".join(LEAN_FLAGS)}


# ----------------------------------------------------------------------------------------------------------------
# Module resolution and compilation
# ----------------------------------------------------------------------------------------------------------------

def module_of(path: Path, root: Path) -> str:
    return ".".join(path.resolve().relative_to(root.resolve()).with_suffix("").parts)


def find_module_file(module: str, roots: list[Path]) -> tuple[Path, Path] | None:
    rel = Path(*module.split(".")).with_suffix(".lean")
    for r in roots:
        if (r / rel).is_file():
            return r / rel, r
    return None


def local_imports(src: Path, prefixes: list[str]) -> list[str]:
    return [m for m in IMPORT_RE.findall(src.read_text(encoding="utf-8")) if any(m.startswith(p) for p in prefixes)]


class Compiler:
    """Compiles programme modules (and their programme imports) into a scratch olean directory, with stamps."""

    def __init__(self, roots: list[Path], scratch: Path, prefixes: list[str], timeout: int, fresh: bool) -> None:
        self.roots, self.scratch, self.prefixes, self.timeout = roots, scratch, prefixes, timeout
        self.done: dict[str, str] = {}
        self.tc = toolchain_info()
        if fresh and scratch.exists():
            shutil.rmtree(scratch)
        scratch.mkdir(parents=True, exist_ok=True)

    def _env(self) -> dict[str, str]:
        lean_pinned.OUT = self.scratch  # lean_path() appends this directory to the pinned LEAN_PATH
        return dict(os.environ, LEAN_PATH=lean_pinned.lean_path(), PATH=f"{lean_pinned.TOOLCHAIN_BIN}:{os.environ.get('PATH', '')}")

    def ensure(self, module: str) -> str:
        """Compile `module` after its programme imports; return its stamp (hash over source + dependency stamps)."""
        if module in self.done:
            return self.done[module]
        found = find_module_file(module, self.roots)
        if found is None:
            raise FileNotFoundError(f"module {module} not found under {[str(r) for r in self.roots]}")
        src, root = found
        dep_stamps = [self.ensure(m) for m in local_imports(src, self.prefixes)]
        stamp = sha256_text(json.dumps([sha256_file(src), dep_stamps, self.tc], sort_keys=True))
        olean = self.scratch / (module.replace(".", "/") + ".olean")
        stamp_file = olean.with_suffix(".lockstamp")
        if olean.is_file() and stamp_file.is_file() and stamp_file.read_text().strip() == stamp:
            self.done[module] = stamp
            return stamp
        olean.parent.mkdir(parents=True, exist_ok=True)
        stamp_file.unlink(missing_ok=True)
        cmd = [str(lean_pinned.TOOLCHAIN_BIN / "lean"), *LEAN_FLAGS, f"--root={root}", "-o", str(olean), "-i",
               str(olean.with_suffix(".ilean")), str(src)]
        t0 = time.time()
        try:
            res = subprocess.run(cmd, env=self._env(), capture_output=True, text=True, timeout=self.timeout)
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(f"compile of {module} exceeded {self.timeout}s") from exc
        if res.returncode != 0:
            raise RuntimeError(f"compile of {module} failed (rc={res.returncode}):\n{(res.stdout + res.stderr)[-3000:]}")
        stamp_file.write_text(stamp + "\n")
        print(f"  compiled {module} in {time.time() - t0:.1f}s", file=sys.stderr)
        self.done[module] = stamp
        return stamp

    def probe(self, module: str, decls: list[str]) -> dict[str, Any]:
        """Run the Lean-side extraction for `decls` of `module`; returns parsed records."""
        self.ensure(module)
        pdir = self.scratch / "_probes"
        pdir.mkdir(parents=True, exist_ok=True)
        key = sha256_text(module + "|" + "|".join(decls))[:16]
        out_path = pdir / f"{key}.out"
        out_path.unlink(missing_ok=True)
        pfile = pdir / f"{key}.lean"
        pfile.write_text(render_probe(module, out_path, self.prefixes, decls), encoding="utf-8")
        cmd = [str(lean_pinned.TOOLCHAIN_BIN / "lean"), *LEAN_FLAGS, str(pfile)]
        try:
            res = subprocess.run(cmd, env=self._env(), capture_output=True, text=True, timeout=self.timeout)
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(f"probe of {module} exceeded {self.timeout}s") from exc
        if res.returncode != 0 or not out_path.is_file():
            raise RuntimeError(f"probe of {module} failed (rc={res.returncode}):\n{(res.stdout + res.stderr)[-3000:]}")
        return parse_probe(out_path.read_text(encoding="utf-8"))


def render_probe(module: str, out_path: Path, prefixes: list[str], decls: list[str]) -> str:
    """Fill the Lean probe template."""
    lits = " ".join(json.dumps(d, ensure_ascii=False) for d in decls)
    return (PROBE_TEMPLATE.replace("@@IMPORTS@@", f"import {module}").replace("@@OUT@@", str(out_path))
            .replace("@@PREFIXES@@", ",".join(prefixes)).replace("@@DECLS@@", lits))


def parse_probe(text: str) -> dict[str, dict[str, dict[str, Any]]]:
    """Parse the sentinel-delimited dump into {"roots": {name: rec}, "defs": {name: rec}}."""
    roots: dict[str, dict[str, Any]] = {}
    defs: dict[str, dict[str, Any]] = {}
    cur: dict[str, Any] = {}
    for chunk in text.split(MARK)[1:]:
        tag = chunk[0]
        if tag in ("R", "E"):
            parts = chunk[1:].split("\n", 1)[0].lstrip("\t").split("\t")
            name, kind, ups, flags, axs, deps = (parts + [""] * 6)[:6]
            cur = {"name": name, "kind": kind, "universe_params": [u for u in ups.split(",") if u], "flags": flags}
            if tag == "R":
                cur["axioms"] = sorted(a for a in axs.split(",") if a)
                cur["deps"] = sorted(d for d in deps.split(" ") if d)
                roots[name] = cur
            else:
                defs[name] = cur
        elif tag in ("T", "V"):
            cur["type" if tag == "T" else "value"] = canon(chunk[1:])
        else:
            raise ValueError(f"unknown probe tag {tag!r}")
    return {"roots": roots, "defs": defs}


# ----------------------------------------------------------------------------------------------------------------
# Lock construction and comparison
# ----------------------------------------------------------------------------------------------------------------

def statement_text(rec: dict[str, Any]) -> str:
    ups = ",".join(rec["universe_params"])
    return f"{rec['kind']} {rec['name']}.{{{ups}}} : {rec['type']}"


def definition_text(rec: dict[str, Any]) -> str:
    ups = ",".join(rec["universe_params"])
    val = f" := {rec['value']}" if "value" in rec else ""
    return f"{rec['kind']} {rec['name']}.{{{ups}}} [{rec['flags']}] : {rec['type']}{val}"


def dependency_digest(dep_names: list[str], def_sha: dict[str, str]) -> str:
    return sha256_text("\n".join(f"{n}\t{def_sha[n]}" for n in sorted(dep_names)))


def entry_from_probe(probe: dict[str, Any], decls: list[str]) -> tuple[list[dict[str, Any]], dict[str, dict[str, str]]]:
    defs: dict[str, dict[str, str]] = {}
    for name, rec in sorted(probe["defs"].items()):
        text = definition_text(rec)
        defs[name] = {"kind": rec["kind"], "sha256": sha256_text(text), "text": text}
    out: list[dict[str, Any]] = []
    for d in decls:
        rec = probe["roots"][d]
        st = statement_text(rec)
        out.append({
            "name": d, "kind": rec["kind"], "statement": st, "statement_sha256": sha256_text(st),
            "dependencies": rec["deps"],
            "dependency_sha256": dependency_digest(rec["deps"], {n: v["sha256"] for n, v in defs.items()}),
            "axioms": rec["axioms"],
        })
    return out, defs


def _word_diff(old: str, new: str) -> str:
    return "\n".join(difflib.unified_diff(old.split(" "), new.split(" "), "locked", "current", lineterm="", n=4))


def compare_entry(lock_entry: dict[str, Any], new_decls: list[dict[str, Any]], new_defs: dict[str, dict[str, str]]) -> list[str]:
    """Return human-readable problems (empty list = the lock holds for this entry)."""
    problems: list[str] = []
    by_name = {d["name"]: d for d in new_decls}
    old_defs: dict[str, dict[str, str]] = lock_entry["definitions"]
    for old in lock_entry["declarations"]:
        name = old["name"]
        new = by_name.get(name)
        if new is None:
            problems.append(f"[{name}] declaration missing")
            continue
        if new["statement_sha256"] != old["statement_sha256"]:
            problems.append(f"[{name}] STATEMENT CHANGED\n{_word_diff(old['statement'], new['statement'])}")
        if new["dependencies"] != old["dependencies"]:
            gone = sorted(set(old["dependencies"]) - set(new["dependencies"]))
            added = sorted(set(new["dependencies"]) - set(old["dependencies"]))
            problems.append(f"[{name}] dependency set changed: removed {gone}, added {added}")
        for dep in sorted(set(old["dependencies"]) & set(new["dependencies"])):
            if old_defs[dep]["sha256"] != new_defs[dep]["sha256"]:
                problems.append(f"[{name}] DEFINITION CHANGED: {dep}\n{_word_diff(old_defs[dep]['text'], new_defs[dep]['text'])}")
        bad = [a for a in new["axioms"] if a not in AXIOM_WHITELIST]
        if bad:
            problems.append(f"[{name}] AXIOM AUDIT: non-whitelisted axioms {bad}")
    return problems


def find_root_for(path: Path, roots: list[Path]) -> Path:
    for r in roots:
        try:
            path.resolve().relative_to(r.resolve())
            return r
        except ValueError:
            continue
    raise ValueError(f"{path} is not under any of the roots {roots}")


def extract_text_lock(file: str, patterns: list[str]) -> dict[str, Any]:
    """Textual lock for non-Lean sources (for example a Lean generator template): the exact source lines matching any regex."""
    lines = [ln.rstrip() for ln in (REPO / file).read_text(encoding="utf-8").splitlines() if any(re.search(p, ln) for p in patterns)]
    if not lines:
        raise ValueError(f"text lock {file}: no line matches {patterns}")
    return {"file": file, "patterns": patterns, "lines": lines, "sha256": sha256_text("\n".join(lines))}


def check_text_lock(tl: dict[str, Any]) -> list[str]:
    now = extract_text_lock(tl["file"], tl["patterns"])
    if now["sha256"] == tl["sha256"]:
        return []
    diff = "\n".join(difflib.unified_diff(tl["lines"], now["lines"], "locked", "current", lineterm="", n=2))
    return [f"TEXT LOCK CHANGED in {tl['file']}\n{diff}"]


def build_lock(spec: dict[str, Any], roots: list[Path], scratch: Path, timeout: int, fresh: bool, date: str,
               allow_partial: bool) -> tuple[dict[str, Any], list[dict[str, str]]]:
    prefixes: list[str] = spec.get("module_prefixes", ["Programmes.", "Autoresearch.", "Triangular.", "BAOCert."])
    comp = Compiler(roots, scratch, prefixes, timeout, fresh)
    entries: list[dict[str, Any]] = []
    todo: list[dict[str, str]] = []
    for e in spec["entries"]:
        src = (REPO / e["file"]).resolve()
        root = find_root_for(src, roots)
        module = module_of(src, root)
        print(f"lock {spec['programme']}: {module} ({len(e['declarations'])} declarations)", file=sys.stderr)
        try:
            probe = comp.probe(module, e["declarations"])
        except (RuntimeError, TimeoutError, FileNotFoundError) as exc:
            todo.append({"file": e["file"], "reason": str(exc)[:600]})
            if not allow_partial:
                raise
            continue
        decls, defs = entry_from_probe(probe, e["declarations"])
        entries.append({"file": e["file"], "module": module, "file_sha256": sha256_file(src),
                        "imports": IMPORT_RE.findall(src.read_text(encoding="utf-8")),
                        "declarations": decls, "definitions": defs})
    lock: dict[str, Any] = {
        "schema": SCHEMA, "programme": spec["programme"], "status": spec.get("status", "post_hoc"), "date": date,
        "root": "formal_cert", "module_prefixes": prefixes, **comp.tc, "entries": entries,
    }
    if spec.get("text_locks"):
        lock["text_locks"] = [extract_text_lock(t["file"], t["patterns"]) for t in spec["text_locks"]]
    if todo:
        lock["todo"] = todo
    return lock, todo


def run_check(lock: dict[str, Any], roots: list[Path], scratch: Path, timeout: int, fresh: bool,
              allow_sorry: bool) -> tuple[int, list[str]]:
    """Recompile and compare.  Returns (exit_code, messages): 0 holds, 1 broken, 2 undecidable."""
    msgs: list[str] = []
    comp = Compiler(roots, scratch, lock["module_prefixes"], timeout, fresh)
    for key in ("lean_version", "mathlib_rev", "lean_flags"):
        if comp.tc[key] != lock[key]:
            return 1, [f"TOOLCHAIN MISMATCH {key}: locked {lock[key]!r}, current {comp.tc[key]!r}"]
    broken, undecided = False, False
    for entry in lock["entries"]:
        names = [d["name"] for d in entry["declarations"]]
        try:
            probe = comp.probe(entry["module"], names)
        except (RuntimeError, TimeoutError, FileNotFoundError) as exc:
            if "declaration not found" in str(exc):
                msgs.append(f"{entry['file']}: FAIL (a locked declaration no longer exists)\n{str(exc)[-400:]}")
                broken = True
            else:
                msgs.append(f"{entry['file']}: UNDECIDABLE ({str(exc)[:500]})")
                undecided = True
            continue
        new_decls, new_defs = entry_from_probe(probe, names)
        problems = compare_entry(entry, new_decls, new_defs)
        if allow_sorry:
            problems = [p for p in problems if "AXIOM AUDIT" not in p]
        found = find_module_file(entry["module"], roots)
        changed = found is not None and sha256_file(found[0]) != entry["file_sha256"]
        if problems:
            broken = True
            msgs.append(f"{entry['file']}: FAIL")
            msgs.extend("  " + p.replace("\n", "\n  ") for p in problems)
        else:
            note = " [source hash differs from lock: proofs/comments/other declarations changed, locked statements did not]" if changed else ""
            msgs.append(f"{entry['file']}: OK, {len(entry['declarations'])} declarations, "
                        f"{len(entry['definitions'])} locked definitions{note}")
    for tl in lock.get("text_locks", []):
        probs = check_text_lock(tl)
        if probs:
            broken = True
            msgs.extend(probs)
        else:
            msgs.append(f"{tl['file']}: TEXT LOCK OK ({len(tl['lines'])} lines)")
    return (1 if broken else 2 if undecided else 0), msgs


def load_lock(path: Path) -> dict[str, Any]:
    lock = json.loads(path.read_text(encoding="utf-8"))
    if lock.get("schema") != SCHEMA:
        raise ValueError(f"{path}: unsupported schema {lock.get('schema')}")
    return lock


# ----------------------------------------------------------------------------------------------------------------
# Negative control and self-test
# ----------------------------------------------------------------------------------------------------------------

def negative_control(lock: dict[str, Any], file: str, old: str, new: str, scratch: Path, timeout: int) -> tuple[int, list[str]]:
    """Mutate `old` -> `new` in a COPY of `file` (the original is never touched) and require check to fail."""
    src = (REPO / file).resolve()
    text = src.read_text(encoding="utf-8")
    if text.count(old) != 1:
        return 2, [f"mutation text must occur exactly once in {file}; found {text.count(old)}"]
    overlay = Path(tempfile.mkdtemp(prefix="stmt_lock_overlay_"))
    try:
        dst = overlay / src.relative_to(DEFAULT_ROOT)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text.replace(old, new), encoding="utf-8")
        sub = {**lock, "entries": [e for e in lock["entries"] if e["file"] == file]}
        code, msgs = run_check(sub, [overlay, DEFAULT_ROOT], scratch, timeout, True, False)
    finally:
        shutil.rmtree(overlay, ignore_errors=True)
    if code == 1:
        return 0, ["NEGATIVE CONTROL OK: the mutated copy was rejected"] + msgs
    if code == 0:
        return 1, ["NEGATIVE CONTROL BROKEN: the mutated copy passed the lock"] + msgs
    return 2, ["NEGATIVE CONTROL INCONCLUSIVE (mutated copy did not compile?)"] + msgs


MINI = """namespace Mini
def bound : Nat := 10
def Good (n : Nat) : Prop := n ≤ bound
/-- headline -/
theorem t (n : Nat) (h : n < 5) : Good n := by
  simp only [Good, bound]
  omega
end Mini
"""


def selftest() -> int:
    """Unit tests of the pure helpers plus end-to-end positive/negative controls on a Mathlib-free mini project."""
    failures: list[str] = []

    def expect(cond: bool, label: str) -> None:
        print(f"  [{'ok' if cond else 'FAIL'}] {label}", file=sys.stderr)
        if not cond:
            failures.append(label)

    expect(canon("a  b\n   c") == "a  b c", "canon collapses line breaks and indentation")
    parsed = parse_probe(f"{MARK}R\tA.t\ttheorem\tu\t-,-\tpropext\tA.d\n{MARK}T\nfoo\n  bar\n"
                         f"{MARK}E\tA.d\tdef\t\treducible,-\t\t\n{MARK}T\nNat\n{MARK}V\n3\n")
    expect(parsed["roots"]["A.t"]["type"] == "foo bar" and parsed["defs"]["A.d"]["value"] == "3", "parse_probe round trip")
    expect(parsed["roots"]["A.t"]["deps"] == ["A.d"] and parsed["roots"]["A.t"]["axioms"] == ["propext"],
           "parse_probe deps and axioms")
    d1 = dependency_digest(["b", "a"], {"a": "1", "b": "2"})
    expect(d1 == dependency_digest(["a", "b"], {"a": "1", "b": "2"}) and d1 != dependency_digest(["a", "b"], {"a": "1", "b": "3"}),
           "dependency digest is order independent and content sensitive")

    work = Path(tempfile.mkdtemp(prefix="stmt_lock_selftest_"))
    scratch = work / "olean"
    try:
        root = work / "proj"
        (root / "Mini").mkdir(parents=True)
        src = root / "Mini" / "A.lean"
        src.write_text(MINI, encoding="utf-8")
        probe = Compiler([root], scratch, ["Mini."], 300, True).probe("Mini.A", ["Mini.t"])
        decls, defs = entry_from_probe(probe, ["Mini.t"])
        again = Compiler([root], scratch, ["Mini."], 300, False).probe("Mini.A", ["Mini.t"])
        expect(entry_from_probe(again, ["Mini.t"]) == (decls, defs), "extraction is deterministic across two probe runs")
        expect(sorted(defs) == ["Mini.Good", "Mini.bound"], f"closure is {{Good, bound}} (got {sorted(defs)})")
        expect(set(decls[0]["axioms"]) <= AXIOM_WHITELIST, f"axioms recorded and whitelisted: {decls[0]['axioms']}")
        entry = {"file": "Mini/A.lean", "module": "Mini.A", "declarations": decls, "definitions": defs}

        def variant(label: str, text: str, must_pass: bool) -> None:
            src.write_text(text, encoding="utf-8")
            pr = Compiler([root], scratch, ["Mini."], 300, False).probe("Mini.A", ["Mini.t"])
            nd, ndefs = entry_from_probe(pr, ["Mini.t"])
            probs = compare_entry(entry, nd, ndefs)
            expect((not probs) == must_pass, f"{label}: {'passes' if must_pass else 'is rejected'}")

        variant("POSITIVE unchanged file", MINI, True)
        variant("POSITIVE proof and docstring edit only",
                MINI.replace("simp only [Good, bound]\n  omega", "unfold Good bound\n  omega").replace("headline", "headline, reworded"), True)
        variant("NEGATIVE weakened hypothesis n<5 -> n<3", MINI.replace("n < 5", "n < 3"), False)
        variant("NEGATIVE definition swap Good n := n <= 100", MINI.replace("n ≤ bound", "n ≤ 100"), False)
        variant("NEGATIVE constant changed bound := 11", MINI.replace("bound : Nat := 10", "bound : Nat := 11"), False)
        variant("NEGATIVE conclusion replaced by True", MINI.replace("Good n := by\n  simp only [Good, bound]\n  omega", "True := trivial"), False)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print("SELFTEST " + ("PASSED" if not failures else f"FAILED: {failures}"))
    return 0 if not failures else 1


# ----------------------------------------------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    up = sub.add_parser("update", help="(re)write a lock from a spec")
    up.add_argument("--spec", type=Path, nargs="+", required=True)
    up.add_argument("--out-dir", type=Path, default=LOCK_DIR)
    up.add_argument("--date", default=dt.date.today().isoformat())
    up.add_argument("--allow-partial", action="store_true", help="skip entries that do not compile in time; list them as todo")
    ck = sub.add_parser("check", help="recompile and verify locks (exit 0 holds, 1 broken, 2 undecidable)")
    ck.add_argument("--lock", type=Path, nargs="*", default=[])
    ck.add_argument("--all", action="store_true", help="every formal_cert/locks/*.lock.json")
    ck.add_argument("--allow-sorry", action="store_true", help="ignore the axiom audit (pre-proof locks only)")
    nc = sub.add_parser("negctl", help="mutate a copy of one locked file and require the check to fail")
    nc.add_argument("--lock", type=Path, required=True)
    nc.add_argument("--file", required=True, help="repo-relative path of a file listed in the lock")
    nc.add_argument("--old", required=True)
    nc.add_argument("--new", required=True)
    sub.add_parser("selftest", help="unit tests plus end-to-end positive/negative controls on a mini project")
    for p in (up, ck, nc):
        p.add_argument("--scratch", type=Path, default=DEFAULT_SCRATCH)
        p.add_argument("--timeout", type=int, default=600, help="seconds per Lean process (default 600)")
        p.add_argument("--fresh", action="store_true", help="wipe the scratch olean directory first (full recompile)")
    args = ap.parse_args(argv)

    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "update":
        rc = 0
        args.out_dir.mkdir(parents=True, exist_ok=True)
        for sp in args.spec:
            spec = json.loads(sp.read_text(encoding="utf-8"))
            try:
                lock, todo = build_lock(spec, [DEFAULT_ROOT], args.scratch, args.timeout, args.fresh, args.date, args.allow_partial)
            except (RuntimeError, TimeoutError, FileNotFoundError, KeyError) as exc:
                print(f"UPDATE FAILED for {spec['programme']}: {exc}", file=sys.stderr)
                rc = 2
                continue
            out = args.out_dir / f"{spec['programme']}.lock.json"
            out.write_text(json.dumps(lock, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
            n = sum(len(e["declarations"]) for e in lock["entries"])
            print(f"wrote {out} ({n} declarations, sha256 {sha256_file(out)}, todo {len(todo)})")
        return rc
    if args.cmd == "check":
        paths = list(args.lock) + (sorted(LOCK_DIR.glob("*.lock.json")) if args.all else [])
        if not paths:
            print("no lock given", file=sys.stderr)
            return 2
        worst = 0
        for lp in paths:
            lock = load_lock(lp)
            code, msgs = run_check(lock, [DEFAULT_ROOT], args.scratch, args.timeout, args.fresh, args.allow_sorry)
            print(f"== {lp.name}: {'LOCK HOLDS' if code == 0 else 'LOCK BROKEN' if code == 1 else 'UNDECIDABLE'} "
                  f"(status {lock['status']}, locked {lock['date']}, lock sha256 {sha256_file(lp)[:16]})")
            print("\n".join(msgs))
            worst = max(worst, code)
        return worst
    if args.cmd == "negctl":
        code, msgs = negative_control(load_lock(args.lock), args.file, args.old, args.new, args.scratch / "negctl", args.timeout)
        print("\n".join(msgs))
        return code
    return 2


if __name__ == "__main__":
    sys.exit(main())
