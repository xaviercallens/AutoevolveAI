# Consistency report (v2.1): Dyadic_NavierStokes_Regulator_Elenchus_Paper.pdf

This file replaces the v2.0 `PEER_REVIEW_REPORT.md`, which was scripted text with invented referee personas and
scores; it is withdrawn. Every line below is a machine comparison, not a review.

- Lean 4 spec gate: `19` declarations verified, `0` sorryAx, spec DefEq `True`
- Elenchus ledger Merkle root: `002553349d556837ff8b59180d40be66773600fcf0bb9c324a03ea170bd80d7c`
- All checks passed: `True`

| check | passed | detail |
|---|---|---|
| lambda6_mode_count_in_text | True | harness 924 |
| lambda6_triad_count_in_text | True | harness 398190 |
| depletion_row::Random Thinning Control ($f \approx 0.48$) | True | |S|=447 |T|=45727 D=1.0143 |
| depletion_row::Even Sublattice $(2\mathbb{Z})^3$ | True | |S|=122 |T|=6642 D=7.2468 |
| depletion_row::Coordinate Planes $k_x k_y k_z = 0$ | True | |S|=300 |T|=25518 D=1.8724 |
| depletion_row::Perfect-Square Shell $|k|^2 = m^2$ | True | |S|=108 |T|=846 D=1.3305 |
| depletion_row::Modular Shell $|k|^2 \equiv 0 \pmod 3$ | True | |S|=336 |T|=20034 D=1.0463 |
| depletion_row::Prime Norm-Square Shell $|k|^2 \in \mathbb{P}$ | True | |S|=236 |T|=3792 D=0.5716 |
| depletion_row::Odd Norm-Square Shell $|k|^2 \equiv 1 \pmod 2$ | True | |S|=466 |T|=0 D=0.0000 |
| square_shell_reported_as_enriched | True | D=1.3305 |
| no_stale_square_depletion_value | True | stale v1 values absent except in the response paragraph |
| theorem_2_2_arithmetic_witness_13 | True | term-by-term sum |
| laplacian_constant_mode_zero | True | spectrum starts with 0 |
| no_percentage_scorekeeping | True |  |
| lean_gate_verified | True | 19 declarations, sorry=0 |
| ledger_merkle_root_in_text | True | 002553349d556837ff8b59180d40be66 |
| zenodo_records_in_text | True | first edition and v2.0 records cited; stale concept id absent |
