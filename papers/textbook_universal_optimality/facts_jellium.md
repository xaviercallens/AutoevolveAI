# facts_jellium.md — every number in `sec_jellium_cancel.tex` and the command that printed it

All numbers below are Tier X (floating point) unless marked. They were printed by ONE command (runtime 6.0 s,
2 cores):

```
taskset -c 6,7 /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I \
  papers/textbook_universal_optimality/code/jellium_cancel.py \
  --json /home/callensxavier_gmail_com/.claude/jobs/6ecda88c/tmp/jel/final.json \
  --fig  papers/textbook_universal_optimality/figures_v2/jellium_cancel.pdf
```
(full stdout kept at `/home/callensxavier_gmail_com/.claude/jobs/6ecda88c/tmp/jel/final.log`; the script is
deterministic: random centre offsets use `numpy.random.default_rng(20261011)`). Paths relative to the worktree
`/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/`.

Conventions: density n = 1, lattice A of FACTS §1 (covolume 1), each pair counted ONCE (same as the
rusty-SUNDIALS crate, FACTS §4 and ch3 eq. (ewald)); g = 1/r (s = 1) and g = −log r (s = 0, length unit = 1).
Background is a uniform disk of radius R_b = sqrt(N/pi), centred at the disk centre, exactly neutral.
Six random centre offsets per R; "mean (std)" over offsets.

## Ingredient checks (tolerances fixed in the script before the first run)
| quantity | value | tolerance |
|---|---|---|
| closed-form disk potential (interior E, exterior E−(1−m)K) vs chord quadrature, 7 radii | max rel err 1.50e-15 | 1e-9 |
| rim potential / (4 n R) | 1.000000000000000 | — |
| ∫_D∫_D 1/|x−y| on the unit disk (quadrature) | 16.755160819145566 vs 16π/3 = 16.755160819145562 (rel 2.22e-16) | 1e-10 |
| ∫_D∫_D log|x−y|, R = 2 | 69.978997817356 vs π²R⁴(log R − 1/4) = 69.978997817356 | 1e-10 |
| FFT pair sums vs brute-force pdist (N = 254) | rel err 0.00e+00 (both kernels) | 1e-12 |
| Python one-cell Ewald, s = 1, α = 1, 2, 4 | −1.960515789320 (all three) | α-spread < 1e-11 |
| … vs crate −1.960515789320 (FACTS §4) | diff 1.08e-13 | 1e-9 |
| … vs literature −1.960515789825 (FACTS §4, Tier L) | diff 5.05e-10 | — |
| Python one-cell Ewald, s = 0 (−log r), α = 1, 2, 4 | −0.660558714214 (all three) | α-spread < 1e-11 |
| all ingredient checks | PASS | |

The s = 0 Ewald value has NO literature cross-check (only α-invariance). It depends on the length unit:
−log(r/ℓ) shifts it by −(1/2) log ℓ (pairs once, neutral) — algebra in the text.

## s = 1 disk table (per particle; means over 6 offsets)
| R | N mean | pp/N | pb/N | bb/N = (8/3)R_b | e = E/N (std) | e − e_tri (std) | √N (e − e_tri) (std) |
|---|---|---|---|---|---|---|---|
| 6.00 | 113.2 | 14.095 | −32.011 | 16.005 | −1.911915 (1.1e-2) | +4.860e-2 | +0.5163 (0.116) |
| 7.86 | 194.3 | 19.052 | −41.949 | 20.973 | −1.923258 | +3.726e-2 | +0.5189 |
| 10.29 | 333.3 | 25.539 | −54.941 | 27.468 | −1.933736 | +2.678e-2 | +0.4890 |
| 13.48 | 569.5 | 33.966 | −71.805 | 35.904 | −1.935070 | +2.545e-2 | +0.6072 |
| 17.65 | 978.5 | 45.120 | −94.126 | 47.062 | −1.943550 | +1.697e-2 | +0.5307 |
| 23.11 | 1678.0 | 59.683 | −123.260 | 61.630 | −1.947564 (4.3e-4) | +1.295e-2 | +0.5305 (0.017) |
| 30.27 | 2877.8 | 78.760 | −161.420 | 80.710 | −1.950307 | +1.021e-2 | +0.5476 |
| 39.64 | 4934.3 | 103.731 | −211.366 | 105.684 | −1.951628 | +8.888e-3 | +0.6243 |
| 51.92 | 8468.5 | 136.497 | −276.902 | 138.451 | −1.954288 | +6.228e-3 | +0.5732 |
| 67.99 | 14522.0 | 179.348 | −362.608 | 181.304 | −1.955890 | +4.626e-3 | +0.5574 |
| 89.04 | 24906.0 | 235.479 | −474.872 | 237.436 | −1.957161 (3.5e-4) | +3.354e-3 | +0.5294 (0.055) |
| 116.61 | 42717.0 | 308.995 | −621.905 | 310.953 | −1.957838 | +2.678e-3 | +0.5534 |
| 152.72 | 73267.8 | 405.282 | −814.480 | 407.240 | −1.958508 | +2.008e-3 | +0.5436 |
| 200.00 | 125655.5 | 531.357 | −1066.632 | 533.316 | −1.958888 (8.3e-5) | +1.628e-3 (8.3e-5) | +0.5771 (0.029) |

e_tri used = −1.960515789320 (Python Ewald, α = 2; equals crate value to 1.1e-13).

- (pb + 2 bb)/N for the 14 radii: −2.13e-03 −2.52e-03 −4.35e-03 +2.90e-03 −1.40e-03 −9.63e-04 −6.56e-04 +1.12e-03
  +2.24e-04 −6.08e-05 −4.53e-04 −1.19e-04 −1.44e-04 +1.75e-05   (so |pb + 2bb|/N ≤ 4.4e-3)
- (pp − bb)/N: −1.9098 … −1.9589 (R = 6 … 200)
- Mean number of lattice points with R_b < |x − c| ≤ R at R = 200: 5.7

## Edge scaling (s = 1)
- log–log slope of |e − e_tri| vs N, R ≥ 40: −0.500
- fit with e_tri FIXED, R ≥ 20: e − e_tri = 0.6059 N^{-1/2} − 2.8230 N^{-1}, rms 3.32e-4
- alternative: e − e_tri = 0.4361 N^{-1/2} + 0.0144 N^{-1/2} log N, rms 3.63e-4 (no improvement → no evidence of a log)
- information only, free intercept: e_inf = −1.961077 (vs e_tri −1.960516), 0.7051 N^{-1/2} − 6.1745 N^{-1}

## Controls (s = 1)
- POSITIVE: |e − e_tri| = 4.860e-2 at R = 6, 1.628e-3 at R = 200; shrink ×29.9 → PASS (criteria: < 0.02 at R_max, shrink > 3)
- NEGATIVE (i) no background: e = 14.095 at R = 6, 531.357 at R = 200; predicted (8/3)R_b = 533.316; ratio 0.9963 → FIRES
- NEGATIVE (ii) background density 0.9 n on the same disk: e = −1.7517 at R = 6, 3.3743 at R = 200;
  (e − e_tri)/[(0.1)²(8/3)R_b] = 1.0003 → FIRES

## s = 0 (g = −log r)
| R | N | pp/N | pb/N | bb/N | −(N/2)(log R_b − 1/4) | e | e − e_Ewald |
|---|---|---|---|---|---|---|---|
| 6.00 | 113.2 | −87.87 | 174.51 | −87.26 | −87.25 | −0.623105 | +3.745e-2 |
| 23.11 | 1678.0 | −2425.62 | 4849.94 | −2424.97 | −2424.97 | −0.647777 | +1.278e-2 |
| 89.04 | 24906.0 | −52789.75 | 105578.19 | −52789.10 | −52789.10 | −0.656046 | +4.513e-3 |
| 200.00 | 125655.5 | −317173.03 | 634344.74 | −317172.37 | −317172.37 | −0.657710 | +2.849e-3 |
(other radii in final.log)
- POSITIVE s = 0: |e − e_Ewald| 3.745e-2 (R = 6) → 2.849e-3 (R = 200) → PASS
- log–log slope R ≥ 40: −0.420; √N (e − e_Ewald) over the 14 radii: 0.398 0.433 0.462 0.622 0.589 0.524 0.761 0.843
  0.793 0.761 0.712 0.826 0.803 1.010 (drifts upward: NOT a clean N^{-1/2}; cause not determined)

## Exact / derived (Tier C, derivations in the text; numerically checked above)
- rim potential of a uniform disk, kernel 1/r: 4nR; centre 2πnR; interior 4nR E(r/R) (E with modulus k = r/R;
  scipy `ellipe` takes m = k²).
- ∫_D∫_D |x−y|^{-1} = 16πR³/3; U_bb = 8πn²R³/3 = (8/(3√π)) n^{1/2} N^{3/2}; per particle (8/3) n R.
- ∫_D log|x−y| dy = π(r²/2 + R² log R − R²/2) (|x| = r ≤ R), πR² log|x| outside; ∫_D∫_D log|x−y| = π²R⁴(log R − 1/4).

## References verified this session (Crossref API, 2026-10-11)
- Ewald, Die Berechnung optischer und elektrostatischer Gitterpotentiale, Ann. Phys. 369(3) (1921) 253–287,
  doi:10.1002/andp.19213690304 — via https://api.crossref.org/works/10.1002/andp.19213690304
- Caffarelli, Silvestre, An extension problem related to the fractional Laplacian, Comm. PDE 32(8) (2007) 1245–1260,
  doi:10.1080/03605300600987306 — via https://api.crossref.org/works/10.1080/03605300600987306
