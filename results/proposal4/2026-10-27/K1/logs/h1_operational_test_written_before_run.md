# K1-H1 operational test (written 2026-10-27 ~12:30 UTC, before any exergy number was computed)

Evaluator: one Python re-implementation of IntrinsicDACCycle v0.0.2 (`code/dac_model.py`), used for BOTH
accountings, so that the only change between them is the heat weighting (`code/exergy.py`).

1. Rows: the 14 Table 2 rows (matched in the dataset by path parameters), plus a seeded random sample of
   materials with an optimized result (seed 20261027), each represented by its stored Pareto path of maximal
   face-value xi. The sample is Tier X (no NSGA-III re-optimisation; that is out of budget on 2 cores).
2. Held fixed: (T_end, P1, P_end) at the stored values. Scanned: T1 on a 1 K grid from 200 K to T_end - 1 K,
   linear path with the code's own discretisation (dT_max 0.25 K, dP_max -125 Pa). Cv off the stored path from a
   Python re-fit of the same SE + Const GP, validated against the stored Cv arrays.
3. Objective: maximise xi subject to purity >= the stored nominal purity of the row (and, separately,
   unconstrained).
4. Face-value control: the face-value scan must put the optimum at low T1 (within 15 K of the stored T1, or at
   the 200 K bound). If it does not, the evaluator is not trusted and H1 is not scored.
5. H1 is scored per row at T0 in {273.15, 298.15, 313.15} K, for the no-credit exergy accounting (r = 0, the
   headline, faithful to "no energy recovery") and for r = 0.5 and r = 1 (signed reversible) as bookends.
   "Optimal T1 moves to T1 >= T0" for a row if argmax T1 under exergy >= T0. H1 (headline) holds if this is
   true for most (> 50 %) rows at T0 = 298.15 K, r = 0.
