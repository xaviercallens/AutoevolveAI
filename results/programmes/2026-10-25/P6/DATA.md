# P6 WORK1 — published S(k) data and the diffraction test

Lane P6 (slug `superfluid_structure_factor`), stage WORK1, 2026-10-25. Everything below is real tool output
(`scripts/analysis.py` -> `results.json`, `data/*.csv`). Tiers: A kernel-checked, L cited literature, C human argument,
X floating point / read from a figure (never supports a claim by itself).

## 0. What is tested

Lean (QuantumFluids environment, `results/autoresearch/2026-10-25/H8/Autoresearch_SkBound.lean`, H8, producer-checked only):

* `sBog_le_sqrt`: for the homogeneous Bogoliubov gas, `S_B(k) = k/sqrt(k*^2+k^2) <= sqrt(k/(2k*))`, `k* = 2mc/hbar`
  (equality only at `k = k*`).
* `free_S_one_violates`: `S = 1` violates the bound for every `0 < k < 2k*` (negative control).
* `not_bogoliubov_of_structure_factor` (project `DualLength.lean`): if Feynman's bound `eps^2 <= (hbar c k^2/(k* S))^2` holds and
  `S^2 > k/(2k*)`, then the measured `eps^2` is not the Bogoliubov one.

Test applied here: a measured `S(k) > sqrt(k/(2k*))` is incompatible with `S` being the Bogoliubov structure factor of a
gas of that sound speed. A point with `S <= sqrt(k/(2k*))` is NOT thereby confirmed Bogoliubov (the bound is an upper envelope;
test power is small where the bound is far above `S_B`, e.g. low `k`).

## 1. Sources (pinned)

| id | source | what was taken | tier |
|---|---|---|---|
| D | R. J. Donnelly and C. F. Barenghi, "The observed properties of liquid helium at the saturated vapor pressure", J. Phys. Chem. Ref. Data 27, 1217 (1998); web edition ch. 14 "Structure Factor", https://pages.uoregon.edu/rjd/vapor15.htm (downloaded 2026-10-25, sha256 `b5a3bc07c0fceef753fb4168e5918c5b6cb817c5783a85d688e4906f92f304b8`; the page is (c) 2004 and its HTML is kept outside the repo in /home/callensxavier_gmail_com/programmes-2026-10-25/P6/raw/donnelly/; only the extracted numbers, `raw/parsed.json`, are in the record). The web edition is ASSUMED, not checked, to reproduce the 1998 journal Table 14.1, and the journal page of Table 14.1 is not pinned (no page number is available to this stage) | **Table 14.1** (adopted database: Q, S(Q), key; 100 rows: 49 key 1, 50 key 2, 1 key 3) and Table 14.3 (spline, 133 rows, cross-check only) | L (secondary compilation; no uncertainties printed) |
| D1 | key 1 = H. N. Robkoff and R. B. Hallock, "Structure factor measurements at saturated vapor pressure for 1.38 < T < 4.24 K", Phys. Rev. B 24, 159 (1981); X-ray, 0.213 <= Q <= 5.129 per A | via D | L |
| D2 | key 2 = E. C. Svensson, V. F. Sears, A. D. B. Woods, P. Martel, Phys. Rev. B 21, 3638 (1980) ("Neutron-diffraction study of the static structure factor and pair correlations in liquid 4He"); neutron, 0.79 <= Q <= 6.66 per A | via D. Note: D's reference list prints the year as 1989; the year 1980 is taken from Morresi and Garberoglio, arXiv:2501.08730v1, ref. [50] (read directly) | L |
| G | H. Godfrin et al., arXiv:2012.09067v1: c = 238.3 +- 0.1 m/s at SVP (Sec. II A, p.2); m4 = 4.0026032 g/mol (Sec. II A, p.3); dispersion eps(k), Table VI (p.26), T < 100 mK | k*, Feynman upper bound | L |
| SK | D. M. Stamper-Kurn et al., "Excitation of phonons in a Bose-Einstein condensate by light scattering", PRL 83, 2876 (1999), arXiv:cond-mat/9906035, **Fig. 3a** (p.3). Na, trapped, Bragg, S(q) as ratio of line strengths trapped/expanded cloud (absolute, normalised to free particles); q fixed, density varied | 3 points, values read from the figure | **X** |
| ST | J. Steinhauer, R. Ozeri, N. Katz, N. Davidson, "Excitation spectrum of a Bose-Einstein condensate", PRL 88, 120407 (2002), arXiv:cond-mat/0111438, **Fig. 4** (p.4). 87Rb, trapped, mu/h = 1.91 kHz | 13 closed + 13 open circles read from the figure | **X** |

No printed table of S(k) was found for any BEC. Ozeri et al., Rev. Mod. Phys. 77, 187 (2005): no arXiv version was found by web search and the publisher page was not attempted; it was NOT read and is not cited for any number. The published
APS abstract pages for the two He-4 primary papers also returned 403: the primary tables were NOT seen. Every He-4 number
is therefore secondary (D). Under the preregistered kill rule ("values only available from figures -> Tier X, stated"),
all BEC numbers are Tier X.

Temperatures (He-4): none is stated per point in D. Robkoff-Hallock cover 1.38-4.24 K (title). Svensson et al.'s pair
correlation data are described as taken at T = 2 K (Morresi and Garberoglio, arXiv:2501.08730v1, p.12, Fig. 2 caption and ref. [50]);
the temperature of the Svensson S(Q) points in D is assumed, not verified, to be the same. The data are therefore at
1.4-4 K, not T = 0, and some X-ray points may lie above T_lambda (2.17 K). Effect on S(0): D adopts S(0) = 0.051.

## 2. Constants

* He-4: k* = 2 m4 c/hbar = **3.00379 per A** (range 3.0025-3.0051 for c = 238.3 +- 0.1 m/s; hbar^2/2m = 0.52218 meV A^2; hbar c = 1.5685 meV A, `results.json`). Reproduces the 3.00379 of `papers/ar_bogoliubov_sk/data/helium_tier_l.json`.
* Na-23 (SK): m = 22.98976928 u; q fixed by hbar q^2/(2m) = h x 1.38 kHz (SK Fig. 3 caption) -> q = 2.506 per um (consistent with the paper's q^-1 = 0.4 um). 87Rb (ST): m = 86.909180527 u. (Standard atomic masses, not literature data points.)
* SK mu/h axis: read from the bottom axis of Fig. 3b (0, 5, 10 kHz ticks, `raw/skfig3b_axis.png`); cross-check: c_s at mu/h = 6.7 kHz computed 10.78 mm/s vs the paper's "11 mm/s" (p.3).

## 3. He-4 result (Tier L data, Tier X arithmetic)

Test on the 99 Table 14.1 points with Q > 0 (`data/test_he4.csv`; the Table 14.3 spline is only a cross-check:
rms deviation of the 99 points from the spline 0.0189).

Uncertainties. Table 14.1 prints none; none were invented. Two scales are reported instead:
* k* error from c = 238.3 +- 0.1 m/s: bound changes by 0.02 % (columns `bound_c_minus/plus`).
* Dataset disagreement `Delta_ds = |max S(key1) - max S(key2)| = |1.458 (Q=2.058) - 1.376 (Q=2.070)| = 0.082`. D itself says the authors "are unable to explain the discrepancy ... in the region of the peak". This is a table-derived proxy for a systematic error, not a published error bar.

The REFUTED/UNDECIDED threshold `Delta_ds` is defined in this stage; it is not in the preregistration.

Verdict per point: CONSISTENT if `S <= bound`; REFUTED if `S - bound > Delta_ds`; UNDECIDED if `0 < S - bound <= Delta_ds`.

| quantity | value |
|---|---|
| counts | 29 CONSISTENT, 7 UNDECIDED, **63 REFUTED** (32 X-ray, 31 neutron) |
| onset (nominal `S > bound`) | last consistent point Q = 1.400 (S = 0.464 vs bound 0.483, key 2); first exceeding point Q = 1.470 (S = 0.532 vs 0.495, key 2). So the onset lies in **(1.40, 1.47] per A**, `k/k*` about 0.47-0.49 |
| strict refuted run (`S - bound > 0.082`) | contiguous from Q = 1.55 (S = 0.624 vs 0.508, margin 0.116) to Q = 5.129 (S = 1.007 vs 0.924, margin 0.083) |
| nominal exceeding run | Q = 1.47 to 5.94 (the upper end approaches 2k* = 6.008, where the bound reaches 1) |
| roton/peak region 1.7 <= Q <= 2.4 (21 points) | **all REFUTED**; S/bound between 1.62 and 2.49; smallest margin 0.328; e.g. Q = 2.058: S = 1.458 vs bound 0.585 (ratio 2.49), Q = 2.000: S = 1.371 vs 0.577 (key 2, ratio 2.38) |
| beyond the peak (Q = 3-5.2) | S about 0.95-1.03 vs bound 0.71-0.93 (e.g. Q = 3.0: 0.952 vs 0.707; Q = 4.0: 1.012 vs 0.816): refuted, but this is the same kind of failure as the S = 1 negative control (S about 1 = free-particle-like at k < 2k*), not roton physics |
| undecided near 2k* | Q = 5.18-5.94: margins 0.077-0.011 (< Delta_ds) -> UNDECIDED; Q >= 6.13: bound >= 1 -> CONSISTENT (vacuous: for k > 2k* the bound exceeds the free value 1) |
| low k (0.213 <= Q < 1.4) | all CONSISTENT, but with no test power: e.g. Q = 0.213: S = 0.081 vs bound 0.188 (S_B = 0.0707) |

Second prong (Lean `not_bogoliubov_of_structure_factor`, uses Feynman's bound): measured eps(k) (Godfrin Table VI) is far below the Bogoliubov
eps_B for the same c at every exceeding point with `0.05 <= Q <= 3.6` (e.g. Q = 1.47: 1.060 vs 2.567 meV; Q = 3.57: 1.544 vs 8.697 meV).

Feynman consistency check of the data themselves (S <= eps0/eps, conservative eps - err, 68 points with 0.05 <= Q <= 3.6): 2 points exceed it, Q = 0.213 and Q = 0.267
(S = 0.081, 0.091 vs S_up = 0.0684, 0.0850). Both are key 1 (X-ray). Consistent with thermal S at T >= 1.38 K but not proven to be (no per-point temperatures); reported, not dropped. Every other point satisfies the bound.

Caveat on the physical reading: Bogoliubov theory requires k a << 1 (not satisfied for He-4 at Q >= 1); the test does not need that: it only says that the measured S is not the S of any Bogoliubov gas with He-4's sound speed. Temperature: the table values are at 1.4-4 K; the roton-region margin is a factor 1.62-2.49 (the table's own two datasets differ by 0.082, i.e. 6 %). A T-dependence of the S peak large enough to remove a factor 1.6 was not quantified here and no source for it was checked; the claim "refuted in the roton region" is therefore conditional on S(k_peak, T -> 0) being of the order of the 1.4-4 K values.

### He-4 controls (all executed)
* Positive: synthetic homogeneous Bogoliubov `S_B(Q)` at the 99 abscissae: 0 violations, max `S/bound` = 0.9999996. With Gaussian noise sigma = 0.01 / 0.02 / 0.04 the fraction of 2000 trials that produce any REFUTED point under the strict criterion is 0 / 0.0005 / 0.41 (so the strict criterion has essentially no false positives for noise up to 0.02; at 0.04 it does). The measured rms scatter of the 99 points about the Donnelly spline is 0.019, i.e. the regime where the false-positive rate was 0.0005.
* Negative: free `S = 1`: 95 of 99 points exceed the bound, exactly the 95 with `Q < 2k*` (strict: 89).
* Sensitivity: planted `1.5 S_B` is flagged at 89 points (strict 81).
* Transcription: two independent parses of the HTML (regex over stripped text; `html.parser` node walk) give identical 300 numbers for Table 14.1 and 266 for Table 14.3; Table 14.1 is 100 triples with monotone Q in both columns; Table 14.3 is a uniform 0.05 grid 0-6.6 (133 rows); first-parse spot checks vs the printed page: (2.058, 1.458, key 1), (2.070, 1.376, key 2), (1.470, 0.532, key 2).

## 4. BEC result (Tier X; illustrative only)

Both BEC experiments are trapped clouds analysed in the local density approximation (LDA), so the homogeneous bound
cannot be applied with a single k*. For Thomas-Fermi clouds the correct statement, implied pointwise by `sBog_le_sqrt`, is
`S_LDA(q) = <S_B(q; n)> <= <sqrt(q/(2k*(n)))> =: B_LDA`, with the atom weight `w(x) = (15/4) x sqrt(1-x)`, `x = n/n0`, `k*(x) = k*_peak sqrt(x)`.

Trapped-gas positive control (this decided the convention): on 24 values of mu/h in 0.5-12 kHz at the Stamper-Kurn q,
the trapped Bogoliubov model `S_LDA` exceeds the bound built from a single k* in **16/24** cases (k* from peak c = sqrt(mu/m)),
**4/24** (mean-density c = sqrt(4/7) sqrt(mu/m)), **8/24** (c_eff = 0.68 sqrt(mu/m)), and in **0/24** for the LDA-averaged bound.
So only `B_LDA` is a valid trapped-gas comparator; single-k* bounds fail their own positive control. Model checks: the
trap-average reproduces the closed form `15 pi/32 sqrt(hbar omega_q/2mu)` in the phonon limit (relative difference 1.0e-6 at e0/mu = 1e-6, 1.0e-4 at e0/mu = 1e-4, as expected for the next-order correction) and
reproduces the solid curve of SK Fig. 3a at six columns to |diff| <= 0.0022 (`results.json: solid_curve_control`), which also validates the q, mu and mass inputs.
Grid control (6 mu x 7 q, Rb): 0 violations of `S_LDA <= B_LDA`; `S = 1` exceeds `B_LDA` at 38/42 grid points (negative control).

### 4.1 Stamper-Kurn et al. 1999, Fig. 3a (the only BEC set with absolute normalisation; Tier X)
q = 2.506 per um fixed; digitised x position -> mu/h from the Fig. 3b axis; sigma = half the plotted vertical error bar:

| peak n (1e14 /cm^3) | mu/h (kHz) | S | sigma | S_LDA model | B_LDA | z = (S - B_LDA)/sigma | q/k*_peak |
|---|---|---|---|---|---|---|---|
| 2.03 | 3.08 | 0.541 | 0.129 | 0.552 | 0.583 | -0.33 | 0.47 |
| 4.44 | 6.72 | 0.379 | 0.091 | 0.415 | 0.480 | -1.10 | 0.32 |
| 6.15 | 9.30 | 0.293 | 0.071 | 0.363 | 0.442 | -2.09 | 0.27 |

All three points lie below `B_LDA` (and below the LDA model within 1 sigma): **no refutation of trapped Bogoliubov**.
Test power is low: the model sits at 0.82-0.95 of `B_LDA`, and a point would need `S > B_LDA` (0.44-0.58) to refute; with these 1 sigma bars (0.07-0.13) a refutation needs S roughly 1 sigma above the bound
(0.71, 0.57, 0.51). Three points read off a figure, 1 sigma bars: this does not establish "BEC consistent"; it only shows the data do not contradict the LDA-averaged bound.
Note: the peak-k* bound would have excluded the first point only if the (invalid) single-k* comparator were used (S = 0.541 vs 0.486 at point 1).

### 4.2 Steinhauer et al. 2002, Fig. 4 (87Rb, mu/h = 1.91 kHz; Tier X)
* Closed circles: the authors state the plotted values are the measured S(k) **multiplied by 2.3** to give "rough agreement" with the Bogoliubov-LDA curve (p.4, text and Fig. 4 caption). The absolute scale is thus fitted to the hypothesis; a test on them is circular. Recorded for completeness: 3 of 13 exceed `B_LDA` nominally (k = 4.18, 6.81, 10.36 per um), none by more than 0.32 sigma; un-rescaled (S/2.3) none exceeds it and all are 3-26 sigma below it, i.e. the unresolved normalisation factor dominates. **Not decisive in either direction.**
* Open circles: `eps0/omega(k)` computed from the measured dispersion via Feynman's relation (Eq. 2 of the paper); a re-expression of the excitation spectrum, not a diffraction value. They follow the LDA model (rms difference 0.026, max 0.059 for 13 points, digitisation plus model) and none exceeds `B_LDA`. Same logic as the He-4 second prong, not an independent diffraction test.
* Related caveat found in the earlier lane: Shammass et al. (arXiv:1207.3440) also rescale their amplitude by a factor 1.5 (excerpt kept in `papers/ar_bogoliubov_sk/ledger/sources/`). Two of the three BEC sources examined here rescale their amplitude to theory (x2.3 Steinhauer, x1.5 Shammass, the latter a phonon-imprinting experiment, not Bragg spectroscopy); only Stamper-Kurn's ratio to the expanded cloud is absolute.

## 5. Bottom line for WORK1

1. He-4 (Tier L data, secondary, T = 1.4-4 K, no printed error bars): the diffraction test fires. The Bogoliubov bound with k* = 3.0038 per A is exceeded by S in the peak region (1.7-2.4 per A) by a factor 1.6-2.5, far outside the 0.082 inter-dataset spread. Onset bracket (1.40, 1.47] per A; strict refutation from 1.55 per A.
2. BEC (Tier X, 3 absolute points + 13 rescaled points): the data do not contradict the LDA-averaged bound; the test has little power there; no "BEC consistent" finding is claimed.
3. Primary He-4 tables were not seen (APS 403); the Donnelly-Barenghi values should be re-checked against PRB 21, 3638 and PRB 24, 159 before any publication statement (pinned as WORK2/audit item).
4. Anything resting on `sBog_le_sqrt` is conditional on H8's producer-only kernel check (independent recompile pending).

Files: `data/he4_Sk_donnelly_table14_1.csv` (provenance per row), `data/he4_Sk_spline_donnelly_table14_3.csv`, `data/test_he4.csv`,
`data/bec_stamper_kurn_fig3a_tierX.csv`, `data/bec_steinhauer_fig4_tierX.csv`, `data/bec_model_curve_stamper_kurn_q.csv`, `results.json`, `scripts/`, `raw/`.
Digitisation: pixel centroids with axis calibration from detected ticks (`scripts/digitize_*.py`); accuracy about 0.01 in S, 0.1 per um in k for ST; SK read-offs: marker centroid to about 1 px (0.002 in S), error-bar ends from the dark-pixel extent.
