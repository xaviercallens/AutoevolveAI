# A1 continuation: L1 pipeline status

Generated 2026-11-02T06:07:57+0000 by `scripts/scheduler.py` (regenerated after every finished chunk; do not edit).
Cores: [0]. Per-chunk status JSON: `/home/callensxavier_gmail_com/a1l1_oleans/status`. Logs: `/home/callensxavier_gmail_com/a1l1_oleans/logs`.

| stage | entries | ok | fail | running | queued | planted rejected | kernel wall s (ok) | peak RSS GB | projected remaining core-h | wall h at current cores |
|---|---|---|---|---|---|---|---|---|---|---|
| cs | 45 | 45 | 0 | 0 | 0 | 2/2 | 26629 | 6.2 | 0.0 | 0.0 |
| core_test | 693 | 692 | 1 | 0 | 0 | 2/2 | 53486 | 3.9 | 0.0 | 0.0 |
| bdsup | 552 | 551 | 1 | 0 | 0 | 1/1 | 369383 | 5.6 | 0.0 | 0.0 |
| global_grid | 2188 | 249 | 0 | 1 | 1938 | 1/1 | 280996 | 5.7 | 609.96 | 609.96 |
| inside_hess | 603 | 2 | 0 | 0 | 601 | 1/1 | 4766 | 5.4 | 794.42 | 794.42 |
| table | 5393 | 15 | 0 | 0 | 5378 | 0/1 | 590 | 3.8 | n/a | n/a |

Probation: a stage's bulk chunks start only after its cores, planted controls and first genuine chunk are ok.
The wall column sums process wall time (inflated by machine load); see projection.json / PIPELINE.md for the measured per-unit projection.

* probation `cs`: passed
* probation `core_test`: passed
* probation `bdsup`: passed
* probation `global_grid`: passed
* probation `inside_hess`: passed
* probation `table`: in progress

## Failures and running entries

* `core_test/Assemble` (assemble): fail compile failed (rc 1) 10.5
* `bdsup/Assemble` (assemble): fail compile failed (rc 1) 24.0
* `global_grid/R0248` (chunk): running  

## Finished entries (most recent 40)

* 2026-11-01T16:55:34+0000 `global_grid/R0208` (chunk) 1098.8 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-01T17:14:02+0000 `global_grid/R0209` (chunk) 1106.9 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-01T17:32:20+0000 `global_grid/R0210` (chunk) 1092.3 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-01T17:52:30+0000 `global_grid/R0211` (chunk) 1203.6 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-01T18:10:48+0000 `global_grid/R0212` (chunk) 1097.3 s, 5.69 GB, compiled, axioms within whitelist
* 2026-11-01T18:29:57+0000 `global_grid/R0213` (chunk) 1143.2 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-01T18:51:29+0000 `global_grid/R0214` (chunk) 1281.8 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-01T19:11:29+0000 `global_grid/R0215` (chunk) 1189.5 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-01T19:37:21+0000 `global_grid/R0216` (chunk) 1547.3 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-01T20:01:20+0000 `global_grid/R0217` (chunk) 1429.0 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-01T20:30:05+0000 `global_grid/R0218` (chunk) 1714.1 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-01T20:58:38+0000 `global_grid/R0219` (chunk) 1708.6 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-01T21:28:31+0000 `global_grid/R0220` (chunk) 1787.6 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-01T21:53:42+0000 `global_grid/R0221` (chunk) 1506.0 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-01T22:12:11+0000 `global_grid/R0222` (chunk) 1101.7 s, 5.69 GB, compiled, axioms within whitelist
* 2026-11-01T22:30:29+0000 `global_grid/R0223` (chunk) 1093.7 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-01T22:49:38+0000 `global_grid/R0224` (chunk) 1145.5 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-01T23:09:48+0000 `global_grid/R0225` (chunk) 1205.0 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-01T23:31:30+0000 `global_grid/R0226` (chunk) 1297.5 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-01T23:52:32+0000 `global_grid/R0227` (chunk) 1252.2 s, 5.67 GB, compiled, axioms within whitelist
* 2026-11-02T00:11:10+0000 `global_grid/R0228` (chunk) 1116.5 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-02T00:29:38+0000 `global_grid/R0229` (chunk) 1099.4 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-02T00:49:37+0000 `global_grid/R0230` (chunk) 1194.7 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-02T01:08:15+0000 `global_grid/R0231` (chunk) 1108.5 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-02T01:26:34+0000 `global_grid/R0232` (chunk) 1095.2 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-02T01:45:03+0000 `global_grid/R0233` (chunk) 1101.1 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-02T02:03:21+0000 `global_grid/R0234` (chunk) 1092.3 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-02T02:22:59+0000 `global_grid/R0235` (chunk) 1170.4 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-02T02:40:57+0000 `global_grid/R0236` (chunk) 1075.7 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-02T02:59:25+0000 `global_grid/R0237` (chunk) 1104.1 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-02T03:18:03+0000 `global_grid/R0238` (chunk) 1117.3 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-02T03:35:51+0000 `global_grid/R0239` (chunk) 1059.2 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-02T03:53:39+0000 `global_grid/R0240` (chunk) 1062.9 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-02T04:11:06+0000 `global_grid/R0241` (chunk) 1045.9 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-02T04:29:34+0000 `global_grid/R0242` (chunk) 1100.4 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-02T04:47:22+0000 `global_grid/R0243` (chunk) 1066.6 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-02T05:05:50+0000 `global_grid/R0244` (chunk) 1103.4 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-02T05:24:38+0000 `global_grid/R0245` (chunk) 1125.7 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-02T05:43:46+0000 `global_grid/R0246` (chunk) 1139.9 s, 5.68 GB, compiled, axioms within whitelist
* 2026-11-02T06:02:55+0000 `global_grid/R0247` (chunk) 1147.3 s, 5.68 GB, compiled, axioms within whitelist
