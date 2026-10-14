# program.md — openai_math hypothesis lab (autoresearch-style)

Adapted from Karpathy's `autoresearch` (copy at
`/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/SocrateAI-Scientific-Agora-LeanMaster/autoresearch/`).
Same shape, different object:

| autoresearch | this lab |
|---|---|
| `prepare.py` fixed (data, eval) | `preregister.py` fixed: statistic, thresholds, controls, sha256 of each runner, written and committed **before** any run |
| agent edits `train.py` | the agent (Claude, in-session; no local LLM generated candidates in run one) edits the search strategy inside one runner (`h4_lienard.py`, `h5_dyadic.py`) |
| 5-minute wall-clock budget | each runner takes `--budget-s`; the budget is recorded in the result |
| metric `val_bpb`, keep if lower | per-hypothesis preregistered metric (below); keep if it improves AND both controls pass |
| `results.tsv` | `results/openai_math/hypotheses/results.tsv` (one row per run, never edited by hand) |

## Rules (binding; they come from LL.md)

1. A run whose positive or negative control fails is `crash`, never `keep`. Its number is not evidence.
2. Numbers that cannot fail at computable heights (zero-free regions, |M(x)| <= x^(7/8)) are
   instrument checks only, never evidence. The Riemann hypothesis is verified far beyond them.
3. Every hypothesis is labelled **(a) corollary** of an upstream theorem (new only in that upstream
   would make it unconditional; contribution = formal derivation) or **(b) conjecture** (goes beyond
   anything upstream claims). Novelty is "checked" only with a cited source, otherwise "unchecked".
4. Upstream anchors are claims by another model. Family 003 and the quintic part of 143 have
   faithful Lean statements and a clean static source scan, but were **not compiled here**
   (needs D2). Anything resting on an unformalized upstream claim says so.
5. Lean statements ending in `sorry` are locked targets, not results.
6. Ground truth is PARI/GP / Sage / ball arithmetic, never hand arithmetic.

## Metrics

- **H4 (Liénard)**: `max_cycles_found(deg)` for deg 5 and 6, counted as sign changes of the
  Poincaré displacement on the positive y-axis, each confirmed by a refined bisection.
  `keep` if a strategy finds a larger verified count than the previous best.
  A count of 3 at degree 5 would contradict upstream's formalized theorem; 5 at degree 6
  refutes H4.
- **H5 (dyadic triangular Hilbert form)**: `best_ratio` = the largest value found of
  sum_k sum_I |L_I| / prod ||F_v||_3. `keep` if larger. A value > 40 contradicts upstream's
  Theorem 1.1.
- **H2 (class numbers)**: a single preregistered train/holdout test, not a loop.
