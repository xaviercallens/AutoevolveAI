# Contributing to ANSE / AutoevolveAI

Contributions are welcome. This document is short on ceremony and specific about the
one thing that is unusual here: **how claims are handled.**

## The one rule that matters

> Report only what you observed. If you did not measure it, do not write it. If it
> cannot be measured, say so.

This is not a style preference. An audit of this repository found 14 components that
reported success without doing the work — a GPU telemetry module returning
`random.uniform()` behind a docstring promising "physical truth", a trainer recording
config-only dry runs as deployed checkpoints, a review script hardcoding
`ACCEPT WITHOUT RESERVATION` while never calling a model. Every one of them looked
fine, because a plausible number is indistinguishable from a real one until you check.

So: **a gap is a publishable result.** "This could not be verified on my machine" is a
sentence we want in a PR description. An invented number is the one thing that will get
a change rejected outright.

## Before you open a PR

```bash
uv sync --all-extras

.venv/bin/python -m pytest tests/ -q          # expect 1080 passed / 14 failed today
.venv/bin/python test_rigor_guard.py          # must exit 0
.venv/bin/python scripts/validate_environment.py
```

Two notes on the current state, so you can tell your failures from ours:

- **14 tests fail on a clean checkout** and 8 error on a missing Playwright browser
  binary. Six of the failures are an earlier fix *working* (`latent_dreamer` now refuses
  to score random vectors through untrained weights, while the old tests assert
  `status == "success"`). If your number differs from 14, that difference is yours.
- **`antigravity_guard.py` exits 1** on 2,306 pre-existing Ruff findings. Its import and
  syntax stages pass. Don't be alarmed; do check you didn't add to the count.

## Mechanically enforced rules

`test_rigor_guard.py` walks the AST and will fail your build for:

1. **Stubs or fake data outside `tests/`** — `pass`, `...`, `NotImplementedError`,
   `mock_`, `dummy_`.
2. **Tests with fewer than 2 real assertions**, or tautological ones (`assert True`,
   `assert x == x`).
3. Mocking anything other than external I/O.

`antigravity_guard.py` additionally checks for unresolvable imports and syntax errors.

Also expected, and reviewed by humans:

- **Type-annotate every function signature.** No exceptions.
- **Comment the *why*, not the *what*.** If removing a comment wouldn't confuse anyone,
  delete it.
- **Fail closed.** If a backend is unreachable, raise. Do not substitute a placeholder
  and report success — that is the exact defect class above. `anse/memory/redis_memory.py`
  and `antigravity-harness/storage/redis_bus.py` are the counterexamples to avoid.

## Where the work is

[`README.md#known-gaps--where-to-help`](README.md#known-gaps--where-to-help) is the real
backlog, ordered by impact. The highest-value items right now:

| | Task | Why it matters |
|---|---|---|
| 🔴 | Restructure the 200-case bank into `(statement, hidden reference, tolerance)` | Every case currently embeds its own solution, so the benchmark measures whether the machine can run the reference implementation. Nothing downstream can be trusted until this is fixed. |
| 🔴 | An independent verifier for math and physics | Cases self-assert via SymPy against their own constants. `anse/benchmark/invariant_registry.yaml` has 993 lines of per-case invariants and tolerances to build from. |
| 🔴 | A reviewer that can reject | Three `scripts/review_*.py` make zero model calls. `scripts/phd_demo/peer_review.py` shows the shape, including both controls. |
| 🟡 | Ruff cleanup (2,306 findings, 868 auto-fixable) | Mechanical, reviewable, unblocks CI. |
| 🟢 | Update the 6 tests that assert fabricating behaviour | Self-contained, and a good first issue. |

## If you are reviewing a claim rather than writing code

**An issue that says "this number looks unsupported" is as valuable as a patch.** That
is literally how the current audit started. If you check a badge against its cited
artifact and they disagree, open an issue — you have found a real bug.

The template for this is `scripts/verify_release.py`, which checks a release's claims
against its own diff. It has blocked two of this project's own releases.

## The pattern worth copying

`scripts/phd_demo/` is the reference for what "verified" means here. One claim
established three independent ways:

- **SymPy derives** the algebra on every run; nothing is recalled from memory.
- **Lean 4 proves** it, accepted only on `#print axioms` showing no `sorryAx` — because
  `sorry` compiles and exits 0, so a return code proves nothing.
- **Python and Rust** implement it separately and must agree within a declared
  tolerance, or the build fails.

And both gates have rejected real work: the axiom audit caught four theorems that were
unprovable as stated, and the peer reviewer produced a false-positive rejection that
exposed a missing control in the harness. **A gate that has never rejected anything is
not a gate** — if you add one, add its negative control in the same PR.

## Commits and PRs

- Explain **why**, not what — the diff shows what.
- Quote real command output for any claim you make.
- If you fixed something the README lists as a known gap, update that list.

## Licence

MIT (see [`LICENSE`](LICENSE)). By contributing you agree your work ships under it.
