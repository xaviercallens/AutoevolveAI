# Spend policy (owner decision, 2026-11-01)

**Rule.** Weekly cap = 60% of the monthly Ultra allowance divided by 4 = **15% of the monthly allowance per week**,
so the month ends at about 60% used. A week runs from the platform's weekly reset (Saturday 09:00 UTC as seen on
2026-10-31); the monthly window is the subscription's billing month.

**What can and cannot be measured.** The agent cannot read the subscription meter (`/usage` is shown to the owner
only). The agent can only record a PROXY: the `subagent_tokens` and tool-use counts that every finished agent reports.
The proxy is logged in `docs/roadmap/SPEND_LEDGER.md` and is only meaningful once the owner supplies one calibration
reading (see below). Until then the policy defaults to the conservative mode.

**Conservative default (in force now).** Week 1 (31 Oct - 6 Nov) already produced 13 audited papers with about
10 Opus audits, which very probably exceeds 15% of a month. Therefore: items already in flight are finished
(producer -> audit -> revision -> publish); NO new items are started until the owner reports the current `/usage`
percentages (weekly and monthly). The daily job still runs the housekeeping, the scout and the PR updates, which are cheap.

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
