# Spend policy (owner decision, 2026-11-01)

**STATUS 2026-11-02: month plan PAUSED by the owner (no daily cron). See HANDOFF_AND_TOKEN_PRACTICES_2026-11-02.md.**

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

**RE-ANCHORED 2026-11-13 (owner `/usage`): week 22% used (all models), Fable 9%, resets Sat 14 Nov 09:00 UTC.**
Mode: NORMAL (cap 60%). Between 7 and 13 Nov the meter went from 4% to 22% (+18 points in 6 days, about 3 per day: under the 8 per day allowed). Session cost $1190.87: Opus $905.40 (76%), Sonnet $252.54 (21%), Fable $31.67, Haiku $1.27. Opus is still the dominant cost although only audits use it; the main loop on Sonnet/Fable is cheap. The week resets tomorrow: re-anchor again then.

**RE-ANCHORED 2026-11-07 (owner `/usage`): NEW WEEK, 4% used (all models), Fable 0%, resets Sat 14 Nov 09:00 UTC.**
Mode: NORMAL. Allowed burn = (60 - 4) / 7 = 8 points per day: one new item per day is affordable.
Session cost breakdown from `/usage` (8 days, all of this project): total $1160.67; Opus $904.46 (78%: 970M cache-read tokens,
the long contexts of Opus producer/audit agents), Sonnet $223.37 (19%), Fable main loop $31.67 (3%), Haiku $1.18.
CORRECTION to the 2026-11-02 note: the dominant cost is the Opus agents (audits, early Opus producers), NOT the main loop.
Levers, in order: (1) keep Opus ONLY for audits and Lean proofs and bound each audit (about 40 tool calls, targeted reads,
no full re-implementation of what an exact checker already does); (2) Sonnet for producers/writers (already); (3) owner
option: allow a Sonnet auditor for tiny rechecks (weakens independence; only with explicit owner approval); (4) the
`/usage` hints also suggest cheaper models for general-purpose subagents and `/clear` when switching tasks (owner action).

**RE-ANCHORED 2026-11-02 (owner reading): weekly meter 36% used (all models), Fable 27%, resets Sat 7 Nov 08:59 UTC.**
The previous reading was 20% (Fable 3%) on 2026-11-01: +16 points in about one day, against +4 predicted by the token
proxy. The proxy (reported subagent tokens) therefore UNDERESTIMATES by about 4x: it omits the main loop's own tokens
(very large session context) and cache effects. New rough conversion: about 0.125M reported subagent tokens per meter
point (main loop included); never trust the proxy over the owner's meter.

**PACING RULE (added 2026-11-02).** The cap is 60% of the weekly meter by the weekly reset. Allowed burn per day =
(60 - used) / days left = (60 - 36) / 5 = about 4.8 points per day. The last day burned 16. Therefore ECONOMY mode now,
even though 36% is below the 42% tier: at most ONE new item every TWO days until the pace is back under the allowed daily
burn; in-flight items finish; no extra parallel lanes; no optional extras; scout and housekeeping only on off days.
Recompute the allowed burn at each owner reading.

**Levers to cut the main-loop cost (owner decisions, not yet applied):** (1) run /compact or start a fresh session so the
main loop does not re-read a huge context on every turn; (2) shorter reports (fewer turns narrating); (3) merge the
producer and writer stages for low-risk rechecks; (4) allow a Sonnet auditor for tiny rechecks (WEAKENS independence: only
with the owner's explicit approval, never silently); (5) pause the month plan for a day.

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
