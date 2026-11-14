# K2 independent audit (producer != verifier)

Auditor: Claude Opus 5.5 (separate session from the producer, Claude Sonnet 5.5). Date 2026-10-31. Auditor code and
outputs are in `/tmp/k2audit/` (scratch, not committed): `model.py` (50-digit point model), `encl.py` (rigorous 4-D
enclosure check), `encl9.py` (9-D attempt), `t1.py`-`t5.py` (point checks, PyCO2SYS, omitted terms), `lean_audit.py`.
No producer code was imported for the numerics. All heavy work ran under `taskset -c 6,7`.

**Verdict: ACCEPT_WITH_CORRECTIONS.** Every numerical claim of part (a) that I could test holds under my own
implementation. The Lean gates pass on recompilation. The Jessen inconsistency is real. The corrections fix one
substantive misreading of U1/U2, one Lean-scope overstatement, rounding, omitted-term quantification, and wording.

## 1. Model and closed form (re-derived)

DIC = C(1 + K1/h + K1K2/h^2), TA = C(K1/h + 2K1K2/h^2) + BT KB/(KB+h) + KW/h - h, C = K0 fCO2. At fixed fCO2
(C fixed), eta = (dDIC/dh)/(dTA/dh) = C(K1/h^2 + 2K1K2/h^3) / [C(K1/h^2 + 4K1K2/h^3) + BT KB/(KB+h)^2 + KW/h^2 + 1].
This is the producer's N/D and, multiplied by h^3/(C K1), their `(h+2K2)/((h+4K2) + h^3 R/(C K1))`. Checks:
- 50-digit closed form against a numerical derivative of DIC(TA) at 3 points (incl. both extreme corners): agreement 5e-9.
  The limit is my mp.diff step, not the closed form. The producer's P2 (1.3e-16) is consistent with this.
- I differentiated N and D by hand: N' = -A(2h+6K2), D' = -A(2h+12K2) - 2RB/(KB+h) - 2RW/h with A = C K1/h^4. These
  match the hand-supplied expressions in `eta_deriv_identity`, so the monotonicity test `2CK1K2/h^2 > |Q|` is a correct
  sufficient condition for d eta/dh > 0.

## 2. Enclosures: independent rigorous check

My method differs from the producer's in three places:
- constants are enclosed by a mean-value (centred) form, with analytic T and S derivatives in intervals (derivatives
  checked against mp.diff to 1e-30);
- h is bracketed by monotonicity of the root in each constant (TA(h) increases in C, K1, K2, BT, KB, KW and decreases
  in h), and the bracket is verified by an interval sign test over the whole cell;
- eta is a plain interval evaluation of 1/(1+g) on 4 h-pieces, with adaptive bisection until each cell's enclosure
  lies inside the target.

The TA interval per cell is widened by a relative 1e-12 outward, to cover float rounding of S/35*TA35. All rows
below are from the re-run with this widening.

Library caveat: python-flint/Arb is not installed, so I also used `mpmath.iv` at 30 digits. The implementation is
independent, but the interval library is the same one the producer used.

| Target (claimed) | Result | Cells | Union of cell enclosures |
|---|---|---|---|
| U0 [0.7036, 0.9557] | every cell inside | 223 | [0.70390, 0.95563] |
| U1 [0.6826, 0.9618] | every cell inside | 167 | [0.68333, 0.96155] |
| U2 [0.6616, 0.9676] | every cell inside | 140 | [0.66166, 0.96494] |
| U0 tighter [0.7410, 0.9455] (auditor) | every cell inside | 3039 | [0.74100, 0.94550] |
| U0 [0.7425, 0.9445] | 101 corner cells unresolved at depth 30 | | (interval dependency) |

So all three enclosures are sound (every point of the box lies inside them). U0 is loose, and a certified
[0.7410, 0.9455] is available.

Sharp side (U0): at the corners I get eta(0 C, S 30, 560 uatm, TA35 2200) = 0.944283244396 and eta(30 C, S 38,
280 uatm, TA35 2400) = 0.742707543316 (50 digits). The producer's rigorous one-sided point bounds in the JSON (0.94428324396 <= max,
0.74270754847 >= min) are consistent with these. The rounded RESULT.md wording **does not follow** from them:
- "a value >= 0.9443 somewhere": the rigorous point bound is 0.944283 < 0.9443;
- "a value <= 0.7427 somewhere": the point bound is 0.7427075 > 0.7427.

Both are rounding-direction slips. My corner and grid values (Tier X) suggest that both rounded statements are in fact
slightly false, but I did not certify a global bound tight enough to refute them (my tightest certified enclosure is
[0.7410, 0.9455]). Correction 1 fixes the wording. Corners
and a 7^4 interior grid give the same range [0.742708, 0.944283]. The finite-difference signs on a 5^4 grid are
uniform: eta decreases with T, S and TA35 and increases with fCO2. This is Tier X support for the "monotone trends"
claim and for the corner choice in the producer's B&B. It is not a certificate.

Producer B&B pruning: I re-read `run_seawater.bb`. A cell is discarded only if its rigorous bound is beaten by a
rigorous point bound, and the reported bound is the extreme over all live cells. That is sound. Two notes:
- both U0 runs stopped at the evaluation cap (3000) with 1300 live cells, not at convergence, which explains the
  looseness;
- `k2lib.eta_box` converts interval endpoints with `float()` (round to nearest, not outward). The error is at most
  1 ulp and does not affect any reported digit.

**U1/U2 misreading.** The U1/U2 enclosures are much wider than the attained ranges. At the two extreme corners, over
all 32 sign combinations of +-1 sigma (+-2 sigma) on (pK0, pK1, pK2, pKB, pKW), I get attained eta ranges of
[0.73743, 0.94675] for U1 and [0.73219, 0.94913] for U2. The extra lower-end width of the producer's U1/U2 enclosures
(0.021 and 0.042) is therefore mostly interval overestimation: the pK intervals are never subdivided. It is not the
effect of the pK uncertainty. The real effect is about 0.005 (1 sigma) and 0.010 (2 sigma) at the bottom. That figure
is Tier X: point values, and I did not prove that the extremes sit at corners. I could not certify a tight U1/U2,
because a 9-D adaptive run with the pK offsets as extra dimensions did not finish in 10 min.

## 3. Constants

- Primary papers: **none read**. What I actually tried:
  - Lueker 2000: ScienceDirect returned HTTP 403. The eScholarship hit was an unrelated 2025 Scripps technical report.
  - Weiss 1974: web search found an unofficial copy on a UCSD server, but the fetch failed (connection refused).
  - Dickson 1990: one search found no open copy.
  - Millero 1995, Uppstrom 1974 and Millero 1979: not searched.

  All constants therefore remain unverified against primary text.
- Guide transcription: I typed eqs (30), (37), (40), (43) and (62) myself from `guide.txt`. They agree term by term
  with `k2lib._logs`, and with the producer's regrouping of ln KB in powers of sqrt(S), which I expanded and checked.
  My values at S 35, 25 C are ln K0 -3.561652, log10 K1 -5.8471529, log10 K2 -8.9659515, ln KB -19.796402 and
  ln KW -30.433844. They reproduce all 5 printed check values.
- Second package: none is installed (`pip list` shows no mocsy, seacarb or other CO2SYS port). My 50-digit
  `model.py` (constants typed from the Guide, own root solver and closed form) is the independent implementation.
- PyCO2SYS 1.8.3.4 cross-check (my 202 points, seed 777, incl. both extreme corners; central difference +-0.01 umol/kg):
  - worst relative difference 4.4e-5 with sulfate = fluoride = 0;
  - 1.4e-10 when PyCO2SYS is fed my KW and BT.
  This confirms the producer's explanation: the only differences are KW (the Guide subtracts 0.015 from the constant;
  Guide footnote 5 calls this an approximate SWS to total conversion; PyCO2SYS uses 148.9802 and converts) and BT
  (0.000416 vs 0.0004157).
- Effect on eta at the extreme corners: KW constant +0.015 changes eta by -4.6e-5 and -2.1e-6; BT 0.0004157 by +1.3e-5
  and +7.8e-6; **Lee et al. 2010 BT (0.0004326 S/35) by -7.2e-4 and -4.3e-4**. The producer said the last was not
  computed.
- U1/U2 sigma values (0.002, 0.0075, 0.015, 0.01, 0.01) match `PyCO2SYS.uncertainty.pKs_OEDG18`. That is still a
  secondary source.
- Freshwater (b): the K1, K2 coefficients (290.9097/-14554.21/-45.0575 and 207.6548/-11843.79/-33.6485) match
  PyCO2SYS `p1atm.py` lines 451-453 and give pK1 6.351 and pK2 10.329 at 25 C (standard values). The Millero 1979
  primary was not read. **Issue:** part (b) evaluates the seawater KW expression (with its -0.015 total-scale shift)
  at S = 0, where the shift means nothing; KW should be about 1.5% larger. This is negligible below pH 6 but should
  be stated. My closed-form estimate h^2 = C K1 puts eta = 0.5 at pH 5.60 (25 C) and 5.54 (0 C). This is inside the
  producer's 5.5-5.7. Part (b) stays Tier X.

## 4. Omitted terms (auditor, PyCO2SYS, 202 points)

- Sulfate + fluoride: eta changes by +2e-6 to +7.2e-5. The producer's "at most 6.8e-5" is a 100-sample maximum.
  Because h is on the total scale, -h already stands for -[H+]_F - [HSO4-]. The real omissions are HF and the
  KW/KB scale conversions.
- Phosphate 2 + silicate 100 umol/kg: eta changes by -4.1e-4 to -1.5e-3. With phosphate 3, silicate 150 and S/F:
  -6.1e-4 to -2.2e-3. Even then the result stays inside the U0 enclosure (min 0.7427 - 0.0022 = 0.7405 > 0.7036),
  but the producer did not quantify this.
- Organic alkalinity: not bounded; unbounded in principle for coastal waters. Pressure: surface, 1 atm only. Fugacity
  coefficient: none, because fCO2 is the input. The result is model-conditional, and RESULT.md states the scale (total)
  and TA definition. The nutrient numbers should be added.

## 5. Lean (pinned 4.34.1 via `lean_pinned.lean_path()`, oleans to `/tmp/k2audit/olean`)

- `Core.lean`: rc 0 (102 s), 14 theorems; each `#print axioms` gives exactly [propext, Classical.choice, Quot.sound].
- Escape grep: no sorry, admit, native_decide, axiom, unsafe, implemented_by, extern, opaque, set_option, macro, elab
  or csimp hits.
- `leanchecker Programmes.CarbonateK2.Core`: rc 0 (64 s).
- `Controls.lean`: rc 0 (compiles), but the axiom output shows `sorryAx` and `CarbonateK2.ctl_cheat`, so both are
  caught.

What the theorems say:
- exact algebra for positive reals: the N/D rewrite, 0 < eta < 1, and the derivative identity with hand-given
  expressions for N' and D' (no `HasDerivAt`, so Lean does not prove these are derivatives);
- Q <= 0;
- delay monotonicity;
- rational Jessen instances.

Lean does not touch the transcendental constants, the h root or the enclosures. Statement locks: no
`tools/statement_lock.py` exists in this repo, and no file outside K2 mentions `CarbonateK2`, so no statement lock
exists for `Core.lean`.

## 6. Jessen reproduction (read `jessen.pdf` text, Supplementary Text 2)

The inputs are as printed: Δβ = (0.55-0.2)+(0.12-0.03) = 0.44, ε 0.3, ρ 2.65, ε_w 0.1, dc 0.80 meq/L, v 5 m/yr.
They give dq = 45.71 and 130.59 meq/L, R = 58.13 and 164.24, v = 8.60 and 3.04 cm/yr, and 11.6 to 32.8 yr/m.

The printed dq (45.4, 131.3) cannot both follow from the printed inputs. The dq ratio is 0.3458, but dq must be
proportional to CEC, which gives 0.56/1.6 = 0.35. The producer's claim is confirmed. The printed R = 58 and 165 and
v = 8.7 cm/yr follow from the printed dq (1+45.4/0.8 = 57.75 gives 8.66 cm/yr). The printed "12-34 yr/m" upper value
is not reproduced: 32.8 from the inputs, and 33.3 even from the printed 3.0 cm/yr. The delay closed form
T = (L/q)(ε_w + k CEC), with k = 10Δβ(1-ε)ρ/dc, equals L R/v with v = q/ε_w (checked by hand and by `delay_via_R`).

## 7. Wording, novelty, licence

- Sections 6/7 of the proposal: RESULT.md disclaims tonnes, climate effect, ecological safety and deployment advocacy
  (line 5 and `not_claimed`). I found no violating sentence. The title and commit phrase "CO2 uptake" is acceptable,
  but "equilibrium DIC increase" is more exact.
- Novelty: the wording is "to our knowledge, eta of about 0.8 ... long known; the only addition is an enclosure ...
  and a monotone closed form". This is appropriately modest. The closed form itself is textbook-level (a ratio of
  buffer derivatives). Literature was not searched by producer or auditor.
- PyCO2SYS licence: GPL-3 (confirmed in its METADATA). It is used only, not redistributed. Non-blocking note: the
  scripts that import it live in an MIT-licensed repo.
- `prereg_K2.json` sha256 = 24b99955...50000 (verified). It was committed in the same commit as the results (e0fbdba),
  so "written before any attempt" cannot be verified from git. All 28 file hashes in `result.json` match.

## Corrections (exact old -> new, RESULT.md unless noted)

1. "U0 (constants exactly as printed): eta in **[0.7036, 0.9557]**" -> "U0 (constants exactly as printed): eta in **[0.7036, 0.9557]**. This is the producer's certificate [0.703565, 0.955707] rounded inward; the rounded interval itself is certified by the independent auditor check, which also certifies the tighter [0.7410, 0.9455]". (Alternatively, round outward to [0.7035, 0.9558].) Also "the true range contains a value >= 0.9443 and a value <= 0.7427" -> "the true range contains a value >= 0.94428 and a value <= 0.74271", and "overshoots by at most 0.0114 above and 0.039 below (U0)" -> "overshoots by at most 0.0115 above and 0.0392 below (U0)".
2. "Uncertainty of the dissociation constants (pK1 +-0.0075, pK2 +-0.015 per sigma) widens the lower end by about 0.02 (1 sigma) and 0.04 (2 sigma)." -> "The U1/U2 enclosures are wider than U0 by about 0.02/0.04 at the lower end, but this is mostly interval overestimation (the pK intervals are not subdivided). Point values at the extreme corners over all +-1 sigma (+-2 sigma) pK sign combinations give [0.7374, 0.9468] ([0.7322, 0.9491]), i.e. the pK uncertainty moves the attained range by about 0.005 (0.010) at the bottom (Tier X, auditor)."
3. "on each piece where an interval test certifies d eta/dh > 0 (the identity of `eta_deriv_identity` in Lean gives the sign test)" -> "on each piece where an interval test certifies d eta/dh > 0 (Lean proves the algebraic identity N'D - ND' = A(2Ah^2K2 + Q) for hand-supplied N', D'; that these are the h-derivatives was checked by hand, not in Lean)".
4. Caveat 4 "Sulfate/fluoride omitted: effect on eta at most 6.8e-5 (Tier X, 100 points, PyCO2SYS). Boron: the Lee et al. 2010 alternative (+4% BT) not computed." -> "Sulfate/fluoride omitted: effect on eta up to 7.2e-5 over 202 sampled points (Tier X, PyCO2SYS; with total-scale h the HSO4- term is already contained in -h). Phosphate 2 and silicate 100 umol/kg lower eta by 0.0004-0.0015 (up to 0.0022 at 3/150). Lee et al. 2010 boron lowers eta by 0.0004-0.0007 at the extreme corners. Organic alkalinity and pressure are not bounded; surface, 1 atm."
5. Method, add after the branch-and-bound sentence: "Both runs stopped at the evaluation cap (3000 evaluations, about 1300 live cells), so the bounds are sound but not tight."
6. P4 row: "11.6 to 32.8 yr/m (printed 12 to 34) ... so P4 is a pass within printed rounding, not to the digit as preregistered." -> "... R and v pass within printed rounding; the printed yr/m upper value 34 is not reproduced (32.8 from the printed inputs, 33.3 from the printed 3.0 cm/yr). P4 is a partial pass, not to the digit as preregistered."
7. Caveat 2, append: "KW in (b) is the seawater expression at S = 0 including the Guide's -0.015 total-scale shift, which does not apply in fresh water (KW about 1.5% low; negligible below pH 6)."
8. Caveat 6, append: "U2 should be re-run with the current code so that the archived hash matches; an independent auditor check confirms the U2 enclosure regardless."
9. Opening paragraph: "was written and hashed before any attempt" -> "was written and hashed before any attempt (by producer statement; it was committed together with the results in e0fbdba, so git cannot confirm the order)".
10. Reading of (a), "larger when cold, low-salinity-alkalinity and high-pCO2 (lower pH)" -> append "(numerical observation on grids, Tier X; not certified)".

## What remains unverified

- Primary-paper coefficients for all constants (see section 3 for what was attempted); verified only against the
  Guide transcription and PyCO2SYS.
- A tight certified U1/U2 range: the attained ranges above are point values.
- Interval-library independence: both producer and auditor use mpmath.iv.
- Statement locks for `Core.lean`: none exist.
- The Jessen PHREEQC/Dataverse model.
- Literature novelty.
- Freshwater activity corrections.
