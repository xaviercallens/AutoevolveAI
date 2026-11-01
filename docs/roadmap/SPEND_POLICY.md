# Spend policy (owner decision, 2026-11-01)

**Rule.** Weekly cap = 60% of the monthly Ultra allowance divided by 4 = **15% of the monthly allowance per week**,
so the month ends at about 60% used. A week runs from the platform's weekly reset (Saturday 09:00 UTC as seen on
2026-10-31); the monthly window is the subscription's billing month.

**What can and cannot be measured.** The agent cannot read the subscription meter (`/usage` is shown to the owner
only). The agent can only record a PROXY: the `subagent_tokens` and tool-use counts that every finished agent reports.
The proxy is logged in `docs/roadmap/SPEND_LEDGER.md` and is only meaningful once the owner supplies one calibration
reading (see below). Until then the policy defaults to the conservative mode.

**CALIBRATED 2026-11-01 (owner reading from `/usage`).** The meter shows the WEEKLY limit: all models 20% used
(Fable 3%), resetting Saturday 7 Nov 08:59 UTC. It does not show the monthly allowance. Assumption (stated, not
verified): the weekly limit is about one quarter of the monthly allowance, so "15% of the monthly allowance per week"
is read as **60% of the weekly meter**. Under that reading the cap is reached at 60% on the weekly meter, and the
tiers below apply to the weekly meter as follows: normal below 42%, economy 42-54%, finish-only 54-60%, pause at 60%.
Reading at calibration: 20% (that is 33% of the cap) after 13 audited papers plus housekeeping, so the 1-per-day plan
fits (about 40 points of meter remain until the cap; roughly 0.5M reported subagent tokens per meter point, a rough
proxy). The owner re-reads `/usage` on each Saturday and whenever asked; if the weekly limit is not a quarter of the
monthly allowance, the owner says so and the cap is rescaled. Mode now: NORMAL.

**Earlier conservative default (superseded by the calibration above).** Before the reading, new starts were held.

**Calibration.** The owner reports two numbers once: the monthly percentage used now, and the weekly percentage used
now. The agent then converts the logged proxy into percent-of-allowance (proxy tokens per percent) and keeps the cap.
The owner should repeat the reading on each Saturday (week start) so the proxy is re-anchored.

**Throttle tiers (fraction of the 15% weekly cap).**

| Used | Mode |
|---|---|
| < 70% | normal: one new item per day, Sonnet producers/writers, Opus audits |
| 70-90% | economy: at most 3 new items for the rest of the week, one audit per item, no extra re-audits, scouts only for the next item |
| 90-100% | finish only: complete in-flight items; start nothing; housekeeping and PR updates only |
| >= 100% | pause: nothing new; write BLOCKED in the journal; resume at the next weekly reset; never swap to a weaker auditor to save budget silently |

**Cost levers (in order).** (1) pick items with high expected value and low prior-art risk; (2) Sonnet for all producers
and writers; (3) Opus only for audits and Lean proofs, one audit per item (corrections are checked by the writer's own
rebuild, not by a second Opus run); (4) cap each agent's scope (core-hours, files read); (5) skip optional extras.

**End-of-month check.** On the last day, report the percentage used. Target: 60% +/- 5.
