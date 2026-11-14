# D1 deviations (written before the affected step)

## 1. Advisory eye aid for the by-eye review (2026-10-08, written after the mechanical run, before the eye review)

The mechanical run (`d1_hole_bodies.py run`, sha256 82b51473..., unchanged) has finished. While reading its output I found
three instrument defects. None of them can turn a DIFFERS into a false MATCHES:

- `run_cmd` is missing from `COMMAND_STARTS`, so in DefocusingNLS.lean the column-0 line
  `run_cmd Lean.modifyEnv ...` that follows a definition is absorbed into the challenge declaration
  (sobolevOddPower: mechanical DIFFERS; sobolevProduct: its challenge_text has the same tail).
- `ᶜ` (U+1D9C, a Unicode letter matched by `\w`) is lexed into the preceding identifier, so `containerᶜ`/`Yᶜ` are
  each a single free token and the bijection cannot apply (Brenier IsSupported: mechanical DIFFERS). Lean lexes `Yᶜ` as `Y` followed by the postfix `ᶜ` notation.
- `shadow_candidates` builds `<opened namespace>.<ident>` from the literal text of an `open` line. It does not resolve
  the opened namespace against the enclosing namespace stack (`open GlobalEndpoint` inside `namespace OAI.KServer`
  can mean `OAI.KServer.GlobalEndpoint`). An empty `shadow_candidates` list is therefore not proof that nothing shadows.

Deviation: I do not edit the frozen script, and the mechanical verdicts stay as they are. For the eye review I add
`results/openai_math/hypotheses/night_2026-10-07/D1/eye_aid.py`, which is advisory only. It does three things:
(a) applies the recorded renaming and runs difflib over the full token streams, so every differing span of each
DIFFERS is listed, not only the first one;
(b) for every hole found in the solution closure, lists each solution-closure declaration whose full name ends in
`.<free identifier>`, is absent from the challenge file and sits in a namespace reachable from the declaration's
scope (each enclosing namespace prefix, plus each `open` resolved against every enclosing prefix);
(c) for opened Mathlib namespaces, greps a local Mathlib source tree for `<NS>.<ident>`, if one is found.
Its output goes to `D1/eye_aid.json` and only informs `eye_review.json` (eye_verdict, note, meaning_pinned).
For a mechanical DIFFERS that reading shows to be equivalent, the eye verdict label is `EQUIVALENT_BY_READING`,
never `MATCHES`, so the table does not show the upgrade that the preregistration forbids.

## 2. Further advisory aids, added after item 1 during the eye review (2026-10-08)

These were added after item 1 and are advisory only. None of them changed a mechanical verdict, and the frozen
script and tests still have their preregistered sha256 (checked in result.json).
- `mathlib_scan.py` → `mathlib_scan.json` replaces item 1(c)'s file-level grep in eye_aid.py. That grep gave false
  positives (for example `structure Finset` at the root of a file that also opens `namespace Finset`). The scan parses
  the files with `d1_hole_bodies.extract_decls` and keeps the namespace stack, and reports per namespace how many
  `<NS>.*` declarations it extracted, as a sensitivity check. A raw-text grep of declaration lines inside
  `namespace ContinuousLinearMap` files supplements it.
- `visible_instances.json` lists, for each solution hole declaration, the instance/notation/attribute lines in the
  OAI import closure of its own file, up to the declaration line. `closure_instances.json` lists the same for the
  whole solution closure. I read them by eye; neither is used mechanically.
- I ran a one-off comparison of modifiers and attributes (challenge vs solution declaration) and of `attribute`
  commands that name a hole. It found no differences and no such commands. Its output was empty and was not kept as
  a file.
- `make_eye_review.py` (writes `eye_review.json`) and `finalize.py` (writes `result.json`, `lane_results.tsv` and
  the summary on top of `definition_holes.md`) only record the review and assemble the outputs.
