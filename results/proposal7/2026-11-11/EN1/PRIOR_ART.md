# EN-1 prior-art screen (2026-11-11, scout)

VERDICT: NOT NEW (D-T core already published by us as E1); residual add-on is NOT USEFUL. No PREREG_DRAFT.

## Our own work (READ, papers/p4_pb_ignition/main.tex, doi 10.5281/zenodo.23733098)
- E1 already did the Wurzel-Hsu 0-D D-T ideal-ignition model with python-flint Arb enclosures (Tier C, not Lean).
- D-T, model of the authors' code (Bosch-Hale integrated, Putvinski bracket, Zeff=1, fc=0.2):
  T_ign [4.2989514,4.2989523] keV; argmin n T tau [14.128,14.442] keV; min n T tau [2.94410,2.94502]e21 keV s/m^3;
  argmin n tau [25.590,26.212] keV; min n tau [1.55227,1.55279]e20.
- Constant hull (C_B, keV/J, fc in [3.5/17.6,0.2]): T_ign [4.2608,4.3468]; min nTtau [2.94400,2.96351]e21. Pure-text row (auditor, Tier X): min in [2.95,2.96846]e21.
- Lean: two elementary real inequalities (not the ignition statement). AI audit ACCEPT_WITH_CORRECTIONS.
- E1 admits Bosch-Hale (1992) coefficients were NOT obtained from the primary paper (taken from the W-H code). Open gap, but small.

## Screen
1. Wurzel & Hsu arXiv:2105.10954 (READ by grep of full text): prints ideal ignition T 4.3 keV, min n T tau 2.9e21 at 14 keV (D-T, Q=inf), min n tau 1.6e20 at 26 keV; impurity (Zeff) bands for SPARC; no interval or reactivity-error propagation found. Update: arXiv:2505.03834 (SECONDARY, titles only).
2. Bosch-Hale, Nucl. Fusion 32, 611 (1992): R-matrix fits; I could NOT retrieve the stated max deviation or validity range (web search returned only abstracts). Do not quote a number.
3. Ignition minimum ~3e21 near 14 keV: stated in W-H Table III; E1 already enclosed it. Freidberg, Lawson 1957, Costley 2016 not read (SECONDARY from memory).
4. Interval arithmetic or Lean for Lawson/power balance: alphaXiv search (2023+) found nothing on D-T Lawson. Only unrelated Lean radii-polynomial work (2610.02335). Not exhaustive.
5. 2025-26 revisits: 2410.18054 (ignition principles), 2601.00241 (p-B11 updated cross sections), 2507.18917 (turbulence-modified criterion): none certified. No competitor for certified D-T windows found.

## Assessment
- Exact-recheck of W-H numbers is done (E1 positive control). A "certified min location/value" repeats E1.
- Conditional statement given BH exact is E1's table; propagating BH fit error (order of percent or less, unverified) only widens the interval by the fit error, which exceeds numerical width (~3e-4 relative) by 1-2 orders: "numerics are not the bottleneck" (Tier X), as the kill criterion foresaw.
- Possible tiny addendum (a Lean lemma of unimodality, or a BH primary-source check) is below publication level; fold into E1 v2 if a v2 is ever made.
