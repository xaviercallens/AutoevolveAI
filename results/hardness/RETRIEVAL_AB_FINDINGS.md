# Premise-retrieval A/B on the Lean hardness ladder — findings (TODO 5 / card M-1)

222 real runs, both provers, greedy decoding, same items, same seed, arms k=0 (no retrieval)
vs k=5 (top-5 `lean_premises` hits prepended) vs k=5-shuffled (wrong item's hits, a negative
control on 5 T1 items). Compiled and axiom-checked against OUR statement
(`anse.formal.lean_runner.verify_file`). Raw data: `results/hardness/retrieval_ab.json`.

## Result: model-dependent, and real (not spurious)

| Tier | DeepSeek-Prover-V2-7B | Goedel-Prover-V2-8B |
|---|---|---|
| T0 (sanity) | 7/10 (k5) | 7/10 (k5) |
| T1 (point on curve) | 0/12 → **2/12** with retrieval | 0/12 → 0/12 (no change) |
| T2 (discriminant) | 0/12 → 0/12 (no change) | 0/12 → 0/12 (no change) |
| T3 (group-law double) | 0/12 → **10/12** with retrieval | 0/12 → 0/12 (no change) |

**Shuffled-premise control** (T1, 5 items, wrong item's hits instead of the real one's):
DeepSeek 0/5, matching the no-retrieval baseline — the gain is not "any text helps," it is
specifically the right premises. **False items accepted: 0 across all 222 runs** — the
soundness gate held perfectly under this experiment, same as the original baseline.

**H2 (TODO 5) is confirmed for DeepSeek, not for Goedel.** The retrieval mechanism worked as
designed (the needed lemma was actually retrieved: 16/16 on T1, 16/16 on T2, 8/16 on T3), but
only one of the two provers converted that into proofs. On T3, DeepSeek reached 10/12 with
only half the needed lemmas retrieved — it generalizes past a partial hint on this tier.
Goedel never used the retrieved premises to close a single new proof, on any tier, despite
receiving the identical context DeepSeek did.

## Reading this honestly

- T2 stayed at 0/0 for both models even with the right premises retrieved 16/16 — retrieval
  fixes a missing-vocabulary problem, not a missing-strategy problem, and T2's gap looks more
  like the latter.
- This is one seed, greedy decoding, 118 items. It is a real, controlled result, not a
  large-sample one.
- Feeds `anse/v2/model_router.py` via `scripts/hardness/capability_matrix.py`: the router
  now has real `deepseek+premises` / `goedel+premises` cells and will route T3 to
  DeepSeek-with-retrieval once that arm clears the routing threshold.

## Next

- Re-run T2 with a stronger retrieval signal (larger k, or a differently-embedded query) to
  check whether T2's flat 0/0 is retrieval-quality-limited or a real reasoning gap.
- Investigate why Goedel does not benefit — read its raw T3 generations with premises present
  to see whether it uses them at all or ignores the prepended context.
