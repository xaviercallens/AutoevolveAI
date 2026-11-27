# Statement locks for the Lean programmes

Tool: `scripts/lean_statement_lock.py` (pinned toolchain via `scripts/certified_numerics/lean_pinned.py`: Lean 4.34.1,
Mathlib d13f23b7, flag `-DautoImplicit=false`). Procedure: `docs/studies/STATEMENT_LOCK_PROCEDURE_2026-11-02.md`.

## What a lock records

For every locked declaration (usually a headline theorem), asked from Lean itself after elaboration:

* `statement`: the elaborated type, printed with `pp.all`, explicit universes and full names, no notation, line breaks
  collapsed; `statement_sha256` is the SHA-256 of that text (preceded by the kind, name and universe parameters).
* `dependencies`: the transitive closure of the definitions, instances, structures, inductives and axioms that the
  statement (and, for definitions, their bodies) mention and that live in the programme's own modules (`Programmes.*`,
  `Autoresearch.*`, `Triangular.*`, `BAOCert.*`). Mathlib and core are NOT expanded. Theorems are never part of the closure
  (proof terms, in definition bodies and in statements, print as `⋯`: they are proof-irrelevant, for example the `Nat.AtLeastTwo` argument of a numeral). Each dependency is stored in `definitions` with kind, reducibility
  and instance flags, type, body, and its own SHA-256. `dependency_sha256` hashes the sorted (name, hash) list.
* `axioms`: `#print axioms` of the declaration at lock time (informational at lock time; `check` fails on anything outside
  `propext`, `Classical.choice`, `Quot.sound`, including `sorryAx`, unless `--allow-sorry` is given for a pre-proof lock).
* `file_sha256` of the source file, the import list, `lean_version`, `mathlib_rev`, `lean_flags`, `date`, `status`
  (`post_hoc`: written after the proof existed; `pre_proof`: written before it).

## Commands

```
python3 scripts/lean_statement_lock.py update --spec formal_cert/locks/specs/<Programme>.spec.json   # write/refresh a lock
python3 scripts/lean_statement_lock.py check  --lock formal_cert/locks/<Programme>.lock.json         # exit 0 holds, 1 broken, 2 undecidable
python3 scripts/lean_statement_lock.py check  --all
python3 scripts/lean_statement_lock.py negctl --lock L --file formal_cert/Programmes/X/Core.lean --old '...' --new '...'
python3 scripts/lean_statement_lock.py selftest
```

Everything compiles into the scratch directory `formal_cert/.olean_out/statement_lock` (git-ignored). Nothing is built in
`formal/`. A scratch olean is reused only when its stamp (hash of the source, of its programme imports and of the toolchain)
matches; `--fresh` wipes the scratch directory.

## What a lock guarantees

If `check` exits 0, then with the recorded toolchain the file still elaborates the named declarations to exactly the same
kernel types, and every programme-own definition they depend on elaborates to exactly the same type and body. So nobody has
weakened a hypothesis, changed a constant, swapped a definition (including the "definition hole": a def whose body was
changed so that the unchanged-looking statement became easy), or replaced the conclusion, while the proof still compiles.
Edits to proofs, comments and docstrings, and to unrelated declarations, do not break the lock (by design).

## What a lock does NOT guarantee

* It does not prove that the statement means what a paper, a preregistration or a ledger row says. A human or independent
  auditor must still read the Lean text (or the locked `statement`) against the plain-language claim. The hash fixes the
  statement as elaborated, not its meaning.
* A `post_hoc` lock proves nothing about whether the statement was chosen after seeing what was provable. Only a lock
  committed with the preregistration, before the proof file exists (`status: pre_proof`), speaks to that.
* It does not look at proofs. Correctness of the proof is the job of the compile, `#print axioms` (whitelisted axioms only,
  `sorryAx` rejected) and an independent `leanchecker` replay, none of which the lock replaces.
* Mathlib and core definitions are not locked, only the Mathlib commit is pinned. A different Mathlib commit makes `check`
  refuse (toolchain mismatch).
* The closure follows constants mentioned in definition bodies, including inside proof terms of definitions, which can only
  make the lock stricter, never weaker. Declarations reached only through a theorem's proof are not locked.
* Locked files and their programme imports are recompiled; a file that no longer compiles gives exit 2 (undecidable), never
  a pass.
* Locks cover only the declarations listed in the spec; other declarations of the same file are unlocked.
