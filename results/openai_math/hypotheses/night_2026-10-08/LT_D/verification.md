# LT_D adversarial verification

Verdict: CORRECTIONS_NEEDED. The numbers hold up and the headline (PARTIAL, no Tier A) is not overstated. The process claims about controls and deviations are not fully supported.

## 1. Preregistration before results: PASS, with a labeling defect
- preregistration.json is tracked. `git log` shows only commit bdd0dcb (2026-10-08 11:06:46 +0000). Its message is "prereg(openai_math): night 2026-10-08 lane LT_A", so LT_D's prereg was bundled into the LT_A commit along with scripts/openai_math/lt_d_lean.py.
- Result mtimes: closure.json 11:13:27, part1a 11:25:56, part1b 11:35:20, lock 11:43:02, elenchus 11:43:56, controls.json 11:52:15, result.json 11:52:42. All are later than the commit. The file mtime of the prereg itself is 11:06:31.
- No diff against HEAD for the prereg or for lt_d_lean.py. The sha256 of lt_d_lean.py recomputed to 471b286d..., matching the prereg's code hash.
- All LT_D result files are untracked. Nothing was committed after the results, as the report says.

## 2. Numbers vs files: PASS (recomputed)
- 38 files and 13717 lines: recomputed from the upstream sources, 13717 lines in total.
- 14 compiled, 1 failed, 23 blocked: the counts in part1b_closure.json match. The 14 compile times run 18.3 to 68.5 s, matching "18-69 s".
- Blocking error: FiniteParity.lean:505:21 `Set.equivOfEq` is in the file as reported.
- I parsed the imports of all 38 files. A file is "blocked" exactly when it transitively imports FiniteParity. There were zero mismatches, so the blocked count is correct.
- Statement lock: 67 + 16 + 5 + 13 = 101 declarations. The LiebThirring sha256 recomputed to 008bcfc1...ab8ade, matching the lock file and the doc.
- Part 1a: rc 0, 732.0 s, one "declaration uses sorry" warning. This matches the claim that the statement parses.
- Elenchus: all four files exit 1 with NO_FOOTPRINT, as reported.

## 3. Controls: PARTIALLY SUPPORTED
- controls.json has `_all_pass` true (2 positive, 3 negative). The mtime of every control file is 11:52, which is after the closure finished (11:35).
- Only one controls run is on disk. The prereg requires controls to run before and after the closure, and the report says "run before and after". No file shows a before-run, because it was overwritten or never kept. This claim cannot be verified from the files.
- The controls test only the axiom classifier. No control exercises the compile-failure path on a real file. The 14 compiled files give some positive evidence for the runner, but this is not a preregistered control.
- Elenchus was not run on a control pair. The prereg allowed this if disclosed, and the report does not disclose it.

## 4. Overstatement checks
- "The failure is version drift": this is an inference. The files show `Set.equivOfEq` unknown locally. They do not show it exists in upstream's Mathlib pin, or that it was removed or renamed between versions. The wording should be "consistent with version drift". The report's own "neither confirms nor refutes the upstream proof" is correct.
- "No vacuity or smuggling finding was printed": the output of NO_FOOTPRINT means the gate checked nothing. Absence of a finding is not evidence that the statements are non-vacuous. The report's wording says this is expected by design, which is fair.
- Nothing claims an upper bound or a discovery, and no claim is Tier A. This is consistent with the preregistered tiering.
- Challenge elaboration took 732 s against 11-14 s for Elenchus on the same files. This is plausibly a cold cache, and the files do not explain it.
- The D2 doc cost figures are labelled as estimates. Nothing was downloaded or installed.

## 5. Process deviations
- deviations.md does not exist in the LT_D directory. The report's notes admit deviations: a single background process instead of resumable slices, and a shell variable used in the controls call. Elenchus ran in-process with REPO_ROOT patched, which the prereg disclosed. The preregistered deviations record is missing.
- The prereg's `Part 1c` (axiom check) was never run, as the report says. The resulting verdict PARTIAL is the correct category.

## Corrections required
1. Say "consistent with version drift", not "is version drift".
2. Drop or qualify "controls run before and after the closure". Only the after-run is evidenced.
3. Disclose that no Elenchus control pair was run.
4. Write deviations.md.
5. Record that the prereg was committed under the LT_A commit message.
