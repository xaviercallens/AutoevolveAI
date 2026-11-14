# Proposal 4, addendum 2 (2026-10-27): C1b, the exhaustive death-Birth amplifier census at N = 11

Written and hashed **before any attempt**. It extends C1 (published as doi:10.5281/zenodo.23704563: no connected graph with N <= 10 is an unweighted death-Birth amplifier of weak selection by Allen et al.'s criterion N_eff > N; Richter's 11-vertex graph is one, in Lean). It changes nothing in Proposal 4 or its first addendum.

## Question
Among the 1,006,700,565 connected unweighted graphs on 11 vertices (OEIS A001349: to be re-read at the start), (i) exactly how many have N_eff > N? (ii) Is Richter's graph (graph6 `J?ouPjI[@i?`, parent `J?ouPjI{@i?`) the unique one up to isomorphism, and what are the others, if any?

## Why it matters, modestly
It would turn "the smallest known amplifier has 11 vertices" into an exact classification at that size: a statement a reader can re-run. It is mathematics of graphs only: no claim about tissues, tumours or any medical use.

## Method (reusing C1)
Enumerate with nauty `geng -c 11` in parallel parts (`res/mod`); decide each graph by the C1 rule: a floating-point solve of Allen's coalescence-time system only proposes a verdict, and an exact integer residual bound (non-negative inverse of I - M) decides it; every graph within a safety margin of N, and every regular graph, is solved exactly with Fractions. Every amplifier found gets an exact certificate and, where feasible, a Lean theorem in the style of `R11_amplifier`.

## Controls (before any N = 11 number counts)
- Positive: the same code reproduces the C1 census at N = 3..10 (zero amplifiers; regular graphs tie at N_eff = N; counts equal OEIS A001349 and A005177), and finds Richter's N = 11 graph with N_eff = 2668552698098/242579025123.
- Negative: a deliberately corrupted criterion (e.g. the r^{-(N-1)} exponent of the arXiv v1 misprint) must change the verdicts; K_11 and the 11-cycle must tie.
- Count check: the total number of graphs processed must equal 1,006,700,565 exactly (sum over all geng parts).

## Priors and kill criteria
- Prior that the census completes within the budget: 0.5. Prior that it finds a graph other than Richter's: 0.25. Prior that Richter's graph is the only amplifier at N = 11: 0.6 (a finding either way).
- Time box: 24 wall-clock hours on 2 cores (taskset -c 2,3). **Kill criterion:** measure throughput on a 10^7-graph sample; if the projected total exceeds 24 h on 2 cores, stop and report the extrapolation (and the partial count of parts completed, labelled partial); do not claim completeness.
- A partial census is a partial result and is reported as such.

## Tiers
The census count is Tier C (enumeration with a certified decision rule, not in Lean). Each amplifier found: the exact N_eff is Tier C; a Lean theorem for it would be Tier A (with the usual gate: axioms within the whitelist, kernel replay, no kernel-bypass construct). The step from N_eff > N to amplification near r = 1 is literature (Allen et al., Tier L).

## Not claimed
No novelty claim beyond 'to our knowledge'; nothing about real tissue; no conjecture proved.
