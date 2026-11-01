# Lean statement-lock procedure (day-1 housekeeping of the 30-day plan)

Drafted by an AI agent (Claude, Sonnet 5.5), 2026-11-02 (session clock 2026-11-01). Not reviewed by a human.
Tool: `scripts/lean_statement_lock.py`. Locks: `formal_cert/locks/*.lock.json`. Specs: `formal_cert/locks/specs/*.spec.json`.
What a lock does and does not guarantee: `formal_cert/locks/README.md`.

## 1. Why, and what the existing tool could not do

Papers say "kernel-checked, independently recompiled, leanchecker-replayed, but Tier A only once a statement-lock entry
exists". None existed. LeanMaster's `tools/statement_lock.py` locks the SOURCE TEXT of a statement (comments removed,
whitespace normalized, up to the top-level `:=`) and the text of `def`s. That is useful but (a) it hashes what was written,
not what Lean elaborated (a changed `open`, notation, `variable`, local instance or an imported definition changes the
meaning without changing the text), and (b) it works on a project tree with its own `docs/statement_lock.json`, not on the
scratch-olean, pinned-toolchain flow used here. The new tool asks Lean itself for the elaborated type, so notation and
implicit-argument tricks are removed, and it follows the programme-own definitions transitively, so a swapped definition
is caught even when the theorem text is unchanged.

## 2. What is locked

For each named declaration: the elaborated type (`pp.all`, explicit universes, full names), and the transitive closure of
programme-own definitions, instances, structures, inductives and axioms mentioned by it (kind, reducibility, instance flag,
type, body); a SHA-256 of each; the `#print axioms` list; the SHA-256 of the source file; Lean 4.34.1; Mathlib commit
d13f23b7; `-DautoImplicit=false`; date; status. `check` recompiles from source in a scratch olean directory (never the main
`formal/` tree), re-extracts, and prints a word-level unified diff of whatever moved. Exit 0 holds, 1 broken, 2 undecidable
(for instance a compile timeout, which is never a pass).

## 3. Procedure

New items (status `pre_proof`):

1. Write the Lean statements with `:= by sorry` (the statement file, no proof). Compile it with the pinned toolchain.
2. Write the plain-language gloss of each statement in the preregistration. The auditor reads gloss against Lean text.
3. `python3 scripts/lean_statement_lock.py update --spec formal_cert/locks/specs/<ID>.spec.json` with `"status": "pre_proof"`.
   Commit the lock together with the preregistration, BEFORE the proof exists. Record the commit hash in the ledger row.
4. Write the proof in the same file or in a file that imports it. Do not edit the locked statement or definitions. If a
   statement must change, that is a new lock with a new date and an explicit "statement revised after proof attempt" note
   in the paper, not a silent update.
5. After the proof: `python3 scripts/lean_statement_lock.py check --lock formal_cert/locks/<ID>.lock.json` must exit 0
   (the axiom audit inside `check` fails on `sorryAx` or any axiom outside propext, Classical.choice, Quot.sound), then
   run lean_runner and the leanchecker replay as before. The auditor reruns `check` independently and compares the lock
   file hash.

Old items (status `post_hoc`): the lock is written after the proof existed, so it proves only that the statement has
not drifted since the lock date. A paper may say "Tier A (statement locked post hoc on 2026-11-02)", never "locked before
the proof". Retrofit one item per reserve day (plan section 4.3).

Updating a lock is an event: it changes `formal_cert/locks/<name>.lock.json`, so it appears in the diff and in the ledger;
`update` is not run to make a failing `check` pass without a documented reason.

## 4. Ledger integration

Tier A rows get a `statement_lock` field:

```json
"statement_lock": {"file": "formal_cert/locks/LowDissE3.lock.json", "sha256": "<sha256 of that file>",
                    "declarations": ["LowDissE3.etaPlus_strictMono", "..."], "status": "post_hoc",
                    "locked_on": "2026-11-02", "checked_on": "<date>", "check_exit": 0}
```

A Tier A row without this field, or whose lock file hash differs from the ledger value, or whose last `check_exit` is
not 0, is rendered "Tier A pending statement lock". The lock file hash is the one printed by `update` and `check`.

## 5. What this lets the published papers claim

Locks written on 2026-11-02 (all `post_hoc`, Lean 4.34.1, Mathlib d13f23b7, `check --all` exit 0 on the same day, scratch
oleans, core 4 only). Lock file hashes (sha256) go into the ledger `statement_lock` field:

| Programme | Locked declarations | Lock file sha256 |
|---|---|---|
| SLR18 | `cover`, `v_injective`, `v_pos` in all 34 files SLRN05..SLRN38 and SLRP1 (105); text lock of the generator template `auditor_tools/gen_lean.py` (7 statement-emitting lines) | `9950d1ebd05b74300b1c385a1ec39efae90181a58c33b9c957b89c3cc01ef2b4` |
| LowDissE3 | `etaPlus_strictMono`, `etaPlus_mono`, `etaPlus_one`, `etaPlus_le_one_value`, `eq1_of_P`, `root_strict_anti`, `root_unique`, `wPlus_root` (Core), `engine_bound` (Engine), `esposito_sandwich` (Instances) | `145e0997c4b2c595bd4766ab27a0489306cf6788aebb10489ec2e00f132d8a33` |
| CarbonK3 | `irf_cm`, `excess_cm_after`, `excess_antitone`, `cm_convexOn`, `excess_convexOn`, `excess_tendsto`; closure includes `ProgCM.IsCompletelyMonotoneOn`, `irf`, `excess` | `99a9eb5085c6a58db057e09657fdedd51fbe7fed976bfc78a2146178e20d332d` |
| CarbonateK2 | all 14 theorems of Core.lean | `831a803d162230c9ecde9fc507cdad5808ed8c978398549409b848832533f619` |
| BornM2 | `foot_witness`, `dia_pd` (Probe); `notpd_0..11`, `pd_0..5`, `pd_0..5_pivots` (Witnesses); the Tamper files are controls, not locked | `a724d17855af3230c627d8c1a9fd2da7149ce37fa4710748149aa7fc486d5d09` |
| PbIgnition | `optimal_mix`, `optimal_mix_eq`, `rpow_25_le_sq`, `ee_term_deriv_pos` | `e08f25bb9571ba3f6431470354e6cb33d3e7f9280ae12b5eb65260c2274ef89d` |
| ZeroPointDipolar | 7 `*_cert` and 7 `*_not_localMin_of_certificate` (riesz3, dipolar 0.1, 0.5, A006, A009, A01, A05); closure includes the 28 numeric certificate constants and `ProgZeroPointCert.t0` | `421b6eeab2b3da2f1323a799c6ea9b83d29a85e655343ed203a3b0bfe98f239b` |
| AmplifierCensus | `R11_amplifier`, `P11_isothermal`, `A1/A2/A3_amplifier`, the `neff_tau*` values, `tau*_eq5`, `GR11_deg`, `GP11_regular`; closure includes `Eq5`, `neff`, `deg`, `remeet`, `p` and the graph/edge/Z data definitions | `b890c2c9a0e35e8f90167922aa03e89cab30a280f451700279d158be6780844a` |
| LonelyRunnerInd | all 9 theorems of ScalarInputs.lean | `95753cd690527d9cadb5ab19e15c6867af6698ec435614f3c17a5cc7e339330a` |

Papers whose Tier A claims rest only on declarations in this table can move from "pending statement lock" to "locked
(post hoc, 2026-11-02)": the SLR-18 shifted lonely runner covering certificates (n=18 and n=38 and the other 33 certificates,
plus the generator template), the E3 low-dissipation engine bounds, the K3 carbon impulse-response / excess results, the K2
carbonate results, the Born M2 witnesses, the PbIgnition lemmas, the dipolar zero-point certificates, the amplifier census
(n=11) and the lonely-runner inductive scalar inputs. Which exact paper sentence maps to which locked declaration still has
to be checked by the auditor of that paper; where a paper's headline uses a declaration not listed above, that claim stays
"pending lock". Not locked (no lock exists, claims stay pending): ZeroPoint / ZeroPointCert / ZeroPointClass / ZeroPointPhys
(only used as dependencies of the dipolar lock), YukawaBccFcc, PopGen, DacExergy, EvoGraph, FeynmanBijl,
CompletelyMonotone (except through the CarbonK3 closure), SandierSerfaty*, Triangular, BAOCert, Autoresearch.

Controls run: self-test (4 unit checks, determinism of two probe runs, 2 positive and 4 negative variants on a Mathlib-free
mini project) PASSED; positive `check` on all 9 locks exit 0; real-file negative controls on copies, original files
untouched: CarbonateK2 `delay_mono_cec` hypothesis `0 ≤ k` replaced by `k = 0` (rejected, statement diff), ZeroPointDipolar
`dip01_M_hi` numerator changed by 1 (rejected, "DEFINITION CHANGED" reported under both theorems that use it), SLR18
SLRP1 conclusion bound `1/6` replaced by `1/5` (rejected, statement diff), and a text-lock negative on the generator template.

## 6. Limits

* A lock fixes the statement as elaborated, not its meaning. The fidelity reading (gloss against Lean text) is still a
  separate, human or independent-auditor step and is not replaced.
* A post-hoc lock says nothing about statement-swap before 2026-11-02. For published items only the (already done) audits
  of the statements speak to that.
* Mathlib definitions are not locked; the Mathlib commit is pinned instead. A Mathlib bump needs a re-lock with review.
* Proof soundness is orthogonal: compile, axiom audit, leanchecker replay.
* Compile time: the check recompiles the file. `LowDissE3/Engine.lean` took 855 s and `Triangular/Riesz.lean` (a dependency of CarbonK3) 678 s on a loaded core; the default per-process timeout is 600 s, so use `--timeout 1500` for those. A full `check --all` from a cold scratch directory takes roughly 2.5 hours on one core (SLR18 alone about 75 minutes); with warm stamps it takes about 15 minutes.
