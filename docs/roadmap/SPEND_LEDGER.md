# Spend ledger (proxy; see SPEND_POLICY.md)

The proxy is the `subagent_tokens` figure that each finished agent reports (output + context of that agent), summed per
day. It is NOT the subscription meter. It becomes percent-of-allowance only after the owner supplies a calibration
reading from `/usage`. Entries below are appended by the daily cycle.

## Week 1 (31 Oct - 6 Nov)

Status before the policy: about 60 agent runs since the weekly reset, including roughly 10 Opus audits (typically
110k-260k reported tokens each) and the producers/writers (typically 90k-400k each). The main loop's own tokens are
not included. A conservative reading is that this week is already at or above the 15% cap.

| Date | Agents finished | Reported subagent tokens (sum, approx.) | Opus audits | Notes |
|---|---|---|---|---|
| 2026-10-31 .. 2026-11-01 | ~60 | ~10M (rough, from notifications; not recomputed) | ~10 | 13 papers published |

## Calibration (owner to fill in or report)

| Date | Monthly % used (from /usage) | Weekly % used | Proxy tokens at that moment | Tokens per 1% |
|---|---|---|---|---|
| 2026-11-01 | not shown by /usage (the meter is weekly) | 20% (all models), Fable 3%; resets 7 Nov 08:59 UTC | ~10M (rough) | ~0.5M (rough) |

Cap in meter terms: 60% of the weekly meter (assumption: weekly limit = monthly allowance / 4). Next re-anchor: 7 Nov.
