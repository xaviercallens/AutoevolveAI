# A1 continuation: L1 pipeline status

Generated 2026-10-26T14:06:42+0000 by `scripts/scheduler.py` (regenerated after every finished chunk; do not edit).
Cores: [0, 1, 2, 3]. Per-chunk status JSON: `/home/callensxavier_gmail_com/a1l1_oleans/status`. Logs: `/home/callensxavier_gmail_com/a1l1_oleans/logs`.

| stage | entries | ok | fail | running | queued | planted rejected | kernel wall s (ok) | peak RSS GB | projected remaining core-h | wall h at current cores |
|---|---|---|---|---|---|---|---|---|---|---|
| cs | 45 | 45 | 0 | 0 | 0 | 2/2 | 26629 | 6.2 | 0.0 | 0.0 |
| core_test | 693 | 619 | 0 | 4 | 70 | 2/2 | 48991 | 3.9 | 5.27 | 1.32 |
| bdsup | 552 | 0 | 0 | 0 | 552 | 0/1 | 0 | 0.0 | n/a | n/a |
| global_grid | 2188 | 0 | 0 | 0 | 2188 | 0/1 | 0 | 0.0 | n/a | n/a |
| inside_hess | 603 | 0 | 0 | 0 | 603 | 0/1 | 0 | 0.0 | n/a | n/a |
| table | 5393 | 0 | 0 | 0 | 5393 | 0/1 | 0 | 0.0 | n/a | n/a |

Probation: a stage's bulk chunks start only after its cores, planted controls and first genuine chunk are ok.
The wall column sums process wall time (inflated by machine load); see projection.json / PIPELINE.md for the measured per-unit projection.

* probation `cs`: passed
* probation `core_test`: passed
* probation `bdsup`: in progress
* probation `global_grid`: in progress
* probation `inside_hess`: in progress
* probation `table`: in progress

## Failures and running entries

* `core_test/S4C0117` (chunk): running  
* `core_test/S4C0120` (chunk): running  
* `core_test/S4C0123` (chunk): running  
* `core_test/S4C0126` (chunk): running  

## Finished entries (most recent 40)

* 2026-10-26T13:57:04+0000 `core_test/S2C0370` (chunk) 289.5 s, 3.83 GB, compiled, axioms within whitelist
* 2026-10-26T13:57:04+0000 `core_test/S3C0000` (chunk) 86.8 s, 3.84 GB, compiled, axioms within whitelist
* 2026-10-26T13:57:15+0000 `core_test/S4C0003` (chunk) 39.6 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T13:57:26+0000 `core_test/S4C0006` (chunk) 40.3 s, 3.88 GB, compiled, axioms within whitelist
* 2026-10-26T13:57:56+0000 `core_test/S4C0012` (chunk) 43.7 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T13:58:07+0000 `core_test/S4C0015` (chunk) 44.1 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T13:58:38+0000 `core_test/S4C0018` (chunk) 67.2 s, 3.88 GB, compiled, axioms within whitelist
* 2026-10-26T13:58:48+0000 `core_test/S4C0021` (chunk) 42.6 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T13:58:59+0000 `core_test/S4C0024` (chunk) 44.2 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T13:59:40+0000 `core_test/S4C0030` (chunk) 45.4 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T13:59:51+0000 `core_test/S4C0027` (chunk) 62.9 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T13:59:51+0000 `core_test/S4C0033` (chunk) 47.2 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:00:32+0000 `core_test/S4C0036` (chunk) 43.2 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:00:42+0000 `core_test/S4C0009` (chunk) 207.5 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:00:53+0000 `core_test/S4C0039` (chunk) 59.7 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:00:53+0000 `core_test/S4C0042` (chunk) 53.6 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:01:14+0000 `core_test/S4C0045` (chunk) 41.5 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:01:35+0000 `core_test/S4C0048` (chunk) 48.9 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:01:45+0000 `core_test/S4C0051` (chunk) 46.8 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:01:45+0000 `core_test/S4C0054` (chunk) 42.9 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:02:06+0000 `core_test/S4C0057` (chunk) 45.6 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:02:30+0000 `core_test/S4C0060` (chunk) 50.1 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:02:41+0000 `core_test/S4C0063` (chunk) 50.4 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:02:41+0000 `core_test/S4C0066` (chunk) 46.2 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:03:02+0000 `core_test/S4C0069` (chunk) 51.4 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:03:23+0000 `core_test/S4C0072` (chunk) 51.5 s, 3.90 GB, compiled, axioms within whitelist
* 2026-10-26T14:03:33+0000 `core_test/S4C0075` (chunk) 51.3 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:03:33+0000 `core_test/S4C0078` (chunk) 47.0 s, 3.90 GB, compiled, axioms within whitelist
* 2026-10-26T14:04:04+0000 `core_test/S4C0081` (chunk) 55.7 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:04:15+0000 `core_test/S4C0084` (chunk) 48.8 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:04:36+0000 `core_test/S4C0087` (chunk) 58.6 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:04:36+0000 `core_test/S4C0090` (chunk) 53.0 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:05:07+0000 `core_test/S4C0093` (chunk) 62.3 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:05:18+0000 `core_test/S4C0096` (chunk) 62.0 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:05:38+0000 `core_test/S4C0102` (chunk) 58.8 s, 3.90 GB, compiled, axioms within whitelist
* 2026-10-26T14:05:49+0000 `core_test/S4C0099` (chunk) 72.2 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:06:10+0000 `core_test/S4C0105` (chunk) 54.0 s, 3.90 GB, compiled, axioms within whitelist
* 2026-10-26T14:06:10+0000 `core_test/S4C0108` (chunk) 50.1 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:06:31+0000 `core_test/S4C0111` (chunk) 45.7 s, 3.89 GB, compiled, axioms within whitelist
* 2026-10-26T14:06:41+0000 `core_test/S4C0114` (chunk) 44.1 s, 3.89 GB, compiled, axioms within whitelist
