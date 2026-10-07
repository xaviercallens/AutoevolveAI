# openai/math — study and the `openai_math` discovery sub-project

Status 2026-10-07: **D0 done.** The study was first written from GitHub's web pages (the
session's `git clone` was refused by the permission mode); the user then cloned the repo to
`/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/SocrateAI-Scientific-Agora-LeanMaster/lean4basesource/openai-math`
(HEAD `adc7f1241b42e322a6451854ab7e4b4c146bf78a`, 132,851 files checked out) and
`scripts/openai_math/index_corpus.py` recounted everything from disk into
`results/openai_math/corpus_index.json`. Numbers marked **[measured]** come from that index;
**[README]** are quoted from upstream; **[web]** came only from a summarised web read and
were not recounted. Section 2b has the D0 results and triage.

## 1. What the repository is

- `github.com/openai/math`, Apache-2.0, a single commit `adc7f124` ("Initial commit",
  2026-10-06) [measured HEAD; date from the GitHub API].
- "722 manuscripts organized into 372 families" produced by "an internal OpenAI model";
  "the model was posed approximately 4,000 problems"; "on average, each result used three
  hours of ChatGPT Pro thinking compute" [README].
- Upstream's own caveats, verbatim [README]: "This collection includes results at different
  stages of verification." "Not all have accompanying Lean formalizations." "Some of the
  unformalized results could have issues." One result (the Re(s) > 11/12 zero-free region)
  "was human edited for readability."
- Layout: `preprints/<Title-Date>/` (722 folders [measured], each with a PDF; 424 name it
  `paper.pdf`, the rest `main.pdf`, `manuscript.pdf`, `article.pdf`, ... plus `README.md`
  and `build/`), `CONTENTS.md` (family index with abstracts), `overview.{tex,pdf}`,
  `reasoning_traces/` (10 PDFs [measured] + 1 `.tex`, for families 007, 017, 087, 102, 159,
  197, 221, 271, 287, 362), and `lean/`.
- Preprint folder names carry dates from September 2026 (23rd–25th seen).

**Reading rule for this project:** an upstream manuscript is a *claim by another model*, not
a result. Only a Comparator-checked Lean theorem (section 2) is upstream's verified tier, and
even that certifies the Lean statement, not that the statement says what the paper says.
Headline unformalized claims (e.g. family 002 "the full BSD formula from low Selmer corank",
032 Hodge/Kuga–Satake, 014 restricted geometric Langlands) are unverified here and must
never be cited as results.

## 2. The Lean side

- `lean/lean-toolchain`: `leanprover/lean4:v4.34.1`. Local `formal/` is
  `v4.34.0-rc2` with a **partial** Mathlib (LL.md §3). **Not compatible.**
- `lean/lakefile.lean`: package `OAI`, `autoImplicit false`, Mathlib pinned at
  `d13f23b723b8a846827a245b89c10fc7d3f11612`, plus ~30 pinned git dependencies
  (PrimeNumberTheoremAnd, StrongPNT, carleson, sphere-eversion, ClassFieldTheory,
  PrimeCert, leancert, a family of `lana-agents/*` libraries such as `iut`,
  `elliptic-curves`, `heights`, `belyi`, ...; 30 `require` lines counted in the verbatim
  lakefile). 23 of them get compatibility patches from `lean/patches/<dep>-lean4341.patch`:
  the 11 `lana-agents/*` packages via a `run_cmd` hook *before* Lake resolves dependencies,
  and 12 more (PrimeNumberTheoremAnd, carleson, SphereEversion, ...) in `post_update`. One
  `lean_lib` per area: `OAI.NumberTheory`, `OAI.Combinatorics`, `OAI.Analysis`, ... 23 in all.
- Upstream warns the full library may hit Linux `vm.max_map_count`; workaround is a Lean
  built with `-DMMAP=OFF` or `GLIBC_TUNABLES=glibc.malloc.mmap_max=0:glibc.malloc.arena_max=1`.
- `lean/docs/NNN.md`: one scope note per formalized family, **235** [measured], every one
  linking at least one Comparator challenge, stating what exactly the Lean proves.
- `lean/ComparatorChallenges/`: **405** challenge/config pairs [measured], every one linked
  from some scope note. `lean/OAI/`: 121,734 `.lean` files [measured].
- `lean/formalization.yaml`: a catalogue whose `sources` list has ~256 article entries [web].
- `lean/OAI/NumberTheory/` has these family folders: Catalan, Chromatic, CubicGauss,
  CubicGram, CubicMoment, DirichletL, DuffinSchaeffer, DukePrimeDegree, EgyptianFractions,
  GaussianMoat, Jacobsthal, JointDickman, NumberField, OrdinaryCorrelations, Ostmann,
  PiExponent, PowerFree, PrimeGaps, PrimePackets, QuadraticForms, ShortEgyptian,
  SiegelZeros, SingleFold, TotientAsymptotic, TotientFibers, TwoPoint,
  TwoPointCorrelations, ZetaFive [web].

### Comparator: the idea worth adopting

Each verified result is a pair in `lean/ComparatorChallenges/`:

```lean
-- Catalan.lean (challenge: the statement only, proof is `sorry`)
import Mathlib
namespace OAI
namespace InternalCatalan
theorem catalan_irrational :
    Irrational (∑' j : ℕ, (-1 : ℝ) ^ j / ((2 * j + 1 : ℕ) : ℝ) ^ 2) := by
  sorry
end InternalCatalan
end OAI
```

```json
{"challenge_module": "ComparatorChallenges.Catalan",
 "solution_module": "OAI.NumberTheory.Catalan.Main",
 "theorem_names": ["OAI.InternalCatalan.catalan_irrational"],
 "definition_names": [], "enable_nanoda": false,
 "permitted_axioms": ["propext", "Quot.sound", "Classical.choice"]}
```

Run with `comparator`, `landrun` (sandbox) and `lean4export` on PATH:
`lake update && lake exe cache get && lake env comparator ComparatorChallenges/<X>.json`.
What Comparator checks, from the `leanprover/comparator` README (read 2026-10-07): every
theorem in `theorem_names` "prove[s] the same statement as provided in `Challenge`" and uses
"no more axioms than listed in `permitted_axioms`". It builds the challenge and the solution
with `lake` inside a `landrun` sandbox, exports each `.olean` with `lean4export` in another
sandbox, checks the declarations agree, and replays the solution into the Lean kernel.
`enable_nanoda: true` adds a second, independent kernel (nanoda). Its stated trust base and
limits: the challenge's transitive imports, the lakefile, landrun, the kernel and the OS are
trusted; you must not have compiled the solution (or any adversarial file) beforehand
outside the sandbox; and definition holes "must always be checked with an additional
(potentially human) verifier". For this project that means: run it on a fresh checkout, and
review the lakefile too, since upstream's lakefile runs `git` and applies patches at
configuration time.

Why this matters for AutoevolveAI: our gate (`anse/formal/lean_runner.py`, file mode)
parses `#print axioms` text from the output of a file that also contains model-written
proof text. Master-math run two found that a proof body can print a forged axiom report and
then `#exit`, and patched `build_ladder.verdict` on branch `worktree-master-math-regen2`,
**which is not merged into main** (checked 2026-10-07: main has no `#exit` guard anywhere in
`scripts/` or `anse/`). `lean_runner.py` on main has no such guard either, so its file mode
is *likely* forgeable; this was not tested in this session. Comparator's split — reviewed
statement module, untrusted solution module, environment-level comparison, sandbox —
removes that whole class.
The permitted-axiom whitelist is the same as ours. What Comparator does **not** check:
whether the challenge statement is faithful to the paper (LL.md §7). That review stays ours.

## 2b. D0 results: index and audit of the clone (2026-10-07)

`results/openai_math/corpus_index.json`, from `python3 scripts/openai_math/index_corpus.py`:

| Measure | Value |
|---|---|
| Preprint folders / with a PDF | 722 / 722 |
| Formalization scope notes | 235 (all link a challenge) |
| Comparator challenges | 405 (all linked from a note) |
| Challenges with a defect | 0 |
| Challenges with a review note | 10 (9 definition holes, 1 axiom-posed) |
| Toolchain match with `formal/` | no (v4.34.1 vs v4.34.0-rc2) |

**Instrument check.** The first run flagged 4 challenges; triage found 3 were indexer
limitations, fixed with a test each: universe-polymorphic names (`theorem one_sample.{u}`
in MatroidProphet / MatroidSecretary), and definition-hole configs with no `theorem_names`
(ElementaryPositivity). Negative controls on the real `Catalan` files: the clean pair audits
clean, and a planted untrusted axiom, a renamed theorem and a proof replacing `sorry` are
each caught.

**HarmonicGrowth** poses its statement as `axiom mainStatement : MainClaim` +
`theorem main : MainClaim := mainStatement` instead of `sorry`. Sound under Comparator
because `mainStatement` is not in `permitted_axioms`, so a solution cannot use it.

**Definition holes are the real finding.** Comparator's source
(`Comparator/Compare.lean`, `definitionHoleMatches`, read 2026-10-07) compares a
definition hole's name, universe levels, type and safety, **not its body**, and does not
check that the challenge's version is `sorry`. Its README says holes must be `sorry`'d in
the challenge and "must always be checked with an additional (potentially human) verifier".
Upstream lists fully defined statement-carrying definitions as holes, e.g. in `KServer` the
theorem is `main_theorem : MainStatement.{u}` and `MainStatement` itself is in
`definition_names`. So Comparator alone would accept a solution with
`def MainStatement : Prop := True`. That was read from source, not executed; it is the D2
negative control. Upstream's actual solution (`OAI/Combinatorics/KServer/Main.lean:123`)
defines `MainStatement` the same as the challenge up to renamed bound variables (read by
eye). The nine hole challenges are Brenier, DefocusingNLS, ElementaryPositivity,
EuclideanFiveColor, KServer, Naimark, OccupiedOverlap, Rokhlin and SpinAngle. For them a
Comparator pass certifies nothing about the hole definitions; each needs a body comparison,
best done on elaborated `Expr`s once the project builds (D2).

## 3. What AutoevolveAI can and cannot do with it today

| Can do now (T4 box, no new downloads) | Needs a user decision first |
|---|---|
| Index + audit the clone (`index_corpus.py`, done) | — (clone made by the user) |
| Statement-faithfulness review of challenges vs abstracts | A separate Lake project for OAI: v4.34.1 toolchain, `lake exe cache get` (many GB), ~30 deps, mmap workaround |
| PARI/GP + Sage numerical checks of quantitative number-theory claims | Installing `comparator`, `landrun`, `lean4export` |
| Use scope notes as a source of well-posed target statements | Building any `OAI.*` module locally |

Hard rules carried in: never copy an `import Mathlib` challenge into `formal/` (it will not
build, LL.md §3); never compile in a worktree (no `formal/.lake`); every experiment gets a
positive and a negative control; PARI/Sage, not hand arithmetic, is ground truth.

### Overlap with LeanMaster

The LeanMaster MCP tools (`search_theorems`, `usage_guide`) were refused in this session, so
this is read from LeanMaster's README, not from a theorem search. Re-run
`search_theorems` before relying on any of it.

- **Same toolchain gap.** LeanMaster is also on Lean v4.34.0-rc2, so no LeanMaster module
  can be imported into the v4.34.1 `OAI` project as is, nor the reverse.
- **Quadratic forms and class numbers.** LeanMaster Stream 5 (`DualScaleDyons`) counts
  Hurwitz class numbers `H` independently and checks DMZ identities against them. Upstream
  has `OAI/NumberTheory/QuadraticForms` (contents not yet read). This is the most concrete
  shared object: a candidate for cross-checking numeric tables, not for sharing proofs.
- **Finite-order integer matrices.** LeanMaster Stream 9 proves `crystallographic_restriction`
  (ψ(n) ≤ d) and `no_order_fifteen_in_rank_five`. Check upstream's `GroupTheory` and
  `LinearAlgebra` libraries for overlapping statements after the clone.
- **K3.** Upstream family 032 (Hodge, Kuga–Satake for K3) is algebraic geometry far above
  LeanMaster's K3/Mukai lattice arithmetic: shared objects, not shared theorems.

**LeanMaster's gate tools are part of the pipeline.** `tools/statement_lock.py` and
`tools/axiom_audit.py` honour `LEAN_PROJECT_ROOT`, so they can point at upstream's `lean/`:
statement locks in D1, axiom audit as a second checker beside Comparator in D2. This is
untested against a v4.34.1 project.

## 4. The sub-project: stages

"Discovery" here is staged honestly. Re-verifying another model's claims is **not**
discovery; it is the instrument check that has to come first (LL.md §1).

- **D0 — index and audit** (done 2026-10-07, section 2b).
  `scripts/openai_math/index_corpus.py` → `results/openai_math/corpus_index.json`: recounts
  every number above, records clone HEAD and README sha256, and audits each challenge
  (permitted axioms ⊆ whitelist, `theorem_names` declared, statement-only file with `sorry`,
  no `axiom`, imports). Tests: `tests/openai_math/` (positive + negative controls).
- **D1 — statement faithfulness.** For the number-theory challenges first: compare each
  Lean statement with its scope note and paper abstract; flag vacuous or weakened
  statements. A model reviewer is recorded as a model, not a human audit (LL.md §12).
  Every reviewed statement is frozen with LeanMaster's
  `LEAN_PROJECT_ROOT=<clone>/lean python tools/statement_lock.py --update <files>`, so a later
  upstream edit to a challenge shows up as a lock failure (`--check`).
- **D2 — independent Comparator re-run** (producer ≠ verifier). After approval: separate
  Lake project on disk 2, start with one small challenge (Catalan), preregister the expected
  outcome, and include a negative control (a challenge with a perturbed statement must fail).
  For a definition-hole challenge (KServer), the decisive control is a solution with
  `MainStatement := True`: if Comparator accepts it, hole bodies need our own `Expr`
  comparison against the challenge before any such result is trusted.
  Run LeanMaster's `tools/axiom_audit.py` on the built solution as a second, independent
  checker (it also rejects `Lean.ofReduceBool`), and `enable_nanoda` if nanoda installs.
- **D3 — numerical cross-checks.** Preregistered PARI/Sage experiments on quantitative
  claims, e.g. family 012: the density of n with P⁺(n) < P⁺(n+1) is 1/2 (upstream scope note).
  Finite-N numerics can only be *consistent* with a limit, never confirm it; the
  preregistration fixes N, the statistic and the tolerance beforehand. Negative control: a
  deliberately wrong prediction must be rejected at the same N.
- **D4 — discovery proper.** From D1–D3-checked families, generate *new* candidate
  statements (parameter extensions, finite instances, sharper constants suggested by D3 data),
  check them numerically, state them in Lean against the locally built Mathlib subset, and
  run the local provers (DeepSeek-Prover-V2-7B; Goedel needs its chat template) behind the
  sound gate. Anything that survives is a candidate, reported with its controls.
- **D5 — learning.** Only gate-verified episodes go to the datalake with real verdicts
  (`verdict: "PASSED"`), under the ≤30% unverified-signal cap.

## 5. Next steps

Re-index after any upstream update (the clone is `--depth 1`; `git pull` then):

```bash
python3 scripts/openai_math/index_corpus.py
```

D1 (statement review, number theory first, plus a by-eye body check of the nine
definition-hole challenges) needs no new downloads. D2 needs a user decision on building
the `OAI` project (toolchain v4.34.1, `lake exe cache get`, ~30 dependencies).
