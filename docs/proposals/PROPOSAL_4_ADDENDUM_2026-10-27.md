# Proposal 4: addendum of 2026-10-27 (after the news study)

This addendum **adds to** `NEXT_STEPS_PROPOSAL_4_2026-10-27.md` (committed as 7b412d0 before any attempt, sha256 a4da03c6…d290a). It changes nothing in the preregistered text or in wave 1 (C1, M3, M1, K1, E1). It records four additions that the news study `docs/studies/NEWS_STUDY_2026-10-27.md` suggests, each with its prior fixed **before any attempt**. Numbers come from that study; the sources it cites must be read in full before an attempt starts, and anything not yet read is marked so.

## What the study could and could not do
- The Reddit thread the owner pointed at could **not be read** (Reddit blocks automated access). The study's best guess for its subject is OpenAI's 26 October release (about 0.55 confidence); that guess is unverified.
- We stay out of OpenAI's computer-science and wave-equation results: named expert groups already examine them, and verifying them is not our question.

## A. Additions

**A1. Mechanical statement-adequacy checks added to the gate (GATE-1).** For every item from now on, before a Lean statement can be called Tier A we add the numeric and vacuity checks of the Mei–Douglas method (arXiv 2610.20573, Apache-2.0; paper not yet read in full here): evaluate the statement on concrete cases it must accept and cases it must reject, and test the hypotheses for vacuity. This targets the gap `METHODOLOGY.md` already admits (a kernel-checked statement may not say what its description says). Prior 0.45, value 2, feasibility 0.70, score 0.630. Rule: if a check flags a vacuous or trivially true statement, that statement may not be labelled Tier A.

**A2. New wave-2 energy item E4 = MHD-1.** An independent exact check of the closed-form three-dimensional plasma equilibria (no stellarator symmetry) reported with Gemini agents (arXiv 2610.07304; to be read in full before the attempt). Method: exact symbolic residuals of the equilibrium equations, a negative control (a perturbed solution must leave a non-zero residual), and a Lean proof of the algebraic core of the first family only. Headline tier: C. Prior 0.45, value 3, feasibility 0.75, score 1.013. It gives open fusion codes a checked benchmark; it is a statement about stated equations, **not** about any reactor. Kill criterion: if the source's formulas cannot be fully read, or the exact residuals cannot be evaluated unambiguously, stop and report why; a non-vanishing residual is reported as a finding about the stated formula, never as an accusation.

**A3. Tooling note for E1, K2, M1 and M3.** LeanCert (Apache-2.0, revision 7f91b6eb) runs on our pinned toolchain, but its interval tactics close goals with `native_decide`, which our axiom whitelist and escape grep reject. Its proofs therefore count only as an independent **Tier C cross-check**, never Tier A, unless a kernel-only path is shown to work (first test: its `Real.exp` paths).

**A4. CARBON-1 as a positive control for K3.** The 2025 low-latency global carbon budget (Ciais et al., arXiv 2609.34226; to be pinned from the text) gives an arithmetic consistency check to be reproduced exactly before any K3 result counts. A hand check in the study (10.38 − 2.04 − 3.15 − 2.06 × 2.124 = 0.81) is Tier X scratch work, not a result.

## B. Unchanged
- Wave 1 stays as launched. C2 and C3 stay deferred until a reader with medical-physics background has seen the wording rules.
- Wave 2 stays M2, K2, K3, E2, E3 plus E4 if capacity allows (E3 gives way if wave 2 must keep its size).
- Same rules throughout: claims written down before the test; a test that must pass and one that must fail; the maker is not the checker; negative results published; no medical, climate or device claims; public data only; no patient data.

## C. What we decline (from the study)
Anything using patient data; therapy-framed modelling; tonnes-removed or commercial carbon-removal accounting and ocean fertilisation; closed or restricted data (including the DIII-D-trained model, battery data with non-commercial or no licence, a tumour code without licence); laser-driven proton-boron yield work (crosses the dual-use line); leaderboard chasing; claiming to have "verified" OpenAI's results or racing expert groups; wet-lab biology; any "peer-reviewed" label without a reviewer.
