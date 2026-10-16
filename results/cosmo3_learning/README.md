# cosmo3 & Phase 1 Verified Traces — JEPA Learning Retrofit (2026-10-16)

Produced by `scripts/cosmo3_retrofit.py`; raw numbers in `retrofit_summary.json`.

## What was stored & fixed
- **Vector DB:** the three literature reviews and paper sources went into the Chroma
  `literature` collection (84 new chunks, 284 total), embedded with qwen3-embedding
  (1024-d) under the shared GPU lease.
- **Root Causes Fixed (TODO 19):**
  1. **`max_energy` normalisation mismatch:** `cosmo3_retrofit.py` previously passed binary `{0, 1}` energies into `JEPADataset(max_energy=100.0)`, squashing all targets into `{0.00, 0.01}` within `energy_accuracy_threshold=0.10` so `energy_accuracy` saturated at `1.00` on both real and shuffled arms. Calibrated `max_energy=16.67` (the 2-failed-tests ceiling of Phase 1 verified traces) and `energy_accuracy_threshold=0.15` so `energy_accuracy_saturated = false`.
  2. **Target-state energy prediction bug:** `JEPATrainer._energy_predictions` and `JEPATrainer.validate` in `anse/jepa/trainer.py` previously evaluated `energy_head` on `h_ctx` instead of `h_tgt`, inverting supervision on `(h_fail -> h_pass)` transition pairs where `energy_actual` is the target state's energy.
  3. **Failure-rich verified corpus:** Evaluated across `383` unique verified states (`323` fail / `60` pass, `84.3%` failure-rich, `270` transitions, `653` items across `20` tasks) with task-held-out splits across 3 seeds (`42, 43, 44`).

## Multi-Seed Real vs. Shuffled-Label Control (`seeds = [42, 43, 44]`)

| Metric | Real Mean (min..max) | Shuffled Mean (min..max) | Mean Delta | All 3 Seeds Beat Shuffled? |
|---|---|---|---|---|
| **AUROC (failure > pass)** | **0.7378** (`0.6663..0.7975`, spread `0.1312`) | **0.4557** (`0.3155..0.6695`, spread `0.3541`) | **+0.2822** (`> 2.1x` real spread) | Yes (`+0.3677`, `+0.3508`, `+0.1280`) |
| **Spearman $\rho$** | **0.3913** (`0.0958..0.6432`) | **0.0098** (`-0.1193..0.2282`) | **+0.3814** | Yes (`+0.7625`, `+0.1752`, `+0.2066`) |
| **Energy Accuracy ($\le 0.15$)** | **0.3803** (`0.2778..0.4404`, spread `0.1626`) | **0.1855** (`0.1009..0.2752`, spread `0.1743`) | **+0.1948** (`> max spread`, `min_real > max_shuf`) | Yes (`+0.3394`, `+0.0972`, `+0.1477`) |
| **Validation Loss** | **34.80** (`32.83..37.37`) | **35.80** (`32.98..39.37`) | **-1.0052** | Yes (`-2.00`, `-0.15`, `-0.87`) |

See `results/cosmo3_learning/retrofit_summary.json` and `TODO.md` item 19.

