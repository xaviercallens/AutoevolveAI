# cosmo3 learning retrofit (2026-09-27)

Produced by `scripts/cosmo3_retrofit.py`; raw numbers in `retrofit_summary.json`.

## What was stored
- **Vector DB:** the three literature reviews and paper sources went into the Chroma
  `literature` collection (84 new chunks, 284 total), embedded with qwen3-embedding
  (1024-d) under the shared GPU lease.
- **JEPA episodes:** 206 verdict-bearing pipeline steps (173 pass, 33 fail), each pointing
  at on-disk evidence, saved as JEPA rows at
  `/mnt/disks/disk-socrateai-local-1/AutoevolveAI/datalake/episodes/cosmo3_2026-09-27.jsonl`.

## What the JEPA training showed: nothing yet (negative result)
| run | val loss | val energy accuracy |
|---|---|---|
| real verdicts | 21.87 | 1.00 |
| energies shuffled across rows (negative control) | 21.46 | 1.00 |

The model trained on real verdicts is indistinguishable from the shuffled-label control,
so it learned no verdict signal from these episodes. Two reasons are visible:
1. **The metric is saturated.** "energy_accuracy" reaches 1.00 even on shuffled labels, so
   it cannot detect signal here and must not be reported as evidence of learning.
2. **The data is small and imbalanced** (206 steps, 84% pass), and consecutive attempts
   within one script are few, so there are few informative transitions.

This corpus is kept because its labels are real; it is not claimed to have trained anything.
See LL.md §12b item 8 and TODO item 19.
