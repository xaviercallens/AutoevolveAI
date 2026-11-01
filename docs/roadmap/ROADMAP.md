# Scientific roadmap (living document)

Owner direction (2026-10-31): continue every day on new mathematics, physics, biology, energy, materials and
medicine-adjacent questions, with a daily roadmap/journal update, experimentation and publication, step by step,
leveraging the foundation already built. Method: **Elenchus** (tiers A/L/C/X, preregistration before any attempt,
positive and negative controls, producer != verifier, negative results published, no human audit claimed).

## What "every day" can honestly mean
- One cycle per day produces **one or two** preregistered items taken through producer -> independent AI audit ->
  revision -> Zenodo -> GitHub. Some days produce only a scout note or a negative result. Nothing is padded.
- **No claim of curing, treating or solving a disease**, of a new energy source, of a deployable material or of a
  climate effect. Items are bounded statements about *models* or *public datasets*, with tiers. Cancer work stays
  in strictly mathematical models of cell populations (Proposal 4 C2, C3), and is gated by section 6 of Proposal 4
  (owner decision: a human reader with radiotherapy / mathematical-oncology background for the wording rules).
- Public data only; no patient data; no dual-use detail; third-party texts stay out of tracked paths.

## The daily cycle
1. **Scout** (<=1 h): new arXiv/news in math.*, math-ph, cond-mat, physics.plasm-ph, q-bio, physics.chem-ph,
   plus claims by labs about AI-found results. Output: `docs/journal/YYYY-MM-DD.md` scout section. Anything
   claimed by others is *checked*, never repeated as fact.
2. **Select** <=2 items from the queue below (ranking p x V x F) or from the scout; write and hash a
   preregistration (prior, controls, kill criterion, tiers) **before** any attempt.
3. **Produce** (Sonnet for papers/numerics; Opus only for Lean proofs and audits; producers on assigned cores).
4. **Audit** by a different agent instance with its own implementation; corrections applied; verdict recorded.
5. **Publish**: Zenodo (staging-tree bundle, no third-party files), GitHub branch push + PR to the public and
   private repos; merges only when the owner says "merge".
6. **Update** this roadmap, the day's journal entry, and (weekly) the public showcase page.
7. **Stop rules**: kill criteria honoured; spend limit hit -> pause, do not swap models silently.

## Done so far (as of 2026-10-31)
Published (Zenodo): textbooks FR/EN, discovery journal FR/EN, N1, N2, A2 (v1.2), C1 (v1.1), C1b, M3, M1, K1, E1,
LR-IND. See `docs/journal/` and the NewDiscoveries addendum (PR #3, awaiting merge).

## In flight
| Lane | Area | State |
|---|---|---|
| A1 | Lean Sandier-Serfaty port | scheduler on core 0 (nothing proved) |

## Queue (ranked; Proposal 4 section 3, Proposal 5)
| Id | Area | Question | Status |
|---|---|---|---|
| C2, C3 | cancer (math models only) | LQ fractionation in Lean; containment vs MTD comparison | **deferred: needs owner + human wording reader** |
| LR-Q84, N1-ext, LR-SPEC, LR-2E, GR-11, S8-ALL | mathematics | Proposal 5 items 5-10 | next (cores free) |
| SLR-18 follow-up | mathematics | n = 39..94 (30 core-h cap reached), statement lock for the Lean covering statements | next |
| B-lane | biology | preregistered audits of published mathematical-biology claims on public data | to define |
| MS-CENSUS, DICE-6 | mathematics | from the 2026-11-01 scout (docs/journal/2026-11-01.md) | next |
| Proposal 6 | all | write after the scout of the week | to do |

## Published (Zenodo), as of 2026-10-31
Textbooks FR/EN, journal FR/EN, N1, N2, A2 v1.2, C1 v1.1, C1b, M3, M1, K1, E1, LR-IND, SLR-18, DH-Psi2, M2,
EG-CB68, E2, K3, K2, E3, GR-11, LR-SPEC, GALE-101 (also: independent router verification and a Gen 6 swarm design, see the journal). Details and DOIs: `docs/journal/2026-10-31.md` and the NewDiscoveries addendum.

## Foundation being leveraged
Lean 4.34.1 pinned runner + leanchecker replay; Arb/mpmath ball arithmetic; nauty; exact rational solvers;
the Elenchus ledger gate; the staging-tree Zenodo publisher; the independent-audit pattern (every published
item so far was changed by its audit at least once).

## Rules that never change
No "breakthrough"/"solved"; the Millennium problems are not claimed; no human audit disclosed; negative and
partial results are published; every number traces to a file; flags are printed, not hidden.
