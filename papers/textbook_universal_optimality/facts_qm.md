# facts_qm.md — provenance of every number in `sec_quantum_melting.tex`

All computed numbers come from ONE command (2 cores, 31.9 s wall, run 2026-10-11):

```
taskset -c 6,7 /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I \
  /home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/papers/textbook_universal_optimality/code/quantum_melting.py \
  /home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/papers/textbook_universal_optimality/figures_v2/qm_phonons_lindemann.pdf
```

Its full output is pasted verbatim into the numbox of the section (and saved in the scratch file
`/home/callensxavier_gmail_com/.claude/jobs/6ecda88c/tmp/qm/final.txt`). It also writes the figure
`figures_v2/qm_phonons_lindemann.pdf`.

## Computed (Tier X), reduced units e = m = hbar = 1, lengths in a_ws (pi a_ws^2 n = 1)

| quantity | value | output line |
|---|---|---|
| a / a_ws (nearest-neighbour spacing) | 1.904626 = sqrt(2 pi/sqrt 3) | `RESULT <|u|^2> ... (a/a_ws = 1.904626)` |
| P1 alpha-invariance of D(k) | 7.77e-16 (alpha 0.6), 1.55e-15 (alpha 1.6) | `== P1` block |
| P2 trace sum rule, Ewald vs direct (R<=400) | 1.285203/1.285203, 1.224116/1.224116, 1.300996/1.300997 | `== P2` block |
| P3 omega_L^2/k at k = 1e-2,1e-3,1e-4 | 1.993087, 1.999309, 1.999931 (limit 2 pi n = 2) | `== P3` block |
| transverse sound speed c_T | 0.371837 (units (e^2/m a_ws)^(1/2)) | `== P3` block |
| <sum omega> on m = 12..384 | 1.6276631027 ... 1.6273718805; order p = 2.52; Richardson 1.62737183 | grid table |
| <sum 1/omega> on m = 12..384 | 3.5780591325 ... 3.6608965985; order p = 1.01; Richardson 3.66348284 | grid table |
| <sum 1/omega^2> on m = 12..384 | 12.91144858 ... 25.46035918 (+~2.51 per doubling) | grid table |
| c_zp | 0.813686 Ha = 1.627372 Ry (E_zp = c_zp r_s^-3/2) | `RESULT c_zp` |
| C_ws | 1.831741 (<|u|^2> = C_ws a_ws^2 r_s^-1/2) | `RESULT <|u|^2>` |
| C | 0.504946 (<|u|^2>/a^2 = C r_s^-1/2) | `RESULT <|u|^2>` |
| N1 slope d<sum 1/w^2>/d ln m (192->384) | 3.61701 vs predicted 1/(2 c_T^2) = 3.61630 | `== N1` |
| N2 (q = -k term dropped) imaginary fraction, 48x48 | 0.064; min omega^2 = -0.0417; omega^2 at k=1e-3: 1.383e-07, 4.371e-07 | `== N2` |
| Lindemann r_s* = (C/gamma_c^2)^2 | 0.20:159.4, 0.22:108.8, 0.24:76.9, 0.26:55.8, 0.28:41.5, 0.30:31.5, 0.33:21.5, 0.36:15.2, 0.40:10.0 | `== Lindemann` |
| harmonic gamma at r_s = 31, 37 | 0.3011, 0.2881 | `harmonic gamma at` |
| relative displacement averages (m=384) | classical 5.40153469, quantum 2.85594296 | `== Relative` table |
| classical gamma_rel^2 | 2.978022/Gamma; at Gamma = 137: gamma_rel = 0.1474 | `classical gamma_rel^2` |
| quantum gamma_rel^2 | 0.787282 r_s^-1/2; at r_s = 31: 0.3760 | `quantum (T=0) gamma_rel^2` |
| exciton CM sign scan | 0/275 negative for d^2 = 1/10, 1, 10; Lennard-Jones control 123/275 negative, first at (r=0, t=1.778) | `== Exciton` |

Derived in the text by hand from the above (no extra command): 0.9^-4 = 1.52, 1.1^-4 = 0.68; ratio 0.376/0.147 = 2.5;
m=24 error of <sum 1/w> vs Richardson: (3.66348-3.62128)/3.66348 = 1.15%; m=384 vs Richardson 7.1e-4 relative;
<sum w> change 192->384: 2.2e-7.

## Literature (Tier L) — source and location

LITERATURE_PLACEHOLDER
