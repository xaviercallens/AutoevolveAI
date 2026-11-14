# K2: certified CO2 uptake per unit alkalinity (eta) and alkalinity-front delay

Outcome: **PARTIAL** (producer, unaudited). Preregistration `prereg_K2.json` (sha256 in `prereg_K2.sha256`) was written and hashed before any attempt; the parent `preregistration.json` is unchanged (sha256 7f7d5ac1...5b438).

This is equilibrium thermodynamics of a model. It says nothing about tonnes of CO2 removed, climate effect, ecological or biogeochemical safety, or whether anyone should deploy ocean alkalinity enhancement (OAE) or enhanced weathering (EW).

## Question and answer

eta = (dDIC/dTA) at fixed fCO2, carbonate + borate + water alkalinity, total pH scale.

| Part | Result | Tier |
|---|---|---|
| (a) seawater, T in [0,30] C, S in [30,38], fCO2 in [280,560] uatm, TA = (S/35) TA35, TA35 in [2200,2400] umol/kg | U0 (constants exactly as printed): eta in **[0.7036, 0.9557]**. U1 (pK +-1 sigma): [0.6826, 0.9618]. U2 (+-2 sigma): [0.6616, 0.9676]. Sharp side: the true range contains a value >= 0.9443 and a value <= 0.7427 (rigorous one-sided point bounds), so the outer enclosure overshoots by at most 0.0114 above and 0.039 below (U0). eta is strictly between 0 and 1 (Lean). | **C** (given the pinned constants; not replayed in Lean) |
| (b) dilute / soil water: pH below which eta is small | eta < 0.01 below pH about 4.5 to 4.7, eta < 0.1 below about 5.0 to 5.2, eta = 0.5 at about 5.5 to 5.7, for fCO2 = 420 uatm and 0 to 30 C (outer pH intervals of width 0.11, see `data/soil_result.json`); at fCO2 = 10 000 uatm every threshold is about 0.7 pH lower. Closed-form reading: eta is about [HCO3-]/([HCO3-]+h) in this regime. | **X** (freshwater K1, K2 not pinned to a primary source) |
| (c) front delay | T(CEC, L, q) = (L/q)(eps_w + k CEC), k = 10 dbeta (1-eps) rho/dc. Monotone: increasing in CEC, L, k, decreasing in q (Lean). With Jessen's printed inputs: R = 58.13 (CEC 0.56) and 164.24 (CEC 1.6), i.e. 11.6 to 32.8 yr per metre. Table of yr/m over CEC and flux in `data/delay_result.json`. | **A** (monotonicity, rational instance); numbers C |

Reading of (a): per mole of alkalinity added, about 0.70 to 0.96 mol of DIC is taken up at equilibrium with the atmosphere over this box, larger when cold, low-salinity-alkalinity and high-pCO2 (lower pH). Uncertainty of the dissociation constants (pK1 +-0.0075, pK2 +-0.015 per sigma) widens the lower end by about 0.02 (1 sigma) and 0.04 (2 sigma). eta of about 0.8 at 25 C is, to our knowledge, long known (e.g. Zeebe and Wolf-Gladrow 2001; Renforth and Henderson 2017; OAE efficiency studies, not re-read here). The only addition is an enclosure with stated constants and a monotone closed form. A finite addition dTA has efficiency equal to a mean of eta over the segment (mean value theorem), hence lies in the enclosure if the segment lies in the box.

## Method

- Closed form eta = (h+2K2) / ((h+4K2) + h^3 R/(C K1)), C = K0 fCO2, R = BT KB/(KB+h)^2 + KW/h^2 + 1. Lean proves this equals N/D and 0 < eta < 1.
- h solves TA(h) = TA; TA(h) is strictly decreasing, so h is bracketed rigorously (interval sign test at both ends, bisection tightening, `mpmath.iv`, 30 digits). The bracket is split into 24 pieces; on each piece where an interval test certifies d eta/dh > 0 (the identity of `eta_deriv_identity` in Lean gives the sign test), eta is evaluated at the two ends only.
- Global enclosure by branch-and-bound over (T, S, fCO2, TA35): upper bound = largest live-cell upper bound once every other cell is pruned against a rigorous point lower bound; lower bound symmetric. Constants per cell are enclosed by hulls over 24 x 6 sub-intervals (reduces interval dependency).
- Constants: Weiss 1974 (K0), Lueker et al. 2000 (K1, K2), Dickson 1990 (KB), Millero 1995 (KW), boron 0.000416 S/35 (Uppstrom 1974), all as printed in Dickson, Sabine, Christian 2007, Guide to Best Practices, Ch.5 sec.7 (read; PDF in `/home/callensxavier_gmail_com/k2_thirdparty/`, not in the repo). Sulfate, fluoride, phosphate, silicate are zero.

## Controls (all run before the numbers above were used)

| Control | Result |
|---|---|
| P3 printed Guide values (ln K0 -3.5617, log10 K1 -5.8472, log10 K2 -8.9660, ln KB -19.7964, ln KW -30.434 at S 35, 25 C) | all 5 reproduced at printed digits |
| P2 closed form vs 50-digit numerical derivative of DIC(TA), 50 random points | worst relative difference 1.3e-16 |
| P1 PyCO2SYS 1.8.3.4 (Lueker, total scale, sulfate = fluoride = 0), 500 random points, eta from a central 1 umol/kg difference | PyCO2SYS value inside our U0 enclosure of a small neighbourhood box (T +-0.5, S +-0.25, f +-5, TA35 +-5) at 500/500; float agreement worst 4.1e-5 (< 1e-4). Point-box containment 0/500: expected, our point box is 1e-9 wide and PyCO2SYS differs by 4e-5. |
| P1b strong form: PyCO2SYS fed our KW and BT | 100/100 inside our point enclosure (+1e-6), worst relative difference 6.7e-10. The 4e-5 offset is therefore fully explained by two input differences, below. |
| Constant cross-check (`data/const_crosscheck.json`) | K0, K1, K2, KB agree with PyCO2SYS to 1e-14 (independent confirmation of the Guide transcription). KW differs by -1.49% (the Guide subtracts 0.015 from the constant term to approximate the SWS to total conversion; PyCO2SYS converts exactly). BT differs by +0.07% (Guide table rounds Uppstrom's 0.0004157 to 0.000416). |
| N1 K1 and K2 swapped | 100/100 PyCO2SYS values excluded by the corrupted model |
| N2 wrong-sign borate term | 100/100 excluded |
| N3 pCO2 unit error (420 read as atm, x1e6) | box guard rejects; forced root solve finds no root (nan) |
| N4 K1 coefficient 3633.86 -> 3733.86 | log10 K1 = -6.1826, P3 value rejected |
| N5 Lean planted `sorry` and extra axiom | both compile (rc 0); `#print axioms` shows `sorryAx`, resp. `CarbonateK2.ctl_cheat`: caught |
| P4 Jessen reproduction | R 58.13 (printed 58, matches), R 164.24 (printed 165: 0.5% off), v 8.60 and 3.04 cm/yr (printed 8.7 and 3.0), 11.6 to 32.8 yr/m (printed 12 to 34). The printed dq values (45.4, 131.3) are not mutually consistent with the printed inputs (we get 45.71 and 130.59; inputs are "ca."), so P4 is a pass within printed rounding, not to the digit as preregistered. |

## Lean (pinned 4.34.1 + Mathlib, `scripts/certified_numerics/lean_pinned.py`)

`formal_cert/Programmes/CarbonateK2/Core.lean`, rc 0, 14 theorems, each `#print axioms` = {propext, Classical.choice, Quot.sound}; no sorry, native_decide, axiom, unsafe (grep). `leanchecker Programmes.CarbonateK2.Core` rc 0 (68 s). Logs: `logs/lean_core.json`, `logs/lean_controls.json`, `logs/leanchecker_replay.json`. Statements: eta rewrite identity, 0 < eta < 1, derivative identity and sign of Q, delay monotone in CEC, L, k and antitone in q, delay = L R/(q/eps_w), exact rational Jessen instance (R in (58,59), (164,165); yr/m in (11,12), (32,33)).
Scope: the Lean file certifies algebra and the delay closed form only; the interval enclosures of (a) are not replayed in Lean (Tier C). **LEDGER_UNAUDITED_TIER_A** stays open.

## Deviations and caveats (honest list)

1. Constants are pinned to the Dickson et al. 2007 Guide, which transcribes the primary papers; Weiss 1974, Lueker 2000, Dickson 1990, Millero 1995 themselves were not read. The cross-check against PyCO2SYS (K0, K1, K2, KB to 1e-14) lowers but does not remove the transcription risk. Strict reading of the kill criterion: (a) is pinned to a secondary transcription, reported as Tier C with this caveat.
2. Part (b) freshwater K1, K2 are Millero 1979 as transcribed in PyCO2SYS (not a primary source); pK uncertainty +-0.02 is an assumption; activity corrections for soil-water ionic strength are ignored. Tier X. The pH intervals are outer (bracket found by doubling, not tightened), width 0.11.
3. Sigma values for scenarios U1, U2 are the OEDG18 values shipped in PyCO2SYS (secondary source); Lueker's own fit errors were not read. They are input intervals, not probabilities.
4. fCO2 is the independent variable; no fugacity coefficient. Sulfate/fluoride omitted: effect on eta at most 6.8e-5 (Tier X, 100 points, PyCO2SYS). Boron: the Lee et al. 2010 alternative (+4% BT) not computed.
5. P4 tolerance relaxed to printed rounding (see table). P1 "inside the sub-box enclosure" was operationalised as a neighbourhood box of stated size, and P1b was added after seeing the 4e-5 offset.
6. The time box (about 4 agent-hours) was exceeded by wall-clock because the branch-and-bound had to be redesigned twice (first grid enclosures were far too loose: eta in [0.69,0.96] with 12% TA spread per cell). U2 was run with an earlier version of the float root seed in `k2lib.float_root` (anderson solver, later bisection); the h bracket is verified by interval signs so the seed does not affect rigor, but the U2 file hash belongs to that earlier code.
7. Not done: re-running the Jessen PHREEQC model (Tier X item), Dataverse files not downloaded (licence unverified), no Lean replay of the interval enclosures, no literature search beyond memory (hence "to our knowledge").
8. The `grid` entry in `data/seawater_result.json` is a leftover of the abandoned grid design and is not used.

## For an independent auditor to redo

- Re-derive each constant from the primary papers (Weiss 1974, Lueker 2000, Dickson 1990, Millero 1995, Uppstrom 1974), not the Guide.
- Replay the enclosure with a different interval library (python-flint/Arb) and a plain grid; check U0 contains the PyCO2SYS range [0.7559, 0.9314] and that eta at box corners agrees.
- Verify the monotonicity test `eta_increasing_in_h` is a correct sufficient condition (Lean identity `eta_deriv_identity`, then Q <= 0).
- Check the branch-and-bound pruning argument (one-sided point bounds) and that no pruned cell can contain the extremum.
- Confirm the Jessen formula and inputs against the paper (Supplementary Text 2) and the Dataverse model.
- Review the statement locks of `Core.lean`.

## Files

`prereg_K2.json`, `prereg_K2.sha256`, `code/` (k2lib.py, run_seawater.py, run_soil_delay.py, controls_P2_P3.py, const_crosscheck.py, leanchecker_replay.py, write_result_json.py), `data/` (enclosure_U0/U1/U2.json, seawater_result.json, soil_result.json, delay_result.json, const_crosscheck.json), `logs/`, `result.json` (sha256 of every file), Lean in `formal_cert/Programmes/CarbonateK2/`. Run with `taskset -c 6,7 .venv/bin/python -I code/<script> data ...` from the K2 directory (PyCO2SYS 1.8.3.4, GPL-3, installed in the venv only, not redistributed).
